"""OpenCode Python - Base Review Agent

Simplified base class for PR review subagents that doesn't depend on
complex SDK infrastructure (AgentRuntime, EventBus, etc.).

This provides a minimal framework for subagents to implement their
review logic without requiring full SDK orchestration.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from opencode_python.agents.builtin import Agent as SDKAgent
from opencode_python.models.review import (
    ReviewOutput,
    ReviewScope,
    Check,
    Skip,
    Finding,
    MergeGate,
)

logger = logging.getLogger(__name__)


class BaseReviewAgent:
    """Simplified base class for PR review subagents

    Provides minimal framework for analyzing changes and generating JSON output
    without requiring complex SDK orchestration infrastructure.

    Subagents can:
    1. Extend this class
    2. Optionally provide an LLM client to make actual API calls
    3. Override analyze_changes() to implement their logic
    4. Override determine_checks() to propose their checks
    5. Override generate_output() to create their JSON

    Attributes:
        - name: Subagent name (e.g., 'architecture', 'security')
        - description: Description of review domain
        - llm_client: Optional LLM client for making API calls
        - system_prompt: System prompt to use for LLM calls
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm_client: Optional[Any] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize BaseReviewAgent

        Args:
            name: Subagent name
            description: Description of what this subagent reviews
            llm_client: Optional LLM client for making API calls
            system_prompt: System prompt to use for LLM calls
        """
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.system_prompt = system_prompt or ""

    async def call_llm(self, user_message: str) -> str:
        """Call LLM with system prompt and user message

        Args:
            user_message: User message to send to LLM

        Returns:
            Response text from LLM

        Raises:
            ValueError: If LLM client not configured
        """
        if not self.llm_client:
            raise ValueError(
                f"LLM client not configured for agent '{self.name}'. "
                "Either provide an llm_client or implement custom logic."
            )

        return await self.llm_client.chat_completion(
            system_prompt=self.system_prompt,
            user_message=user_message,
            max_tokens=4096,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

    @classmethod
    def _init_with_llm(cls, agent_class: type, llm_client: Optional[Any] = None, **kwargs):
        """Initialize an agent with LLM client if supported

        Helper method that initializes an agent with llm_client if the agent
        supports it, otherwise falls back to default initialization.

        Args:
            agent_class: Agent class to initialize
            llm_client: Optional LLM client
            **kwargs: Additional kwargs to pass to agent __init__

        Returns:
            Initialized agent instance
        """
        try:
            return agent_class(llm_client=llm_client, **kwargs)
        except TypeError:
            return agent_class(**kwargs)

    async def review_with_llm(self, changed_files: List[str], diff: str) -> ReviewOutput:
        """Generate full review using LLM

        Subclasses can override this method to use LLM for generating
        complete review output. Default implementation raises NotImplementedError.

        Args:
            changed_files: List of changed file paths
            diff: Unified diff of changes

        Returns:
            ReviewOutput from LLM

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement review_with_llm()"
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files and determine scope

        Default implementation filters files and provides basic reasoning.
        Subagents should override this to implement their specific logic.

        Args:
            changed_files: List of all changed file paths
            diff: Unified diff of changes

        Returns:
            ReviewScope with all files as relevant and empty ignored list
        """
        return ReviewScope(
            relevant_files=list(set(changed_files)),  # All files are relevant
            ignored_files=[],
            reasoning=f"Reviewed {len(changed_files)} changed file(s)"
        )

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine what checks to run

        Default implementation returns empty list.
        Subagents should override this to implement their check logic.

        Args:
            scope: ReviewScope from analyze_changes()

        Returns:
            Empty list of checks
        """
        return []

    def execute_checks(
        self,
        checks: List[Check],
        tools: Any,  # Simplified: no ToolRegistry
        ctx: Any,  # Simplified: no ToolContext
    ) -> List[Dict[str, str]]:
        """Execute proposed checks

        Default implementation is no-op.
        Subagents should override this or not use tools.

        Args:
            checks: List of Check objects
            tools: ToolRegistry (ignored in this simplified version)
            ctx: ToolContext (ignored)

        Returns:
            Empty list of results
        """
        # No actual tool execution in simplified version
        logger.warning(f"{self.name}: execute_checks() not implemented (simplified version)")
        return []

    def generate_output(
        self,
        scope: ReviewScope,
        checks: List[Check],
        skips: List[Skip],
        findings: List[Finding],
        check_results: List[Dict[str, str]],
    ) -> ReviewOutput:
        """Generate final ReviewOutput JSON

        Args:
            scope: ReviewScope from analyze_changes()
            checks: List from determine_checks()
            skips: Optional list
            findings: List of Finding objects
            check_results: Optional results from execute_checks()

        Returns:
            ReviewOutput ready for JSON serialization
        """
        # Determine severity based on findings
        if not findings:
            severity = "merge"
        elif any(f.severity == "blocking" for f in findings):
            severity = "blocking"
        elif any(f.severity == "critical" for f in findings):
            severity = "critical"
        else:
            severity = "warning"

        # Determine merge gate decision
        if severity == "blocking":
            decision = "block"
            must_fix = [f.id for f in findings]
            should_fix = []
        elif severity == "critical":
            decision = "needs_changes"
            must_fix = [f.id for f in findings]
            should_fix = []
        elif severity == "warning":
            decision = "approve_with_warnings"
            must_fix = []
            should_fix = [f.id for f in findings]
        else:  # merge
            decision = "approve"
            must_fix = []
            should_fix = []

        # Generate summary
        summary = f"Reviewed {len(scope.relevant_files)} files, found {len(findings)} issues"

        # Notes for coding agent
        notes_for_coding_agent = []
        if findings:
            notes_for_coding_agent.append(
                f"Fix {len(findings)} findings: {', '.join([f.id for f in findings])}"
            )

        return ReviewOutput(
            agent=self.name,
            summary=summary,
            severity=severity,
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            merge_gate=MergeGate(
                decision=decision,
                must_fix=must_fix,
                should_fix=should_fix,
                notes_for_coding_agent=notes_for_coding_agent,
            ),
        )


def create_base_review_agent(
    name: str,
    description: str,
) -> BaseReviewAgent:
    """Factory function to create BaseReviewAgent instance

    Creates a BaseReviewAgent with minimal dependencies.

    Args:
        name: Subagent name (e.g., 'architecture', 'security')
        description: Description of review domain

    Returns:
        BaseReviewAgent instance
    """
    return BaseReviewAgent(name=name, description=description)
