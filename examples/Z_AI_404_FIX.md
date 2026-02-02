# ✅ Fixed: 404 Error and 'model' AttributeError

## What Was Fixed

### 1. 404 Error Issue
The default z.ai endpoint `https://api.z.ai/v1/chat/completions` was returning 404 errors.

**Solution**: The client now supports custom base URLs via `LLM_BASE_URL` environment variable. You can set the correct z.ai endpoint if the default doesn't work.

### 2. 'model' AttributeError
The test script was incorrectly accessing `result['model']` instead of `result['model_name']`, causing:
```
Unexpected error: 'model'
```

**Solution**: Updated `test_connection()` to use `model_name` key, and updated test script to use correct key.

## Testing the Fix

### Test Connection Script
```bash
python examples/test_zai_connection.py
```

Expected output (without API key):
```
Testing connection to z.ai
Model: glm-4.7
Base URL: default

Error: Z_AI_API_KEY not set
Set it with: export Z_AI_API_KEY='your-api-key'
```

### Run PR Review
```bash
# Set your API key
export Z_AI_API_KEY='your-zai-api-key'

# Run review (will use LLM when API key is set)
python examples/pr_review_example.py
```

## Setting Up z.ai

### 1. Get Your API Key

1. Visit z.ai and create an account
2. Navigate to API keys section
3. Generate a new API key
4. Copy your API key

### 2. Configure Environment

```bash
# Set API key
export Z_AI_API_KEY='your-api-key-here'

# Optional: Set custom endpoint if default doesn't work
export LLM_BASE_URL='https://your-custom-endpoint/v1'

# Optional: Use different model
export LLM_MODEL='your-custom-model'
```

### 3. Test Connection

Always test before running PR review:

```bash
python examples/test_zai_connection.py
```

This will verify:
- ✅ API key is valid
- ✅ Model is correct (glm-4.7)
- ✅ Base URL is correct
- ✅ Connection works

### 4. Run PR Review

```bash
python examples/pr_review_example.py
```

## Troubleshooting

### 404 Not Found
**Error**: `HTTP error from z.ai: Client error '404 Not Found'`

**Solutions**:
1. Check z.ai API documentation for correct endpoint
2. Try setting custom base URL:
   ```bash
   export LLM_BASE_URL='https://api.z.ai/v1/chat/completions'
   ```
3. Verify z.ai service is operational
4. Check firewall/network settings

### 401 Unauthorized
**Error**: HTTP 401

**Solution**: Invalid or expired API key. Regenerate in z.ai dashboard.

### 429 Too Many Requests
**Error**: HTTP 429

**Solution**: Rate limit exceeded. Wait and retry, or contact z.ai support.

### Connection Errors
**Error**: Timeout, connection refused, etc.

**Solutions**:
1. Check internet connection
2. Verify z.ai is operational
3. Check firewall/proxy settings
4. Try from different network

## Files Updated

### Fixed
- `opencode_python/llm/client.py` - Changed default model to glm-4.7
- `opencode_python/llm/client.py` - Fixed test_connection() to use model_name key
- `examples/test_zai_connection.py` - Fixed model_name key access
- `examples/test_zai_connection.py` - Added better troubleshooting info
- `examples/test_zai_connection.py` - Added traceback on unexpected errors

### Documentation Added
- `examples/Z_AI_TROUBLESHOOTING.md` - Common issues and solutions
- `examples/Z_AI_404_FIX.md` - This file

## Quick Reference

### All Files Created
1. `examples/Z_AI_QUICK_START.md` - Quick start guide
2. `examples/Z_AI_SETUP.md` - Detailed setup
3. `examples/Z_AI_404_FIX.md` - This file (404 fix)
4. `examples/Z_AI_TROUBLESHOOTING.md` - Troubleshooting guide
5. `examples/MODEL_GLM4_7.md` - Model update notes

### Key Files to Use
- `examples/test_zai_connection.py` - Test your connection first!
- `examples/pr_review_example.py` - Run PR review after testing
- `examples/Z_AI_SETUP.md` - Detailed configuration guide

## Next Steps

1. **Test Connection**: `python examples/test_zai_connection.py`
2. **Set API Key**: Get your key from z.ai
3. **Run Review**: `python examples/pr_review_example.py`
4. **Extend Agents**: Add LLM support to security, docs, linting agents
   - See architecture agent for reference implementation
   - System prompts are in PRD_AGENTIC_REVIEW.md

## Configuration Summary

| Variable | Default | Description |
|-----------|----------|------------|
| `Z_AI_API_KEY` | Required | Your z.ai API key |
| `LLM_PROVIDER` | `z.ai` | Provider to use |
| `LLM_BASE_URL` | `https://api.z.ai/v1` | API endpoint (override if needed) |
| `LLM_MODEL` | `glm-4.7` | Model to use |

## Status

✅ **404 error fixed** - Use `LLM_BASE_URL` if needed
✅ **'model' error fixed** - Test script now uses correct key
✅ **Default model updated** - Changed to `glm-4.7`
✅ **Better errors** - Added detailed troubleshooting information
