import pytest
from ai.graph import build_graph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from business.models import Customer, Order
from ai.models import Agent, Tool, AgentTool


@pytest.fixture
def seed_agents_data(db):
    """Fixture to ensure agents and tools exist for tests."""
    supervisor = Agent.objects.create(
        key="supervisor",
        name="Supervisor",
        role="Routing",
        llm_provider="openai",
        llm_model="gpt-4o",
        temperature=0.0,
    )
    data_agent = Agent.objects.create(
        key="data_agent",
        name="Data",
        role="Retrieval",
        llm_provider="openai",
        llm_model="gpt-4o",
        temperature=0.0,
    )
    support_agent = Agent.objects.create(
        key="support_agent",
        name="Customer Support",
        role="Customer Support",
        llm_provider="openai",
        llm_model="gpt-4o",
        temperature=0.7,
    )

    # Create Tools (NEW MODULAR PATHS)
    check_order = Tool.objects.create(
        key="check_order_status",
        name="Check Order",
        python_path="ai.tools.order_tools.check_order_status",
    )

    # Link Tools
    AgentTool.objects.create(agent=data_agent, tool=check_order, allowed=True)

    return {"supervisor": supervisor, "data": data_agent, "support": support_agent}


@pytest.mark.django_db
def test_workflow_data_agent_path(seed_agents_data, mocker):
    """Test that the workflow routes to DataAgent and fetches order status."""
    # Mock LLM to simulate decision agent routing
    mock_model = mocker.Mock()
    # First call (decision agent) returns routing
    # Second call (data agent) - wait, data agent binds tools.
    # We need to mock get_llm to return different mocks for different agents or same mock behaving differently.

    # Let's mock the get_llm function itself
    mock_get_llm = mocker.patch("ai.agents.get_llm")

    def side_effect(key):
        m = mocker.Mock()
        if key == "supervisor":
            m.invoke.return_value = AIMessage(content="ROUTING_TO_DATA")
        elif key == "data_agent":
            # Data Agent returns a tool call
            m.bind_tools.return_value = m
            m.invoke.return_value = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "check_order_status",
                        "args": {"order_id": 999},
                        "id": "call_1",
                    }
                ],
            )
        return m

    mock_get_llm.side_effect = side_effect

    # Setup business data
    customer = Customer.objects.create(name="Bob", email="bob@test.com")
    Order.objects.create(
        customer=customer, total_amount=50.00, status="DELIVERED", id=999
    )

    app = build_graph()
    config = {"configurable": {"thread_id": "test_1"}}
    inputs = {"messages": [HumanMessage(content="What is the status of order 999?")]}

    # Execute graph
    events = list(app.stream(inputs, config=config))

    # Analyze trace
    node_names = [list(e.keys())[0] for e in events]
    assert "supervisor" in node_names
    assert "data_agent" in node_names
    assert "support_agent" not in node_names

    data_agent_output = next(e for e in events if "data_agent" in e)["data_agent"]
    data_agent_messages = data_agent_output["messages"]

    # We verify that the "tool execution" logic in the node worked.
    # Since we mocked the LLM to return a tool call, the node (which isn't mocked)
    # should have executed the tool. The tool is real (using DB).
    assert any(
        isinstance(m, ToolMessage) and "DELIVERED" in m.content
        for m in data_agent_messages
    )


@pytest.mark.django_db
def test_workflow_support_agent_path(seed_agents_data):
    """Test that the workflow routes to SupportAgent for general queries."""
    app = build_graph()
    config = {"configurable": {"thread_id": "test_2"}}
    inputs = {"messages": [HumanMessage(content="My computer is broken.")]}

    events = list(app.stream(inputs, config=config))

    node_names = [list(e.keys())[0] for e in events]
    assert "supervisor" in node_names
    assert "support_agent" in node_names
    assert "data_agent" not in node_names

    support_output = next(e for e in events if "support_agent" in e)["support_agent"]
    support_msg = support_output["messages"][0]
    assert "Support Agent" in support_msg.content or "help" in support_msg.content
