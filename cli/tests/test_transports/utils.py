from polyaxon import settings
from polyaxon.utils.test_utils import BaseTestCase


class BaseTestCaseTransport(BaseTestCase):
    def setUp(self):
        super().setUp()
        settings.MIN_TIMEOUT = 0.001
