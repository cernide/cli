from typing import Dict, List, Optional, Set, Union

from clipped.types.ref_or_obj import RefField
from pydantic import Field, StrictStr

from polyaxon.contexts import refs as ctx_refs
from polyaxon.lifecycle import V1Statuses
from polyaxon.polyflow.component.base import BaseComponent
from polyaxon.polyflow.events import V1EventKind, V1EventTrigger
from polyaxon.polyflow.joins import V1Join
from polyaxon.polyflow.matrix import MatrixMixin, V1Matrix
from polyaxon.polyflow.schedules import ScheduleMixin, V1Schedule
from polyaxon.polyflow.trigger_policies import V1TriggerPolicy


class BaseOp(BaseComponent, MatrixMixin, ScheduleMixin):
    _FIELDS_SAME_KIND_PATCH = ["schedule", "matrix"]

    schedule: Optional[V1Schedule]
    events: Optional[Union[List[V1EventTrigger], RefField]]
    matrix: Optional[V1Matrix]
    joins: Optional[Union[List[V1Join], RefField]]
    dependencies: Optional[Union[List[StrictStr], RefField]]
    trigger: Optional[Union[V1TriggerPolicy, RefField]]
    conditions: Optional[StrictStr]
    skip_on_upstream_skip: Optional[bool] = Field(alias="skipOnUpstreamSkip")

    def get_matrix_kind(self):
        return self.matrix.kind if self.matrix else None

    def get_schedule_kind(self):
        return self.schedule.kind if self.schedule else None

    def get_upstream_statuses_events(self, upstream: Set) -> Dict[str, V1Statuses]:
        statuses_by_refs = {u: [] for u in upstream}
        events = self.events or []  # type: List[V1EventTrigger]
        for e in events:
            entity_ref = ctx_refs.get_entity_ref(e.ref)
            if not entity_ref:
                continue
            if entity_ref not in statuses_by_refs:
                continue
            for kind in e.kinds:
                status = V1EventKind.get_events_statuses_mapping().get(kind)
                if status:
                    statuses_by_refs[entity_ref].append(status)

        return statuses_by_refs

    def has_events_for_upstream(self, upstream: str) -> bool:
        events = self.events or []  # type: List[V1EventTrigger]
        for e in events:
            entity_ref = ctx_refs.get_entity_ref(e.ref)
            if not entity_ref:
                continue
            if entity_ref == upstream:
                return True

        return False
