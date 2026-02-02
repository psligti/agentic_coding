"""OpenCode Python SDK - PR Review Example

Demonstrates how to use the multi-subagent PR review system.
"""
import asyncio
import os
from typing import List, Optional

from opencode_python.agents.review import PRReviewOrchestrator, create_pr_review_orchestrator
from opencode_python.models.review import OrchestratorOutput
from opencode_python.llm.client import LLMClient


async def main():
    """Main entry point for PR review example"""

    llm_client: Optional[LLMClient] = None

    provider_id = os.getenv("LLM_PROVIDER", "zai-coding-plan")
    api_key = os.getenv(f"{provider_id.upper().replace('-', '_')}_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "glm-4.7")

    if api_key:
        print(f"Configuring LLM client: {provider_id}")
        llm_client = LLMClient(
            provider_id=provider_id,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        orchestrator = PRReviewOrchestrator(llm_client=llm_client)
    else:
        print("No LLM API key found - using mock/static review data")
        print("To enable actual LLM calls, set environment variables:")
        print(f"  export {provider_id.upper().replace('.', '_')}_API_KEY='your-api-key'")
        orchestrator = create_pr_review_orchestrator()

    changed_files = [
        "src/agent.py",
        "src/agent_runtime.py",
        "tests/test_agent.py",
    ]

    diff = """diff --git a/src/agent.py b/src/agent.py
index abc123..def456 100644
--- a/src/agent.py
+++ b/src/agent.py
@@ -10,6 +10,8 @@ class Agent:
     def __init__(self):
         self.name = "test"
+        self.temperature = 0.7
+        self.max_tokens = 4096

     def execute(self, message: str):
         return f"Response: {message}"
"""

    print("Starting PR review...")
    print(f"Changed files: {len(changed_files)}")
    print(f"Diff size: {len(diff)} characters")
    print()

    result: OrchestratorOutput = await orchestrator.review_pr(
        changed_files=changed_files,
        diff=diff,
        repo_root="/path/to/repo",
        base_ref="main",
        head_ref="feature-branch",
    )

    print("=" * 60)
    print("PR REVIEW RESULTS")
    print("=" * 60)
    print()

    print("SUMMARY")
    print("-" * 40)
    print(f"Change Intent: {result.summary.change_intent}")
    print(f"Risk Level: {result.summary.risk_level}")
    print(f"Changed Files: {result.summary.changed_files_count}")
    if result.summary.high_risk_areas:
        print(f"High Risk Areas: {', '.join(result.summary.high_risk_areas)}")
    print()

    print("FINAL DECISION")
    print("-" * 40)
    print(f"Decision: {result.rollup.final_decision}")
    print(f"Severity: {result.rollup.final_severity}")
    print(f"Rationale: {result.rollup.rationale}")
    print()

    if result.merge_gate.must_fix:
        print("MUST FIX (Blocking Issues)")
        print("-" * 40)
        for finding_id in result.merge_gate.must_fix:
            print(f"  - {finding_id}")
        print()

    if result.merge_gate.should_fix:
        print("SHOULD FIX (Warnings)")
        print("-" * 40)
        for finding_id in result.merge_gate.should_fix:
            print(f"  - {finding_id}")
        print()

    print("FINDINGS")
    print("-" * 40)
    for finding in result.findings:
        print(f"[{finding.id}] {finding.title}")
        print(f"  Severity: {finding.severity}")
        print(f"  Confidence: {finding.confidence}")
        print(f"  Owner: {finding.owner}")
        print(f"  Estimate: {finding.estimate}")
        print(f"  Evidence: {finding.evidence[:80]}...")
        print(f"  Risk: {finding.risk}")
        print(f"  Recommendation: {finding.recommendation}")
        if finding.suggested_patch:
            print(f"  Suggested Patch: {finding.suggested_patch[:80]}...")
        print()

    print("TOOL PLAN")
    print("-" * 40)
    print(f"Recommended Checks: {len(result.tool_plan.recommended_checks)}")
    for check in result.tool_plan.recommended_checks:
        print(f"  - {check.name}: {check.why}")
    print()

    print(f"Skipped Checks: {len(result.tool_plan.skipped_checks)}")
    for skip in result.tool_plan.skipped_checks:
        print(f"  - {skip.name}: {skip.why_safe} (when: {skip.when_to_run})")
    print()

    print("SUBAGENT RESULTS")
    print("-" * 40)
    for subagent_result in result.subagent_results:
        agent_name = subagent_result.get("agent", "unknown")
        severity = subagent_result.get("severity", "unknown")
        summary = subagent_result.get("summary", "")
        print(f"{agent_name}: {severity}")
        print(f"  {summary[:100]}...")
    print()

    print("=" * 60)
    print("Review Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
