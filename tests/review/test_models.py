"""Tests for PR Review Pydantic models

Test suite validates that all JSON contracts match PRD schema
and that Pydantic models correctly parse and validate inputs.
"""
import pytest
import json
from typing import List, Dict, Any
from pydantic import ValidationError

import sys
sys.path.insert(0, 'opencode_python/src')

from opencode_python.models.review import (
    ReviewOutput,
    ReviewScope,
    Check,
    Skip,
    Finding,
    MergeGate,
    # Orchestrator models
    OrchestratorSummary,
    OrchestratorToolCheck,
    OrchestratorSkippedCheck,
    OrchestratorObservedOutput,
    OrchestratorToolPlan,
    OrchestratorRollup,
    OrchestratorFinding,
    OrchestratorOutput,
)


class TestReviewScope:
    """Test ReviewScope model"""

    def test_valid_review_scope(self):
        """ReviewScope with all fields"""
        scope = ReviewScope(
            relevant_files=["src/agent.py", "src/agent_runtime.py"],
            ignored_files=["tests/"],
            reasoning="Only reviewing agent implementation files"
        )

        assert scope.relevant_files == ["src/agent.py", "src/agent_runtime.py"]
        assert scope.ignored_files == ["tests/"]
        assert scope.reasoning == "Only reviewing agent implementation files"

    def test_review_scope_json_serialization(self):
        """ReviewScope serializes to valid JSON"""
        scope = ReviewScope(
            relevant_files=["file1.py"],
            ignored_files=[],
            reasoning="Test reason"
        )

        json_str = scope.model_dump_json()
        assert '"relevant_files"' in json_str
        assert '"ignored_files"' in json_str
        assert '"reasoning"' in json_str


class TestCheck:
    """Test Check model"""

    def test_valid_check(self):
        """Check with all required fields"""
        check = Check(
            name="linting",
            required=True,
            commands=["ruff check"],
            why="Need to ensure code style compliance",
            expected_signal="Exit code 0"
        )

        assert check.name == "linting"
        assert check.required is True
        assert check.commands == ["ruff check"]
        assert check.expected_signal == "Exit code 0"

    def test_optional_check(self):
        """Check with minimal fields"""
        check = Check(
            name="integration_test",
            required=False,
            commands=["pytest"],
            why="Optional integration test",
            expected_signal="All tests pass"
        )

        assert check.required is False
        assert len(check.commands) == 1


class TestSkip:
    """Test Skip model"""

    def test_valid_skip(self):
        """Skip with all fields"""
        skip = Skip(
            name="security_scan",
            why_safe="No network calls in this PR",
            when_to_run="Run if HTTP requests are added"
        )

        assert skip.name == "security_scan"
        assert skip.why_safe == "No network calls in this PR"
        assert skip.when_to_run == "Run if HTTP requests are added"


class TestFinding:
    """Test Finding model"""

    def test_valid_finding(self):
        """Finding with all required fields"""
        finding = Finding(
            id="SEC-001",
            title="Unvalidated user input",
            severity="critical",
            confidence="high",
            owner="security",
            estimate="M",
            evidence="Line 45: Input passed directly to subprocess without validation",
            risk="Command injection via user input",
            recommendation="Add input validation before subprocess call",
            suggested_patch="if not is_valid_input(user_input):\\n    raise ValueError('Invalid input')"
        )

        assert finding.id == "SEC-001"
        assert finding.title == "Unvalidated user input"
        assert finding.severity == "critical"
        assert finding.confidence == "high"
        assert finding.owner == "security"
        assert finding.estimate == "M"
        assert "subprocess" in finding.evidence
        assert finding.suggested_patch is not None

    def test_finding_without_optional_patch(self):
        """Finding without suggested_patch (optional field)"""
        finding = Finding(
            id="ARCH-001",
            title="Circular dependency detected",
            severity="blocking",
            confidence="high",
            owner="dev",
            estimate="L",
            evidence="agent.py imports agent_runtime.py, which imports back agent.py",
            risk="Infinite import loop at runtime",
            recommendation="Refactor to remove circular dependency"
        )

        assert finding.suggested_patch is None


