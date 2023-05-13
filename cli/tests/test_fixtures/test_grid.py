import pytest

from polyaxon.polyflow import V1Operation
from polyaxon.utils.fixtures import get_fxt_grid_with_inputs_outputs
from polyaxon.utils.test_utils import BaseTestCase


@pytest.mark.fixtures_mark
class TestGridsFixtures(BaseTestCase):
    def test_fxt_grid_with_inputs_outputs(self):
        config = get_fxt_grid_with_inputs_outputs()
        assert V1Operation.read(config).to_dict() == config
