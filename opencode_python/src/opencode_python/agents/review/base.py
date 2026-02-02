"""Base ReviewerAgent abstract class for all review subagents."""
from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from pathlib import Path
import pydantic as pd

from opencode_python.agents.review.contracts import ReviewOutput, Scope


def _match_glob_pattern(file_path: str, pattern: str) -> bool:
    """Match file path against glob pattern, handling ** correctly.

    Args:
        file_path: File path to check
        pattern: Glob pattern (supports *, **, ?)

    Returns:
        True if file path matches pattern
    """
    from fnmatch import fnmatch

    path = Path(file_path)
    path_parts = list(path.parts)

    if '**' in pattern:
        parts = pattern.split('**')
        if len(parts) == 2:
            prefix = parts[0].rstrip('/')
            suffix = parts[1].lstrip('/')

            if prefix:
                prefix_parts = prefix.split('/')
                if not path_parts[:len(prefix_parts)] == prefix_parts:
                    return False
                remaining = path_parts[len(prefix_parts):]
            else:
                remaining = path_parts

            if suffix:
                suffix_parts = suffix.split('/')
                if not suffix_parts:
                    return True

                if len(remaining) >= len(suffix_parts):
                    if remaining[-len(suffix_parts):] == suffix_parts:
                        return True

                if len(suffix_parts) == 1 and remaining:
                    if fnmatch(remaining[-1], suffix_parts[0]):
                        return True
                    if fnmatch('/'.join(remaining), suffix_parts[0]):
                        return True
                return False
            return True

    return fnmatch(str(path), pattern)


class ReviewContext(pd.BaseModel):
    """Context data passed to reviewer agents."""

    changed_files: List[str]
    diff: str
    repo_root: str
    base_ref: str | None = None
    head_ref: str | None = None
    pr_title: str | None = None
    pr_description: str | None = None

    model_config = pd.ConfigDict(extra="forbid")


class BaseReviewerAgent(ABC):
    """Abstract base class for all review subagents.

    All specialized reviewers must inherit from this class and implement
    the required abstract methods. This ensures consistent interface across
    all review agents.
    """

    @abstractmethod
    async def review(self, context: ReviewContext) -> ReviewOutput:
        """Perform review on the given context.

        Args:
            context: ReviewContext containing changed files, diff, and metadata

        Returns:
            ReviewOutput with findings, severity, and merge gate decision
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this reviewer agent.

        Returns:
            System prompt string for LLM
        """
        pass

    @abstractmethod
    def get_relevant_file_patterns(self) -> List[str]:
        """Get file patterns this reviewer is relevant to.

        Returns:
            List of glob patterns (e.g., ["*.py", "src/**/*.py"])
        """
        pass

    def is_relevant_to_changes(self, changed_files: List[str]) -> bool:
        """Check if this reviewer is relevant to the given changed files.

        Args:
            changed_files: List of changed file paths

        Returns:
            True if any changed file matches the relevant patterns
        """
        patterns = self.get_relevant_file_patterns()
        if not patterns:
            return False

        for file_path in changed_files:
            for pattern in patterns:
                try:
                    if _match_glob_pattern(file_path, pattern):
                        return True
                except ValueError:
                    continue
        return False

    def format_inputs_for_prompt(self, context: ReviewContext) -> str:
        """Format review context for inclusion in LLM prompt.

        Args:
            context: ReviewContext to format

        Returns:
            Formatted string suitable for inclusion in prompt
        """
        parts = [
            "## Review Context",
            "",
            f"**Repository Root**: {context.repo_root}",
            "",
            "### Changed Files",
        ]

        for file_path in context.changed_files:
            parts.append(f"- {file_path}")

        if context.base_ref and context.head_ref:
            parts.append("")
            parts.append("### Git Diff")
            parts.append(f"**Base Ref**: {context.base_ref}")
            parts.append(f"**Head Ref**: {context.head_ref}")

        parts.append("")
        parts.append("### Diff Content")
        parts.append("```diff")
        parts.append(context.diff)
        parts.append("```")

        if context.pr_title:
            parts.append("")
            parts.append("### Pull Request")
            parts.append(f"**Title**: {context.pr_title}")
            if context.pr_description:
                parts.append(f"**Description**:\n{context.pr_description}")

        return "\n".join(parts)