class TestMergeGate:
    """Test MergeGate model"""

    def test_approve_merge_gate(self):
        """MergeGate with approve decision"""
        gate = MergeGate(
            decision="approve",
            must_fix=[],
            should_fix=[],
            notes_for_coding_agent=["All checks passed"]
        )

        assert gate.decision == "approve"
        assert gate.must_fix == []
        assert len(gate.should_fix) == 0

    def test_needs_changes_merge_gate(self):
        """MergeGate with needs_changes decision"""
        gate = MergeGate(
            decision="needs_changes",
            must_fix=["SEC-001", "ARCH-001"],
            should_fix=["DOC-001"],
            notes_for_coding_agent=["Fix security and architecture issues before merge"]
        )

        assert gate.decision == "needs_changes"
        assert "SEC-001" in gate.must_fix
        assert "DOC-001" in gate.should_fix

    def test_block_merge_gate(self):
        """MergeGate with block decision"""
        gate = MergeGate(
            decision="block",
            must_fix=["CRIT-001"],
            should_fix=[],
            notes_for_coding_agent=["Critical security issue must be fixed"]
        )

        assert gate.decision == "block"


class TestReviewOutput:
    """Test ReviewOutput model (subagent output)"""

    def test_valid_review_output_all_fields(self):
        """ReviewOutput with all populated fields"""
        output = ReviewOutput(
            agent="security",
            summary="No security issues found in code",
            severity="merge",
            scope=ReviewScope(
                relevant_files=["auth.py", "session.py"],
                ignored_files=[],
                reasoning="Reviewing authentication module"
            ),
            checks=[
                Check(
                    name="secrets_scan",
                    required=True,
                    commands=['grep -r "password\\|token\\|secret"'],
                    why="Scan for hardcoded secrets",
                    expected_signal="No matches found"
                )
            ],
            skips=[
                Skip(
                    name="dependency_audit",
                    why_safe="No new dependencies added",
                    when_to_run="Run when requirements files change"
                )
            ],
            findings=[],
            merge_gate=MergeGate(
                decision="approve",
                must_fix=[],
                should_fix=[],
                notes_for_coding_agent=[]
            )
        )

        assert output.agent == "security"
        assert output.summary == "No security issues found in code"
        assert output.severity == "merge"
        assert len(output.checks) == 1
        assert len(output.skips) == 1
        assert output.merge_gate.decision == "approve"

    def test_review_output_json_roundtrip(self):
        """ReviewOutput can serialize and deserialize correctly"""
        output = ReviewOutput(
            agent="architecture",
            summary="Well-structured code",
            severity="warning",
            scope=ReviewScope(relevant_files=[], ignored_files=[], reasoning=""),
            checks=[],
            skips=[],
            findings=[
                Finding(
                    id="ARCH-001",
                    title="Missing error handling",
                    severity="warning",
                    confidence="medium",
                    owner="dev",
                    estimate="S",
                    evidence="Function process_data lacks try/except block",
                    risk="Uncaught exceptions could crash application",
                    recommendation="Add error handling for data processing",
                    suggested_patch=None
                )
            ],
            merge_gate=MergeGate(
                decision="approve_with_warnings",
                must_fix=[],
                should_fix=["ARCH-001"],
                notes_for_coding_agent=["Add error handling before merge"]
            )
        )

        # Serialize to JSON
        json_str = output.model_dump_json()
        parsed = ReviewOutput.model_validate_json(json_str)

        assert parsed.agent == output.agent
        assert parsed.summary == output.summary
        assert len(parsed.findings) == 1
        assert parsed.findings[0].id == "ARCH-001"


