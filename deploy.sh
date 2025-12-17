#!/bin/bash

# HospiTrack Deployment Script
# This script helps push changes to GitHub for Render deployment

set -e  # Exit on error

echo "🏥 HospiTrack Deployment Script"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in HospiTrack directory"
    echo "Please run this script from /home/ubuntu/hospitracker"
    exit 1
fi

# Check git status
echo "📊 Checking git status..."
git status
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "Please commit them first:"
    echo "  git add <files>"
    echo "  git commit -m 'Your message'"
    exit 1
fi

# Show recent commits
echo "📝 Recent commits:"
git log --oneline -5
echo ""

# Check current branch
BRANCH=$(git branch --show-current)
echo "🌿 Current branch: $BRANCH"
echo ""

# Confirm push
read -p "🚀 Push to GitHub and trigger Render deployment? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin $BRANCH

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🔄 Render will automatically detect the changes and start deployment."
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to Render Dashboard: https://dashboard.render.com"
    echo "2. Check deployment status for 'hospitracker' service"
    echo "3. Wait 5-10 minutes for build to complete"
    echo "4. Test your application at the Render URL"
    echo ""
    echo "📚 For detailed deployment instructions, see:"
    echo "   DEPLOYMENT_GUIDE.md"
    echo ""
    echo "🎉 Deployment initiated!"
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "1. Authentication required - Set up GitHub credentials:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your@email.com'"
    echo ""
    echo "2. Need personal access token - Create at:"
    echo "   https://github.com/settings/tokens"
    echo "   Then use: git push https://TOKEN@github.com/JZembower/HospiTrack.git main"
    echo ""
    echo "3. SSH key setup - See:"
    echo "   https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    exit 1
fi
