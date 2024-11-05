import asyncio
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Tuple, Type
from urllib3.exceptions import HTTPError

from clipped.utils.tz import now
from clipped.utils.versions import clean_version_for_check
from clipped.utils.workers import async_exit_context, get_wait
from kubernetes.client.rest import ApiException

from polyaxon import pkg, settings
from polyaxon._auxiliaries import V1PolyaxonInitContainer, V1PolyaxonSidecarContainer
from polyaxon._connections import V1Connection
from polyaxon._constants.globals import DEFAULT
from polyaxon._env_vars.getters import get_run_info
from polyaxon._k8s.client import Client
from polyaxon._schemas.checks import ChecksConfig
from polyaxon._schemas.lifecycle import LiveState, V1Statuses
from polyaxon._sdk.schemas.v1_agent import V1Agent
from polyaxon._sdk.schemas.v1_agent_state_response import V1AgentStateResponse
from polyaxon._utils.fqn_utils import get_run_instance
from polyaxon._k8s.executor import Executor
from polyaxon.client import V1AgentStateResponse
from polyaxon.exceptions import ApiException as SDKApiException
from polyaxon.exceptions import PolyaxonAgentError, PolyaxonConverterError
from polyaxon.logger import logger


class Agent():
    EXECUTOR = Executor
    HEALTH_FILE = "/tmp/.healthz"
    SLEEP_STOP_TIME = 60 * 5
    SLEEP_ARCHIVED_TIME = 60 * 60
    SLEEP_AGENT_DATA_COLLECT_TIME = 60 * 30
    IS_ASYNC = True

    def __init__(
        self,
        owner: Optional[str] = None,
        agent_uuid: Optional[str] = None,
        max_interval: Optional[int] = None,
    ):
        self.max_interval = 6 if agent_uuid else 4
        if max_interval:
            self.max_interval = max(max_interval, 3)
        if not agent_uuid and not owner:
            owner = DEFAULT
        self.executor = None
        self._default_auth = bool(agent_uuid)
        self._executor_refreshed_at = now()
        self._graceful_shutdown = False
        self._last_reconciled_at = now()
        self.client = Client(
            owner=owner, agent_uuid=agent_uuid, is_async=self.IS_ASYNC
        )
        self.executor = self.EXECUTOR()
        self.content = settings.AGENT_CONFIG.to_json()

    def cron(self):
        return self.client.cron_agent()

    def collect_agent_data(self):
        logger.info("Collecting agent data.")
        self._last_reconciled_at = now()
        try:
            return self.client.collect_agent_data(
                namespace=settings.CLIENT_CONFIG.namespace
            )
        except Exception as e:
            logger.warning(
                "Agent failed to collect agent data: {}\n"
                "Retrying ...".format(repr(e))
            )

    def sync_compatible_updates(self, compatible_updates: Dict):
        if compatible_updates and settings.AGENT_CONFIG:
            init = compatible_updates.get("init")
            if init and settings.AGENT_CONFIG.init:
                init = V1PolyaxonInitContainer.from_dict(init)
                settings.AGENT_CONFIG.init = settings.AGENT_CONFIG.init.patch(
                    init)

            sidecar = compatible_updates.get("sidecar")
            if sidecar and settings.AGENT_CONFIG.sidecar:
                sidecar = V1PolyaxonSidecarContainer.from_dict(sidecar)
                settings.AGENT_CONFIG.sidecar = settings.AGENT_CONFIG.sidecar.patch(
                    sidecar
                )
            connections = compatible_updates.get("connections")
            if connections:
                settings.AGENT_CONFIG.connections = [
                    V1Connection.from_dict(c) for c in connections
                ]

            self.content = settings.AGENT_CONFIG.to_json()
            return self.sync()

    @classmethod
    def get_healthz_config(cls) -> Optional[ChecksConfig]:
        try:
            return ChecksConfig.read(cls.HEALTH_FILE, config_type=".json")
        except Exception:  # noqa
            return None

    @classmethod
    def ping(cls):
        if not settings.AGENT_CONFIG.enable_health_checks:
            return
        ChecksConfig.init_file(cls.HEALTH_FILE)
        config = cls.get_healthz_config()
        if config:
            config.last_check = now()
            config.write(cls.HEALTH_FILE, mode=config._WRITE_MODE)

    @classmethod
    def pong(cls, interval: int = 15) -> bool:
        config = cls.get_healthz_config()
        if not config:
            return False
        return not config.should_check(interval=interval)

    def end(self, sleep: Optional[int] = None):
        self._graceful_shutdown = True
        if sleep:
            time.sleep(sleep)
        else:
            logger.info("Agent is shutting down.")

    def _check_status(self, agent_state):
        if agent_state.status == V1Statuses.STOPPED:
            logger.warning(
                "Agent has been stopped from the platform,"
                "but the deployment is still running."
                "Please either set the agent to starting or teardown the agent deployment."
            )
            return self.end(sleep=self.SLEEP_STOP_TIME)
        elif agent_state.live_state < LiveState.LIVE:
            logger.warning(
                "Agent has been archived from the platform,"
                "but the deployment is still running."
                "Please either restore the agent or teardown the agent deployment."
            )
            return self.end(sleep=self.SLEEP_ARCHIVED_TIME)

    def make_run_resource(
        self,
        owner_name: str,
        project_name: str,
        run_name: str,
        run_uuid: str,
        content: str,
        default_auth: bool = False,
    ) -> Optional[Any]:
        try:
            return self.executor.make_and_convert(
                owner_name=owner_name,
                project_name=project_name,
                run_uuid=run_uuid,
                run_name=run_name,
                content=content,
                default_auth=default_auth,
            )
        except PolyaxonConverterError as e:
            logger.info(
                "Run could not be cleaned. Agent failed converting run manifest: {}\n{}".format(
                    repr(e), traceback.format_exc()
                )
            )
        except Exception as e:
            logger.info(
                "Agent failed during compilation with unknown exception: {}\n{}".format(
                    repr(e), traceback.format_exc()
                )
            )
        return None

    async def _enter(self):
        if not self.client._is_managed:
            return self
        logger.warning("Agent is starting.")
        await self.executor.refresh()
        try:
            agent = self.client.get_info()
            self._check_status(agent)
            await self.sync()
            self.client.log_agent_running()
            logger.warning("Agent is running.")
            return self
        except (ApiException, SDKApiException, HTTPError) as e:
            message = "Could not start the agent."
            if e.status == 404:
                reason = "Agent not found."
            elif e.status == 403:
                reason = "Agent is not approved yet or has invalid token."
            else:
                reason = "Error {}.".format(repr(e))
            self.client.log_agent_failed(
                message="{} {}".format(message, reason))
            raise PolyaxonAgentError(message="{} {}".format(message, reason))
        except Exception as e:
            raise PolyaxonAgentError from e

    async def _exit(self):
        if not self.client._is_managed:
            return
        if not self._graceful_shutdown:
            self.client.log_agent_warning()
        await asyncio.sleep(1)

    async def __aenter__(self):
        return await self._enter()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit()

    async def refresh_executor(self):
        if (
            now() - self._executor_refreshed_at
        ).total_seconds() > settings.AGENT_CONFIG.get_executor_refresh_interval():
            logger.debug("Refreshing executor ... ")
            await self.executor.refresh()
            self._executor_refreshed_at = now()

    async def sync(self):
        version_api = await self.executor.manager.get_version()
        return self.client.sync_agent(
            agent=V1Agent(
                content=settings.AGENT_CONFIG.to_json(),
                version=clean_version_for_check(pkg.VERSION),
                version_api=version_api,
            ),
        )

    async def reconcile(self):
        if (
            now() - self._last_reconciled_at
        ).total_seconds() > self.SLEEP_AGENT_DATA_COLLECT_TIME:
            return

        # Collect data
        await self.collect_agent_data()

        # Update reconcile
        namespaces = [settings.AGENT_CONFIG.namespace]
        namespaces += settings.AGENT_CONFIG.additional_namespaces or []
        ops = []
        for namespace in namespaces:
            _ops = await self.executor.list_ops(namespace=namespace)
            if _ops:
                ops += [
                    (
                        get_run_instance(
                            owner=op["metadata"]["annotations"][
                                "operation.polyaxon.com/owner"
                            ],
                            project=op["metadata"]["annotations"][
                                "operation.polyaxon.com/project"
                            ],
                            run_uuid=op["metadata"]["labels"][
                                "app.kubernetes.io/instance"
                            ],
                        ),
                        op["metadata"]["annotations"]["operation.polyaxon.com/kind"],
                        op["metadata"]["annotations"]["operation.polyaxon.com/name"],
                        namespace,
                    )
                    for op in _ops
                ]
        if not ops:
            return None

        logger.info("Reconcile agent.")
        return self.client.reconcile_agent(
            reconcile={"ops": ops},
        )

    async def start(self):
        try:
            async with async_exit_context() as exit_event:
                index = 0
                timeout = get_wait(index, max_interval=self.max_interval)

                while True:
                    try:
                        await asyncio.wait_for(exit_event.wait(), timeout=timeout)
                        break  # If exit_event is set, we break out of the loop
                    except asyncio.TimeoutError:
                        index += 1
                        await self.refresh_executor()
                        if self._default_auth:
                            await self.reconcile()
                        else:
                            await self.cron()
                        agent_state = await self.process()
                        if not agent_state:
                            logger.warning(
                                "Agent state is empty, waiting for next check."
                            )
                            index = self.max_interval
                            continue
                        self._check_status(agent_state)
                        if agent_state.state.full:
                            index = 2
                        self.ping()
                        timeout = get_wait(
                            index, max_interval=self.max_interval)
                        logger.info("Sleeping for {} seconds".format(timeout))
        except Exception as e:
            logger.warning("Agent failed to start: {}".format(repr(e)))
        finally:
            self.end()

    async def process(self, **kwargs) -> V1AgentStateResponse:
        try:
            agent_state = self.client.get_state()
            if agent_state.compatible_updates:
                self.sync_compatible_updates(agent_state.compatible_updates)

            if agent_state:
                logger.info("Checking agent state.")
            else:
                logger.info("No state was found.")
                return V1AgentStateResponse.construct()

            state = agent_state.state
            if not state:
                return agent_state
            for run_data in state.schedules or []:
                await self.submit_run(run_data)
            for run_data in state.queued or []:
                await self.submit_run(run_data)
            for run_data in state.checks or []:
                await self.check_run(run_data)
            for run_data in state.stopping or []:
                await self.stop_run(run_data)
            for run_data in state.apply or []:
                await self.apply_run(run_data)
            for run_data in state.deleting or []:
                await self.delete_run(run_data)
            for run_data in state.hooks or []:
                await self.make_and_create_run(run_data)
            for run_data in state.watchdogs or []:
                await self.make_and_create_run(run_data)
            for run_data in state.tuners or []:
                await self.make_and_create_run(run_data, True)
            return agent_state
        except Exception as exc:
            logger.error(exc)
            return V1AgentStateResponse.construct()

    async def prepare_run_resource(
        self,
        owner_name: str,
        project_name: str,
        run_name: str,
        run_uuid: str,
        content: str,
    ) -> Optional[Any]:
        try:
            return self.executor.convert(
                owner_name=owner_name,
                project_name=project_name,
                run_name=run_name,
                run_uuid=run_uuid,
                content=content,
                default_auth=self._default_auth,
                agent_content=self.content,
            )
        except PolyaxonConverterError as e:
            self.client.log_run_failed(
                run_owner=owner_name,
                run_project=project_name,
                run_uuid=run_uuid,
                exc=e,
                message="Agent failed converting run manifest.\n",
            )
        except Exception as e:
            self.client.log_run_failed(
                run_owner=owner_name,
                run_project=project_name,
                run_uuid=run_uuid,
                exc=e,
                message="Agent failed during compilation with unknown exception.\n",
            )
        return None

    async def submit_run(self, run_data: Tuple[str, str, str, str, str]):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        resource = await self.prepare_run_resource(
            owner_name=run_owner,
            project_name=run_project,
            run_name=run_data[2],
            run_uuid=run_uuid,
            content=run_data[3],
        )
        if not resource:
            return

        namespace = None if len(run_data) < 5 else run_data[4]
        try:
            await self.executor.create(
                run_uuid=run_uuid,
                run_kind=run_data[1],
                resource=resource,
                namespace=namespace,
            )
        except ApiException as e:
            if e.status == 409:
                logger.info(
                    "Run already running, triggering an apply mechanism.")
                await self.apply_run(run_data=run_data)
            else:
                logger.info("Run submission error.")
                self.client.log_run_failed(
                    run_owner=run_owner,
                    run_project=run_project,
                    run_uuid=run_uuid,
                    exc=e,
                )
        except Exception as e:
            self.client.log_run_failed(
                run_owner=run_owner,
                run_project=run_project,
                run_uuid=run_uuid,
                exc=e,
            )

    async def make_and_create_run(
        self, run_data: Tuple[str, str, str, str, str], default_auth: bool = False
    ):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        resource = await self.make_run_resource(
            owner_name=run_owner,
            project_name=run_project,
            run_name=run_data[2],
            run_uuid=run_uuid,
            content=run_data[3],
            default_auth=default_auth,
        )
        if not resource:
            return

        namepsace = None if len(run_data) < 5 else run_data[4]

        try:
            await self.executor.create(
                run_uuid=run_uuid,
                run_kind=run_data[1],
                resource=resource,
                namespace=namepsace,
            )
        except ApiException as e:
            if e.status == 409:
                logger.info(
                    "Run already running, triggering an apply mechanism.")
            else:
                logger.info("Run submission error.")
        except Exception as e:
            logger.info(
                "Run could not be cleaned. Agent failed converting run manifest: {}\n{}".format(
                    repr(e), traceback.format_exc()
                )
            )

    async def apply_run(self, run_data: Tuple[str, str, str, str, str]):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        resource = await self.prepare_run_resource(
            owner_name=run_owner,
            project_name=run_project,
            run_name=run_data[2],
            run_uuid=run_uuid,
            content=run_data[3],
        )
        if not resource:
            return

        namespace = None if len(run_data) < 5 else run_data[4]

        try:
            await self.executor.apply(
                run_uuid=run_uuid,
                run_kind=run_data[1],
                resource=resource,
                namespace=namespace,
            )
            self.client.log_run_running(
                run_owner=run_owner, run_project=run_project, run_uuid=run_uuid
            )
        except Exception as e:
            self.client.log_run_failed(
                run_owner=run_owner, run_project=run_project, run_uuid=run_uuid, exc=e
            )
            await self.clean_run(
                run_uuid=run_uuid, run_kind=run_data[1], namespace=namespace
            )

    async def check_run(self, run_data: Tuple[str, str, str]):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        namespace = None if len(run_data) < 3 else run_data[2]
        try:
            await self.executor.get(
                run_uuid=run_uuid, run_kind=run_data[1], namespace=namespace
            )
        except ApiException as e:
            if e.status == 404:
                logger.info(
                    "Run does not exist anymore, it could have been stopped or deleted."
                )
                self.client.log_run_stopped(
                    run_owner=run_owner, run_project=run_project, run_uuid=run_uuid
                )

    async def stop_run(self, run_data: Tuple[str, str, str]):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        namespace = None if len(run_data) < 3 else run_data[2]
        try:
            await self.executor.stop(
                run_uuid=run_uuid, run_kind=run_data[1], namespace=namespace
            )
        except ApiException as e:
            if e.status == 404:
                logger.info(
                    "Run does not exist anymore, it could have been stopped.")
                self.client.log_run_stopped(
                    run_owner=run_owner, run_project=run_project, run_uuid=run_uuid
                )
        except Exception as e:
            self.client.log_run_failed(
                run_owner=run_owner,
                run_project=run_project,
                run_uuid=run_uuid,
                exc=e,
                message="Agent failed stopping run.\n",
            )

    async def delete_run(self, run_data: Tuple[str, str, str, str, str]):
        run_owner, run_project, run_uuid = get_run_info(
            run_instance=run_data[0])
        namespace = None if len(run_data) < 5 else run_data[4]
        if run_data[3]:
            await self.make_and_create_run(run_data)
        else:
            await self.clean_run(
                run_uuid=run_uuid, run_kind=run_data[1], namespace=namespace
            )

    async def clean_run(self, run_uuid: str, run_kind: str, namespace: str = None):
        try:
            await self.executor.clean(
                run_uuid=run_uuid, run_kind=run_kind, namespace=namespace
            )
            await self.executor.stop(
                run_uuid=run_uuid, run_kind=run_kind, namespace=namespace
            )
        except ApiException as e:
            if e.status == 404:
                logger.info("Run does not exist.")
        except Exception as e:
            logger.info(
                "Run could not be cleaned: {}\n{}".format(
                    repr(e), traceback.format_exc()
                )
            )
