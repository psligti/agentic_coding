"""Linting and Style Review Subagent."""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Literal

import pydantic as pd

from opencode_python.agents.review.base import BaseReviewerAgent, ReviewContext
from opencode_python.agents.review.contracts import (
    ReviewOutput,
    Scope,
    MergeGate,
    Finding,
    Check,
)
from opencode_python.agents.review.utils.executor import CommandExecutor

logger = logging.getLogger(__name__)

LINTING_SYSTEM_PROMPT = """You are the Linting & Style Review Subagent.

Use this shared behavior:
- Identify which changed files/diffs are relevant to lint/style.
- Propose minimal changed-files-only lint commands first.
- If changed_files or diff are missing, request them.
- Discover repo conventions (ruff/black/flake8/isort, format settings in pyproject).

You specialize in:
- formatting and lint adherence
- import hygiene, unused vars, dead code
- type hints sanity (quality, not architecture)
- consistency with repo conventions
- correctness smells (shadowing, mutable defaults)

Relevant changes:
- any Python source changes (*.py)
- lint config changes (pyproject.toml, ruff.toml, etc.)

Checks you may request:
- ruff check <changed_files>
- ruff format <changed_files>
- formatter/linter commands used by the repo
- type check if enforced (only when relevant)

Severity:
- warning: minor style issues
- critical: new lint violations likely failing CI
- blocking: syntax errors, obvious correctness issues, format prevents CI merge

Output MUST be valid JSON only with agent="linting" and the standard schema.
Return JSON only."""


