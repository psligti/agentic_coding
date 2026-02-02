# Setting Up z.ai for PR Review

This guide shows how to configure and connect to z.ai as an LLM provider for PR review.

## Quick Start

```bash
# 1. Get your z.ai API key
# Sign up at z.ai and obtain your API key

# 2. Set environment variable
export Z_AI_API_KEY='your-zai-api-key'

# 3. Test connection
python examples/test_zai_connection.py

# 4. Run PR review
python examples/pr_review_example.py
```

## Step-by-Step Setup

### 1. Create z.ai Account

1. Visit [z.ai](https://z.ai)
2. Sign up for an account
3. Navigate to API keys section
4. Generate a new API key
5. Copy your API key

### 2. Configure Environment

Choose one of these methods:

#### Method A: Set in Current Session (Linux/Mac)
```bash
export Z_AI_API_KEY='your-api-key-here'
```

#### Method B: Add to Shell Profile (Linux/Mac)

Add to `~/.bashrc`, `~/.zshrc`, or `~/.profile`:
```bash
echo 'export Z_AI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Method C: Use `.env` File

Create `.env` file in project root:
```bash
echo 'Z_AI_API_KEY=your-api-key-here' > .env
```

Then load it before running:
```bash
# Load .env
set -a .env

# Run PR review
python examples/pr_review_example.py
```

#### Method D: Set Directly in Command
```bash
Z_AI_API_KEY='your-api-key-here' python examples/pr_review_example.py
```

### 3. Test Connection

Verify your API key works:

```bash
python examples/test_zai_connection.py
```

Expected output:
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

### 4. Run PR Review

With your API key configured, run the PR review example:

```bash
python examples/pr_review_example.py
```

The system will now:
- Call z.ai API for each review subagent
- Get intelligent review feedback
- Parse LLM responses
- Generate findings and merge gate decision

## Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|-----------|-------------|----------|----------|
| `LLM_PROVIDER` | Provider to use | `z.ai` | `z.ai`, `openai`, `anthropic` |
| `Z_AI_API_KEY` | z.ai API key | Required | `sk-ant-...` |
| `LLM_BASE_URL` | Custom base URL | `https://api.z.ai/v1` | Custom endpoint |
| `LLM_MODEL` | Model to use | `glm-4.7` | `claude-opus-4-...` |

### Models

Available models depend on your z.ai plan. Common options:

- `glm-4.7` - Balanced (default)
- `glm-4.7` - Faster
- `claude-3-opus-20240229` - Most capable

Set custom model:
```bash
export LLM_MODEL='claude-opus-4-20250514'
```

### Custom Base URL

If using a custom z.ai endpoint or proxy:

```bash
export LLM_BASE_URL='https://your-custom-endpoint/v1'
```

## Troubleshooting

### Error: API key not configured

**Problem:**
```
Error: Z_AI_API_KEY not set
Set it with: export Z_AI_API_KEY='your-api-key'
```

**Solution:**
```bash
export Z_AI_API_KEY='your-actual-api-key'
```

### Error: Invalid API key

**Problem:**
```
HTTP error from z.ai: 401 Unauthorized
Response: {"error": "Invalid API key"}
```

**Solution:**
1. Check your API key is correct
2. Regenerate API key in z.ai dashboard
3. Update environment variable

### Error: Connection failed

**Problem:**
```
Connection test failed for z.ai: HTTPSConnectionPool(host='api.z.ai', port=443): ...
```

**Solution:**
1. Check internet connection
2. Verify z.ai service is operational
3. Check firewall/network settings
4. If using custom base URL, verify it's correct

### Error: Rate limit

**Problem:**
```
HTTP error from z.ai: 429 Too Many Requests
```

**Solution:**
1. Wait and retry later
2. Contact z.ai support to increase limits
3. Use a higher-tier plan

## Architecture

### How LLM Calls Work

```
┌─────────────────────────────────────────────────────────────────────┐
│  PR Review Orchestrator                                    │
│       │                                                        │
│       ├─ Architecture Review Agent ──┐                                │
│       │                            │                                   │
│       │                            ├─ System Prompt (PRD)              │
│       │                            │                                   │
│       │                            └─ LLM Call (z.ai)              │
│       │                                 │                            │
│       │                                 └─ JSON Response            │
│       │                                      │                 │
│       │                                      └─ ReviewOutput      │
│       │                                        │              │
│       ├─ Security Review Agent ──┐        │              │
│       │                           │                                   │
│       │                           └─ [Similar flow]               │
│       │                                                                │
│       └─ Aggregate Results ──→ Final Merge Gate Decision       │
└─────────────────────────────────────────────────────────────────────┘
```

### System Prompts

Each review agent uses a specialized system prompt from the PRD:

1. **Architecture**: Boundaries, layering, design patterns
2. **Security**: Secrets, auth, injection risks
3. **Documentation**: Docstrings, README, API docs
4. **Linting**: Code quality, formatting, style
5. **Unit Tests**: Test coverage, assertions

See `PRD_AGENTIC_REVIEW.md` section 10 for full prompts.

## Examples

### Example 1: Test Connection

```bash
# Test your z.ai credentials
python examples/test_zai_connection.py
```

### Example 2: Run PR Review with LLM

```bash
# Set API key
export Z_AI_API_KEY='sk-ant-api0324...'

# Run review
python examples/pr_review_example.py
```

### Example 3: Use Different Model

```bash
# Use faster model
export Z_AI_API_KEY='your-key'
export LLM_MODEL='claude-haiku-4-20250514'

python examples/pr_review_example.py
```

### Example 4: Custom Endpoint

```bash
# Use custom endpoint
export Z_AI_API_KEY='your-key'
export LLM_BASE_URL='https://my-proxy.com/v1'

python examples/pr_review_example.py
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use `.env` files** and add to `.gitignore`
3. **Rotate API keys** regularly
4. **Use read-only keys** for production
5. **Monitor usage** in z.ai dashboard
6. **Set rate limits** appropriately

## Next Steps

After setting up z.ai:

1. Run `test_zai_connection.py` to verify
2. Run `pr_review_example.py` to review PRs
3. Extend other review agents with LLM (security, docs, linting)
4. Customize system prompts for your use case

For detailed architecture and extension guide, see `examples/LLM_CHANGES.md`.
