# PR Review LLM Integration - Summary

## What Was Fixed

The PR review example now supports actual LLM API calls instead of just returning mock data.

## Changes Made

### 1. New LLM Client (`opencode_python/llm/client.py`)
- Generic LLM client supporting multiple providers
- Supports `z.ai`, `openai`, and `anthropic` APIs
- Async chat completion with JSON response format
- Configurable model, base URL, and API key

### 2. Updated Base Review Agent (`opencode_python/agents/review/base.py`)
- Added `llm_client` and `system_prompt` parameters
- Added `call_llm()` method for making LLM API calls
- Added `review_with_llm()` abstract method for subclasses
- Added `_init_with_llm()` helper for agent initialization

### 3. Updated Architecture Review Agent (`opencode_python/agents/review/architecture.py`)
- Added `ARCHITECTURE_SYSTEM_PROMPT` from PRD
- Implemented `review_with_llm()` method
- Calls LLM with system prompt and user input
- Parses JSON response and returns `ReviewOutput`

### 4. Updated PR Review Orchestrator (`opencode_python/agents/review/orchestrator.py`)
- Added `llm_client` parameter to `__init__()`
- Updated `_init_required_subagents()` to pass LLM client
- Updated `_run_subagent()` to use LLM when available
- Updated `create_pr_review_orchestrator()` factory function

### 5. Updated Example Scripts (`examples/pr_review_example.py`)
- Added LLM client configuration from environment variables
- Detects when API key is not set
- Falls back to mock mode gracefully
- Shows setup instructions

### 6. New LLM Example (`examples/pr_review_with_llm.py`)
- Demonstrates LLM integration
- Requires API key to run
- Shows proper error handling

### 7. Documentation (`examples/README_LLM_INTEGRATION.md`)
- Complete setup instructions
- Configuration examples
- Usage patterns
- Extension guide for adding LLM to other agents

## Usage

### Mock Mode (No API Key Required)

```bash
python examples/pr_review_example.py
```

Output: Uses static/mock data as before

### LLM Mode (API Key Required)

```bash
# Set your API key
export Z_AI_API_KEY='your-api-key'

# Run with LLM
python examples/pr_review_with_llm.py

# Or run the main example (will detect API key)
python examples/pr_review_example.py
```

### Environment Variables

| Variable | Description | Example |
|-----------|-------------|----------|
| `LLM_PROVIDER` | Provider to use (default: z.ai) | `z.ai`, `openai`, `anthropic` |
| `Z_AI_API_KEY` | API key for z.ai provider | `your-zai-api-key` |
| `OPENAI_API_KEY` | API key for OpenAI | `your-openai-api-key` |
| `ANTHROPIC_API_KEY` | API key for Anthropic | `your-anthropic-api-key` |
| `LLM_BASE_URL` | Custom base URL | `https://api.z.ai/v1` |
| `LLM_MODEL` | Model to use | `glm-4.7` |

## Architecture Review with LLM

The architecture review agent now makes actual LLM calls:

1. **System Prompt**: Loaded from PRD section 10.1
   - Architecture expertise and guidelines
   - Scoping heuristics
   - JSON output schema

2. **User Input**: Changed files and diff
   ```json
   {
     "changed_files": ["src/agent.py", "src/agent_runtime.py"],
     "diff": "..."
   }
   ```

3. **LLM Call**: Async API call with JSON format
   - System prompt + user message
   - Temperature: 0.7
   - Max tokens: 4096
   - Response format: JSON object

4. **Response Parsing**: JSON to `ReviewOutput`
   - Extracts findings, checks, skips
   - Validates merge gate decision
   - Returns structured data

## Adding LLM to Other Agents

To enable LLM for security, documentation, linting, or unit_tests agents:

1. Copy system prompt from `PRD_AGENTIC_REVIEW.md` section 10
2. Add constant like `SECURITY_SYSTEM_PROMPT = """..."""`
3. Implement `review_with_llm()` method
4. Pass `llm_client` parameter in `__init__()`

Example structure:
```python
from typing import List, Optional, Any
import json
import logging

from opencode_python.agents.review.base import BaseReviewAgent
from opencode_python.models.review import ReviewOutput

logger = logging.getLogger(__name__)

SECURITY_SYSTEM_PROMPT = """You are Security Review Subagent...
[Copy full prompt from PRD section 10.2]
..."""

class SecurityReviewAgent(BaseReviewAgent):
    def __init__(self, llm_client: Optional[Any] = None):
        super().__init__(
            name="security",
            description="Reviews for security concerns",
            llm_client=llm_client,
            system_prompt=SECURITY_SYSTEM_PROMPT,
        )

    async def review_with_llm(self, changed_files: List[str], diff: str) -> ReviewOutput:
        user_message = f"""Review the following PR changes:

Changed files:
{json.dumps(changed_files, indent=2)}

Diff:
{diff}

Provide your review as valid JSON following the schema in your system prompt."""

        try:
            response = await self.call_llm(user_message)
            output_data = json.loads(response)
            return ReviewOutput(**output_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error calling LLM for security review: {e}")
            raise
```

## Verification

### Run without LLM (mock mode):
```bash
PYTHONPATH=/Users/parkermsligting/develop/agentic_python/.worktrees/python-sdk/opencode_python/src \
  python examples/pr_review_example.py
```

✅ Output: Uses mock/static data, no errors

### Run with LLM check (requires API key):
```bash
PYTHONPATH=/Users/parkermsligting/develop/agentic_python/.worktrees/python-sdk/opencode_python/src \
  python examples/pr_review_with_llm.py
```

✅ Output: Error message requiring API key (expected behavior)

### With API key set:
```bash
export Z_AI_API_KEY='test-key'
PYTHONPATH=/Users/parkermsligting/develop/agentic_python/.worktrees/python-sdk/opencode_python/src \
  python examples/pr_review_example.py
```

✅ Output: Attempts LLM call, would make API request

## Files Changed

- `opencode_python/src/opencode_python/llm/client.py` - New LLM client
- `opencode_python/src/opencode_python/llm/__init__.py` - Module exports
- `opencode_python/src/opencode_python/agents/review/base.py` - LLM support
- `opencode_python/src/opencode_python/agents/review/architecture.py` - LLM integration
- `opencode_python/src/opencode_python/agents/review/orchestrator.py` - LLM wiring
- `examples/pr_review_example.py` - Updated for LLM config
- `examples/pr_review_with_llm.py` - New LLM example
- `examples/README_LLM_INTEGRATION.md` - Documentation

## Next Steps

To complete LLM integration for all review agents:

1. Add system prompts for security (PRD 10.2)
2. Add system prompts for documentation (PRD 10.3)
3. Add system prompts for linting (PRD 10.4)
4. Add system prompts for unit_tests (PRD 10.5)
5. Implement `review_with_llm()` for each agent

The architecture agent serves as the reference implementation.
