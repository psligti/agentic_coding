"""Documentation Review Subagent.

Reviews code changes for documentation coverage including:
- Docstrings for public functions/classes
- README updates for new features
- Configuration documentation
- Usage examples
"""

from __future__ import annotations
from typing import List, Optional
import ast
import re
from pathlib import Path

from opencode_python.agents.review.base import BaseReviewerAgent, ReviewContext
from opencode_python.agents.review.contracts import (
    ReviewOutput,
    Finding,
    Scope,
    MergeGate,
    Check,
    Skip,
)


SYSTEM_PROMPT = """You are the Documentation Review Subagent.

Use this shared behavior:
- Identify which changed files/diffs are relevant to documentation.
- Propose minimal checks; request doc build checks only if relevant.
- If changed_files or diff are missing, request them.
- Discover repo conventions (README, docs toolchain) to propose correct commands.

You specialize in:
- docstrings for public functions/classes
- module-level docs explaining purpose and contracts
- README / usage updates when behavior changes
- configuration documentation (env vars, settings, CLI flags)
- examples and edge case documentation

Relevant changes:
- new public APIs, new commands/tools/skills/agents
- changes to behavior, defaults, outputs, error handling
- renamed modules, moved files, breaking interface changes

Checks you may request:
- docs build/check (mkdocs/sphinx) if repo has it
- docstring linting if configured
- ensure examples match CLI/help output if changed

Documentation review must answer:
1) Would a new engineer understand how to use the changed parts?
2) Are contracts described (inputs/outputs/errors)?
3) Are sharp edges warned?
4) Is terminology consistent?

Severity guidance:
- warning: missing docstring or minor README mismatch
- critical: behavior changed but docs claim old behavior; config/env changes undocumented
- blocking: public interface changed with no documentation and high risk of misuse

Output MUST be valid JSON only with agent="documentation" and the standard schema.
Return JSON only."""


def _is_public_name(name: str) -> bool:
    """Check if a function/class name is public (not private/protected).

    Args:
        name: Function or class name

    Returns:
        True if name is public (doesn't start with _)
    """
    return not name.startswith("_")


def _has_docstring(node: ast.FunctionDef | ast.ClassDef | ast.Module) -> bool:
    """Check if an AST node has a docstring.

    Args:
        node: AST node to check

    Returns:
        True if node has a docstring
    """
    if not node.body:
        return False

    first_stmt = node.body[0]
    if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
        return isinstance(first_stmt.value.value, str)
    return False


def _extract_function_info(
    tree: ast.Module,
) -> List[tuple[str, int, bool, str]]:
    """Extract function information from AST tree.

    Args:
        tree: AST module

    Returns:
        List of (name, line_number, is_public, has_docstring)
    """
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            is_public = _is_public_name(name)
            has_doc = _has_docstring(node)
            functions.append((name, node.lineno, is_public, has_doc))

    return functions


def _extract_class_info(
    tree: ast.Module,
) -> List[tuple[str, int, bool, bool, int]]:
    """Extract class information from AST tree.

    Args:
        tree: AST module

    Returns:
        List of (name, line_number, is_public, has_docstring, public_method_count)
    """
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name
            is_public = _is_public_name(name)
            has_doc = _has_docstring(node)

            public_methods = 0
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if _is_public_name(item.name):
                        public_methods += 1

            classes.append((name, node.lineno, is_public, has_doc, public_methods))

    return classes


def _check_readme_for_features(
    file_path: str,
    repo_root: str,
) -> Optional[Finding]:
    """Check if README mentions new public APIs.

    This is a simplified check - in production, would need more sophisticated
    analysis to understand what's actually "new" vs existing.

    Args:
        file_path: Path to changed file
        repo_root: Repository root

    Returns:
        Finding if README is missing for new features, None otherwise
    """
    readme_path = Path(repo_root) / "README.md"

    if not readme_path.exists():
        return None

    return None


