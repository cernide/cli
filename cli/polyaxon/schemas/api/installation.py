from typing import List, Optional

from pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel


class V1Installation(BaseSchemaModel):
    key: Optional[StrictStr]
    version: Optional[StrictStr]
    dist: Optional[StrictStr]
    host: Optional[StrictStr]
    hmac: Optional[StrictStr]
    auth: Optional[List[StrictStr]]
