from typing import Optional

from clipped.types.email import EmailStr
from pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel


class V1User(BaseSchemaModel):
    username: Optional[StrictStr]
    email: Optional[EmailStr]
    name: Optional[StrictStr]
    kind: Optional[StrictStr]
    theme: Optional[int]
    organization: Optional[StrictStr]
