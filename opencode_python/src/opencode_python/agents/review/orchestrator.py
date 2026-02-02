"""OpenCode Python - PR Review Orchestrator

Coordinates multiple review subagents and aggregates results
into a final merge gate decision.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import asyncio
import logging

from opencode_python.agents.review.base import BaseReviewAgent
from opencode_python.models.review import (
    ReviewOutput,
    ReviewScope,
    Check,
    Skip,
    Finding,
    MergeGate,
    OrchestratorSummary,
    OrchestratorToolCheck,
    OrchestratorSkippedCheck,
    OrchestratorObservedOutput,
    OrchestratorToolPlan,
    OrchestratorRollup,
    OrchestratorFinding,
    OrchestratorOutput,
)
from typing import cast

logger = logging.getLogger(__name__)


class PRReviewOrchestrator:
    """PR Review Orchestrator

    Coordinates review subagents and aggregates results.
    Implements:
    - Identify changed files and summarize change intent
    - Execute required subagents (architecture, security, documentation, telemetry_metrics, linting, unit_tests)
    - Aggregate and dedupe findings
    - Generate tool plan
    - Apply merge gate policy for final decision
    """

    REQUIRED_SUBAGENTS = [
        "architecture",
        "security",
        "documentation",
        "telemetry_metrics",
        "linting",
        "unit_tests",
    ]

    OPTIONAL_SUBAGENTS = [
        "diff_scoper",
        "requirements",
        "performance_reliability",
        "dependency_license",
        "release_changelog",
    ]

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize PRReviewOrchestrator

        Args:
            llm_client: Optional LLM client for making API calls
        """
        self.subagents: Dict[str, BaseReviewAgent] = {}
        self.subagent_results: List[Dict[str, Any]] = []
        self.llm_client = llm_client
        self._init_required_subagents()

    def _init_required_subagents(self):
        """Initialize all required review subagents"""
        from opencode_python.agents.review import (
            ArchitectureReviewAgent,
            SecurityReviewAgent,
            DocumentationReviewAgent,
            TelemetryMetricsReviewAgent,
            LintingReviewAgent,
            UnitTestsReviewAgent,
        )

        self.subagents["architecture"] = BaseReviewAgent._init_with_llm(
            ArchitectureReviewAgent, llm_client=self.llm_client
        )
        self.subagents["security"] = BaseReviewAgent._init_with_llm(
            SecurityReviewAgent, llm_client=self.llm_client
        )
        self.subagents["documentation"] = BaseReviewAgent._init_with_llm(
            DocumentationReviewAgent, llm_client=self.llm_client
        )
        self.subagents["telemetry_metrics"] = BaseReviewAgent._init_with_llm(
            TelemetryMetricsReviewAgent, llm_client=self.llm_client
        )
        self.subagents["linting"] = BaseReviewAgent._init_with_llm(
            LintingReviewAgent, llm_client=self.llm_client
        )
        self.subagents["unit_tests"] = BaseReviewAgent._init_with_llm(
            UnitTestsReviewAgent, llm_client=self.llm_client
        )

    async def review_pr(
        self,
        changed_files: List[str],
        diff: str,
        repo_root: Optional[str] = None,
        base_ref: Optional[str] = None,
        head_ref: Optional[str] = None,
    ) -> OrchestratorOutput:
        """Review a PR by running all subagents and aggregating results

        Args:
            changed_files: List of changed file paths
            diff: Unified diff of changes
            repo_root: Path to repository (optional)
            base_ref: Base git ref (e.g., main)
            head_ref: Head git ref (e.g., PR branch)

        Returns:
            OrchestratorOutput with aggregated results and final decision
        """
        logger.info(f"Starting PR review for {len(changed_files)} changed files")

        self.subagent_results: List[Dict[str, Any]] = []

        for agent_name in self.REQUIRED_SUBAGENTS:
            agent = self.subagents.get(agent_name)
            if not agent:
                logger.warning(f"Subagent {agent_name} not found, skipping")
                continue

            logger.info(f"Running subagent: {agent_name}")

            try:
                result = await self._run_subagent(
                    agent, changed_files, diff
                )
                self.subagent_results.append(result.model_dump(mode="json"))
            except Exception as e:
                logger.error(f"Error running {agent_name} subagent: {e}")
                continue

        rollup = self._aggregate_results(self.subagent_results)
        tool_plan = self._generate_tool_plan(changed_files, self.subagent_results)
        summary = self._generate_summary(changed_files, diff)

        final_severity = self._determine_final_severity(rollup)
        final_decision = self._map_severity_to_decision(final_severity)

        orchestrator_output = OrchestratorOutput(
            summary=summary,
            tool_plan=tool_plan,
            rollup=OrchestratorRollup(
                final_severity=final_severity,  # type: ignore
                final_decision=final_decision,  # type: ignore
                rationale=self._generate_rationale(final_severity, rollup),
                findings=rollup.findings,
            ),
            findings=rollup.findings,
            subagent_results=self.subagent_results,
            merge_gate=MergeGate(
                decision=final_decision,  # type: ignore
                must_fix=[f.id for f in rollup.findings if f.severity in ["critical", "blocking"]],
                should_fix=[f.id for f in rollup.findings if f.severity == "warning"],
                notes_for_coding_agent=[f"Address {len(rollup.findings)} findings"],
            ),
        )

        logger.info(f"PR review complete: {final_decision} (severity: {final_severity})")

        return orchestrator_output

    async def _run_subagent(
        self,
        agent: BaseReviewAgent,
        changed_files: List[str],
        diff: str,
    ) -> ReviewOutput:
        """Run a single subagent"""
        if agent.llm_client and hasattr(agent, 'review_with_llm'):
            output = await agent.review_with_llm(changed_files, diff)
        else:
            scope = agent.analyze_changes(changed_files, diff)
            checks = agent.determine_checks(scope)
            skips: List[Skip] = []
            findings: List[Finding] = []
            check_results: List[dict] = []

            output = agent.generate_output(scope, checks, skips, findings, check_results)

        return output

    def _aggregate_results(
        self,
        subagent_results: List[Dict[str, Any]]
    ) -> OrchestratorRollup:
        """Aggregate results from all subagents

        Merge and dedupe findings from multiple subagents
        """
        all_findings: List[OrchestratorFinding] = []

        for result in subagent_results:
            findings_data = result.get("findings", [])
            agent_name = result.get("agent", "unknown")
            for f_data in findings_data:
                try:
                    finding = Finding(**f_data)
                    # Convert Finding to OrchestratorFinding
                    orch_finding = OrchestratorFinding(
                        id=finding.id,
                        source_agents=[agent_name],
                        title=finding.title,
                        severity=finding.severity,
                        confidence=finding.confidence,
                        evidence=finding.evidence,
                        recommendation=finding.recommendation,
                        suggested_patch=finding.suggested_patch,
                        owner=finding.owner,
                        estimate=finding.estimate,
                    )
                    all_findings.append(orch_finding)
                except Exception as e:
                    logger.error(f"Failed to parse finding: {e}")

        deduped_findings = self._dedupe_findings(all_findings)

        return OrchestratorRollup(
            final_severity="merge",  # type: ignore - Will be overridden
            final_decision="approve",  # type: ignore - Will be overridden
            rationale="",  # Will be overridden
            findings=deduped_findings,
        )

    def _dedupe_findings(
        self, findings: List[OrchestratorFinding]
    ) -> List[OrchestratorFinding]:
        """Deduplicate findings based on title and evidence"""
        seen = set()
        deduped = []

        for finding in findings:
            key = f"{finding.title}:{finding.evidence[:100]}"
            if key not in seen:
                seen.add(key)
                deduped.append(finding)

        logger.info(f"Deduped {len(findings)} findings to {len(deduped)} unique findings")

        return deduped

    def _generate_tool_plan(
        self,
        changed_files: List[str],
        subagent_results: List[Dict[str, Any]],
    ) -> OrchestratorToolPlan:
        """Generate minimal tool execution plan

        Aggregates recommended checks from all subagents
        """
        recommended_checks: List[OrchestratorToolCheck] = []
        skipped_checks: List[OrchestratorSkippedCheck] = []
        observed_outputs: List[OrchestratorObservedOutput] = []

        for result in subagent_results:
            checks_data = result.get("checks", [])
            for check_data in checks_data:
                try:
                    check = OrchestratorToolCheck(
                        name=check_data.get("name", ""),
                        required=check_data.get("required", False),
                        commands=check_data.get("commands", []),
                        scope=changed_files,
                        why=check_data.get("why", ""),
                        expected_signal=check_data.get("expected_signal", ""),
                    )
                    recommended_checks.append(check)
                except Exception as e:
                    logger.error(f"Failed to parse check: {e}")

            skips_data = result.get("skips", [])
            for skip_data in skips_data:
                try:
                    skip = OrchestratorSkippedCheck(
                        name=skip_data.get("name", ""),
                        why_safe=skip_data.get("why_safe", ""),
                        when_to_run=skip_data.get("when_to_run", ""),
                    )
                    skipped_checks.append(skip)
                except Exception as e:
                    logger.error(f"Failed to parse skip: {e}")

        return OrchestratorToolPlan(
            recommended_checks=recommended_checks,
            skipped_checks=skipped_checks,
            observed_outputs=observed_outputs,
        )

    def _generate_summary(
        self,
        changed_files: List[str],
        diff: str,
    ) -> OrchestratorSummary:
        """Generate high-level summary of PR"""
        risk_level = "low"

        for result_data in self._get_all_subagent_results():
            severity = result_data.get("severity", "merge")
            if severity in ["critical", "blocking"]:
                risk_level = "high"
                break
            elif severity == "warning" and risk_level != "high":
                risk_level = "medium"

        high_risk_areas = []
        for result_data in self._get_all_subagent_results():
            if result_data.get("severity") in ["critical", "blocking"]:
                high_risk_areas.append(result_data.get("agent", ""))

        return OrchestratorSummary(
            change_intent=self._infer_change_intent(changed_files, diff),
            risk_level=risk_level,
            high_risk_areas=high_risk_areas,
            changed_files_count=len(changed_files),
        )

    def _infer_change_intent(
        self, changed_files: List[str], diff: str
    ) -> str:
        """Infer the intent of changes from file paths and diff"""
        if not diff:
            return f"Review of {len(changed_files)} changed files"

        diff_lower = diff.lower()

        if "def " in diff_lower or "class " in diff_lower:
            return "Implementation of new code"

        if "import " in diff_lower:
            return "Dependency or import changes"

        if "test" in diff_lower:
            return "Test additions or modifications"

        return f"Review of {len(changed_files)} changed files"

    def _determine_final_severity(
        self, rollup: OrchestratorRollup
    ) -> str:
        """Determine final severity based on merge gate policy

        Merge gate rollup policy (from PRD section 7):
        - If ANY subagent returns blocking -> final blocking
        - Else if ANY returns critical -> final critical
        - Else if ANY returns warning -> final warning
        - Else -> final merge
        """
        if not rollup.findings:
            return "merge"

        for finding in rollup.findings:
            if finding.severity == "blocking":
                return "blocking"
            elif finding.severity == "critical":
                return "critical"
            elif finding.severity == "warning":
                return "warning"

        return "merge"

    def _map_severity_to_decision(
        self, severity: str
    ) -> str:
        """Map severity to merge gate decision"""
        decision_map = {
            "blocking": "block",
            "critical": "needs_changes",
            "warning": "approve_with_warnings",
            "merge": "approve",
        }
        return decision_map.get(severity, "approve")

    def _generate_rationale(
        self, final_severity: str, rollup: OrchestratorRollup
    ) -> str:
        """Generate rationale for final decision"""
        if final_severity == "merge":
            return "No issues found across all review domains"

        blocking_count = sum(1 for f in rollup.findings if f.severity == "blocking")
        critical_count = sum(1 for f in rollup.findings if f.severity == "critical")
        warning_count = sum(1 for f in rollup.findings if f.severity == "warning")

        parts = []
        if blocking_count > 0:
            parts.append(f"{blocking_count} blocking issue(s)")
        if critical_count > 0:
            parts.append(f"{critical_count} critical issue(s)")
        if warning_count > 0:
            parts.append(f"{warning_count} warning(s)")

        return "; ".join(parts)

    def _get_all_subagent_results(self) -> List[Dict[str, Any]]:
        """Get all subagent results that have been run"""
        return self.subagent_results


def create_pr_review_orchestrator(llm_client: Optional[Any] = None) -> PRReviewOrchestrator:
    """Factory function to create PRReviewOrchestrator instance

    Args:
        llm_client: Optional LLM client for making API calls

    Returns:
        PRReviewOrchestrator instance
    """
    return PRReviewOrchestrator(llm_client=llm_client)
