#!/bin/bash
# Git commands to commit all changes from this session

# 1. Check current status
echo "📊 Checking Git status..."
git status

# 2. Add all changes
echo ""
echo "📦 Adding all changes..."
git add .

# 3. Commit with detailed message (using file)
echo ""
echo "💾 Committing changes..."
git commit -F COMMIT_MESSAGE_SHORT.txt

# Alternative: Commit with inline message
# Uncomment the following line if you prefer:
# git commit -m "feat: Complete multi-agent system with TMDB integration and improved architecture" \
#   -m "- Add python-dotenv configuration management" \
#   -m "- Integrate TMDB movie discovery (Movie Agent + 2 tools)" \
#   -m "- Rename Decision Agent to Supervisor for clarity" \
#   -m "- Migrate message roles to LangChain terminology (human/ai)" \
#   -m "- Improve agent tracking from 7% to 97%" \
#   -m "- Rename Support Agent to Customer Support Agent" \
#   -m "" \
#   -m "Total: 5 agents, 13 tools, 97% message tracking"

echo ""
echo "✅ Done! Changes committed."
echo ""
echo "To push to remote:"
echo "  git push origin main"
