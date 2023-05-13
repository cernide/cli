from typing import Dict, Iterable, Optional

from kubernetes import client as k8s_client

from polyaxon.auxiliaries import V1PolyaxonInitContainer, V1PolyaxonSidecarContainer
from polyaxon.connections import V1Connection, V1ConnectionResource
from polyaxon.exceptions import PolyaxonCompilerError
from polyaxon.k8s.converter.converters import CONVERTERS
from polyaxon.polyflow import V1CompiledOperation


def convert(
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
) -> Dict:
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
    if run_kind not in CONVERTERS:
        raise PolyaxonCompilerError(
            "Converter Error. "
            "Specification with run kind: {} is not supported in this deployment version.".format(
                run_kind
            )
        )

    converter = CONVERTERS[run_kind](
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
        resource = converter.get_resource(
            compiled_operation=compiled_operation,
            artifacts_store=artifacts_store,
            connection_by_names=connection_by_names,
            secrets=secrets,
            config_maps=config_maps,
            default_sa=default_sa,
            default_auth=default_auth,
        )
        api = k8s_client.ApiClient()
        return api.sanitize_for_serialization(resource)
