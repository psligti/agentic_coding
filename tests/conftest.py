"""Pytest configuration for TUI tests"""
import sys
from pathlib import Path

# Get absolute path to local opencode_python
local_opencode_python = str(Path(__file__).parent.parent / "opencode_python")

# Insert local directory at the beginning of sys.path to ensure it's imported first
sys.path.insert(0, local_opencode_python)

# Remove any cached opencode_python modules to prevent loading from wrong directory
modules_to_remove = [name for name in list(sys.modules.keys()) if name.startswith("opencode_python")]
for module_name in modules_to_remove:
    del sys.modules[module_name]

import pytest

# Now import from local directory
from opencode_python.tui.app import OpenCodeTUI


@pytest.fixture
def app() -> OpenCodeTUI:
    """
    Fixture to provide a Textual app instance for testing.
    The test should handle running the app in a testing context.
    """
    return OpenCodeTUI()
