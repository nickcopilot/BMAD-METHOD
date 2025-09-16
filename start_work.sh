#!/bin/bash
echo "🎯 Starting new work session..."

# Ensure we're in the right place
pwd

# Install Claude Code if needed (in case of session reset)
npm install @anthropic-ai/claude-code

# Source custom commands
source ~/.bashrc

# Show recent work
echo "📚 Recent commits:"
git log --oneline -5 2>/dev/null || echo "No commits yet"

echo ""
echo "📝 Recent Claude conversations:"
ls -lt session_logs/ 2>/dev/null | head -3 || echo "No previous sessions"

echo ""
echo "📋 Previous context:"
review_context

echo ""
echo "🤖 Getting AI recommendations..."
cc_save "Based on this project and my recent work history, what should I focus on in this session?"

echo ""
echo "✅ Session ready! Your commands:"
echo "  cc_save 'your question'        - Ask Claude and auto-save"
echo "  set_current_focus 'your goal'  - Set session focus"
echo "  update_context 'what learned'  - Track progress"
echo "  quick_save                     - Backup everything"
echo "  show_recent_work              - See recent activity"
echo ""
