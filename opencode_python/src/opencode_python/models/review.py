"""OpenCode Python - PR Review JSON Contracts

Pydantic models for multi-subagent PR review system.
Defines type-safe JSON output contracts for all subagents per PRD section 8.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
import pydantic as pd


class ReviewScope(pd.BaseModel):
    """Review scope - which files are relevant to this review"""
    relevant_files: List[str] = pd.Field(
        description="List of file paths that are relevant to this review"
    )
    ignored_files: List[str] = pd.Field(
        default_factory=list,
        description="List of file paths that were intentionally ignored in this review"
    )
    reasoning: str = pd.Field(
        ...,
        description="Explanation of why files were scoped this way"
    )


class Check(pd.BaseModel):
    """A check or tool execution that should be run"""
    name: str = pd.Field(
        ...,
        description="Name of the check (e.g., 'linting', 'unit_tests')"
    )
    required: bool = pd.Field(
        ...,
        description="Whether this check must pass for the PR to be mergeable"
    )
    commands: List[str] = pd.Field(
        ...,
        description="Shell commands to execute this check"
    )
    why: str = pd.Field(
        ...,
        description="Why this check is needed"
    )
    expected_signal: str = pd.Field(
        ...,
        description="What indicates pass/fail for this check"
    )


class Skip(pd.BaseModel):
    """A check or review area that was intentionally skipped"""
    name: str = pd.Field(
        ...,
        description="Name of the check or review area that was skipped"
    )
    why_safe: str = pd.Field(
        ...,
        description="Why it is safe to skip this check for this PR"
    )
    when_to_run: str = pd.Field(
        ...,
        description="What conditions would make this check necessary to run"
    )


class Finding(pd.BaseModel):
    """A specific issue or observation found during review"""
    id: str = pd.Field(
        ...,
        description="Stable identifier for this finding (e.g., 'SEC-001', 'ARCH-023')"
    )
    title: str = pd.Field(
        ...,
        description="Short, descriptive title of the finding"
    )
    severity: Literal["merge", "warning", "critical", "blocking"] = pd.Field(
        ...,
        description="Severity level of this finding (use 'merge' when no issues found)"
    )
    confidence: Literal["high", "medium", "low"] = pd.Field(
        ...,
        description="Confidence level in the accuracy of this finding"
    )
    owner: Literal["dev", "docs", "devops", "security"] = pd.Field(
        ...,
        description="Who owns fixing this issue"
    )
    estimate: Literal["S", "M", "L"] = pd.Field(
        ...,
        description="Effort estimate to fix: S=small, M=medium, L=large"
    )
    evidence: str = pd.Field(
        ...,
        description="Evidence supporting this finding (code quotes, file references, etc.)"
    )
    risk: str = pd.Field(
        ...,
        description="What can go wrong if this issue is not addressed"
    )
    recommendation: str = pd.Field(
        ...,
        description="What to change to fix this issue"
    )
    suggested_patch: Optional[str] = pd.Field(
        None,
        description="Optional minimal patch instructions or pseudo-diff to fix the issue"
    )


class MergeGate(pd.BaseModel):
    """Merge gate decision for this subagent"""
    decision: Literal["approve", "approve_with_warnings", "needs_changes", "block", "merge_with_warnings"] = pd.Field(
        ...,
        description="Merge gate decision for this subagent"
    )
    must_fix: List[str] = pd.Field(
        default_factory=list,
        description="List of finding IDs that must be fixed before merge"
    )
    should_fix: List[str] = pd.Field(
        default_factory=list,
        description="List of finding IDs that should be fixed soon but don't block merge"
    )
    notes_for_coding_agent: List[str] = pd.Field(
        default_factory=list,
        description="Specific notes for a coding agent to implement fixes"
    )


class ReviewOutput(pd.BaseModel):
    """Top-level output from a review subagent

    All subagents must return JSON matching this schema per PRD section 8.
    """
    agent: str = pd.Field(
        ...,
        description="Name of the subagent (e.g., 'architecture', 'security')"
    )
    summary: str = pd.Field(
        ...,
        description="One-paragraph summary of the review"
    )
    severity: Literal["merge", "warning", "critical", "blocking"] = pd.Field(
        ...,
        description="Overall severity level for this review"
    )
    scope: ReviewScope = pd.Field(
        ...,
        description="Scoping information about which files were reviewed and why"
    )
    checks: List[Check] = pd.Field(
        default_factory=list,
        description="List of checks that were run or should be run"
    )
    skips: List[Skip] = pd.Field(
        default_factory=list,
        description="List of checks that were intentionally skipped"
    )
    findings: List[Finding] = pd.Field(
        default_factory=list,
        description="List of issues or observations found during review"
    )
    merge_gate: MergeGate = pd.Field(
        ...,
        description="Merge gate decision for this subagent"
    )


# Orchestrator-level models (for aggregated results)


class OrchestratorSummary(pd.BaseModel):
    """High-level summary from the PR review orchestrator"""
    change_intent: str = pd.Field(
        ...,
        description="What this PR appears to do"
    )
    risk_level: Literal["low", "medium", "high"] = pd.Field(
        ...,
        description="Overall risk level assessment"
    )
    high_risk_areas: List[str] = pd.Field(
        default_factory=list,
        description="List of areas identified as high risk"
    )
    changed_files_count: int = pd.Field(
        ...,
        description="Number of files changed in this PR"
    )


class OrchestratorToolCheck(pd.BaseModel):
    """A recommended or observed check in the orchestrator's tool plan"""
    name: str = pd.Field(
        ...,
        description="Name of the check"
    )
    required: bool = pd.Field(
        ...,
        description="Whether this check must pass for merge"
    )
    commands: List[str] = pd.Field(
        default_factory=list,
        description="Commands to execute this check"
    )
    scope: List[str] = pd.Field(
        default_factory=list,
        description="Files or directories this check applies to"
    )
    why: str = pd.Field(
        ...,
        description="Why this check is needed"
    )
    expected_signal: str = pd.Field(
        ...,
        description="What indicates pass/fail"
    )


