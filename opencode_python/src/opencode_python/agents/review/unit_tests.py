"""OpenCode Python - Unit Tests Review Subagent

Reviews code for test coverage concerns including test adequacy,
correctness, edge case coverage, and brittle test detection.
"""
from __future__ import annotations
from typing import List
import logging

from opencode_python.agents.review.base import BaseReviewAgent
from opencode_python.models.review import (
    ReviewScope,
    Check,
    Skip,
    Finding,
    MergeGate,
    ReviewOutput,
)

logger = logging.getLogger(__name__)


class UnitTestsReviewAgent(BaseReviewAgent):
    """Unit Tests review subagent

    Reviews changes for:
    - Adequacy of tests for changed behavior
    - Correctness of tests (assertions, determinism, fixtures)
    - Edge case and failure mode coverage
    - Avoiding brittle tests (time, randomness, network)
    - Selecting minimal test runs to validate change

    Severity:
    - warning: Tests exist but miss an edge case
    - critical: Behavior changed with no tests and moderate risk
    - blocking: High-risk change with no tests; broken/flaky tests introduced
    """

    def __init__(self):
        super().__init__(
            name="unit_tests",
            description="Reviews code for test coverage concerns including test adequacy, "
                       "correctness, edge case coverage, and brittle test detection",
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for unit test relevance

        Relevant changes:
        - Behavior changes in code
        - New modules/functions/classes
        - Bug fixes (prefer regression tests)
        - Changes to test/fixture utilities, CI test steps
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_test_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} test-relevant file(s), ignored {len(ignored)} non-test file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_test_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to unit test review"""
        test_patterns = [
            "test",
            "_test",
            "tests/",
        ]

        python_patterns = [".py"]

        lower_path = file_path.lower()

        for pattern in test_patterns:
            if pattern in lower_path:
                for py_pattern in python_patterns:
                    if py_pattern in lower_path:
                        return True
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine unit test-specific checks"""
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="pytest_run",
                required=True,
                commands=["pytest -q " + " ".join([f for f in scope.relevant_files if f.endswith('.py')])],
                why="Run unit tests to verify code correctness",
                expected_signal="All tests pass",
            ),
        ]

        return checks

    def generate_output(
        self,
        scope: ReviewScope,
        checks: List[Check],
        skips: List[Skip],
        findings: List[Finding],
        check_results: List[dict],
    ) -> ReviewOutput:
        """Generate unit tests review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_unit_tests_review_agent() -> UnitTestsReviewAgent:
    """Factory function to create UnitTestsReviewAgent instance"""
    return UnitTestsReviewAgent()
