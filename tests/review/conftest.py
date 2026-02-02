"""Pytest configuration for PR review tests"""
import pytest
import sys
import os

# Add opencode_python/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'opencode_python', 'src'))