def _check_config_documentation(
    changed_files: List[str],
    repo_root: str,
) -> List[Finding]:
    """Check if config files have corresponding documentation.

    Args:
        changed_files: List of changed files
        repo_root: Repository root

    Returns:
        List of findings about missing config documentation
    """
    findings = []
    config_patterns = ["pyproject.toml", "setup.cfg", ".env.example", "config/**"]

    for file_path in changed_files:
        for pattern in config_patterns:
            if _matches_pattern(file_path, pattern):
                readme_path = Path(repo_root) / "README.md"
                docs_path = Path(repo_root) / "docs"

                config_doc_exists = readme_path.exists() or docs_path.exists()

                if not config_doc_exists:
                    findings.append(
                        Finding(
                            id="doc-missing-config-docs",
                            title=f"Configuration file {file_path} lacks documentation",
                            severity="warning",
                            confidence="medium",
                            owner="docs",
                            estimate="S",
                            evidence=f"File: {file_path} contains configuration changes but no README.md or docs/ directory found",
                            risk="Configuration changes may be unclear to users",
                            recommendation="Document configuration options in README.md or docs/ directory",
                        )
                    )

    return findings


def _matches_pattern(file_path: str, pattern: str) -> bool:
    """Simple pattern matching for file paths.

    Args:
        file_path: File path to check
        pattern: Pattern to match

    Returns:
        True if file matches pattern
    """
    if "**" in pattern:
        parts = pattern.split("**")
        if len(parts) == 2:
            return file_path.startswith(parts[0].rstrip("/"))

    if "*" in pattern:
        regex = pattern.replace(".", r"\.").replace("*", ".*")
        return re.search(regex, file_path) is not None

    return file_path == pattern


