#!/bin/bash
# Mulberry HF Demo - GitHub Auto Push Script
# CTO Koda - 2026-03-03

set -e

echo "🚀 Mulberry HF Demo - GitHub Push"
echo "=================================="

# GitHub Token (from CEO)
GITHUB_TOKEN="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"
GITHUB_REPO="https://github.com/re-eul/mulberry-hf-demo.git"

# Navigate to HF demo directory
cd /mnt/user-data/outputs/MULBERRY_PROJECT/hf-demo

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git config user.name "Koda CTO"
    git config user.email "koda@mulberry.io"
fi

# Add all files
echo "📝 Adding files..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "feat: Mulberry x Google Cloud HF Space Demo

- Gradio UI with 3-layer layout
- Mastodon ActivityPub integration
- Real-time event simulation
- Issue #78 Douglas Challenge response
- DeepSeek V4 + mHC optimization
- Field-proven metrics (Inje-gun, n=3,247)

Prepared for HF Spaces deployment.
"

# Add remote
echo "🔗 Adding remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GITHUB_TOKEN}@github.com/re-eul/mulberry-hf-demo.git"

# Push to main branch
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main --force

echo "✅ Push complete!"
echo ""
echo "Repository URL: https://github.com/re-eul/mulberry-hf-demo"
echo ""
echo "Next: 대표님께서 HF Spaces에서 이 repository를 import하시면 됩니다!"
