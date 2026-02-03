"""Pydantic contracts for review agent output."""
from __future__ import annotations
from typing import List, Literal
import pydantic as pd


class Scope(pd.BaseModel):
    relevant_files: List[str]
    ignored_files: List[str] = pd.Field(default_factory=list)
    reasoning: str

    model_config = pd.ConfigDict(extra="forbid")


class Check(pd.BaseModel):
    name: str
    required: bool
    commands: List[str]
    why: str
    expected_signal: str | None = None

    model_config = pd.ConfigDict(extra="forbid")


class Skip(pd.BaseModel):
    name: str
    why_safe: str
    when_to_run: str

    model_config = pd.ConfigDict(extra="forbid")


class Finding(pd.BaseModel):
    id: str
    title: str
    severity: Literal["warning", "critical", "blocking"]
    confidence: Literal["high", "medium", "low"]
    owner: Literal["dev", "docs", "devops", "security"]
    estimate: Literal["S", "M", "L"]
    evidence: str
    risk: str
    recommendation: str
    suggested_patch: str | None = None

    model_config = pd.ConfigDict(extra="forbid")


class MergeGate(pd.BaseModel):
    decision: Literal["approve", "needs_changes", "block"]
    must_fix: List[str] = pd.Field(default_factory=list)
    should_fix: List[str] = pd.Field(default_factory=list)
    notes_for_coding_agent: List[str] = pd.Field(default_factory=list)

    model_config = pd.ConfigDict(extra="forbid")


class ReviewOutput(pd.BaseModel):
    agent: str
    summary: str
    severity: Literal["merge", "warning", "critical", "blocking"]
    scope: Scope
    checks: List[Check] = pd.Field(default_factory=list)
    skips: List[Skip] = pd.Field(default_factory=list)
    findings: List[Finding] = pd.Field(default_factory=list)
    merge_gate: MergeGate

    model_config = pd.ConfigDict(extra="forbid")


class ReviewInputs(pd.BaseModel):
    repo_root: str
    base_ref: str
    head_ref: str
    pr_title: str = ""
    pr_description: str = ""
    ticket_description: str = ""
    include_optional: bool = False
    timeout_seconds: int = 60

    model_config = pd.ConfigDict(extra="forbid")


class ToolPlan(pd.BaseModel):
    proposed_commands: List[str] = pd.Field(default_factory=list)
    auto_fix_available: bool = False
    execution_summary: str = ""

    model_config = pd.ConfigDict(extra="forbid")


class OrchestratorOutput(pd.BaseModel):
    merge_decision: MergeGate
    findings: List[Finding] = pd.Field(default_factory=list)
    tool_plan: ToolPlan
    subagent_results: List[ReviewOutput] = pd.Field(default_factory=list)
    summary: str = ""
    total_findings: int = 0

    model_config = pd.ConfigDict(extra="forbid")


def get_review_output_schema() -> str:
    """Return the JSON schema for ReviewOutput as a string for inclusion in prompts.

    This schema must match exactly the ReviewOutput Pydantic model above.
    Any changes to the model must be reflected here.

    Returns:
        JSON schema string with explicit type information
    """
    return '''You MUST output valid JSON matching this exact schema:

{
  "agent": "string - your agent name",
  "summary": "string - brief summary of your review",
  "severity": "one of: 'merge', 'warning', 'critical', 'blocking'",
  "scope": {
    "relevant_files": ["array of strings - files you reviewed"],
    "ignored_files": ["array of strings - files you chose to ignore"],
    "reasoning": "string - explain why these files are relevant/ignored"
  },
  "checks": [
    {
      "name": "string - name of check",
      "required": "boolean - is this check mandatory?",
      "commands": ["array of strings - commands to run"],
      "why": "string - why this check is needed",
      "expected_signal": "string or null - what success looks like (optional)"
    }
  ],
  "skips": [
    {
      "name": "string - name of skipped check",
      "why_safe": "string - why it's safe to skip now",
      "when_to_run": "string - when should this check run instead?"
    }
  ],
  "findings": [
    {
      "id": "string - unique identifier (e.g., AGENT-001)",
      "title": "string - short descriptive title",
      "severity": "one of: 'warning', 'critical', 'blocking'",
      "confidence": "one of: 'high', 'medium', 'low'",
      "owner": "one of: 'dev', 'docs', 'devops', 'security'",
      "estimate": "one of: 'S', 'M', 'L' - fix effort estimate",
      "evidence": "string - specific code/reasoning supporting the finding",
      "risk": "string - what could go wrong if not fixed",
      "recommendation": "string - specific action to fix",
      "suggested_patch": "string or null - optional code patch suggestion"
    }
  ],
  "merge_gate": {
    "decision": "one of: 'approve', 'needs_changes', 'block'",
    "must_fix": ["array of strings - blocking issues that must be fixed"],
    "should_fix": ["array of strings - non-blocking improvements"],
    "notes_for_coding_agent": ["array of strings - specific guidance for the coding agent"]
  }
}

CRITICAL RULES:
- Include ALL required fields: agent, summary, severity, scope, merge_gate
- NEVER include extra fields not in this schema (will cause validation errors)
- severity in findings is NOT the same as severity in the root object
- findings severity options: 'warning', 'critical', 'blocking' (NOT 'merge')
- root severity options: 'merge', 'warning', 'critical', 'blocking'
- All fields are MANDATORY unless marked as optional with "optional"
- Empty arrays are allowed: [], null values are allowed only where specified
- Return ONLY the JSON object, no other text or markdown'''
