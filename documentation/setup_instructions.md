# BMAD Method Codespace Setup

## Quick Start Commands
```bash
# Install Claude Code
npm install @anthropic-ai/claude-code

# Authenticate
npx @anthropic-ai/claude-code auth

# Start working
cc_save "your question here"
```

## Available Functions
- `quick_save` - Save current workspace state
- `cc_save "question"` - Save Claude responses  
- `start_session` - Begin logged session

## Directory Structure
- `documentation/` - Project docs and progress
- `session_logs/` - Saved Claude interactions
- `code_analysis/` - Code review outputs
- `experiments/` - Test implementations

## Auto-save Features
All responses and workspace changes are automatically committed to GitHub for persistence across sessions.
