import pytest
from ai.graph import build_graph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from business.models import Customer, Order

@pytest.mark.django_db
def test_workflow_data_agent_path():
    """Test that the workflow routes to DataAgent and fetches order status."""
    # Setup data
    customer = Customer.objects.create(name="Bob", email="bob@test.com")
    Order.objects.create(customer=customer, total_amount=50.00, status="DELIVERED", id=999)

    app = build_graph()
    config = {"configurable": {"thread_id": "test_1"}}
    inputs = {"messages": [HumanMessage(content="What is the status of order 999?")]}

    # Execute graph
    events = list(app.stream(inputs, config=config))

    # Analyze trace
    node_names = [list(e.keys())[0] for e in events]
    assert "decision_agent" in node_names
    assert "data_agent" in node_names
    assert "support_agent" not in node_names

    # Check final output
    last_event = events[-1]
    data_agent_messages = last_event["data_agent"]["messages"]

    # We expect a ToolMessage with the result
    assert any(isinstance(m, ToolMessage) and "DELIVERED" in m.content for m in data_agent_messages)

@pytest.mark.django_db
def test_workflow_support_agent_path():
    """Test that the workflow routes to SupportAgent for general queries."""
    app = build_graph()
    config = {"configurable": {"thread_id": "test_2"}}
    inputs = {"messages": [HumanMessage(content="My computer is broken.")]}

    events = list(app.stream(inputs, config=config))

    node_names = [list(e.keys())[0] for e in events]
    assert "decision_agent" in node_names
    assert "support_agent" in node_names
    assert "data_agent" not in node_names

    last_event = events[-1]
    support_msg = last_event["support_agent"]["messages"][0]
    assert "Support Agent" in support_msg.content
