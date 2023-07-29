from typing_extensions import Literal

from clipped.compact.pydantic import StrictStr

from polyaxon.polyflow.references.mixin import RefMixin
from polyaxon.schemas.base import BaseSchemaModel


class V1HubRef(BaseSchemaModel, RefMixin):
    _IDENTIFIER = "hub_ref"
    _USE_DISCRIMINATOR = True

    kind: Literal[_IDENTIFIER] = _IDENTIFIER
    name: StrictStr

    def get_kind_value(self):
        return self.name