class OrchestratorSkippedCheck(pd.BaseModel):
    """A check that was intentionally skipped"""
    name: str = pd.Field(
        ...,
        description="Name of the check that was skipped"
    )
    why_safe: str = pd.Field(
        ...,
        description="Why it is safe to skip this check"
    )
    when_to_run: str = pd.Field(
        ...,
        description="What would make this check necessary"
    )


class OrchestratorObservedOutput(pd.BaseModel):
    """Actual output from running a check"""
    check: str = pd.Field(
        ...,
        description="Name of the check"
    )
    status: Literal["not_run", "pass", "fail", "unknown"] = pd.Field(
        ...,
        description="Status of the check execution"
    )
    evidence: str = pd.Field(
        ...,
        description="Tool output excerpt or reference"
    )


class OrchestratorToolPlan(pd.BaseModel):
    """Tool execution plan from the orchestrator"""
    recommended_checks: List[OrchestratorToolCheck] = pd.Field(
        default_factory=list,
        description="List of recommended checks to run"
    )
    skipped_checks: List[OrchestratorSkippedCheck] = pd.Field(
        default_factory=list,
        description="List of checks that were intentionally skipped"
    )
    observed_outputs: List[OrchestratorObservedOutput] = pd.Field(
        default_factory=list,
        description="Actual outputs from checks that were executed"
    )


class OrchestratorRollup(pd.BaseModel):
    """Aggregated results and final decision from the orchestrator"""
    final_severity: Literal["merge", "warning", "critical", "blocking"] = pd.Field(
        ...,
        description="Final overall severity level"
    )
    final_decision: Literal["approve", "approve_with_warnings", "needs_changes", "block", "merge_with_warnings"] = pd.Field(
        ...,
        description="Final merge gate decision"
    )
    rationale: str = pd.Field(
        ...,
        description="Tight explanation of the final decision tied to evidence"
    )
    findings: List[OrchestratorFinding] = pd.Field(
        default_factory=list,
        description="Merged findings from all subagents"
    )


class OrchestratorFinding(pd.BaseModel):
    """A finding in the orchestrator's rollup (may merge multiple subagent findings)"""
    id: str = pd.Field(
        ...,
        description="Stable ID (e.g., 'ROLLUP-001' or reuse subagent finding ID)"
    )
    source_agents: List[str] = pd.Field(
        ...,
        description="List of subagents that reported this finding"
    )
    title: str = pd.Field(
        ...,
        description="Short title"
    )
    severity: Literal["merge", "warning", "critical", "blocking"] = pd.Field(
        ...,
        description="Severity level of this finding (use 'merge' for no issues found)"
    )
    confidence: Literal["high", "medium", "low"] = pd.Field(
        ...,
        description="Confidence level"
    )
    evidence: str = pd.Field(
        ...,
        description="What supports this finding"
    )
    recommendation: str = pd.Field(
        ...,
        description="What to do"
    )
    suggested_patch: Optional[str] = pd.Field(
        None,
        description="Optional patch instructions"
    )
    owner: Literal["dev", "docs", "devops", "security"] = pd.Field(
        ...,
        description="Who owns fixing this"
    )
    estimate: Literal["S", "M", "L"] = pd.Field(
        ...,
        description="Effort estimate"
    )


class OrchestratorOutput(pd.BaseModel):
    """Top-level output from a PR review orchestrator

    Per PRD section 12, orchestrator aggregates all subagent results
    and produces a final merge gate decision.
    """
    summary: OrchestratorSummary = pd.Field(
        ...,
        description="High-level summary of PR review"
    )
    tool_plan: OrchestratorToolPlan = pd.Field(
        ...,
        description="Tool execution plan with recommended and skipped checks"
    )
    rollup: OrchestratorRollup = pd.Field(
        ...,
        description="Aggregated results and final merge gate decision"
    )
    findings: List[OrchestratorFinding] = pd.Field(
        default_factory=list,
        description="Deduped and merged findings from all subagents"
    )
    subagent_results: List[Dict[str, Any]] = pd.Field(
        ...,
        description="Raw results from each subagent"
    )
    merge_gate: MergeGate = pd.Field(
        ...,
        description="Merge gate with must_fix, should_fix, and notes for coding agent"
    )


# Export all models

# Export all models
__all__ = [
    # Subagent models
    "ReviewOutput",
    "ReviewScope",
    "Check",
    "Skip",
    "Finding",
    "MergeGate",
    # Orchestrator models
    "OrchestratorSummary",
    "OrchestratorToolCheck",
    "OrchestratorSkippedCheck",
    "OrchestratorObservedOutput",
    "OrchestratorToolPlan",
    "OrchestratorRollup",
    "OrchestratorFinding",
    "OrchestratorOutput",
]
