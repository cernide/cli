import pytest

from mock import MagicMock, patch

from polxaxon._k8s.agent import Agent
from polxaxon._k8s.executor import Executor
from polyaxon._k8s.client import Client
from polyaxon._utils.test_utils import AsyncMock, patch_settings


@pytest.mark.agent_mark
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@patch(
    "polyaxon._runner.agent.async_agent.Agent._enter", new_callable=AsyncMock
)
async def test_init_agent_component(register):
    patch_settings()
    agent = Agent(owner="foo", agent_uuid="uuid")
    assert agent.max_interval == 6
    assert isinstance(agent.executor, Executor)
    assert isinstance(agent.client, Client)
    assert register.call_count == 0


@pytest.mark.agent_mark
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@patch("polyaxon._sdk.api.AgentsV1Api.sync_agent", new_callable=AsyncMock)
@patch("polyaxon._sdk.api.AgentsV1Api.create_agent_status", new_callable=AsyncMock)
@patch("polyaxon._sdk.api.AgentsV1Api.get_agent_state", new_callable=AsyncMock)
@patch("polyaxon._sdk.api.AgentsV1Api.get_agent", new_callable=AsyncMock)
@patch(
    "polyaxon._k8s.executor.async_executor.Executor.manager",
    new_callable=AsyncMock,
)
async def test_init_agent(
    _, get_agent, get_agent_state, create_agent_status, sync_agent
):
    patch_settings()
    get_agent.return_value = MagicMock(status=None, live_state=1)
    get_agent_state.return_value = MagicMock(status=None, live_state=1)
    agent = Agent(owner="foo", agent_uuid="uuid")
    agent.executor.manager.get_version.return_value = {}
    assert agent.max_interval == 6
    assert agent.executor is not None
    assert isinstance(agent.client, Client)
    assert get_agent.call_count == 0
    assert get_agent_state.call_count == 0
    assert create_agent_status.call_count == 0
    assert sync_agent.call_count == 0
    assert agent.executor.manager.get_version.call_count == 0

    await agent._enter()
    assert agent.max_interval == 6
    assert agent.executor is not None
    assert isinstance(agent.client, Client)
    assert get_agent.call_count == 1
    assert get_agent_state.call_count == 0
    assert create_agent_status.call_count == 1
    assert sync_agent.call_count == 1
    assert agent.executor.manager.get_version.call_count == 1
