import os

from typing import Optional

from polyaxon._env_vars.keys import (
    ENV_KEYS_ARTIFACTS_STORE_NAME,
)


def get_artifacts_store_name(default: Optional[str] = "artifacts_store"):
    """Get the artifacts store name"""
    return os.getenv(ENV_KEYS_ARTIFACTS_STORE_NAME, default)
