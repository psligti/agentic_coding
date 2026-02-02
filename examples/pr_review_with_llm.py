"""Test PR review with LLM

This example shows how to use the PR review system with actual LLM calls.
"""
import asyncio
import os

from opencode_python.agents.review import PRReviewOrchestrator
from opencode_python.llm.client import LLMClient


async def main():
    """Run PR review with LLM"""

    llm_client = LLMClient(
        provider_id="zai-coding-plan",
        api_key=os.getenv("ZAI_CODING_PLAN_API_KEY") or os.getenv("Z_AI_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        model="glm-4.7",
    )

    orchestrator = PRReviewOrchestrator(llm_client=llm_client)

    changed_files = [
        "src/agent.py",
        "src/agent_runtime.py",
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

    print("Starting PR review with LLM...")
    print(f"Changed files: {len(changed_files)}")
    print()

    result = await orchestrator.review_pr(
        changed_files=changed_files,
        diff=diff,
        repo_root="/path/to/repo",
        base_ref="main",
        head_ref="feature-branch",
    )

    print("\n" + "=" * 60)
    print("PR REVIEW COMPLETE")
    print("=" * 60)
    print(f"\nDecision: {result.rollup.final_decision}")
    print(f"Severity: {result.rollup.final_severity}")
    print(f"Findings: {len(result.findings)}")


if __name__ == "__main__":
    if not os.getenv("Z_AI_API_KEY"):
        print("Error: Z_AI_API_KEY environment variable not set")
        print("Set it with: export Z_AI_API_KEY='your-api-key'")
        exit(1)

    asyncio.run(main())
