#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from polyaxon.env_vars.keys import EV_KEYS_HOME
from polyaxon.schemas.api.home import HomeConfig
from polyaxon.utils.test_utils import BaseTestCase


@pytest.mark.api_mark
class TestHomeConfig(BaseTestCase):
    def test_home_wrong_config(self):
        config_dict = {EV_KEYS_HOME: "foo/bar/moo", "foo": "bar"}
        config = HomeConfig.from_dict(config_dict)
        assert config.to_dict() != config_dict
        config_dict.pop("foo")
        assert config.to_dict() == config_dict

    def test_home_config(self):
        config_dict = {EV_KEYS_HOME: "foo/bar/moo"}
        config = HomeConfig.from_dict(config_dict)
        assert config.to_dict() == config_dict
