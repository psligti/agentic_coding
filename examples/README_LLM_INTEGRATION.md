# PR Review Example with LLM Integration

This example demonstrates how to use the PR review system with actual LLM API calls.

## Overview

The PR review system can operate in two modes:

1. **Mock Mode (default)**: Uses static/mock data without LLM calls
2. **LLM Mode**: Makes actual API calls to an LLM provider for each review subagent

## Setting up LLM Integration

### Supported Providers

- `z.ai`: Custom provider (default)
- `openai`: OpenAI API
- `anthropic`: Anthropic API

### Configuration

Set the following environment variables:

```bash
# Required: API key for your provider
export Z_AI_API_KEY='your-zai-api-key'
# or
export OPENAI_API_KEY='your-openai-api-key'
# or
export ANTHROPIC_API_KEY='your-anthropic-api-key'

# Optional: Custom base URL (for z.ai)
export LLM_BASE_URL='https://api.z.ai/v1'

# Optional: Model to use
export LLM_MODEL='glm-4.7'
```

## Usage

### Run without LLM (mock mode):

```bash
python examples/pr_review_example.py
```

Output:
```
No LLM API key found - using mock/static review data
To enable actual LLM calls, set environment variables:
  export Z_AI_API_KEY='your-api-key'
Starting PR review...
...
```

### Run with LLM:

```bash
# Set your API key
export Z_AI_API_KEY='your-api-key'

# Run the example
python examples/pr_review_with_llm.py
```

## Architecture Review with LLM

The architecture review agent is the first agent with full LLM integration:

1. System prompt is loaded from PRD (architectural guidelines)
2. LLM is called with changed files and diff as input
3. LLM returns JSON review output with findings, checks, and severity
4. Output is parsed and used for the final merge gate decision

## Example Output

With LLM enabled, you'll see actual findings and intelligent review:

```
architecture: warning
  Reviewed 2 files, found 1 issues...
  
  Finding ARCH-001: Add docstring to new parameters
  Severity: warning
  Confidence: medium
  Evidence: temperature and max_tokens added to __init__ without documentation
  Recommendation: Add docstring to parameters
  Owner: dev
  Estimate: S
```

## Extending LLM Integration

To add LLM support to other review agents (security, documentation, etc.):

1. Add system prompt constant (see `architecture.py`)
2. Implement `review_with_llm()` method (see `architecture.py`)
3. Pass `llm_client` parameter to agent constructor

Example:

```python
SECURITY_SYSTEM_PROMPT = """You are Security Review Subagent..."""

class SecurityReviewAgent(BaseReviewAgent):
    def __init__(self, llm_client=None):
        super().__init__(
            name="security",
            description="Reviews for security concerns",
            llm_client=llm_client,
            system_prompt=SECURITY_SYSTEM_PROMPT,
        )

    async def review_with_llm(self, changed_files, diff):
        # Call LLM with system prompt and user input
        user_message = f"Review: {json.dumps(changed_files)}\nDiff: {diff}"
        response = await self.call_llm(user_message)
        return ReviewOutput(**json.loads(response))
```

## System Prompts

Each subagent has a detailed system prompt in the PRD:
- Architecture: Boundaries, layering, cohesion, design patterns
- Security: Secrets, auth, injection risks, supply chain
- Documentation: Docstrings, README, API docs
- Linting: Code quality, formatting, style
- Unit Tests: Test coverage, assertions, edge cases

See `PRD_AGENTIC_REVIEW.md` section 10 for full system prompts.
