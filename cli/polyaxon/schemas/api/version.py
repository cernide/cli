from typing import Optional

from clipped.compact.pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel


class V1Version(BaseSchemaModel):
    min: Optional[StrictStr]
    latest: Optional[StrictStr]
