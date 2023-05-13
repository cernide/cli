import datetime

from typing import Optional

from clipped.types.email import EmailStr
from pydantic import StrictStr

from polyaxon.schemas.base import BaseSchemaModel


class V1TeamMember(BaseSchemaModel):
    user: Optional[StrictStr]
    user_email: Optional[EmailStr]
    role: Optional[StrictStr]
    org_role: Optional[StrictStr]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
