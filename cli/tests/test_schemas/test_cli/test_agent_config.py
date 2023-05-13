import pytest

from clipped.utils.json import orjson_dumps
from pydantic import ValidationError

from polyaxon.connections import (
    V1BucketConnection,
    V1ConnectionKind,
    V1ConnectionResource,
)
from polyaxon.env_vars.keys import (
    EV_KEYS_AGENT_ARTIFACTS_STORE,
    EV_KEYS_AGENT_CONNECTIONS,
    EV_KEYS_K8S_NAMESPACE,
)
from polyaxon.schemas.cli.agent_config import AgentConfig
from polyaxon.utils.test_utils import BaseTestCase


@pytest.mark.schemas_mark
class TestAgentConfig(BaseTestCase):
    def test_agent_config(self):
        config_dict = {EV_KEYS_AGENT_ARTIFACTS_STORE: 12}
        with self.assertRaises(ValidationError):
            AgentConfig.from_dict(config_dict)

        config_dict = {EV_KEYS_AGENT_ARTIFACTS_STORE: "some"}
        with self.assertRaises(ValidationError):
            AgentConfig.from_dict(config_dict)

        config_dict = {
            EV_KEYS_K8S_NAMESPACE: "foo",
            EV_KEYS_AGENT_ARTIFACTS_STORE: {
                "name": "some",
                "kind": V1ConnectionKind.GCS,
                "schema": V1BucketConnection(bucket="gs://test").to_dict(),
            },
        }
        config = AgentConfig.from_dict(config_dict)
        assert config.to_light_dict() == config_dict

        config_dict = {
            EV_KEYS_K8S_NAMESPACE: "foo",
            EV_KEYS_AGENT_ARTIFACTS_STORE: "some",
            EV_KEYS_AGENT_CONNECTIONS: [
                {
                    "name": "some",
                    "kind": V1ConnectionKind.GCS,
                    "schema": V1BucketConnection(bucket="gs://test").to_dict(),
                    "secretResource": "some",
                }
            ],
        }
        with self.assertRaises(ValidationError):
            AgentConfig.from_dict(config_dict)

        config_dict = {
            EV_KEYS_K8S_NAMESPACE: "foo",
            EV_KEYS_AGENT_ARTIFACTS_STORE: {
                "name": "test",
                "kind": V1ConnectionKind.GCS,
                "schema": V1BucketConnection(bucket="gs://test").to_dict(),
                "secret": V1ConnectionResource(name="some").to_dict(),
            },
            EV_KEYS_AGENT_CONNECTIONS: [
                {
                    "name": "some",
                    "kind": V1ConnectionKind.GCS,
                    "schema": V1BucketConnection(bucket="gs://test").to_dict(),
                    "secret": V1ConnectionResource(name="some").to_dict(),
                },
                {
                    "name": "slack",
                    "kind": V1ConnectionKind.SLACK,
                    "secret": V1ConnectionResource(name="some").to_dict(),
                },
            ],
        }
        config = AgentConfig.from_dict(config_dict)
        assert config.to_light_dict() == config_dict

    def test_agent_config_from_str_envs(self):
        config_dict = {
            EV_KEYS_K8S_NAMESPACE: "foo",
            EV_KEYS_AGENT_ARTIFACTS_STORE: orjson_dumps(
                {
                    "name": "test1",
                    "kind": V1ConnectionKind.GCS,
                    "schema": V1BucketConnection(bucket="gs://test").to_dict(),
                    "secret": V1ConnectionResource(name="some").to_dict(),
                }
            ),
            EV_KEYS_AGENT_CONNECTIONS: orjson_dumps(
                [
                    {
                        "name": "test2",
                        "kind": V1ConnectionKind.GCS,
                        "schema": V1BucketConnection(bucket="gs://test").to_dict(),
                        "secret": V1ConnectionResource(name="some").to_dict(),
                    },
                    {
                        "name": "slack",
                        "kind": V1ConnectionKind.SLACK,
                        "secret": V1ConnectionResource(name="some").to_dict(),
                    },
                ]
            ),
        }

        config = AgentConfig.from_dict(config_dict)
        assert len(config.secrets) == 1
        assert len(config.to_light_dict()[EV_KEYS_AGENT_CONNECTIONS]) == 2
