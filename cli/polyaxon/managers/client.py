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
import os

from polyaxon.config_reader.manager import ConfigManager
from polyaxon.config_reader.spec import ConfigSpec
from polyaxon.managers.base import BaseConfigManager
from polyaxon.schemas.cli.client_config import ClientConfig


class ClientConfigManager(BaseConfigManager):
    """Manages client configuration .client file."""

    VISIBILITY = BaseConfigManager.VISIBILITY_GLOBAL
    CONFIG_FILE_NAME = ".client"
    CONFIG = ClientConfig

    @classmethod
    def get_config_from_env(cls, **kwargs) -> ClientConfig:
        tmp_path = cls.get_tmp_config_path()
        glob_path = cls.get_global_config_path()

        config = ConfigManager.read_configs(
            [
                ConfigSpec(tmp_path, config_type=".json", check_if_exists=False),
                ConfigSpec(glob_path, config_type=".json", check_if_exists=False),
                os.environ,
            ]
        )
        return ClientConfig.from_dict(config.data)
