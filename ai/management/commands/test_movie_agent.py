"""
Management command to interact with Movie Agent.

Usage:
    python manage.py test_movie_agent
    python manage.py test_movie_agent --user-id 1
    python manage.py test_movie_agent --thread-id my-thread
    python manage.py test_movie_agent --auto-test
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai.services.graph_executor import GraphExecutor
from ai.models import Agent

User = get_user_model()


class Command(BaseCommand):
    help = "Interactive CLI to test Movie Agent with TMDB integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="User ID for movie queries (default: creates test user)",
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
        self.stdout.write(self.style.SUCCESS("🎬 Movie Agent Interactive Test"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        # Setup user
        user_id = options.get("user_id")
        if not user_id:
            # Create or get test user
            test_user, created = User.objects.get_or_create(
                username="test_movie_user", defaults={"email": "test@example.com"}
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

        # Verify Movie Agent exists
        try:
            movie_agent = Agent.objects.get(key="movie_agent")
            self.stdout.write(
                self.style.SUCCESS(f"✅ Movie Agent found: {movie_agent.name}")
            )
        except Agent.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Movie Agent not found. Run: python manage.py seed_agents"
                )
            )
            return

        # Check TMDB API key
        from django.conf import settings

        if not settings.TMDB_API_KEY:
            self.stdout.write(
                self.style.ERROR(
                    "❌ TMDB_API_KEY not configured. Check your .env file."
                )
            )
            return
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ TMDB API configured"))

        # Initialize executor
        executor = GraphExecutor(graph_key="main_workflow")

        if auto_test:
            self._run_auto_test(executor, user_id, thread_id)
        else:
            self._run_interactive_mode(executor, user_id, thread_id)

    def _run_auto_test(self, executor, user_id, thread_id):
        """Run automated test suite for all Movie Agent capabilities"""
        self.stdout.write(self.style.SUCCESS("\n🤖 Running Automated Test Suite\n"))

        test_cases = [
            {
                "name": "1️⃣  Search Popular Movie",
                "message": "Find movies about Inception",
                "expected": ["inception", "movie"],
            },
            {
                "name": "2️⃣  Search by Genre",
                "message": "Show me sci-fi movies about space",
                "expected": ["space", "sci-fi"],
            },
            {
                "name": "3️⃣  Get Movie Details",
                "message": "Tell me more about The Matrix",
                "expected": ["matrix", "details"],
            },
            {
                "name": "4️⃣  Search Action Movies",
                "message": "Find action movies with explosions",
                "expected": ["action"],
            },
            {
                "name": "5️⃣  Movie Recommendations",
                "message": "What are the best Christopher Nolan movies?",
                "expected": ["nolan"],
            },
            {
                "name": "6️⃣  Recent Movies",
                "message": "What are some recent blockbuster movies?",
                "expected": ["movie"],
            },
        ]

        results = []

        for i, test in enumerate(test_cases, 1):
            self.stdout.write(self.style.WARNING(f"\n{test['name']}"))
            self.stdout.write(f"📤 Query: {test['message']}")

            try:
                result = executor.execute(
                    test["message"],
                    thread_id=thread_id or f"auto-test-movie-{i}",
                    triggered_by="manual",
                    user_id=user_id,
                )

                response = result.get("response", "")
                execution_id = result.get("execution_id")

                # Truncate long responses
                display_response = (
                    response[:300] + "..." if len(response) > 300 else response
                )
                self.stdout.write(f"📥 Response: {display_response}")
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Execution ID: {execution_id}")
                )

                # Validation - check if any expected keyword is in response
                success = any(
                    keyword.lower() in response.lower() for keyword in test["expected"]
                )

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
                        self.style.ERROR(
                            f"❌ Test FAILED (expected keywords not found: {test['expected']})"
                        )
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
        self.stdout.write(self.style.SUCCESS("\n💬 Interactive Mode - Movie Agent\n"))
        self.stdout.write("Type your movie-related queries:")
        self.stdout.write("  • Search for movies by title, genre, or theme")
        self.stdout.write("  • Get detailed information about specific movies")
        self.stdout.write("  • Ask for recommendations")
        self.stdout.write("  • 'examples' - Show example queries")
        self.stdout.write("  • 'popular' - Show popular searches")
        self.stdout.write("  • 'quit' or 'exit' - Exit\n")

        conversation_thread = thread_id or f"interactive-movie-{user_id}"

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

                if user_input.lower() == "popular":
                    self._show_popular_searches()
                    continue

                # Process natural language query
                self.stdout.write(self.style.SUCCESS("🤖 Movie Agent is searching..."))

                result = executor.execute(
                    user_input,
                    thread_id=conversation_thread,
                    triggered_by="manual",
                    user_id=user_id,
                )

                response = result.get("response", "No response")
                execution_id = result.get("execution_id")

                self.stdout.write(self.style.SUCCESS(f"\n🤖 Movie Agent: {response}"))
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
            ("Search by Title", "Find movies about Interstellar"),
            ("Search by Genre", "Show me sci-fi movies about time travel"),
            ("Get Details", "Tell me more about The Dark Knight"),
            ("By Director", "What are Christopher Nolan's best movies?"),
            ("By Actor", "Show me Leonardo DiCaprio movies"),
            ("By Theme", "Find movies about artificial intelligence"),
            ("Recent", "What are the latest Marvel movies?"),
            ("Classic", "Show me classic 80s action movies"),
            ("Foreign", "What are good Japanese anime films?"),
            ("Recommendations", "Recommend movies similar to Inception"),
        ]

        for category, example in examples:
            self.stdout.write(f"  {category:20} → {example}")

        self.stdout.write("\n💡 Tip: You can ask follow-up questions about movies!")

    def _show_popular_searches(self):
        """Show popular movie search topics"""
        self.stdout.write(self.style.SUCCESS("\n🔥 Popular Search Topics:\n"))

        categories = [
            "🚀 Sci-Fi & Space",
            "  • Movies about space exploration",
            "  • Time travel movies",
            "  • Dystopian future films",
            "",
            "💥 Action & Adventure",
            "  • Superhero movies",
            "  • Spy thrillers",
            "  • Heist movies",
            "",
            "🎭 Drama & Thriller",
            "  • Psychological thrillers",
            "  • Crime dramas",
            "  • Courtroom dramas",
            "",
            "😂 Comedy & Family",
            "  • Romantic comedies",
            "  • Animated films",
            "  • Family adventures",
            "",
            "👻 Horror & Mystery",
            "  • Supernatural horror",
            "  • Murder mysteries",
            "  • Found footage films",
        ]

        for line in categories:
            self.stdout.write(line)

        self.stdout.write("\n💡 Try: 'Find movies about [any topic above]'")
