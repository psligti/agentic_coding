# z.ai Integration - Quick Reference

## Status: ✅ Ready to Connect to z.ai

You can now connect to z.ai as a provider for PR review!

## Quick Setup (3 Commands)

```bash
# 1. Set your z.ai API key
export Z_AI_API_KEY='your-zai-api-key'

# 2. Test connection
python examples/test_zai_connection.py

# 3. Run PR review with LLM
python examples/pr_review_example.py
```

## What's New

### LLM Client (`opencode_python/llm/client.py`)
- ✅ Supports z.ai provider (default: `https://api.z.ai/v1`)
- ✅ Async chat completion API
- ✅ JSON response format support
- ✅ Error handling with detailed logging
- ✅ Connection testing (`test_connection()` method)

### Base Review Agent (`opencode_python/agents/review/base.py`)
- ✅ `llm_client` parameter for dependency injection
- ✅ `call_llm()` method for making API calls
- ✅ `review_with_llm()` abstract method for subclasses
- ✅ `_init_with_llm()` helper for flexible initialization

### Architecture Review Agent (`opencode_python/agents/review/architecture.py`)
- ✅ System prompt from PRD (architectural guidelines)
- ✅ `review_with_llm()` implementation
- ✅ Calls z.ai API with changed files and diff
- ✅ Parses JSON response into `ReviewOutput`

### PR Review Orchestrator (`opencode_python/agents/review/orchestrator.py`)
- ✅ Accepts optional `llm_client` parameter
- ✅ Passes LLM client to subagents
- ✅ Uses LLM when available, falls back to mock otherwise
- ✅ Updated factory function to support LLM client

### Example Scripts
- ✅ `examples/test_zai_connection.py` - Test your z.ai credentials
- ✅ `examples/pr_review_example.py` - Auto-detects LLM config
- ✅ `examples/pr_review_with_llm.py` - Pure LLM mode example
- ✅ `examples/Z_AI_SETUP.md` - Complete setup guide

## Usage Examples

### Test Connection First

```bash
# Verify your z.ai API key works
python examples/test_zai_connection.py
```

**Expected Success Output:**
```
Testing connection to z.ai
Model: glm-4.7
Base URL: default

Testing connection...
--------------------------------------------------
Status: success
Provider: z.ai
Model: glm-4.7
Response: OK
--------------------------------------------------
SUCCESS: Connection to z.ai is working!

You can now run PR review with:
  python examples/pr_review_example.py
```

### Run PR Review

```bash
# With API key set, PR review uses real LLM calls
export Z_AI_API_KEY='your-api-key'
python examples/pr_review_example.py
```

**What happens:**
1. Orchestrator calls 6 review subagents
2. Each subagent calls z.ai API with system prompt
3. LLM returns JSON with findings and severity
4. System parses responses and aggregates results
5. Final merge gate decision generated

### Mock Mode (No API Key)

```bash
# Without API key, system uses mock/static data
python examples/pr_review_example.py
```

**What happens:**
- No API calls made
- Uses hardcoded mock responses
- Faster for testing/debugging
- Same output structure

## Configuration

### Required

| Variable | Description | Example |
|-----------|-------------|----------|
| `Z_AI_API_KEY` | Your z.ai API key | `sk-ant-...` |

### Optional

| Variable | Description | Default |
|-----------|-------------|----------|
| `LLM_PROVIDER` | Provider (z.ai, openai, anthropic) | `z.ai` |
| `LLM_BASE_URL` | Custom API endpoint | `https://api.z.ai/v1` |
| `LLM_MODEL` | Model to use | `glm-4.7` |

## Models

Choose a model based on your needs:

| Model | Speed | Capability | Use Case |
|-------|--------|------------|----------|
| `claude-3-haiku` | Fast | Focused | Quick reviews, small PRs |
| `claude-3-sonnet` | Balanced | Balanced | General PR review |
| `claude-3-opus` | Slow | Advanced | Complex code, security review |

Set custom model:
```bash
export LLM_MODEL='claude-3-opus'
python examples/pr_review_example.py
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Your PR                                                │
│     │                                                        │
│     ▼                                                        │
│  PR Review Orchestrator                                        │
│     │    │                                                    │
│     ├─ Architecture ──┐                                      │
│     │                   │                                       │
│     │                   └─ z.ai LLM API                    │
│     │                        │                                │
│     │                        └─ JSON (findings)               │
│     │                                                        │
│     ├─ Security ──┐                                        │
│     │              │                                           │
│     │              └─ z.ai LLM API ──→ JSON (findings)   │
│     │                                                        │
│     ├─ Documentation ──┐                                     │
│     │                   │                                       │
│     │                   └─ z.ai LLM API ──→ JSON (findings)   │
│     │                                                        │
│     └─ Aggregate Results ──→ Merge Gate Decision            │
└──────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### "API key not configured"
**Error:** `ValueError: API key not configured for provider 'z.ai'`
**Fix:** `export Z_AI_API_KEY='your-api-key'`

### "404 Not Found"
**Error:** HTTP error from z.ai: Client error '404 Not Found'
**Cause:** Using test key or incorrect base URL
**Fix:** Use actual z.ai API key from your account

### "401 Unauthorized"
**Error:** HTTP error from z.ai: 401 Unauthorized
**Cause:** Invalid or expired API key
**Fix:** Regenerate API key in z.ai dashboard

## Next Steps

1. **Get API Key**: Sign up at z.ai and generate API key
2. **Test Connection**: `python examples/test_zai_connection.py`
3. **Run Review**: `python examples/pr_review_example.py`
4. **Extend**: Add LLM support to other review agents
   - Security (system prompt from PRD 10.2)
   - Documentation (PRD 10.3)
   - Linting (PRD 10.4)
   - Unit Tests (PRD 10.5)

## Documentation

- **Setup Guide**: `examples/Z_AI_SETUP.md` - Detailed configuration
- **LLM Changes**: `examples/LLM_CHANGES.md` - Implementation details
- **Integration Docs**: `examples/README_LLM_INTEGRATION.md` - Architecture and usage

## Verification

Run this to verify everything works:

```bash
PYTHONPATH=/Users/parkermsligting/develop/agentic_python/.worktrees/python-sdk/opencode_python/src \
  python -c "
from opencode_python.llm import LLMClient
from opencode_python.agents.review import PRReviewOrchestrator
print('✓ LLM Client imported')
print('✓ PR Review Orchestrator imported')
print('✓ Ready to connect to z.ai')
"
```

Output should be:
```
✓ LLM Client imported
✓ PR Review Orchestrator imported
✓ Ready to connect to z.ai
```
