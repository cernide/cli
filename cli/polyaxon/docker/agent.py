from polyaxon.docker.executor import Executor
from polyaxon.runner.agent.sync_agent import BaseSyncAgent


class Agent(BaseSyncAgent):
    EXECUTOR = Executor
