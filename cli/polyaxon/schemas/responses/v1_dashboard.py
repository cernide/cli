import datetime

from typing import List, Optional

from clipped.types.uuids import UUIDStr
from pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel
from polyaxon.schemas.responses.v1_dashboard_spec import V1DashboardSpec


class V1Dashboard(BaseSchemaModel):
    uuid: Optional[UUIDStr]
    name: Optional[StrictStr]
    description: Optional[StrictStr]
    tags: Optional[List[StrictStr]]
    live_state: Optional[int]
    spec: Optional[V1DashboardSpec]
    org_level: Optional[bool]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