class TestOrchestratorModels:
    """Test orchestrator-level models"""

    def test_orchestrator_summary(self):
        """OrchestratorSummary model"""
        summary = OrchestratorSummary(
            change_intent="Add authentication flow",
            risk_level="medium",
            high_risk_areas=["session management", "token storage"],
            changed_files_count=5
        )

        assert summary.change_intent == "Add authentication flow"
        assert summary.risk_level == "medium"
        assert len(summary.high_risk_areas) == 2
        assert summary.changed_files_count == 5

    def test_orchestrator_tool_check(self):
        """OrchestratorToolCheck model"""
        check = OrchestratorToolCheck(
            name="unit_tests",
            required=True,
            commands=["pytest tests/unit/"],
            scope=["tests/unit/"],
            why="Verify unit tests pass",
            expected_signal="All tests pass"
        )

        assert check.name == "unit_tests"
        assert check.scope == ["tests/unit/"]

    def test_orchestrator_observed_output(self):
        """OrchestratorObservedOutput model"""
        output = OrchestratorObservedOutput(
            check="unit_tests",
            status="pass",
            evidence="523 tests passed, 3 failed"
        )

        assert output.check == "unit_tests"
        assert output.status == "pass"

    def test_orchestrator_tool_plan(self):
        """OrchestratorToolPlan model"""
        plan = OrchestratorToolPlan(
            recommended_checks=[
                OrchestratorToolCheck(
                    name="linting",
                    required=True,
                    commands=["ruff check"],
                    scope=["src/"],
                    why="Check code style",
                    expected_signal="No lint errors"
                )
            ],
            skipped_checks=[
                OrchestratorSkippedCheck(
                    name="security_scan",
                    why_safe="No security-related changes",
                    when_to_run="Run when auth files change"
                )
            ],
            observed_outputs=[
                OrchestratorObservedOutput(
                    check="linting",
                    status="pass",
                    evidence="No lint errors found"
                )
            ]
        )

        assert len(plan.recommended_checks) == 1
        assert len(plan.skipped_checks) == 1
        assert len(plan.observed_outputs) == 1

    def test_orchestrator_rollup(self):
        """OrchestratorRollup model"""
        rollup = OrchestratorRollup(
            final_severity="warning",
            final_decision="approve_with_warnings",
            rationale="Minor style issues found but no critical blockers",
            findings=[
                OrchestratorFinding(
                    id="ROLLUP-001",
                    source_agents=["linting", "documentation"],
                    title="Style inconsistencies",
                    severity="warning",
                    confidence="high",
                    evidence="ruff found 3 style issues, docstring missing",
                    recommendation="Fix style issues",
                    owner="dev",
                    estimate="S",
                    suggested_patch=None
                )
            ]
        )

        assert rollup.final_severity == "warning"
        assert rollup.final_decision == "approve_with_warnings"
        assert len(rollup.findings) == 1

    def test_orchestrator_finding(self):
        """OrchestratorFinding model"""
        finding = OrchestratorFinding(
            id="ROLLUP-001",
            source_agents=["architecture", "security"],
            title="Design pattern mismatch",
            severity="critical",
            confidence="medium",
            evidence="Security agent found auth issue, architecture agent did not",
            recommendation="Align security and architecture reviews",
            owner="security",
            estimate="M",
            suggested_patch=None
        )

        assert len(finding.source_agents) == 2
        assert finding.severity == "critical"

    def test_orchestrator_output(self):
        """OrchestratorOutput model"""
        output = OrchestratorOutput(
            summary=OrchestratorSummary(
                change_intent="Refactor agent system",
                risk_level="low",
                high_risk_areas=[],
                changed_files_count=3
            ),
            tool_plan=OrchestratorToolPlan(
                recommended_checks=[],
                skipped_checks=[],
                observed_outputs=[]
            ),
            rollup=OrchestratorRollup(
                final_severity="merge",
                final_decision="approve",
                rationale="No issues found",
                findings=[],
                subagent_results=[]
            ),
            merge_gate=MergeGate(
                decision="approve",
                must_fix=[],
                should_fix=[],
                notes_for_coding_agent=[]
            ),
            findings=[],
            subagent_results=[]
        )

        assert output.summary.change_intent == "Refactor agent system"
        assert output.rollup.final_decision == "approve"
        assert output.rollup.final_severity == "merge"


