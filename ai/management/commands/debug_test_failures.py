"""
Management command to debug test failures by analyzing execution logs.

Usage:
    python manage.py debug_test_failures --execution-id 30
    python manage.py debug_test_failures --range 28-39
"""

from django.core.management.base import BaseCommand
from ai.models import Execution, AgentMessage, Agent
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Debug test failures by analyzing execution logs and agent routing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--execution-id",
            type=int,
            help="Specific execution ID to debug",
        )
        parser.add_argument(
            "--range",
            type=str,
            help="Range of execution IDs (e.g., 28-39)",
        )
        parser.add_argument(
            "--failed-only",
            action="store_true",
            help="Only show failed test patterns",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS("🔍 Test Failure Debugger"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        execution_id = options.get("execution_id")
        exec_range = options.get("range")
        failed_only = options.get("failed_only")

        if execution_id:
            self._debug_single_execution(execution_id)
        elif exec_range:
            start, end = map(int, exec_range.split("-"))
            self._debug_execution_range(start, end, failed_only)
        else:
            # Default: analyze recent executions
            self.stdout.write(
                self.style.WARNING(
                    "No execution ID specified. Analyzing recent tests..."
                )
            )
            recent_execs = Execution.objects.order_by("-id")[:20]
            self.stdout.write(f"\n📊 Found {recent_execs.count()} recent executions\n")

            for exec in recent_execs:
                self.stdout.write(
                    f"ID: {exec.id} | Query: {exec.query[:60]}... | Status: {exec.status}"
                )

    def _debug_single_execution(self, execution_id):
        """Debug a single execution in detail"""
        self.stdout.write(
            self.style.SUCCESS(f"\n🔎 Debugging Execution ID: {execution_id}\n")
        )

        try:
            execution = Execution.objects.get(id=execution_id)
        except Execution.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Execution {execution_id} not found")
            )
            return

        # Basic info
        self.stdout.write(self.style.WARNING("📋 Execution Details:"))
        self.stdout.write(f"  Query: {execution.query}")
        self.stdout.write(f"  Status: {execution.status}")
        self.stdout.write(f"  Thread: {execution.thread_id}")
        self.stdout.write(f"  User ID: {execution.user_id}")
        self.stdout.write(f"  Created: {execution.created_at}")

        # Messages and agent routing
        messages = AgentMessage.objects.filter(execution=execution).order_by("id")

        self.stdout.write(
            self.style.WARNING(f"\n💬 Message Flow ({messages.count()} messages):")
        )

        for i, msg in enumerate(messages, 1):
            agent_name = msg.agent.name if msg.agent else "System"
            role_emoji = "🧑" if msg.role == "human" else "🤖"

            self.stdout.write(
                f"\n  {i}. {role_emoji} {msg.role.upper()} - [{agent_name}]"
            )
            self.stdout.write(f"     Content: {msg.content[:150]}...")

            if msg.tool_calls:
                self.stdout.write(
                    self.style.SUCCESS(f"     🔧 Tool Calls: {msg.tool_calls}")
                )

        # Analyze routing
        self._analyze_routing(messages)

        # Final response
        self.stdout.write(self.style.WARNING("\n📤 Final Response:"))
        self.stdout.write(f"  {execution.final_response[:300]}...")

    def _debug_execution_range(self, start_id, end_id, failed_only):
        """Debug a range of executions"""
        self.stdout.write(
            self.style.SUCCESS(f"\n🔎 Debugging Executions {start_id} to {end_id}\n")
        )

        executions = Execution.objects.filter(
            id__gte=start_id, id__lte=end_id
        ).order_by("id")

        # Map known test cases
        test_cases = {
            "List all my documents": ("Document", "list"),
            "Create a document": ("Document", "create"),
            "Search for documents": ("Document", "search"),
            "Get details of document": ("Document", "get"),
            "Update the document": ("Document", "update"),
            "Delete the document": ("Document", "delete"),
            "Find movies about": ("Movie", "search"),
            "Show me sci-fi": ("Movie", "search"),
            "Tell me more about": ("Movie", "details"),
            "Find action movies": ("Movie", "search"),
            "best Christopher Nolan": ("Movie", "recommendations"),
            "recent blockbuster": ("Movie", "search"),
        }

        results = []

        for execution in executions:
            # Determine expected agent
            expected_agent = None
            test_type = None
            for pattern, (agent, test) in test_cases.items():
                if pattern.lower() in execution.query.lower():
                    expected_agent = agent
                    test_type = test
                    break

            # Get actual agents used
            messages = AgentMessage.objects.filter(execution=execution)
            actual_agents = set(
                msg.agent.name for msg in messages if msg.agent and msg.role == "ai"
            )

            # Check routing
            routing_correct = expected_agent and any(
                expected_agent.lower() in agent.lower() for agent in actual_agents
            )

            # Determine if test would pass
            response = execution.final_response.lower()
            passed = self._check_test_pass(execution.query, response)

            result = {
                "id": execution.id,
                "query": execution.query[:60],
                "expected_agent": expected_agent,
                "actual_agents": list(actual_agents),
                "routing_correct": routing_correct,
                "passed": passed,
                "response_preview": response[:100],
            }

            results.append(result)

            # Display
            if not failed_only or not passed:
                self._display_result(result)

        # Summary
        self._display_summary(results)

    def _analyze_routing(self, messages):
        """Analyze which agents were involved"""
        self.stdout.write(self.style.WARNING("\n🔀 Agent Routing Analysis:"))

        agents_involved = {}
        for msg in messages:
            if msg.agent:
                agent_key = msg.agent.key
                if agent_key not in agents_involved:
                    agents_involved[agent_key] = {
                        "name": msg.agent.name,
                        "messages": 0,
                        "tools_used": [],
                    }
                agents_involved[agent_key]["messages"] += 1
                if msg.tool_calls:
                    agents_involved[agent_key]["tools_used"].extend(
                        msg.tool_calls.get("tools", [])
                    )

        for agent_key, info in agents_involved.items():
            self.stdout.write(
                f"  • {info['name']} ({agent_key}): {info['messages']} messages"
            )
            if info["tools_used"]:
                self.stdout.write(f"    Tools: {', '.join(set(info['tools_used']))}")

        # Check for routing issues
        if "supervisor" in agents_involved:
            self.stdout.write(
                self.style.SUCCESS("\n  ✅ Supervisor was involved (routing active)")
            )
        else:
            self.stdout.write(
                self.style.WARNING("\n  ⚠️  No supervisor detected (direct agent call?)")
            )

    def _check_test_pass(self, query, response):
        """Simple heuristic to determine if test would pass"""
        query_lower = query.lower()
        response_lower = response.lower()

        # Document tests
        if "list all my documents" in query_lower:
            return "document" in response_lower or "don't have any" in response_lower
        elif "create a document" in query_lower:
            return "created" in response_lower or "successfully" in response_lower
        elif "search for documents" in query_lower:
            return "found" in response_lower or "search" in response_lower
        elif "get details" in query_lower:
            return "details" in response_lower or "retrieved" in response_lower
        elif "update the document" in query_lower:
            return "updated" in response_lower or "successfully" in response_lower
        elif "delete the document" in query_lower:
            return "deleted" in response_lower or "successfully" in response_lower

        # Movie tests
        elif "find movies" in query_lower or "inception" in query_lower:
            return "inception" in response_lower or "movie" in response_lower
        elif "sci-fi" in query_lower or "space" in query_lower:
            return ("space" in response_lower or "sci-fi" in response_lower) and len(
                response
            ) > 100
        elif "matrix" in query_lower:
            return "matrix" in response_lower and len(response) > 100
        elif "action movies" in query_lower:
            return "action" in response_lower or "movie" in response_lower
        elif "nolan" in query_lower:
            return "nolan" in response_lower and len(response) > 100
        elif "recent" in query_lower or "blockbuster" in query_lower:
            return "movie" in response_lower and len(response) > 100

        return False

    def _display_result(self, result):
        """Display a single test result"""
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        routing = "✅" if result["routing_correct"] else "❌"

        self.stdout.write(f"\n{status} Execution {result['id']}")
        self.stdout.write(f"  Query: {result['query']}...")
        self.stdout.write(
            f"  Expected: {result['expected_agent']} | Actual: {', '.join(result['actual_agents'])}"
        )
        self.stdout.write(f"  Routing: {routing}")

        if not result["passed"]:
            self.stdout.write(
                self.style.ERROR(f"  Response: {result['response_preview']}...")
            )

    def _display_summary(self, results):
        """Display summary statistics"""
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 80))
        self.stdout.write(self.style.SUCCESS("📊 Summary"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        routing_correct = sum(1 for r in results if r["routing_correct"])

        self.stdout.write(f"\n  Total Tests: {total}")
        self.stdout.write(f"  Passed: {passed} ({passed/total*100:.1f}%)")
        self.stdout.write(f"  Failed: {total - passed}")
        self.stdout.write(
            f"  Routing Correct: {routing_correct} ({routing_correct/total*100:.1f}%)"
        )

        # Agent usage
        agent_usage = {}
        for result in results:
            for agent in result["actual_agents"]:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        self.stdout.write("\n📊 Agent Usage:")
        for agent, count in sorted(agent_usage.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  • {agent}: {count} times")
