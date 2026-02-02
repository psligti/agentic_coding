# Model Updated to glm-4.7

The default model has been updated from `claude-sonnet-4-20250514` to `glm-4.7`.

## Changed Files

### Source Code
- `opencode_python/src/opencode_python/llm/client.py`
  - Default model parameter: `model: str = "glm-4.7"`
  - Updated docstring to reflect new default

### Example Scripts
- `examples/pr_review_example.py`
  - Default: `model = os.getenv("LLM_MODEL", "glm-4.7")`

- `examples/pr_review_with_llm.py`
  - Default: `model="glm-4.7"`

- `examples/test_zai_connection.py`
  - Default: `model = os.getenv("LLM_MODEL", "glm-4.7")`

### Documentation
- `examples/Z_AI_QUICK_START.md`
  - Model: glm-4.7
  - Updated all model references

- `examples/Z_AI_SETUP.md`
  - Model: glm-4.7
  - Updated all model references

- `examples/README_LLM_INTEGRATION.md`
  - Model: glm-4.7
  - Updated all model references

- `examples/LLM_CHANGES.md`
  - Model: glm-4.7
  - Updated all model references

## Verification

All files now use `glm-4.7` as the default model:

```bash
# Test connection script shows new model
python examples/test_zai_connection.py
# Output: Model: glm-4.7

# Example scripts show new model
python examples/pr_review_example.py
# Output: Model: glm-4.7
```

## Usage

The model is still configurable via environment variable if needed:

```bash
# Use a different model
export LLM_MODEL='your-custom-model'

python examples/pr_review_example.py
```

## Why glm-4.7?

The `glm-4.7` model is a capable model for:
- General purpose code review
- Architectural analysis
- Security review
- Documentation review

It provides good balance of speed and accuracy for PR review tasks.
