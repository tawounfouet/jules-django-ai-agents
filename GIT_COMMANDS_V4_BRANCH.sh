#!/bin/bash
# Git commands to create v4 branch and commit all session changes

echo "🌿 Creating v4 branch workflow"
echo "================================"

# 1. Check current status
echo ""
echo "📊 Step 1: Checking current status..."
git status --short

# 2. Create and checkout new v4 branch
echo ""
echo "🌿 Step 2: Creating new branch 'jules/multi-agent-tmdb-supervisor-v4'..."
git checkout -b jules/multi-agent-tmdb-supervisor-v4

# 3. Add all changes
echo ""
echo "📦 Step 3: Adding all changes..."
git add .

# 4. Show what will be committed
echo ""
echo "📋 Step 4: Files to be committed:"
git status --short

# 5. Commit with detailed message
echo ""
echo "💾 Step 5: Committing changes..."
git commit -F COMMIT_MESSAGE.txt

# 6. Show the commit
echo ""
echo "✅ Step 6: Commit created successfully!"
git log -1 --oneline

echo ""
echo "================================"
echo "✅ Branch 'jules/multi-agent-tmdb-supervisor-v4' created and changes committed!"
echo ""
echo "📌 Current branch:"
git branch --show-current

echo ""
echo "🚀 Next steps:"
echo "   1. Review the changes:"
echo "      git log -1 --stat"
echo ""
echo "   2. Push to remote (optional):"
echo "      git push -u origin jules/multi-agent-tmdb-supervisor-v4"
echo ""
echo "   3. Create Pull Request on GitHub (optional)"
echo ""
echo "   4. Merge to main when ready:"
echo "      git checkout main"
echo "      git merge jules/multi-agent-tmdb-supervisor-v4"
echo "      git push origin main"
echo ""
echo "   5. Or merge to another branch:"
echo "      git checkout jules/django-langgraph-poc-12133445574000865863"
echo "      git merge jules/multi-agent-tmdb-supervisor-v4"
