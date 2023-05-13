from typing import Any, Dict, List, Optional

from pydantic import StrictStr

from polyaxon.schemas import V1RunPending
from polyaxon.schemas.base import BaseSchemaModel


class V1OperationBody(BaseSchemaModel):
    content: Optional[StrictStr]
    is_managed: Optional[bool]
    pending: Optional[V1RunPending]
    name: Optional[StrictStr]
    description: Optional[StrictStr]
    tags: Optional[List[StrictStr]]
    meta_info: Optional[Dict[str, Any]]
