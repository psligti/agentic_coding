"""OpenCode Python - Telemetry & Metrics Review Subagent

Reviews code for observability concerns including logging quality,
tracing spans, metrics, error reporting, and performance signals.
"""
from __future__ import annotations
from typing import List
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


class TelemetryMetricsReviewAgent(BaseReviewAgent):
    """Telemetry & Metrics review subagent

    Reviews changes for:
    - Logging quality (structured logs, levels, correlation IDs)
    - Tracing spans / propagation (if applicable)
    - Metrics: counters/gauges/histograms, cardinality control
    - Error reporting: meaningful errors, no sensitive data
    - Observability coverage of new workflows and failure modes
    - Performance signals: timing, retries, rate limits, backoff

    Blocking:
    - Secrets/PII likely logged
    - Critical path introduced with no error logging/metrics
    - Retry loops without visibility or limits (runaway risk)
    - High-cardinality metric labels introduced
    """

    def __init__(self):
        super().__init__(
            name="telemetry_metrics",
            description="Reviews code for observability concerns including logging quality, "
                       "tracing spans, metrics, error reporting, and performance signals",
        )

    def analyze_changes(
        self,
        changed_files: List[str],
        diff: str,
    ) -> ReviewScope:
        """Analyze changed files for telemetry relevance

        Relevant changes:
        - New workflows, background jobs, pipelines, orchestration
        - Network calls, IO boundaries, retry logic, timeouts
        - Error handling changes, exception mapping
        """
        relevant = []
        ignored = []

        for file_path in changed_files:
            if self._is_telemetry_relevant(file_path):
                relevant.append(file_path)
            else:
                ignored.append(file_path)

        reasoning = f"Reviewed {len(relevant)} telemetry-relevant file(s), ignored {len(ignored)} non-telemetry file(s)"

        return ReviewScope(
            relevant_files=relevant,
            ignored_files=ignored,
            reasoning=reasoning,
        )

    def _is_telemetry_relevant(self, file_path: str) -> bool:
        """Check if file is relevant to telemetry review"""
        telemetry_patterns = [
            "workflow",
            "pipeline",
            "orchestrator",
            "service",
            "client",
            "api",
            "handler",
        ]

        python_patterns = [".py"]

        lower_path = file_path.lower()

        for pattern in telemetry_patterns:
            if pattern in lower_path:
                for py_pattern in python_patterns:
                    if py_pattern in lower_path:
                        return True
                return True

        return False

    def determine_checks(self, scope: ReviewScope) -> List[Check]:
        """Determine telemetry-specific checks"""
        if not scope.relevant_files:
            return []

        checks = [
            Check(
                name="logging_usage",
                required=True,
                commands=["grep -rE 'logger\\.(debug|info|warning|error|critical)' " + " ".join(scope.relevant_files)],
                why="Ensure logging is used for observability",
                expected_signal="Logging appropriately used",
            ),
            Check(
                name="sensitive_data_logging",
                required=True,
                commands=["grep -rE '(password|token|secret|api_key|private_key).*logger' " + " ".join(scope.relevant_files) + " || echo 'No sensitive data logging found'"],
                why="Check for sensitive data being logged",
                expected_signal="No sensitive data logging detected",
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
    ) -> ReviewOutput:
        """Generate telemetry metrics review output"""
        return super().generate_output(
            scope=scope,
            checks=checks,
            skips=skips,
            findings=findings,
            check_results=check_results,
        )


def create_telemetry_metrics_review_agent() -> TelemetryMetricsReviewAgent:
    """Factory function to create TelemetryMetricsReviewAgent instance"""
    return TelemetryMetricsReviewAgent()
