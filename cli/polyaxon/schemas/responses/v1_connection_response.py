import datetime

from typing import List, Optional

from clipped.compact.pydantic import StrictStr
from clipped.types.uuids import UUIDStr

from polyaxon.connections import V1ConnectionKind
from polyaxon.schemas.base import BaseResponseModel


class V1ConnectionResponse(BaseResponseModel):
    uuid: Optional[UUIDStr]
    name: Optional[StrictStr]
    agent: Optional[StrictStr]
    description: Optional[StrictStr]
    tags: Optional[List[StrictStr]]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    live_state: Optional[int]
    kind: Optional[V1ConnectionKind]
