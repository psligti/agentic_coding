"""Diff Scoper Subagent - pre-pass reviewer for diff risk classification and routing."""
from typing import List
from opencode_python.agents.review.base import BaseReviewerAgent, ReviewContext
from opencode_python.agents.review.contracts import (
    ReviewOutput,
    Scope,
    MergeGate,
    Finding,
    Check,
)


_SYSTEM_PROMPT = """You are the Diff Scoper Subagent.

Use this shared behavior:
- If changed_files or diff are missing, request them.
- Summarize change intent and classify risk.
- Route attention to which other subagents matter most.
- Propose minimal checks to run first.

Goal:
- Summarize what changed in 5–10 bullets.
- Classify risk: low/medium/high.
- Produce a routing table: which subagents are most relevant and why.
- Propose the minimal set of checks to run first.

Return JSON with agent="diff_scoper" using the standard schema.
In merge_gate.notes_for_coding_agent include:
- "routing": { "architecture": "...", "security": "...", ... }
- "risk rationale"
Return JSON only."""


class DiffScoperReviewer(BaseReviewerAgent):
    """Pre-pass reviewer that classifies diff risk and routes attention to appropriate subagents.

    This agent runs early in the review pipeline to:
    1. Analyze the git diff to identify scope and magnitude of changes
    2. Classify risk level (high/medium/low) based on multiple factors
    3. Route attention findings to appropriate specialized reviewers
    4. Suggest minimal checks to run first for quick feedback
    """

    def get_agent_name(self) -> str:
        """Return the agent name."""
        return "diff_scoper"

    def get_system_prompt(self) -> str:
        """Return the system prompt for this reviewer agent."""
        return _SYSTEM_PROMPT

    def get_relevant_file_patterns(self) -> List[str]:
        """Return file patterns this reviewer is relevant to.

        Diff scoper is relevant to all files since it analyzes overall change scope.
        """
        return ["**/*"]

    async def review(self, context: ReviewContext) -> ReviewOutput:
        """Perform review on the given context.

        Analyzes the git diff to classify risk and route attention to appropriate subagents.

        Args:
            context: ReviewContext containing changed files, diff, and metadata

        Returns:
            ReviewOutput with risk classification, routing findings, and merge gate decision
        """
        # Extract metrics from diff
        findings: List[Finding] = []
        checks: List[Check] = []

        # Analyze diff scope
        num_files_changed = len(context.changed_files)
        diff_lines = context.diff.strip().split('\n')

        # Count actual code changes (not just file headers or context lines)
        added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        total_code_changes = added_lines + removed_lines

        # Analyze file types touched
        critical_paths = {
            'auth': any('auth' in f.lower() for f in context.changed_files),
            'security': any('security' in f.lower() for f in context.changed_files),
            'config': any(f.endswith(('.yml', '.yaml', '.json', '.toml', '.ini', 'config.*')) for f in context.changed_files),
            'docs': any(f.endswith(('.md', '.txt', '.rst', 'docs/')) for f in context.changed_files),
            'tests': any('test' in f.lower() for f in context.changed_files),
            'critical': any(
                any(cp in f.lower() for cp in ['/', 'lib/', 'core/', 'api/', 'db/'])
                for f in context.changed_files
            )
        }

        # Classify risk level
        risk_level = self._classify_risk(
            num_files_changed,
            total_code_changes,
            critical_paths
        )

        # Create routing findings based on risk and file types
        routing = self._create_routing_findings(
            context.changed_files,
            critical_paths,
            risk_level
        )
        findings.extend(routing)

        # Create minimal checks based on risk
        checks = self._create_minimal_checks(
            risk_level,
            critical_paths,
            context.changed_files
        )

        # Build summary
        summary = self._build_summary(
            num_files_changed,
            added_lines,
            removed_lines,
            risk_level,
            critical_paths
        )

        from typing import Literal
        severity_map: dict[str, Literal["merge", "warning", "critical", "blocking"]] = {
            "high": "critical",
            "medium": "warning",
            "low": "merge"
        }
        severity = severity_map.get(risk_level, "warning")

        # Create merge gate - pre-pass is advisory only
        merge_gate = MergeGate(
            decision="approve",  # Pre-pass agent, always advisory
            must_fix=[],
            should_fix=[],
            notes_for_coding_agent=self._build_routing_notes(risk_level, critical_paths)
        )

        # Create scope - all changed files are relevant for scoping
        scope = Scope(
            relevant_files=context.changed_files,
            ignored_files=[],
            reasoning=f"Diff scoper analyzes all {num_files_changed} changed files to assess overall risk and routing"
        )

        return ReviewOutput(
            agent=self.get_agent_name(),
            summary=summary,
            severity=severity,
            scope=scope,
            checks=checks,
            findings=findings,
            merge_gate=merge_gate
        )

    def _classify_risk(
        self,
        num_files: int,
        code_changes: int,
        critical_paths: dict
    ) -> str:
        """Classify risk level based on diff metrics and file types.

        Args:
            num_files: Number of files changed
            code_changes: Total lines of code changed
            critical_paths: Dictionary of critical path flags

        Returns:
            Risk level: "high", "medium", or "low"
        """
        # High risk indicators
        high_risk_triggers = [
            critical_paths.get('security', False),
            critical_paths.get('auth', False),
            code_changes > 500,
            num_files > 20
        ]

        if any(high_risk_triggers):
            return "high"

        # Medium risk indicators
        medium_risk_triggers = [
            critical_paths.get('config', False),
            code_changes > 100,
            num_files > 5
        ]

        if any(medium_risk_triggers):
            return "medium"

        # Low risk - minimal changes
        return "low"

    def _create_routing_findings(
        self,
        changed_files: List[str],
        critical_paths: dict,
        risk_level: str
    ) -> List[Finding]:
        """Create routing findings based on file types and risk level.

        Args:
            changed_files: List of changed file paths
            critical_paths: Dictionary of critical path flags
            risk_level: Classified risk level

        Returns:
            List of routing findings
        """
        findings: List[Finding] = []
        routing_relevance = {}

        # Determine routing based on critical paths
        if critical_paths.get('security'):
            routing_relevance['security'] = "Security-related files modified, requires security review"

        if critical_paths.get('auth'):
            routing_relevance['security'] = "Authentication/authorization changes, requires security review"

        if critical_paths.get('config'):
            routing_relevance['devops'] = "Configuration files changed, requires devops review"

        if critical_paths.get('critical'):
            routing_relevance['architecture'] = "Core code paths modified, requires architecture review"

        # Python files route to specific reviewers
        py_files = [f for f in changed_files if f.endswith('.py')]
        if py_files:
            if risk_level == 'high':
                routing_relevance['code'] = "Python code changes with high risk, requires thorough code review"
            else:
                routing_relevance['code'] = "Python code changes, requires code review"

        # Documentation only changes may require minimal review
        if critical_paths.get('docs') and len(changed_files) == critical_paths.get('docs_count', 0):
            routing_relevance['docs'] = "Documentation changes, requires docs review"

        # Create findings for each routing
        for agent, reason in routing_relevance.items():
            # Find first relevant file for evidence
            evidence_file = next(
                (f for f in changed_files if any(
                    pattern in f.lower()
                    for pattern in [agent, 'security', 'auth', 'config', 'docs', '.py']
                )),
                changed_files[0] if changed_files else "unknown"
            )

            findings.append(Finding(
                id=f"route-{agent}",
                title=f"Route to {agent.title()} Reviewer",
                severity="warning" if risk_level == "high" else "critical",
                confidence="high",
                owner=agent if agent in ['dev', 'docs', 'devops', 'security'] else 'dev',
                estimate="S",
                evidence=f"File: {evidence_file}",
                risk=risk_level,
                recommendation=reason,
                suggested_patch=None
            ))

        # Add risk classification finding
        if risk_level == "high":
            findings.append(Finding(
                id="risk-classification",
                title=f"High Risk Change Detected",
                severity="critical",
                confidence="high",
                owner="dev",
                estimate="M",
                evidence=f"Files changed: {len(changed_files)}, Risk level: {risk_level}",
                risk=risk_level,
                recommendation="This change touches critical paths or has significant impact. Route to specialized reviewers.",
                suggested_patch=None
            ))

        return findings

    def _create_minimal_checks(
        self,
        risk_level: str,
        critical_paths: dict,
        changed_files: List[str]
    ) -> List[Check]:
        """Create minimal checks to run first based on risk level.

        Args:
            risk_level: Classified risk level
            critical_paths: Dictionary of critical path flags
            changed_files: List of changed file paths

        Returns:
            List of checks to run first
        """
        checks: List[Check] = []

        # Basic checks for all risks
        checks.append(Check(
            name="format_check",
            required=False,
            commands=["pre-commit run --all-files"],
            why="Quick format validation",
            expected_signal="passed"
        ))

        # Medium and high risk checks
        if risk_level in ["medium", "high"]:
            py_files = [f for f in changed_files if f.endswith('.py')]
            if py_files:
                checks.append(Check(
                    name="lint_check",
                    required=False,
                    commands=["ruff check"],
                    why="Code quality validation",
                    expected_signal="No errors found"
                ))

                checks.append(Check(
                    name="type_check",
                    required=False,
                    commands=["mypy --strict"],
                    why="Type safety validation",
                    expected_signal="Success: no issues found"
                ))

        # High risk additional checks
        if risk_level == "high":
            checks.append(Check(
                name="security_scan",
                required=True,
                commands=["bandit -r ."],
                why="Security vulnerability scan for high-risk changes",
                expected_signal="No issues found"
            ))

            if critical_paths.get('tests'):
                checks.append(Check(
                    name="test_suite",
                    required=True,
                    commands=["pytest --cov"],
                    why="Full test suite with coverage for high-risk changes",
                    expected_signal="passed"
                ))

        return checks

    def _build_summary(
        self,
        num_files: int,
        added_lines: int,
        removed_lines: int,
        risk_level: str,
        critical_paths: dict
    ) -> str:
        """Build a summary of the diff scoping analysis.

        Args:
            num_files: Number of files changed
            added_lines: Number of lines added
            removed_lines: Number of lines removed
            risk_level: Classified risk level
            critical_paths: Dictionary of critical path flags

        Returns:
            Summary string
        """
        parts = [
            f"Diff Scoping Analysis: {risk_level.upper()} RISK",
            "",
            "## Change Summary",
            f"- Files changed: {num_files}",
            f"- Lines added: {added_lines}",
            f"- Lines removed: {removed_lines}",
            f"- Total code changes: {added_lines + removed_lines}",
        ]

        parts.append("")
        parts.append("## File Types Touched")
        touched_types = []
        if critical_paths.get('security'):
            touched_types.append("Security-sensitive files")
        if critical_paths.get('auth'):
            touched_types.append("Authentication/Authorization code")
        if critical_paths.get('config'):
            touched_types.append("Configuration files")
        if critical_paths.get('docs'):
            touched_types.append("Documentation")
        if critical_paths.get('tests'):
            touched_types.append("Test files")
        if critical_paths.get('critical'):
            touched_types.append("Core code paths")

        if touched_types:
            for ttype in touched_types:
                parts.append(f"- {ttype}")
        else:
            parts.append("- General code changes")

        parts.append("")
        parts.append("## Risk Assessment")
        parts.append(f"Risk Level: {risk_level.upper()}")

        if risk_level == "high":
            parts.append("- High risk: touches critical paths, significant changes, or security/auth code")
            parts.append("- Recommendation: Route to security, architecture, and code reviewers")
        elif risk_level == "medium":
            parts.append("- Medium risk: moderate changes, may affect configuration or core paths")
            parts.append("- Recommendation: Route to appropriate specialized reviewers")
        else:
            parts.append("- Low risk: minimal changes, likely documentation or simple updates")
            parts.append("- Recommendation: Minimal review required")

        return "\n".join(parts)

    def _build_routing_notes(
        self,
        risk_level: str,
        critical_paths: dict
    ) -> List[str]:
        """Build routing notes for merge_gate.notes_for_coding_agent.

        Args:
            risk_level: Risk level string
            critical_paths: Dictionary of critical path flags

        Returns:
            List of routing notes
        """
        notes = [f"Risk Rationale: {risk_level.upper()} risk classification based on diff analysis"]

        routing_table = {}
        if critical_paths.get('security') or critical_paths.get('auth'):
            routing_table['security'] = "Critical: security/auth changes detected"
        if critical_paths.get('config'):
            routing_table['devops'] = "Important: configuration files modified"
        if critical_paths.get('critical'):
            routing_table['architecture'] = "Recommended: core code paths changed"
        if risk_level in ['medium', 'high']:
            routing_table['code'] = "Recommended: code review for medium/high risk changes"

        # Add routing table as JSON-formatted string
        if routing_table:
            import json
            notes.append(f"routing: {json.dumps(routing_table)}")

        return notes
