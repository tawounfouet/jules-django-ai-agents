from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_core.messages import HumanMessage
from .graph import build_graph
import json
import uuid

@csrf_exempt
def trigger_agent(request):
    """
    API View to trigger the agent workflow.
    Expected Payload: {"message": "User query", "thread_id": "optional-uuid"}
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            thread_id = data.get("thread_id", str(uuid.uuid4()))

            if not user_message:
                return JsonResponse({"error": "Message is required"}, status=400)

            app = build_graph()
            config = {"configurable": {"thread_id": thread_id}}
            inputs = {"messages": [HumanMessage(content=user_message)]}

            # Run the graph
            final_response = None
            # Collect events
            for event in app.stream(inputs, config=config):
                for node_name, node_value in event.items():
                    if "messages" in node_value:
                         final_response = node_value["messages"][-1].content

            return JsonResponse({
                "thread_id": thread_id,
                "response": final_response
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