class LintingReviewer(BaseReviewerAgent):
    """Reviewer agent for linting, formatting, and code quality checks.

    Checks for:
    - Formatting issues (indentation, line length)
    - Lint adherence (PEP8 violations, style issues)
    - Type hints coverage (missing type annotations)
    - Code quality smells (unused imports, dead code)
    """

    def __init__(self, executor: CommandExecutor | None = None):
        """Initialize the LintingReviewer.

        Args:
            executor: Optional CommandExecutor for running linters.
        """
        self.executor = executor

    def get_agent_name(self) -> str:
        """Return the agent name."""
        return "linting"

    def get_system_prompt(self) -> str:
        """Return the system prompt for this reviewer."""
        return LINTING_SYSTEM_PROMPT

    def get_relevant_file_patterns(self) -> List[str]:
        """Return file patterns this reviewer is relevant to."""
        return [
            "**/*.py",
            "*.json",
            "*.toml",
            "*.yaml",
            "*.yml",
            "pyproject.toml",
            "ruff.toml",
            ".flake8",
            "setup.cfg",
        ]

    async def review(self, context: ReviewContext) -> ReviewOutput:
        """Perform linting review on the given context.

        Args:
            context: ReviewContext containing changed files, diff, and metadata

        Returns:
            ReviewOutput with findings, severity, and merge gate decision
        """
        findings: List[Finding] = []
        checks: List[Check] = []

        # Filter to relevant files
        relevant_files = [
            f for f in context.changed_files
            if self.is_relevant_to_changes([f])
        ]

        if not relevant_files:
            return ReviewOutput(
                agent="linting",
                summary="No Python or lint config files changed. Linting review not applicable.",
                severity="merge",
                scope=Scope(
                    relevant_files=[],
                    reasoning="No relevant files for linting review",
                ),
                checks=checks,
                findings=findings,
                merge_gate=MergeGate(
                    decision="approve",
                    notes_for_coding_agent=[
                        "No Python or lint configuration files were changed.",
                    ],
                ),
            )

        # Initialize executor if not provided
        executor = self.executor or CommandExecutor(
            repo_root=Path(context.repo_root),
        )

        # Run linters and gather findings
        try:
            # Run ruff check if available
            ruff_result = await executor.execute(
                f"ruff check {' '.join(relevant_files)}",
                timeout=60,
            )

            if ruff_result.parsed_findings:
                for finding in ruff_result.parsed_findings:
                    severity_str = self._determine_severity_from_ruff(
                        finding.get("code", ""),
                    )
                    severity: Literal["warning", "critical", "blocking"] = (
                        "warning" if severity_str == "warning"
                        else "critical" if severity_str == "critical"
                        else "blocking"
                    )

                    findings.append(Finding(
                        id=f"lint-ruff-{len(findings)}",
                        title=f"Ruff issue: {finding.get('code', 'unknown')}",
                        severity=severity,
                        confidence="high",
                        owner="dev",
                        estimate="S",
                        evidence=self._format_finding_evidence(finding),
                        risk="Linting violation that may affect code quality",
                        recommendation=self._get_ruff_recommendation(finding),
                    ))

                checks.append(Check(
                    name="ruff_check",
                    required=True,
                    commands=[f"ruff check {' '.join(relevant_files)}"],
                    why="Check for PEP8 violations and code quality issues",
                    expected_signal="No lint errors",
                ))

        except Exception as e:
            logger.warning(f"Ruff check failed: {e}")
            findings.append(Finding(
                id="lint-ruff-execution",
                title="Ruff execution failed",
                severity="warning",
                confidence="medium",
                owner="devops",
                estimate="S",
                evidence=f"Failed to run ruff: {str(e)}",
                risk="Unable to verify linting status",
                recommendation="Ensure ruff is installed and configured",
            ))

        try:
            # Run ruff format check if available
            format_result = await executor.execute(
                f"ruff format --check {' '.join(relevant_files)}",
                timeout=60,
            )

            if format_result.exit_code != 0:
                findings.append(Finding(
                    id="lint-format",
                    title="Code formatting issues detected",
                    severity="warning",
                    confidence="high",
                    owner="dev",
                    estimate="M",
                    evidence=f"Files not properly formatted: {relevant_files}",
                    risk="Inconsistent formatting reduces readability",
                    recommendation="Run 'ruff format' to fix formatting issues",
                ))

                checks.append(Check(
                    name="ruff_format",
                    required=True,
                    commands=[f"ruff format --check {' '.join(relevant_files)}"],
                    why="Ensure code follows consistent formatting",
                    expected_signal="All files formatted correctly",
                ))

        except Exception as e:
            logger.warning(f"Ruff format check failed: {e}")

        # Check for type hints coverage (basic analysis)
        type_hint_findings = self._check_type_hints(context, relevant_files)
        findings.extend(type_hint_findings)

        # Determine overall severity and merge gate decision
        severity_str = self._determine_overall_severity(findings)
        severity: Literal["merge", "warning", "critical", "blocking"] = (
            "merge" if severity_str == "merge"
            else "warning" if severity_str == "warning"
            else "critical" if severity_str == "critical"
            else "blocking"
        )

        merge_gate_str = self._determine_merge_gate(findings, severity_str)
        merge_gate_decision: Literal["approve", "needs_changes", "block"] = (
            "approve" if merge_gate_str == "approve"
            else "needs_changes" if merge_gate_str == "needs_changes"
            else "block"
        )

        summary = self._generate_summary(findings, severity)

        return ReviewOutput(
            agent="linting",
            summary=summary,
            severity=severity,
            scope=Scope(
                relevant_files=relevant_files,
                reasoning="Linting and formatting review for Python files and lint configs",
            ),
            checks=checks,
            findings=findings,
            merge_gate=MergeGate(
                decision=merge_gate_decision,
                must_fix=[f.id for f in findings if f.severity in ("critical", "blocking")],
                should_fix=[f.id for f in findings if f.severity == "warning"],
                notes_for_coding_agent=self._generate_notes_for_coding_agent(findings),
            ),
        )

    def _determine_severity_from_ruff(self, code: str) -> str:
        """Determine severity from ruff error code.

        Args:
            code: Ruff error code (e.g., "E501", "F401")

        Returns:
            Severity level ("warning", "critical", or "blocking")
        """
        # Error codes starting with E are typically syntax/structure errors
        # Error codes starting with F are pyflakes (unused imports, etc.)
        # Error codes starting with W are warnings
        # Error codes starting with I are import-related

        if not code:
            return "warning"

        code_prefix = code[0] if code else ""

        if code_prefix == "E":
            # Syntax/structure errors are critical
            return "critical"
        elif code_prefix == "F":
            # Pyflakes errors (unused imports, undefined names)
            return "critical"
        elif code_prefix in ("W", "I"):
            # Warnings and import issues are typically warnings
            return "warning"
        else:
            # Other codes (UP, N, etc.) are generally warnings
            return "warning"

    def _format_finding_evidence(self, finding: dict) -> str:
        """Format finding evidence for readability.

        Args:
            finding: Finding dictionary with filename, line, etc.

        Returns:
            Formatted evidence string
        """
        parts = []

        if "filename" in finding:
            parts.append(f"File: {finding['filename']}")

        if "line" in finding:
            parts.append(f"Line: {finding['line']}")

        if "column" in finding:
            parts.append(f"Column: {finding['column']}")

        if "message" in finding:
            parts.append(f"Message: {finding['message']}")

        return " | ".join(parts)

    def _get_ruff_recommendation(self, finding: dict) -> str:
        """Get recommendation for ruff finding.

        Args:
            finding: Finding dictionary

        Returns:
            Recommendation string
        """
        code = finding.get("code", "")
        message = finding.get("message", "")

        if code == "F401":
            return "Remove unused import or use it in the code"
        elif code == "F841":
            return "Remove unused variable or use it in the code"
        elif code == "E501":
            return "Break long line to adhere to line length limit"
        elif code.startswith("W"):
            return "Fix warning according to PEP8 guidelines"
        elif code.startswith("I"):
            return "Fix import ordering or duplication"
        else:
            return f"Fix: {message}"

    def _check_type_hints(self, context: ReviewContext, relevant_files: List[str]) -> List[Finding]:
        """Check for type hints coverage in changed files.

        Args:
            context: ReviewContext
            relevant_files: List of relevant Python files

        Returns:
            List of type hint findings
        """
        findings: List[Finding] = []

        for file_path in relevant_files:
            if not file_path.endswith(".py"):
                continue

            try:
                full_path = Path(context.repo_root) / file_path
                if not full_path.exists():
                    continue

                content = full_path.read_text()

                # Check for function definitions without type hints
                import re

                func_pattern = re.compile(
                    r'^\s*(?:async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[^:]+)?:',
                    re.MULTILINE,
                )

                functions = func_pattern.finditer(content)

                for match in functions:
                    func_name = match.group(1)
                    func_def = match.group(0)

                    # Check if function has return type annotation
                    has_return_type = "->" in func_def

                    # Skip dunder methods, test functions, and private methods
                    if func_name.startswith("__"):
                        continue
                    if func_name.startswith("test_"):
                        continue

                    if not has_return_type:
                        findings.append(Finding(
                            id=f"type-hint-{file_path}-{func_name}",
                            title=f"Missing type hints in function: {func_name}",
                            severity="warning",
                            confidence="medium",
                            owner="dev",
                            estimate="S",
                            evidence=f"File: {file_path} | Function: {func_name} lacks return type annotation",
                            risk="Missing type hints reduce code maintainability and type safety",
                            recommendation=f"Add return type annotation to function '{func_name}'",
                        ))

            except Exception as e:
                logger.warning(f"Failed to check type hints in {file_path}: {e}")

        return findings

    def _determine_overall_severity(self, findings: List[Finding]) -> str:
        """Determine overall severity from all findings.

        Args:
            findings: List of all findings

        Returns:
            Overall severity level
        """
        if not findings:
            return "merge"

        # Check for blocking or critical issues
        for finding in findings:
            if finding.severity == "blocking":
                return "blocking"
            if finding.severity == "critical":
                return "critical"

        # If only warnings, use warning severity
        return "warning"

    def _determine_merge_gate(self, findings: List[Finding], severity: str) -> str:
        """Determine merge gate decision.

        Args:
            findings: List of all findings
            severity: Overall severity level

        Returns:
            Merge gate decision ("approve", "needs_changes", or "block")
        """
        if severity == "blocking":
            return "block"
        elif severity == "critical":
            return "needs_changes"
        elif severity == "warning" and findings:
            return "needs_changes"
        else:
            return "approve"

    def _generate_summary(self, findings: List[Finding], severity: Literal["merge", "warning", "critical", "blocking"]) -> str:
        if not findings:
            return "Linting review complete. No issues found."

        critical = [f for f in findings if f.severity in ("critical", "blocking")]
        warnings = [f for f in findings if f.severity == "warning"]

        parts = [f"Linting review complete. Found {len(findings)} total issues:"]
        if critical:
            parts.append(f" - {len(critical)} critical/blocking issues")
        if warnings:
            parts.append(f" - {len(warnings)} warnings")

        return " ".join(parts)

    def _generate_notes_for_coding_agent(self, findings: List[Finding]) -> List[str]:
        """Generate notes for the coding agent.

        Args:
            findings: List of findings

        Returns:
            List of notes for the coding agent
        """
        notes = []

        if not findings:
            return ["No linting issues found. Code is clean!"]

        # Group findings by severity
        critical = [f for f in findings if f.severity == "critical"]
        warnings = [f for f in findings if f.severity == "warning"]

        if critical:
            notes.append(f"Found {len(critical)} critical linting issues that must be fixed:")
            for finding in critical[:3]:  # Limit to first 3
                notes.append(f"  - {finding.title}")

        if warnings:
            notes.append(f"Found {len(warnings)} style warnings that should be fixed:")
            for finding in warnings[:3]:  # Limit to first 3
                notes.append(f"  - {finding.title}")

        # Add general recommendations
        notes.append("Run 'ruff check --fix' to auto-fix many issues")
        notes.append("Run 'ruff format' to fix formatting issues")
        notes.append("Consider adding type hints to improve code maintainability")

        return notes