class TestJSONValidation:
    """Test JSON validation scenarios"""

    def test_invalid_severity_rejected(self):
        """Invalid severity value should raise ValidationError"""
        with pytest.raises(ValidationError):
            Finding(
                id="TEST-001",
                title="Test",
                severity="invalid",  # Invalid severity
                confidence="high",
                owner="dev",
                estimate="S",
                evidence="Test",
                risk="Test",
                recommendation="Test"
            )

    def test_invalid_confidence_rejected(self):
        """Invalid confidence value should raise ValidationError"""
        with pytest.raises(ValidationError):
            Finding(
                id="TEST-002",
                title="Test",
                severity="warning",
                confidence="invalid",  # Invalid confidence
                owner="dev",
                estimate="S",
                evidence="Test",
                risk="Test",
                recommendation="Test"
            )

    def test_invalid_owner_rejected(self):
        """Invalid owner value should raise ValidationError"""
        with pytest.raises(ValidationError):
            Finding(
                id="TEST-003",
                title="Test",
                severity="warning",
                confidence="high",
                owner="invalid",  # Invalid owner
                estimate="S",
                evidence="Test",
                risk="Test",
                recommendation="Test"
            )

    def test_invalid_decision_rejected(self):
        """Invalid decision value should raise ValidationError"""
        with pytest.raises(ValidationError):
            MergeGate(
                decision="invalid",  # Invalid decision
                must_fix=[],
                should_fix=[],
                notes_for_coding_agent=[]
            )


class TestJSONIntegration:
    """Integration tests for JSON serialization/deserialization"""

    def test_full_subagent_output_integration(self):
        """Full subagent output roundtrip: Python -> JSON -> Python"""
        output = ReviewOutput(
            agent="security",
            summary="Review complete",
            severity="merge",
            scope=ReviewScope(
                relevant_files=["auth.py"],
                ignored_files=[],
                reasoning="Reviewing auth module"
            ),
            checks=[
                Check(name="secrets", required=True, commands=[], why="", expected_signal="")
            ],
            skips=[],
            findings=[
                Finding(
                    id="SEC-001",
                    title="No secrets found",
                    severity="merge",
                    confidence="high",
                    owner="security",
                    estimate="S",
                    evidence="No hardcoded secrets detected",
                    risk="None",
                    recommendation="Continue monitoring for secrets",
                    suggested_patch=None
                )
            ],
            merge_gate=MergeGate(
                decision="approve",
                must_fix=[],
                should_fix=[],
                notes_for_coding_agent=[]
            )
        )

        # Serialize
        json_output = output.model_dump_json()

        # Deserialize - Note: "approve_with_warnings" used here, not in MergeGate Literal
        reconstructed = ReviewOutput.model_validate_json(json_output)

        # Verify
        assert reconstructed.agent == output.agent
        assert reconstructed.severity == output.severity
        assert len(reconstructed.findings) == len(output.findings)
        assert reconstructed.findings[0].id == "SEC-001"

    def test_orchestrator_output_integration(self):
        """Full orchestrator output roundtrip"""
        output = OrchestratorOutput(
            summary=OrchestratorSummary(
                change_intent="Test PR",
                risk_level="low",
                high_risk_areas=[],
                changed_files_count=1
            ),
            tool_plan=OrchestratorToolPlan(
                recommended_checks=[],
                skipped_checks=[],
                observed_outputs=[]
            ),
            rollup=OrchestratorRollup(
                final_severity="merge",
                final_decision="approve",
                rationale="All checks pass",
                findings=[],
                subagent_results=[]
            ),
            merge_gate=MergeGate(
                decision="approve",
                must_fix=[],
                should_fix=[],
                notes_for_coding_agent=[]
            ),
            findings=[],
            subagent_results=[]
        )

        json_output = output.model_dump_json()
        reconstructed = OrchestratorOutput.model_validate_json(json_output)

        assert reconstructed.summary.change_intent == "Test PR"
        assert reconstructed.rollup.final_decision == "approve"
