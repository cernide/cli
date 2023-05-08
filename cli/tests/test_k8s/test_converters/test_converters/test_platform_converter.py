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

from polyaxon import settings
from polyaxon.api import VERSION_V1
from polyaxon.env_vars.keys import EV_KEYS_PLATFORM_HOST
from polyaxon.exceptions import PolyaxonConverterError
from polyaxon.k8s.converter.common.env_vars import get_service_env_vars
from polyaxon.k8s.converter.converters.base import BaseConverter
from polyaxon.services.auth import AuthenticationTypes
from polyaxon.services.headers import PolyaxonServiceHeaders
from polyaxon.services.values import PolyaxonServices
from polyaxon.utils.test_utils import BaseTestCase


class DummyConverter(BaseConverter):
    SPEC_KIND = "dummy"
    API_VERSION = "v1alpha1"
    PLURAL = "dummies"
    GROUP = "dummy"
    K8S_ANNOTATIONS_KIND = "dummies_name"
    K8S_LABELS_COMPONENT = "dummies_component"
    K8S_LABELS_PART_OF = "dummies_part_of"
    MAIN_CONTAINER_ID = "dummy"

    def get_main_env_vars(self, external_host: bool = False, **kwargs):
        pass

    def get_resource(self, **kwargs):
        pass


class TestBaseConverter(BaseTestCase):
    SET_AGENT_SETTINGS = True

    def setUp(self):
        super().setUp()
        settings.AGENT_CONFIG.app_secret_name = "polyaxon"
        settings.AGENT_CONFIG.agent_secret_name = "agent"
        settings.CLIENT_CONFIG.host = "https://polyaxon.com"
        self.converter = DummyConverter(
            owner_name="owner-name",
            project_name="project-name",
            run_name="run-name",
            run_uuid="run_uuid",
        )

    def test_get_service_env_vars(self):
        # Call with default
        env_vars = self.converter._get_service_env_vars(service_header=None)
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=None,
            log_level=None,
            authentication_type=None,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=False,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )

        self.converter.internal_auth = True
        env_vars = self.converter._get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            include_secret_key=True,
            include_internal_token=True,
            include_agent_token=False,
            authentication_type="internal",
        )
        assert env_vars == get_service_env_vars(
            header="header-foo",
            service_header="sa-foo",
            authentication_type="internal",
            include_secret_key=True,
            include_internal_token=True,
            include_agent_token=False,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )

        self.converter.internal_auth = False
        env_vars = self.converter._get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
        )
        assert env_vars == get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        env_vars = self.converter._get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            external_host=True,
        )
        # Default platform host
        assert env_vars == get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        # Setting an env var for the EV_KEYS_PLATFORM_HOST and LOG_LEVEL
        current = os.environ.get(EV_KEYS_PLATFORM_HOST)
        os.environ[EV_KEYS_PLATFORM_HOST] = "foo"
        env_vars = self.converter._get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            log_level="info",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            external_host=True,
        )
        assert env_vars == get_service_env_vars(
            service_header="sa-foo",
            header="header-foo",
            authentication_type="internal",
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level="info",
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host="foo",
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        if current:
            os.environ[EV_KEYS_PLATFORM_HOST] = current
        else:
            del os.environ[EV_KEYS_PLATFORM_HOST]

        with self.assertRaises(PolyaxonConverterError):
            self.converter._get_service_env_vars(
                service_header="sa-foo",
                header="header-foo",
                include_secret_key=False,
                include_internal_token=True,
                include_agent_token=True,
                authentication_type="internal",
                log_level="info",
            )

    def test_get_auth_service_env_vars(self):
        self.converter.internal_auth = True
        env_vars = self.converter.get_auth_service_env_vars()
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.INTERNAL,
            service_header=PolyaxonServices.INITIALIZER,
            authentication_type=AuthenticationTypes.INTERNAL_TOKEN,
            include_secret_key=False,
            include_internal_token=True,
            include_agent_token=False,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )

        self.converter.internal_auth = False
        env_vars = self.converter.get_auth_service_env_vars(log_level="info")
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.INITIALIZER,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level="info",
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        env_vars = self.converter.get_auth_service_env_vars(external_host=True)
        # Default platform host
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.INITIALIZER,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        # Setting an env var for the EV_KEYS_PLATFORM_HOST
        current = os.environ.get(EV_KEYS_PLATFORM_HOST)
        os.environ[EV_KEYS_PLATFORM_HOST] = "foo"
        env_vars = self.converter.get_auth_service_env_vars(external_host=True)
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.INITIALIZER,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=True,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host="foo",
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        if current:
            os.environ[EV_KEYS_PLATFORM_HOST] = current
        else:
            del os.environ[EV_KEYS_PLATFORM_HOST]

    def test_get_polyaxon_sidecar_service_env_vars(self):
        self.converter.internal_auth = True
        env_vars = self.converter.get_polyaxon_sidecar_service_env_vars()
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.SIDECAR,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=False,
            log_level=None,
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )

        self.converter.internal_auth = False
        env_vars = self.converter.get_polyaxon_sidecar_service_env_vars(
            log_level="info"
        )
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.SIDECAR,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=False,
            log_level="info",
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        env_vars = self.converter.get_polyaxon_sidecar_service_env_vars(
            external_host=True, log_level="debug"
        )
        # Default platform host
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.SIDECAR,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=False,
            log_level="debug",
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host=settings.CLIENT_CONFIG.host,
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        # Setting an env var for the EV_KEYS_PLATFORM_HOST
        current = os.environ.get(EV_KEYS_PLATFORM_HOST)
        os.environ[EV_KEYS_PLATFORM_HOST] = "foo"
        env_vars = self.converter.get_polyaxon_sidecar_service_env_vars(
            external_host=True,
            log_level="debug",
        )
        assert env_vars == get_service_env_vars(
            header=PolyaxonServiceHeaders.SERVICE,
            service_header=PolyaxonServices.SIDECAR,
            authentication_type=AuthenticationTypes.TOKEN,
            include_secret_key=False,
            include_internal_token=False,
            include_agent_token=False,
            log_level="debug",
            polyaxon_default_secret_ref=settings.AGENT_CONFIG.app_secret_name,
            polyaxon_agent_secret_ref=settings.AGENT_CONFIG.agent_secret_name,
            api_host="foo",
            api_version=VERSION_V1,
            run_instance=self.converter.run_instance,
            namespace=self.converter.namespace,
            resource_name=self.converter.get_resource_name(),
            use_proxy_env_vars_use_in_ops=False,
        )
        if current:
            os.environ[EV_KEYS_PLATFORM_HOST] = current
        else:
            del os.environ[EV_KEYS_PLATFORM_HOST]
