from typing import List, Optional

from pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel
from polyaxon.schemas.responses.v1_tag import V1Tag


class V1ListTagsResponse(BaseSchemaModel):
    count: Optional[int]
    results: Optional[List[V1Tag]]
    previous: Optional[StrictStr]
    next: Optional[StrictStr]
