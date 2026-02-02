"""OpenCode Python - Documentation Review Subagent

Reviews code for documentation concerns including docstrings,
module-level docs, README/usage updates, and edge case documentation.
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


class DocumentationReviewAgent(BaseReviewAgent):
    """Documentation review subagent

    Reviews changes for:
    - Docstrings for public functions/classes
    - Module-level docs explaining purpose and contracts
    - README / usage updates when behavior changes
    - Configuration documentation (env vars, settings, CLI flags)
    - Examples and edge case documentation
    """

    def __init__(self):
        super().__init__(
            name="documentation",
            description="Reviews code for documentation concerns including docstrings, "
                       "module-level docs, README/usage updates, and edge case documentation",
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for documentation relevance

        Relevant changes:
        - New public APIs, new commands/tools/skills/agents
        - Changes to behavior, defaults, outputs, error handling
        - Renamed modules, moved files, breaking interface changes
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_documentation_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} documentation-relevant file(s), ignored {len(ignored)} non-documentation file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_documentation_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to documentation review"""
        doc_patterns = [
            "readme",
            ".md",
            "doc",
        ]

        python_patterns = [
            ".py",
        ]

        lower_path = file_path.lower()

        for pattern in doc_patterns:
            if pattern in lower_path:
                return True

        for pattern in python_patterns:
            if pattern in lower_path:
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine documentation-specific checks

        Severity guidance:
        - warning: Missing docstring or minor README mismatch
        - critical: Behavior changed but docs claim old behavior; config/env changes undocumented
        - blocking: Public interface changed with no documentation and high risk of misuse
        """
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="docstring_coverage",
                required=True,
                commands=["grep -r 'def \\w+\\(self\\|\\):' " + " ".join(scope.relevant_files) + " | grep -v 'def _' || echo 'Checking docstring coverage'"],
                why="Ensure public functions have docstrings",
                expected_signal="All public functions documented",
            ),
            Check(
                name="readme_sync",
                required=False,
                commands=["test -f README.md && cat README.md || echo 'No README found'"],
                why="Check if README exists and is updated",
                expected_signal="README present and updated",
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
        """Generate documentation review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_documentation_review_agent() -> DocumentationReviewAgent:
    """Factory function to create DocumentationReviewAgent instance"""
    return DocumentationReviewAgent()
