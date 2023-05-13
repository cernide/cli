from typing import Dict

from polyaxon.api import (
    EXTERNAL_V1_LOCATION,
    REWRITE_EXTERNAL_V1_LOCATION,
    REWRITE_SERVICES_V1_LOCATION,
    SERVICES_V1_LOCATION,
)
from polyaxon.compiler.contexts.base import BaseContextsManager
from polyaxon.connections import V1Connection
from polyaxon.polyflow import V1CompiledOperation
from polyaxon.utils.urls_utils import get_proxy_run_url


class ServiceContextsManager(BaseContextsManager):
    @classmethod
    def resolve(
        cls,
        namespace: str,
        owner_name: str,
        project_name: str,
        run_uuid: str,
        contexts: Dict,
        compiled_operation: V1CompiledOperation,
        connection_by_names: Dict[str, V1Connection],
    ) -> Dict:
        contexts = cls._resolver_replica(
            contexts=contexts,
            init=compiled_operation.run.init,
            connections=compiled_operation.run.connections,
            connection_by_names=connection_by_names,
        )
        if compiled_operation.is_service_run:
            contexts["globals"]["ports"] = compiled_operation.run.ports
            if compiled_operation.run.is_external:
                service = (
                    REWRITE_EXTERNAL_V1_LOCATION
                    if compiled_operation.run.rewrite_path
                    else EXTERNAL_V1_LOCATION
                )
            else:
                service = (
                    REWRITE_SERVICES_V1_LOCATION
                    if compiled_operation.run.rewrite_path
                    else SERVICES_V1_LOCATION
                )
            base_url = get_proxy_run_url(
                service=service,
                namespace=namespace,
                owner=owner_name,
                project=project_name,
                run_uuid=run_uuid,
            )
            contexts["globals"]["base_url"] = base_url

        return contexts
