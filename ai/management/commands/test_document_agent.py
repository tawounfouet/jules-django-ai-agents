"""
Management command to interact with Document Agent.

Usage:
    python manage.py test_document_agent
    python manage.py test_document_agent --user-id 1
    python manage.py test_document_agent --thread-id my-thread
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai.services.graph_executor import GraphExecutor
from ai.models import Agent
from documents.models import Document

User = get_user_model()


class Command(BaseCommand):
    help = "Interactive CLI to test Document Agent with all CRUD operations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="User ID for document operations (default: creates test user)",
        )
        parser.add_argument(
            "--thread-id",
            type=str,
            help="Thread ID for conversation continuity",
        )
        parser.add_argument(
            "--auto-test",
            action="store_true",
            help="Run automated test suite",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("📄 Document Agent Interactive Test"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        # Setup user
        user_id = options.get("user_id")
        if not user_id:
            # Create or get test user
            test_user, created = User.objects.get_or_create(
                username="test_document_user", defaults={"email": "test@example.com"}
            )
            user_id = test_user.id
            if created:
                self.stdout.write(
                    self.style.WARNING(f"✅ Created test user (ID: {user_id})")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"✅ Using existing test user (ID: {user_id})")
                )

        thread_id = options.get("thread_id")
        auto_test = options.get("auto_test")

        # Verify Document Agent exists
        try:
            doc_agent = Agent.objects.get(key="document_agent")
            self.stdout.write(
                self.style.SUCCESS(f"✅ Document Agent found: {doc_agent.name}")
            )
        except Agent.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Document Agent not found. Run: python manage.py seed_agents"
                )
            )
            return

        # Initialize executor
        executor = GraphExecutor(graph_key="main_workflow")

        if auto_test:
            self._run_auto_test(executor, user_id, thread_id)
        else:
            self._run_interactive_mode(executor, user_id, thread_id)

    def _run_auto_test(self, executor, user_id, thread_id):
        """Run automated test suite for all Document Agent capabilities"""
        self.stdout.write(self.style.SUCCESS("\n🤖 Running Automated Test Suite\n"))

        test_cases = [
            {
                "name": "1️⃣  List Documents",
                "message": "List all my documents",
                "expected": "documents",
            },
            {
                "name": "2️⃣  Create Document",
                "message": "Create a document with title 'Test Report' and content 'This is a test document for the automated suite'",
                "expected": "created",
            },
            {
                "name": "3️⃣  Search Documents",
                "message": "Search for documents containing 'test'",
                "expected": "found",
            },
            {
                "name": "4️⃣  Get Document Details",
                "message": "Get details of document with title 'Test Report'",
                "expected": "Test Report",
            },
            {
                "name": "5️⃣  Update Document",
                "message": "Update the document 'Test Report' with new content: 'Updated content for testing'",
                "expected": "updated",
            },
            {
                "name": "6️⃣  Delete Document",
                "message": "Delete the document titled 'Test Report'",
                "expected": "deleted",
            },
        ]

        results = []

        for i, test in enumerate(test_cases, 1):
            self.stdout.write(self.style.WARNING(f"\n{test['name']}"))
            self.stdout.write(f"📤 Query: {test['message']}")

            try:
                result = executor.execute(
                    test["message"],
                    thread_id=thread_id or f"auto-test-{i}",
                    triggered_by="manual",
                    user_id=user_id,
                )

                response = result.get("response", "")
                execution_id = result.get("execution_id")

                self.stdout.write(f"📥 Response: {response[:200]}...")
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Execution ID: {execution_id}")
                )

                # Simple validation
                success = test["expected"].lower() in response.lower()
                results.append(
                    {
                        "test": test["name"],
                        "success": success,
                        "response": response,
                    }
                )

                if success:
                    self.stdout.write(self.style.SUCCESS("✅ Test PASSED"))
                else:
                    self.stdout.write(
                        self.style.ERROR("❌ Test FAILED (expected keyword not found)")
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
                results.append(
                    {
                        "test": test["name"],
                        "success": False,
                        "response": str(e),
                    }
                )

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("📊 Test Results Summary"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        passed = sum(1 for r in results if r["success"])
        total = len(results)

        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            self.stdout.write(f"{status} - {result['test']}")

        self.stdout.write(f"\n📈 Score: {passed}/{total} ({passed/total*100:.1f}%)")

        if passed == total:
            self.stdout.write(self.style.SUCCESS("🎉 All tests passed!"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {total - passed} test(s) failed"))

    def _run_interactive_mode(self, executor, user_id, thread_id):
        """Run interactive CLI mode"""
        self.stdout.write(
            self.style.SUCCESS("\n💬 Interactive Mode - Document Agent\n")
        )
        self.stdout.write("Type your document-related queries or commands:")
        self.stdout.write("  • 'list' - List all documents")
        self.stdout.write("  • 'create' - Create a new document")
        self.stdout.write("  • 'search <query>' - Search documents")
        self.stdout.write("  • 'get <id>' - Get document by ID")
        self.stdout.write("  • 'update <id>' - Update document")
        self.stdout.write("  • 'delete <id>' - Delete document")
        self.stdout.write("  • 'examples' - Show example queries")
        self.stdout.write("  • 'stats' - Show document statistics")
        self.stdout.write("  • 'quit' or 'exit' - Exit\n")

        conversation_thread = thread_id or f"interactive-doc-{user_id}"

        while True:
            try:
                # Get user input
                user_input = input(self.style.WARNING("\n🧑 You: ")).strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    self.stdout.write(self.style.SUCCESS("\n👋 Goodbye!"))
                    break

                if user_input.lower() == "examples":
                    self._show_examples()
                    continue

                if user_input.lower() == "stats":
                    self._show_stats(user_id)
                    continue

                # Process natural language query
                self.stdout.write(
                    self.style.SUCCESS("🤖 Document Agent is thinking...")
                )

                result = executor.execute(
                    user_input,
                    thread_id=conversation_thread,
                    triggered_by="manual",
                    user_id=user_id,
                )

                response = result.get("response", "No response")
                execution_id = result.get("execution_id")

                self.stdout.write(
                    self.style.SUCCESS(f"\n🤖 Document Agent: {response}")
                )
                self.stdout.write(
                    self.style.HTTP_INFO(f"   (Execution ID: {execution_id})")
                )

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\n\n👋 Interrupted. Goodbye!"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ Error: {e}"))

    def _show_examples(self):
        """Show example queries"""
        self.stdout.write(self.style.SUCCESS("\n📖 Example Queries:\n"))

        examples = [
            ("List documents", "Show me all my documents"),
            (
                "Create",
                "Create a document titled 'Meeting Notes' with content 'Discussed Q1 goals'",
            ),
            ("Search", "Find documents about 'project alpha'"),
            ("Get details", "Show me the document with ID 5"),
            ("Update", "Update document 5 with new content: 'Revised notes'"),
            ("Delete", "Delete document with ID 5"),
            (
                "Complex",
                "Create a document about today's meeting and then list all documents",
            ),
        ]

        for category, example in examples:
            self.stdout.write(f"  {category:15} → {example}")

    def _show_stats(self, user_id):
        """Show document statistics"""
        self.stdout.write(self.style.SUCCESS("\n📊 Document Statistics:\n"))

        total_docs = Document.objects.count()
        user_docs = Document.objects.filter(owner_id=user_id).count() if user_id else 0

        self.stdout.write(f"  Total documents in system: {total_docs}")
        self.stdout.write(f"  Your documents: {user_docs}")

        if user_docs > 0:
            recent = Document.objects.filter(owner_id=user_id).order_by("-created_at")[
                :3
            ]
            self.stdout.write("\n  Recent documents:")
            for doc in recent:
                self.stdout.write(f"    • {doc.title} (ID: {doc.id})")
