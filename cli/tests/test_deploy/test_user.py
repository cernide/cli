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

from pydantic import ValidationError

from polyaxon.deploy.schemas.root_user import RootUserConfig
from polyaxon.utils.test_utils import BaseTestCase


class TestRootUserConfig(BaseTestCase):
    def test_root_user_config(self):
        bad_config_dicts = [
            {"username": False, "password": "foo", "email": "sdf"},
            {"username": "sdf", "password": "foo", "email": "sdf"},
            {"username": "sdf", "password": "foo", "email": "sdf@boo"},
            {"username": "foo.bar", "password": "foo", "email": "foo@bar.com"},
            {"username": "foo bar", "password": "foo", "email": "foo@bar.com"},
        ]

        for config_dict in bad_config_dicts:
            with self.assertRaises(ValidationError):
                RootUserConfig.from_dict(config_dict)

        config_dict = {"username": "sdf", "password": "foo"}

        config = RootUserConfig.from_dict(config_dict)
        assert config.to_light_dict() == config_dict

        config_dict = {"username": "sdf", "password": "foo", "email": "foo@bar.com"}

        config = RootUserConfig.from_dict(config_dict)
        assert config.to_light_dict() == config_dict
