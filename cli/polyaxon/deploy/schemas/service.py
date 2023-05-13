from typing import Dict, List, Optional

from pydantic import Extra, Field, StrictInt, StrictStr

from polyaxon.deploy.schemas.celery import CeleryConfig
from polyaxon.deploy.schemas.service_types import ServiceTypes
from polyaxon.schemas.base import BaseSchemaModel
from polyaxon.schemas.services import BaseServiceConfig


class DeploymentService(BaseServiceConfig):
    enabled: Optional[bool]
    replicas: Optional[StrictInt]
    concurrency: Optional[StrictInt]
    scheme: Optional[StrictStr]


class WorkerServiceConfig(DeploymentService):
    celery: Optional[CeleryConfig]


class AgentServiceConfig(DeploymentService):
    instance: Optional[StrictStr]
    token: Optional[StrictStr]
    is_replica: Optional[bool] = Field(alias="isReplica")
    compressed_logs: Optional[bool] = Field(alias="compressedLogs")


class OperatorServiceConfig(DeploymentService):
    skip_crd: Optional[bool] = Field(alias="skipCRD")


class BaseService(BaseSchemaModel):
    name: Optional[StrictStr]
    type: Optional[ServiceTypes]
    port: Optional[StrictInt]
    target_port: Optional[StrictInt] = Field(alias="targetPort")
    node_port: Optional[StrictInt] = Field(alias="nodePort")
    annotations: Optional[Dict]

    class Config:
        extra = Extra.allow


class ApiServiceConfig(DeploymentService):
    service: Optional[BaseService]


class HooksConfig(DeploymentService):
    load_fixtures: Optional[bool] = Field(alias="loadFixtures")
    tables: Optional[bool] = Field(alias="tables")
    sync_db: Optional[bool] = Field(alias="syncdb")
    admin_user: Optional[bool] = Field(alias="adminUser")


class ThirdPartyService(DeploymentService):
    persistence: Optional[Dict]

    class Config:
        extra = Extra.allow


class PostgresqlConfig(ThirdPartyService):
    auth: Optional[Dict]
    conn_max_age: Optional[StrictInt] = Field(alias="connMaxAge")


class RedisConfig(ThirdPartyService):
    image: Optional[Dict]  # type: ignore[assignment]
    non_broker: Optional[bool] = Field(alias="nonBroker")
    use_password: Optional[bool] = Field(alias="usePassword")
    auth: Optional[Dict]


class RabbitmqConfig(ThirdPartyService):
    auth: Optional[Dict]


class ExternalService(BaseSchemaModel):
    user: Optional[StrictStr]
    password: Optional[StrictStr]
    host: Optional[StrictStr]
    port: Optional[StrictInt]
    database: Optional[StrictStr]
    use_password: Optional[bool] = Field(alias="usePassword")
    conn_max_age: Optional[StrictInt] = Field(alias="connMaxAge")
    pgbouncer: Optional[Dict]
    options: Optional[Dict]
    use_resolver: Optional[bool] = Field(alias="useResolver")
    corporate_proxy: Optional[StrictStr] = Field(alias="corporateProxy")


class ExternalBackend(BaseSchemaModel):
    enabled: Optional[bool]
    backend: Optional[StrictStr]
    options: Optional[Dict]


class AuthServicesConfig(BaseSchemaModel):
    github: Optional[ExternalBackend]
    gitlab: Optional[ExternalBackend]
    bitbucket: Optional[ExternalBackend]
    google: Optional[ExternalBackend]
    saml: Optional[ExternalBackend]


class ExternalServicesConfig(BaseSchemaModel):
    redis: Optional[ExternalService]
    rabbitmq: Optional[ExternalService]
    postgresql: Optional[ExternalService]
    gateway: Optional[ExternalService]
    api: Optional[ExternalService]
    transactions: Optional[ExternalBackend]
    analytics: Optional[ExternalBackend]
    metrics: Optional[ExternalBackend]
    errors: Optional[ExternalBackend]
    auth: Optional[AuthServicesConfig]
    allowed_versions: Optional[List[StrictStr]] = Field(alias="allowedVersions")
