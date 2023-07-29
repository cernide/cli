import datetime

from typing import List, Optional

from clipped.compact.pydantic import StrictStr
from clipped.types.uuids import UUIDStr

from polyaxon.schemas.base import BaseResponseModel
from polyaxon.schemas.responses.v1_dashboard_spec import V1DashboardSpec


class V1Dashboard(BaseResponseModel):
    uuid: Optional[UUIDStr]
    name: Optional[StrictStr]
    description: Optional[StrictStr]
    tags: Optional[List[StrictStr]]
    live_state: Optional[int]
    spec: Optional[V1DashboardSpec]
    org_level: Optional[bool]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
