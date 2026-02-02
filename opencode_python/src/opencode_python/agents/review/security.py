"""OpenCode Python - Security Review Subagent

Reviews code for security concerns including secrets handling,
authentication/authorization, injection risks, and supply chain issues.
"""
from __future__ import annotations
from typing import List
import logging
import re

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


class SecurityReviewAgent(BaseReviewAgent):
    """Security review subagent

    Reviews changes for:
    - Secrets handling (keys/tokens/passwords), logging of sensitive data
    - Authn/authz, permission checks, RBAC
    - Injection risks: SQL injection, command injection, template injection
    - SSRF, unsafe network calls, insecure defaults
    - Dependency/supply chain risk signals (new deps, loosened pins)
    - Cryptography misuse
    - File/path handling, deserialization, eval/exec usage
    - CI/CD exposures (tokens, permissions, workflow changes)
    """

    def __init__(self):
        super().__init__(
            name="security",
            description="Reviews code for security concerns including secrets handling, "
                       "authentication/authorization, injection risks, and supply chain issues",
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for security relevance

        High-signal file patterns:
        - auth/**, security/**, iam/**, permissions/**, middleware/**
        - network clients, webhook handlers, request parsers
        - subprocess usage, shell commands
        - config files: *.yml, *.yaml (CI), Dockerfile, terraform, deploy scripts
        - dependency files: pyproject.toml, requirements*.txt, poetry.lock, uv.lock
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_security_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} security-relevant file(s), ignored {len(ignored)} non-security file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_security_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to security review"""
        security_patterns = [
            "auth/",
            "security/",
            "iam/",
            "permissions/",
            "middleware/",
        ]

        config_patterns = [
            ".yml",
            ".yaml",
            "dockerfile",
            "terraform",
            "deploy",
        ]

        dependency_patterns = [
            "pyproject.toml",
            "requirements",
            "poetry.lock",
            "uv.lock",
        ]

        lower_path = file_path.lower()

        for pattern in security_patterns:
            if pattern in lower_path:
                return True

        for pattern in config_patterns:
            if pattern in lower_path:
                return True

        for pattern in dependency_patterns:
            if pattern in lower_path:
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine security-specific checks

        Blocking conditions:
        - Plaintext secrets committed or leaked into logs
        - Authz bypass risk or missing permission checks
        - Code execution risk (eval/exec) without strong sandboxing
        - Command injection risk via subprocess with untrusted input
        - Unsafe deserialization of untrusted input
        """
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="secrets_scan",
                required=True,
                commands=["grep -rE '(password|token|secret|api[_-]?key|private[_-]?key|aws[_-]?access[_-]?key)' " + " ".join(scope.relevant_files) + " || echo 'No secrets found'"],
                why="Scan for hardcoded secrets and sensitive data",
                expected_signal="No secrets found or matches reported",
            ),
            Check(
                name="subprocess_injection",
                required=True,
                commands=["grep -rE 'subprocess\\.(run|call|Popen)' " + " ".join(scope.relevant_files)],
                why="Check for subprocess usage that may be vulnerable to injection",
                expected_signal="All subprocess calls reviewed for injection risk",
            ),
            Check(
                name="eval_usage",
                required=True,
                commands=["grep -rE '(eval|exec\\(\\(|compile\\()' " + " ".join(scope.relevant_files)],
                why="Check for eval/exec usage that may enable code injection",
                expected_signal="No unsafe eval/exec usage found",
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
    ) -> "ReviewOutput":
        """Generate security review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_security_review_agent() -> SecurityReviewAgent:
    """Factory function to create SecurityReviewAgent instance"""
    return SecurityReviewAgent()
