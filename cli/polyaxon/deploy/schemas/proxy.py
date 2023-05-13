from typing import Optional

from pydantic import Field, StrictInt, StrictStr

from polyaxon.schemas.base import BaseSchemaModel


class ProxyConfig(BaseSchemaModel):
    enabled: Optional[bool]
    use_in_ops: Optional[bool] = Field(alias="useInOps")
    http_proxy: Optional[StrictStr] = Field(alias="httpProxy")
    https_proxy: Optional[StrictStr] = Field(alias="httpsProxy")
    no_proxy: Optional[StrictStr] = Field(alias="noProxy")
    port: Optional[StrictInt]
    host: Optional[StrictStr]
    kind: Optional[StrictStr]
