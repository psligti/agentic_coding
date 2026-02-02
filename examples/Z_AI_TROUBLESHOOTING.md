# z.ai Connection - Troubleshooting Guide

## 404 Error Fixes

### Problem
```
HTTP error from z.ai: Client error '404 Not Found'
for url 'https://api.z.ai/v1/chat/completions'
```

### Solution

The default z.ai endpoint may not use `/chat/completions`. Try setting a custom base URL:

```bash
# Try different z.ai endpoint
export LLM_BASE_URL='https://api.z.ai/v1/chat/completions'

# Or check z.ai documentation for correct endpoint
```

### Test Connection First

Always test your connection before running PR review:

```bash
python examples/test_zai_connection.py
```

This will show:
- Status (success/failed)
- Model being used
- Base URL being called
- Response from API

## Common Issues

### "API key not configured"
**Error**: `ValueError: API key not configured for provider 'z.ai'`

**Fix**:
```bash
export Z_AI_API_KEY='your-zai-api-key'
```

### "401 Unauthorized"
**Error**: HTTP 401 Unauthorized

**Cause**: Invalid API key

**Fix**:
1. Regenerate API key in z.ai dashboard
2. Update environment variable
3. Test connection again

### "429 Too Many Requests"
**Error**: HTTP 429

**Cause**: Rate limit exceeded

**Fix**:
1. Wait and retry later
2. Contact z.ai support to increase limits

### "Unexpected error: 'model'"
**Fixed**: This was caused by incorrect key access in test_connection()

The script now uses `model_name` instead of `model` to avoid conflicts.

## Testing Steps

### 1. Verify API Key
```bash
echo $Z_AI_API_KEY
```

### 2. Test Connection
```bash
python examples/test_zai_connection.py
```

### 3. Run PR Review
```bash
python examples/pr_review_example.py
```

## Quick Commands

```bash
# Set API key
export Z_AI_API_KEY='sk-ant-...'

# Test connection
python examples/test_zai_connection.py

# Run review
python examples/pr_review_example.py
```

## Documentation

- **Setup Guide**: `examples/Z_AI_SETUP.md`
- **Quick Reference**: `examples/Z_AI_QUICK_START.md`
- **Model Changes**: `examples/MODEL_GLM4_7.md`

## Contact Support

If issues persist:
1. Check z.ai documentation for current API endpoints
2. Verify your API key is active
3. Check account status/billing
