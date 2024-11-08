from typing import Any, Dict, Iterable, Optional

from clipped.utils.enums import get_enum_value
from clipped.utils.paths import delete_path

from kubernetes import client as k8s_client
from kubernetes.client import Configuration

from polyaxon import settings
from polyaxon._auxiliaries import V1PolyaxonInitContainer, V1PolyaxonSidecarContainer
from polyaxon._compiler import resolver
from polyaxon._compiler.resolver import AgentResolver
from polyaxon._connections import V1Connection, V1ConnectionResource
from polyaxon._contexts import paths as ctx_paths
from polyaxon._flow import V1CompiledOperation
from polyaxon._k8s.converter.converters import CONVERTERS
from polyaxon._k8s.converter.mixins import MIXIN_MAPPING, BaseMixin
from polyaxon._polyaxonfile import (
    CompiledOperationSpecification,
    OperationSpecification,
)
from polyaxon._k8s.manager.async_manager import AsyncK8sManager
from polyaxon._schemas.agent import AgentConfig
from polyaxon._utils.fqn_utils import get_resource_name
from polyaxon.client import V1Run
from polyaxon.exceptions import PolyaxonAgentError, PolyaxonCompilerError


class Executor():
    MIXIN_MAPPING = MIXIN_MAPPING
    CONVERTERS = CONVERTERS

    def __init__(
        self,
        namespace: Optional[str] = None,
        k8s_config: Configuration = None,
        in_cluster: Optional[bool] = None,
    ):
        super().__init__()
        if in_cluster is None:
            in_cluster = settings.CLIENT_CONFIG.in_cluster

        if not namespace:
            namespace = settings.CLIENT_CONFIG.namespace

        self.namespace = namespace
        self.in_cluster = in_cluster
        self.k8s_config = k8s_config

    def _get_manager(self):
        return AsyncK8sManager(
            namespace=self.namespace,
            in_cluster=self.in_cluster,
        )

    async def refresh(self):
        if self._manager:
            await self._manager.close()
        manager = super().refresh()
        await manager.setup()
        return manager

    def create(
        self, run_uuid: str, run_kind: str, resource: Dict, namespace: str = None
    ) -> Dict:
        mixin = self._get_mixin_for_kind(kind=run_kind)
        resource_name = get_resource_name(run_uuid)
        return self.manager.create_custom_object(
            name=resource_name,
            group=mixin.GROUP,
            version=mixin.API_VERSION,
            plural=mixin.PLURAL,
            body=resource,
            namespace=namespace,
        )

    def apply(
        self, run_uuid: str, run_kind: str, resource: Dict, namespace: str = None
    ) -> Dict:
        mixin = self._get_mixin_for_kind(kind=run_kind)
        resource_name = get_resource_name(run_uuid)
        return self.manager.update_custom_object(
            name=resource_name,
            group=mixin.GROUP,
            version=mixin.API_VERSION,
            plural=mixin.PLURAL,
            body=resource,
            namespace=namespace,
        )

    def stop(self, run_uuid: str, run_kind: str, namespace: str = None):
        mixin = self._get_mixin_for_kind(kind=run_kind)
        resource_name = get_resource_name(run_uuid)
        return self.manager.delete_custom_object(
            name=resource_name,
            group=mixin.GROUP,
            version=mixin.API_VERSION,
            plural=mixin.PLURAL,
            namespace=namespace,
        )

    def clean(self, run_uuid: str, run_kind: str, namespace: str = None):
        return self.apply(
            run_uuid=run_uuid,
            run_kind=run_kind,
            resource={"metadata": {"finalizers": None}},
            namespace=namespace,
        )

    def get(self, run_uuid: str, run_kind: str, namespace: str = None):
        mixin = self._get_mixin_for_kind(kind=run_kind)
        resource_name = get_resource_name(run_uuid)
        return self.manager.get_custom_object(
            name=resource_name,
            group=mixin.GROUP,
            version=mixin.API_VERSION,
            plural=mixin.PLURAL,
            namespace=namespace,
        )

    def list_ops(self, namespace: str = None):
        return self.manager.list_custom_objects(
            group=BaseMixin.GROUP,
            version=BaseMixin.API_VERSION,
            plural=BaseMixin.PLURAL,
            namespace=namespace,
        )

    @classmethod
    def _get_mixin_for_kind(cls, kind: str) -> Any:
        m = cls.MIXIN_MAPPING.get(kind)
        if not m:
            raise PolyaxonAgentError(
                "Agent received unrecognized kind {}".format(
                    get_enum_value(kind))
            )
        return m

    @property
    def manager(self):
        if not self._manager:
            self._manager = self._get_manager()
        return self._manager

    def refresh(self):
        self._manager = None
        return self.manager

    def _clean_temp_execution_path(self, run_uuid: str):
        delete_path(ctx_paths.CONTEXT_TMP_RUNS_ROOT_FORMAT.format(run_uuid))

    @classmethod
    def get_resource(
        cls,
        namespace: Optional[str],
        owner_name: str,
        project_name: str,
        run_name: str,
        run_uuid: str,
        run_path: str,
        compiled_operation: V1CompiledOperation,
        artifacts_store: Optional[V1Connection],
        connection_by_names: Optional[Dict[str, V1Connection]],
        secrets: Optional[Iterable[V1ConnectionResource]],
        config_maps: Optional[Iterable[V1ConnectionResource]],
        polyaxon_sidecar: Optional[V1PolyaxonSidecarContainer] = None,
        polyaxon_init: Optional[V1PolyaxonInitContainer] = None,
        default_sa: Optional[str] = None,
        internal_auth: bool = False,
        default_auth: bool = False,
    ):
        if not namespace:
            raise PolyaxonCompilerError(
                "Converter Error. "
                "Namespace is required to create a k8s resource specification."
            )
        if compiled_operation.has_pipeline:
            raise PolyaxonCompilerError(
                "Converter Error. "
                "Specification with matrix/dag/schedule section is not supported in this function."
            )

        run_kind = compiled_operation.get_run_kind()
        if run_kind not in cls.CONVERTERS:
            raise PolyaxonCompilerError(
                "Converter Error. "
                "Specification with run kind: {} is not supported in this deployment version.".format(
                    run_kind
                )
            )

        converter = cls.CONVERTERS[run_kind](
            owner_name=owner_name,
            project_name=project_name,
            run_name=run_name,
            run_uuid=run_uuid,
            namespace=namespace,
            polyaxon_init=polyaxon_init,
            polyaxon_sidecar=polyaxon_sidecar,
            internal_auth=internal_auth,
            run_path=run_path,
        )
        if converter:
            return converter.get_resource(
                compiled_operation=compiled_operation,
                artifacts_store=artifacts_store,
                connection_by_names=connection_by_names,
                secrets=secrets,
                config_maps=config_maps,
                default_sa=default_sa,
                default_auth=default_auth,
            )

    @classmethod
    def convert(
        cls,
        owner_name: str,
        project_name: str,
        run_name: str,
        run_uuid: str,
        content: str,
        default_auth: bool,
        agent_content: Optional[str] = None,
    ) -> Optional[Any]:
        agent_env = AgentResolver.construct()
        compiled_operation = CompiledOperationSpecification.read(content)

        agent_env.resolve(
            compiled_operation=compiled_operation,
            agent_config=AgentConfig.read(
                agent_content) if agent_content else None,
        )
        resource = cls.get_resource(
            owner_name=owner_name,
            project_name=project_name,
            run_name=run_name,
            run_uuid=run_uuid,
            run_path=run_uuid,
            namespace=compiled_operation.namespace or agent_env.namespace,
            compiled_operation=compiled_operation,
            polyaxon_init=agent_env.polyaxon_init,
            polyaxon_sidecar=agent_env.polyaxon_sidecar,
            artifacts_store=agent_env.artifacts_store,
            connection_by_names=agent_env.connection_by_names,
            secrets=agent_env.secrets,
            config_maps=agent_env.config_maps,
            default_auth=default_auth,
            default_sa=agent_env.default_sa,
        )

        api = k8s_client.ApiClient()
        return api.sanitize_for_serialization(resource)

    @classmethod
    def make_and_convert(
        cls,
        owner_name: str,
        project_name: str,
        run_uuid: str,
        run_name: str,
        content: str,
        default_sa: Optional[str] = None,
        internal_auth: bool = False,
        default_auth: bool = False,
    ) -> Optional[Any]:
        operation = OperationSpecification.read(content)
        compiled_operation = OperationSpecification.compile_operation(
            operation)
        resolver_obj, compiled_operation = resolver.resolve(
            compiled_operation=compiled_operation,
            owner_name=owner_name,
            project_name=project_name,
            project_uuid=project_name,
            run_name=run_name,
            run_path=run_uuid,
            run_uuid=run_uuid,
            params=operation.params,
        )
        return cls.get_resource(
            namespace=compiled_operation.namespace or resolver_obj.namespace,
            owner_name=resolver_obj.owner_name,
            project_name=resolver_obj.project_name,
            run_name=resolver_obj.run_name,
            run_path=resolver_obj.run_path,
            run_uuid=resolver_obj.run_uuid,
            compiled_operation=compiled_operation,
            connection_by_names=resolver_obj.connection_by_names,
            internal_auth=internal_auth,
            artifacts_store=resolver_obj.artifacts_store,
            secrets=resolver_obj.secrets,
            config_maps=resolver_obj.config_maps,
            polyaxon_sidecar=resolver_obj.polyaxon_sidecar,
            polyaxon_init=resolver_obj.polyaxon_init,
            default_sa=default_sa,
            default_auth=default_auth,
        )

    def create_from_run(self, response: V1Run, default_auth: bool = False):
        resource = self.convert(
            owner_name=response.owner,
            project_name=response.project,
            run_name=response.name,
            run_uuid=response.uuid,
            default_auth=default_auth,
            content=response.content,
            agent_content=settings.AGENT_CONFIG.to_json(),
        )
        return self.create(
            run_uuid=response.uuid,
            run_kind=response.kind,
            resource=resource,
            namespace=response.settings.namespace if response.settings else None,
        )
