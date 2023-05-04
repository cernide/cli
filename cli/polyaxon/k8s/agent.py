#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import sys
import time

from typing import Dict, Optional

from clipped.utils.versions import clean_version_for_check
from urllib3.exceptions import HTTPError

from polyaxon import pkg, settings
from polyaxon.auxiliaries import V1PolyaxonInitContainer, V1PolyaxonSidecarContainer
from polyaxon.compiler.resolver import AgentResolver
from polyaxon.connections import V1Connection
from polyaxon.k8s import converter
from polyaxon.k8s.executor.executor import Executor
from polyaxon.lifecycle import V1StatusCondition, V1Statuses
from polyaxon.polyaxonfile import CompiledOperationSpecification, OperationSpecification
from polyaxon.runner.agent import BaseAgent
from polyaxon.schemas.cli.agent_config import AgentConfig
from polyaxon.schemas.responses.v1_agent import V1Agent
from polyaxon.schemas.responses.v1_agent_state_response import V1AgentStateResponse
from polyaxon.sdk.exceptions import ApiException


class Agent(BaseAgent):
    def __init__(self, owner: str, agent_uuid: str):
        super().__init__(sleep_interval=None)

        self.owner = owner
        self.agent_uuid = agent_uuid
        self.executor = Executor()
        self._register()

    def _register(self):
        print("Agent is starting.")
        try:
            agent = self.get_info()
            self._check_status(agent)
            self.sync()
            self.log_agent_running()
            print("Agent is running.")
        except (ApiException, HTTPError) as e:
            self.log_agent_failed(
                message="Could not start the agent {}.".format(repr(e))
            )
            sys.exit(1)
        atexit.register(self._wait)

    def _wait(self):
        if not self._graceful_shutdown:
            self.log_agent_warning()
        time.sleep(1)

    def _make_and_convert(
        self,
        owner_name: str,
        project_name: str,
        run_uuid: str,
        run_name: str,
        content: str,
        default_auth: bool = False,
    ):
        operation = OperationSpecification.read(content)
        compiled_operation = OperationSpecification.compile_operation(operation)
        return converter.make(
            owner_name=owner_name,
            project_name=project_name,
            project_uuid=project_name,
            run_uuid=run_uuid,
            run_name=run_name,
            run_path=run_uuid,
            compiled_operation=compiled_operation,
            params=operation.params,
            default_auth=default_auth,
        )

    def _convert(
        self,
        owner_name: str,
        project_name: str,
        run_name: str,
        run_uuid: str,
        content: str,
        default_auth: bool,
        agent_content: Optional[str] = None,
    ):
        agent_env = AgentResolver.construct()
        compiled_operation = CompiledOperationSpecification.read(content)

        agent_env.resolve(
            compiled_operation=compiled_operation,
            agent_config=AgentConfig.read(agent_content) if agent_content else None,
        )
        return converter.convert(
            compiled_operation=compiled_operation,
            owner_name=owner_name,
            project_name=project_name,
            run_name=run_name,
            run_uuid=run_uuid,
            namespace=agent_env.namespace,
            polyaxon_init=agent_env.polyaxon_init,
            polyaxon_sidecar=agent_env.polyaxon_sidecar,
            run_path=run_uuid,
            artifacts_store=agent_env.artifacts_store,
            connection_by_names=agent_env.connection_by_names,
            secrets=agent_env.secrets,
            config_maps=agent_env.config_maps,
            default_sa=agent_env.default_sa,
            default_auth=default_auth,
        )

    def get_info(self) -> V1Agent:
        return self.client.agents_v1.get_agent(owner=self.owner, uuid=self.agent_uuid)

    def get_state(self) -> V1AgentStateResponse:
        return self.client.agents_v1.get_agent_state(
            owner=self.owner, uuid=self.agent_uuid
        )

    def log_agent_status(
        self, status: str, reason: Optional[str] = None, message: Optional[str] = None
    ):
        status_condition = V1StatusCondition.get_condition(
            type=status, status=True, reason=reason, message=message
        )
        self.client.agents_v1.create_agent_status(
            owner=self.owner,
            uuid=self.agent_uuid,
            body={"condition": status_condition},
            async_req=True,
        )

    def sync(self):
        self.client.agents_v1.sync_agent(
            owner=self.owner,
            agent_uuid=self.agent_uuid,
            body=V1Agent(
                content=settings.AGENT_CONFIG.to_json(),
                version=clean_version_for_check(pkg.VERSION),
                version_api=self.executor.k8s_manager.get_version(),
            ),
        )

    def sync_compatible_updates(self, compatible_updates: Dict):
        if compatible_updates and settings.AGENT_CONFIG:
            init = compatible_updates.get("init")
            if init and settings.AGENT_CONFIG.init:
                init = V1PolyaxonInitContainer.from_dict(init)
                settings.AGENT_CONFIG.init = settings.AGENT_CONFIG.init.patch(init)

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
            self.sync()

    def log_agent_running(self):
        self.log_agent_status(status=V1Statuses.RUNNING, reason="AgentLogger")

    def log_agent_failed(self, message=None):
        self.log_agent_status(
            status=V1Statuses.FAILED, reason="AgentLogger", message=message
        )

    def log_agent_warning(self):
        self.log_agent_status(
            status=V1Statuses.WARNING,
            reason="AgentLogger",
            message="The agent was interrupted, please check your deployment.",
        )