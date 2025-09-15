#!/bin/bash
echo "🔄 Auto-saving workspace..."
git add .
git commit -m "Auto-save: $(date '+%Y-%m-%d %H:%M:%S')"
git push
echo "✅ Workspace saved to GitHub"