class DocumentationReviewer(BaseReviewerAgent):
    """Reviewer agent for documentation quality and coverage."""

    def __init__(self) -> None:
        """Initialize the DocumentationReviewer."""
        self.agent_name = "documentation"

    def get_agent_name(self) -> str:
        """Get the name of this reviewer agent.

        Returns:
            Agent name string
        """
        return self.agent_name

    def get_system_prompt(self) -> str:
        """Get the system prompt for this reviewer agent.

        Returns:
            System prompt string for LLM
        """
        return SYSTEM_PROMPT

    def get_relevant_file_patterns(self) -> List[str]:
        """Get file patterns this reviewer is relevant to.

        Returns:
            List of glob patterns for relevant files
        """
        return [
            "**/*.py",
            "README*",
            "docs/**",
            "*.md",
            "pyproject.toml",
            "setup.cfg",
            ".env.example",
        ]

    async def review(self, context: ReviewContext) -> ReviewOutput:
        """Perform documentation review on the given context.

        Args:
            context: ReviewContext containing changed files, diff, and metadata

        Returns:
            ReviewOutput with findings, severity, and merge gate decision
        """
        findings: List[Finding] = []
        relevant_files: List[str] = []
        ignored_files: List[str] = []

        for file_path in context.changed_files:
            if not self.is_relevant_to_changes([file_path]):
                ignored_files.append(file_path)
                continue

            relevant_files.append(file_path)

            if file_path.endswith("/"):
                continue

            full_path = Path(context.repo_root) / file_path

            if not full_path.exists():
                continue

            if file_path.endswith(".py"):
                findings.extend(self._check_python_docstrings(file_path, full_path))

        findings.extend(_check_config_documentation(relevant_files, context.repo_root))

        scope = Scope(
            relevant_files=relevant_files,
            ignored_files=ignored_files,
            reasoning=f"Analyzed {len(relevant_files)} relevant files for documentation coverage. "
            f"Ignored {len(ignored_files)} files not matching documentation patterns.",
        )

        severity = "merge"
        critical_findings = [f for f in findings if f.severity == "critical"]
        blocking_findings = [f for f in findings if f.severity == "blocking"]
        warning_findings = [f for f in findings if f.severity == "warning"]

        if blocking_findings:
            severity = "blocking"
        elif critical_findings:
            severity = "critical"
        elif warning_findings:
            severity = "warning"

        must_fix = [f.id for f in findings if f.severity in ("blocking", "critical")]
        should_fix = [f.id for f in findings if f.severity == "warning"]

        merge_gate = MergeGate(
            decision="block" if blocking_findings else "needs_changes" if must_fix else "approve",
            must_fix=must_fix,
            should_fix=should_fix,
            notes_for_coding_agent=[
                f"Add docstrings to public functions/classes",
                "Document configuration changes in README.md",
                "Update usage examples for new features",
            ]
            if warning_findings
            else [],
        )

        return ReviewOutput(
            agent=self.agent_name,
            summary=self._build_summary(findings),
            severity=severity,
            scope=scope,
            findings=findings,
            merge_gate=merge_gate,
        )

    def _check_python_docstrings(self, file_path: str, full_path: Path) -> List[Finding]:
        """Check Python file for docstring coverage.

        Args:
            file_path: Relative file path
            full_path: Absolute file path

        Returns:
            List of findings about missing docstrings
        """
        findings = []

        try:
            content = full_path.read_text()
            tree = ast.parse(content)

            functions = _extract_function_info(tree)
            for name, lineno, is_public, has_doc in functions:
                if is_public and not has_doc:
                    findings.append(
                        Finding(
                            id=f"doc-missing-func-{name}-{lineno}",
                            title=f"Public function '{name}' lacks docstring",
                            severity="warning",
                            confidence="high",
                            owner="dev",
                            estimate="S",
                            evidence=f"File: {file_path}:{lineno} - Function '{name}' is public but has no docstring",
                            risk="Users may not understand the function's purpose, parameters, or return value",
                            recommendation=f"Add docstring to function '{name}' describing its purpose, parameters, and return value",
                        )
                    )

            classes = _extract_class_info(tree)
            for name, lineno, is_public, has_doc, public_methods in classes:
                if is_public and not has_doc:
                    findings.append(
                        Finding(
                            id=f"doc-missing-class-{name}-{lineno}",
                            title=f"Public class '{name}' lacks docstring",
                            severity="warning",
                            confidence="high",
                            owner="dev",
                            estimate="M",
                            evidence=f"File: {file_path}:{lineno} - Class '{name}' is public but has no docstring. "
                            f"Has {public_methods} public methods.",
                            risk="Users may not understand the class's purpose or how to use it",
                            recommendation=f"Add docstring to class '{name}' describing its purpose and usage",
                        )
                    )

            if not _has_docstring(tree):
                findings.append(
                    Finding(
                        id=f"doc-missing-module-{file_path}",
                        title=f"Module {file_path} lacks module-level docstring",
                        severity="warning",
                        confidence="medium",
                        owner="dev",
                        estimate="S",
                        evidence=f"File: {file_path} - No module-level docstring found",
                        risk="Module purpose and contracts are not documented",
                        recommendation="Add module-level docstring explaining the module's purpose and key exports",
                    )
                )

        except (SyntaxError, UnicodeDecodeError) as e:
            pass

        return findings

    def _build_summary(self, findings: List[Finding]) -> str:
        """Build a summary of documentation review findings.

        Args:
            findings: List of findings

        Returns:
            Summary string
        """
        if not findings:
            return "Documentation review passed. All public functions/classes have docstrings."

        by_severity = {
            "warning": [f for f in findings if f.severity == "warning"],
            "critical": [f for f in findings if f.severity == "critical"],
            "blocking": [f for f in findings if f.severity == "blocking"],
        }

        parts = []

        if by_severity["blocking"]:
            parts.append(f"Found {len(by_severity['blocking'])} blocking documentation issues")

        if by_severity["critical"]:
            parts.append(f"Found {len(by_severity['critical'])} critical documentation issues")

        if by_severity["warning"]:
            parts.append(f"Found {len(by_severity['warning'])} warnings about missing docstrings")

        return ". ".join(parts) + "."
