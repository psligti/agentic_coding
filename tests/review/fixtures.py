"""Pytest fixtures for PR review tests"""
import pytest
from pathlib import Path
from typing import Dict, Any

# Test fixture: sample changed files for PR review
@pytest.fixture
def sample_changed_files(tmp_path):
    """Sample changed files list for testing"""
    return [
        "src/agent.py",
        "src/agent_runtime.py",
        "src/registry.py",
        "README.md",
    ]

# Test fixture: sample diff for PR review
@pytest.fixture
def sample_diff():
    """Sample unified diff for testing"""
    return """diff --git a/main b/feature-agent
index 0000000..0000000 100644
--- /dev/null
+++ b/feature-agent
@@ -1,3 +1,4 @@
@@ public class Agent
-public mode: str
-public temperature: Optional[float] = None

     def execute(self, user_message: str) -> Dict[str, Any]:
         return {"response": "Test response"}
"""

# Test fixture: sample repo tree
@pytest.fixture
def sample_repo_tree():
    """Sample repository tree structure"""
    return """src/
    ├── __init__.py
    ├── agents/
    │   ├── __init__.py
    │   ├── builtin.py
    │   ├── registry.py
    │   └── runtime.py
    ├── tools/
    │   ├── __init__.py
    │   ├── framework.py
    │   └── registry.py
    └── core/
        ├── __init__.py
        └── models.py
"""
