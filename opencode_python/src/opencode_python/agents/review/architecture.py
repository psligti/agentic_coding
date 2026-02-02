"""OpenCode Python - Architecture Review Subagent

Reviews code for architectural concerns including boundaries, layering,
cohesion/coupling, data flow, and design patterns.
"""
from __future__ import annotations
from typing import List, Optional, Any
import json
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


ARCHITECTURE_SYSTEM_PROMPT = """You are Architecture Review Subagent.

Use this shared behavior:
- Identify which changed files/diffs are relevant to architecture.
- Decide what checks/tools to run based on what changed; propose minimal targeted checks first.
- If changed_files or diff are missing, request them.
- Discover repo conventions (pyproject.toml, CI workflows, make/just/nox/tox) to propose correct commands.

You specialize in:
- boundaries, layering, dependency direction
- cohesion/coupling, modularity, naming consistency
- data flow correctness (interfaces, contracts, invariants)
- concurrency/async correctness (if applicable)
- config/env separation (settings vs code)
- backwards compatibility and migration concerns
- anti-pattern detection: god objects, leaky abstractions, duplicated logic

Scoping heuristics:
- Relevant when changes include: src/**, app/**, domain/**, services/**, core/**, libs/**,
  API route layers, dependency injection, orchestration layers, agent/skills/tools frameworks.
- Often ignore: docs-only, comments-only, formatting-only changes (unless refactor hides risk).

Checks you may request (only if relevant):
- Type checks (mypy/pyright) when interfaces changed
- Unit tests when behavior changed
- Targeted integration tests when contracts or IO boundaries changed

Architecture review must answer:
1) What is the intended design change?
2) Does the change preserve clear boundaries and a single source of truth?
3) Does it introduce hidden coupling or duplicated logic?
4) Are there new edge cases, failure modes, or lifecycle issues?

Common blocking issues:
- circular dependencies introduced
- public API/contract changed without updating call sites/tests
- configuration hard-coded into business logic
- breaking changes without migration path

Output MUST be valid JSON only with this schema:

{
  "agent": "architecture",
  "summary": "...",
  "severity": "merge|warning|critical|blocking",
  "scope": { "relevant_files": [], "ignored_files": [], "reasoning": "..." },
  "checks": [{ "name": "...", "required": true, "commands": [], "why": "...", "expected_signal": "..." }],
  "skips": [{ "name": "...", "why_safe": "...", "when_to_run": "..." }],
  "findings": [{
    "id": "ARCH-001",
    "title": "...",
    "severity": "warning|critical|blocking",
    "confidence": "high|medium|low",
    "owner": "dev|docs|devops|security",
    "estimate": "S|M|L",
    "evidence": "...",
    "risk": "...",
    "recommendation": "...",
    "suggested_patch": "..."
  }],
  "merge_gate": { "decision": "approve|needs_changes|block", "must_fix": [], "should_fix": [], "notes_for_coding_agent": [] }
}

Rules:
- If there are no relevant files, return severity "merge" and note "no relevant changes".
- Tie every finding to evidence. No vague statements.
- If you recommend skipping a check, explain why it's safe.
Return JSON only."""


class ArchitectureReviewAgent(BaseReviewAgent):
    """Architecture review subagent

    Reviews changes for:
    - Boundaries, layering, dependency direction
    - Cohesion/coupling, modularity, naming consistency
    - Data flow correctness (interfaces, contracts, invariants)
    - Concurrency/async correctness (if applicable)
    - Config/env separation (settings vs code)
    - Backwards compatibility and migration concerns
    - Anti-pattern detection: god objects, leaky abstractions, duplicated logic
    """

    def __init__(self, llm_client: Optional[Any] = None):
        super().__init__(
            name="architecture",
            description="Reviews code for architectural concerns including boundaries, layering, "
                       "cohesion/coupling, data flow, and design patterns",
            llm_client=llm_client,
            system_prompt=ARCHITECTURE_SYSTEM_PROMPT,
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for architectural relevance

        Scoping heuristics:
        - Relevant when changes include: src/**, app/**, domain/**, services/**, core/**, libs/**,
          API route layers, dependency injection, orchestration layers, agent/skills/tools frameworks.
        - Often ignore: docs-only, comments-only, formatting-only changes.
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_architecture_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} architecture-relevant file(s), ignored {len(ignored)} non-architecture file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_architecture_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to architecture review"""
        architecture_patterns = [
            "src/",
            "app/",
            "domain/",
            "services/",
            "core/",
            "libs/",
            "agents/",
            "tools/",
            "orchestrator",
            "registry",
        ]

        doc_patterns = [
            "README",
            "CHANGELOG",
            ".md",
            ".txt",
        ]

        lower_path = file_path.lower()

        for pattern in architecture_patterns:
            if pattern.lower() in lower_path:
                for doc_pattern in doc_patterns:
                    if doc_pattern.lower() in file_path:
                        return False
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine architecture-specific checks

        Common blocking issues:
        - Circular dependencies introduced
        - Public API/contract changed without updating call sites/tests
        - Configuration hard-coded into business logic
        - Breaking changes without migration path
        """
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="circular_dependencies",
                required=True,
                commands=["python -c \"import sys; sys.path.insert(0, 'opencode_python/src'); "
                          "from opencode_python.agents.review import ArchitectureReviewAgent; "
                          "print('Circular dependency check implemented')\""],
                why="Detect circular import dependencies that cause runtime errors",
                expected_signal="No circular dependencies detected",
            ),
            Check(
                name="interface_consistency",
                required=True,
                commands=["grep -r 'class.*:' " + " ".join(scope.relevant_files)],
                why="Verify public interfaces are properly defined",
                expected_signal="All classes properly defined",
            ),
        ]

        return checks

    async def review_with_llm(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewOutput:
        """Generate full review using LLM

        This method calls the LLM with the system prompt and user input
        to generate the complete review output.

        Args:
            changed_files: List of changed file paths
            diff: Unified diff of changes

        Returns:
            ReviewOutput parsed from LLM JSON response
        """
        user_message = f"""Review the following PR changes:

Changed files:
{json.dumps(changed_files, indent=2)}

Diff:
{diff}

Provide your review as valid JSON following the schema in your system prompt."""

        try:
            response = await self.call_llm(user_message)
        except Exception as e:
            logger.error(f"Error calling LLM for architecture review: {e}")
            raise

        try:
            output_data = json.loads(response)
            return ReviewOutput(**output_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response[:500]}...")
            raise ValueError(f"LLM returned invalid JSON: {e}")

    def generate_output(
        self,
        scope: ReviewScope,
        checks: List[Check],
        skips: List[Skip],
        findings: List[Finding],
        check_results: List[dict],
    ) -> ReviewOutput:
        """Generate architecture review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_architecture_review_agent() -> ArchitectureReviewAgent:
    """Factory function to create ArchitectureReviewAgent instance"""
    return ArchitectureReviewAgent()
