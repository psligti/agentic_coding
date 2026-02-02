"""Tests for BaseReviewAgent

Test suite validates BaseReviewAgent class functionality
including change analysis, check determination, output generation.
"""
import pytest
from typing import List, Dict, Any

import sys
sys.path.insert(0, 'opencode_python/src')

from opencode_python.agents.review.base import BaseReviewAgent, create_base_review_agent
from opencode_python.models.review import (
    ReviewOutput,
    ReviewScope,
    Check,
    Skip,
    Finding,
    MergeGate,
)


class TestBaseReviewAgent:
    """Test BaseReviewAgent class"""

    def test_create_base_review_agent_factory(self):
        """Factory function creates BaseReviewAgent with correct defaults"""
        agent = create_base_review_agent(
            name="test_agent",
            description="Test agent for review",
        )

        assert isinstance(agent, BaseReviewAgent)
        assert agent.name == "test_agent"
        assert agent.description == "Test agent for review"

    def test_analyze_changes_basic(self):
        """analyze_changes() returns ReviewScope with all files as relevant"""
        agent = create_base_review_agent(name="test", description="Test")

        scope = agent.analyze_changes(
            changed_files=["file1.py", "file2.py"],
            diff="test diff"
        )

        assert set(scope.relevant_files) == {"file1.py", "file2.py"}
        assert scope.ignored_files == []
        assert "2 changed file(s)" in scope.reasoning

    def test_generate_output_with_findings(self):
        """generate_output() with findings returns correct severity and decision"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Warning issue",
                severity="warning",
                confidence="high",
                owner="dev",
                estimate="S",
                evidence="Test",
                risk="Test",
                recommendation="Test",
                suggested_patch=None,
            ),
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        assert output.severity == "warning"
        assert output.merge_gate.decision == "approve_with_warnings"
        assert output.merge_gate.should_fix == ["TEST-001"]

    def test_generate_output_no_findings_returns_merge(self):
        """generate_output() with no findings returns severity='merge' and decision='approve'"""
        agent = create_base_review_agent(name="test", description="Test")

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=[],
            check_results=[],
        )

        assert output.severity == "merge"
        assert output.merge_gate.decision == "approve"
        assert output.merge_gate.must_fix == []
        assert output.merge_gate.should_fix == []


    def test_generate_output_warning_severity(self):
        """generate_output() with warning findings returns severity='warning'"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Minor style issue",
                severity="warning",
                confidence="high",
                owner="dev",
                estimate="S",
                evidence="Line 10: extra space",
                risk="Minor inconsistency",
                recommendation="Remove extra space",
                suggested_patch=None,
            )
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        assert output.severity == "warning"
        assert output.merge_gate.decision == "approve_with_warnings"
        assert output.merge_gate.should_fix == ["TEST-001"]
        assert len(output.merge_gate.notes_for_coding_agent) == 1

    def test_generate_output_critical_severity(self):
        """generate_output() with critical findings returns severity='critical'"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Missing error handling",
                severity="critical",
                confidence="medium",
                owner="dev",
                estimate="M",
                evidence="Function lacks try/except block",
                risk="Uncaught exceptions crash app",
                recommendation="Add error handling",
                suggested_patch=None,
            )
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        assert output.severity == "critical"
        assert output.merge_gate.decision == "needs_changes"
        assert output.merge_gate.must_fix == ["TEST-001"]

    def test_generate_output_blocking_severity(self):
        """generate_output() with blocking findings returns severity='blocking'"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Security vulnerability",
                severity="blocking",
                confidence="high",
                owner="security",
                estimate="L",
                evidence="SQL injection via user input",
                risk="Database compromise",
                recommendation="Parameterized queries",
                suggested_patch=None,
            )
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        assert output.severity == "blocking"
        assert output.merge_gate.decision == "block"
        assert output.merge_gate.must_fix == ["TEST-001"]
        assert len(output.merge_gate.notes_for_coding_agent) == 1

    def test_generate_output_mixed_severities(self):
        """generate_output() prioritizes blocking over critical over warning"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Blocking issue",
                severity="blocking",
                confidence="high",
                owner="security",
                estimate="L",
                evidence="Hardcoded secret",
                risk="Security compromise",
                recommendation="Remove secret",
                suggested_patch=None,
            ),
            Finding(
                id="TEST-002",
                title="Critical issue",
                severity="critical",
                confidence="medium",
                owner="dev",
                estimate="M",
                evidence="Missing validation",
                risk="Data corruption",
                recommendation="Add validation",
                suggested_patch=None,
            ),
            Finding(
                id="TEST-003",
                title="Warning issue",
                severity="warning",
                confidence="high",
                owner="docs",
                estimate="S",
                evidence="Outdated doc",
                risk="User confusion",
                recommendation="Update documentation",
                suggested_patch=None,
            ),
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        # Blocking should take priority
        assert output.severity == "blocking"
        assert output.merge_gate.decision == "block"

    def test_notes_for_coding_agent_with_findings(self):
        """Notes for coding agent are generated when findings exist"""
        agent = create_base_review_agent(name="test", description="Test")

        findings = [
            Finding(
                id="TEST-001",
                title="Issue",
                severity="warning",
                confidence="high",
                owner="dev",
                estimate="S",
                evidence="Test",
                risk="Test",
                recommendation="Test",
                suggested_patch=None,
            ),
        ]

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=findings,
            check_results=[],
        )

        assert len(output.merge_gate.notes_for_coding_agent) == 1
        assert "TEST-001" in output.merge_gate.notes_for_coding_agent[0]

    def test_notes_for_coding_agent_no_findings(self):
        """No notes generated when no findings exist"""
        agent = create_base_review_agent(name="test", description="Test")

        output = agent.generate_output(
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=[],
            check_results=[],
        )

        assert len(output.merge_gate.notes_for_coding_agent) == 0
