import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_core.messages import HumanMessage
from .services import GraphExecutor


@csrf_exempt
def trigger_agent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            thread_id = data.get("thread_id")  # can be None, handled by service

            if not user_message:
                return JsonResponse({"error": "Message is required"}, status=400)

            # Extract user_id from authenticated request
            # For now, default to None (anonymous), but in production you'd use request.user.id
            user_id = None
            if request.user and request.user.is_authenticated:
                user_id = request.user.id

            # Use GraphExecutor to handle execution and logging
            executor = GraphExecutor(graph_key="main_workflow")
            result = executor.execute(
                user_message,
                thread_id=thread_id,
                triggered_by="api",
                user_id=user_id,  # Pass user context
            )

            return JsonResponse(
                {
                    "thread_id": result["thread_id"],
                    "response": result["response"],
                    "execution_id": result["execution_id"],
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def chat_ui(request):
    """
    Renders the Chat UI template.
    """
    return render(request, "ai/chat.html")
