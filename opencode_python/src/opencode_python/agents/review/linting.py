"""OpenCode Python - Linting & Style Review Subagent

Reviews code for formatting and linting concerns including
import hygiene, unused vars, type hints, and correctness smells.
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


class LintingReviewAgent(BaseReviewAgent):
    """Linting & Style review subagent

    Reviews changes for:
    - Formatting and lint adherence
    - Import hygiene, unused vars, dead code
    - Type hints sanity (quality, not architecture)
    - Consistency with repo conventions
    - Correctness smells (shadowing, mutable defaults)

    Severity:
    - warning: Minor style issues
    - critical: New lint violations likely failing CI
    - blocking: Syntax errors, obvious correctness issues, format prevents CI merge
    """

    def __init__(self):
        super().__init__(
            name="linting",
            description="Reviews code for formatting and linting concerns including "
                       "import hygiene, unused vars, type hints, and correctness smells",
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for linting relevance

        Relevant changes:
        - Any Python source changes (*.py)
        - Lint config changes (pyproject.toml, ruff.toml, etc.)
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_linting_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} linting-relevant file(s), ignored {len(ignored)} non-linting file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_linting_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to linting review"""
        python_patterns = [".py"]
        config_patterns = ["pyproject.toml", "ruff.toml", "setup.cfg", "setup.py"]

        lower_path = file_path.lower()

        for pattern in python_patterns:
            if pattern in lower_path:
                return True

        for pattern in config_patterns:
            if pattern in lower_path:
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine linting-specific checks"""
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="ruff_check",
                required=True,
                commands=["ruff check " + " ".join(scope.relevant_files)],
                why="Run ruff linter to check code quality",
                expected_signal="No ruff errors found",
            ),
            Check(
                name="ruff_format",
                required=True,
                commands=["ruff format --check " + " ".join(scope.relevant_files)],
                why="Check code formatting consistency",
                expected_signal="All files formatted",
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
        """Generate linting review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_linting_review_agent() -> LintingReviewAgent:
    """Factory function to create LintingReviewAgent instance"""
    return LintingReviewAgent()
