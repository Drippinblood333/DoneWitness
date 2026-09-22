"""Real browser acceptance for new assertions, retries, and private diagnostics."""

import json
from pathlib import Path

from test_browser import local_app_url  # noqa: F401

from donewitness.browser import BrowserVerifier
from donewitness.browser_plan_v3 import BrowserVerificationPlanV3
from donewitness.domain import Verdict
from donewitness.evidence import EvidenceStore
from donewitness.run import build_browser_verification_results


def test_v3_assertions_retry_classify_and_preserve_private_evidence(
    local_app_url: str,  # noqa: F811
    tmp_path: Path,
) -> None:
    assertions: list[tuple[dict[str, object], Verdict]] = [
        ({"type": "assert_text", "selector": "#message", "text": "Hello, Ada!"}, Verdict.PASS),
        ({"type": "assert_value", "selector": "#name", "value": "Ada"}, Verdict.PASS),
        ({"type": "assert_count", "selector": "input", "count": 1}, Verdict.PASS),
        ({"type": "assert_count", "selector": ".missing", "count": 0}, Verdict.PASS),
        ({"type": "assert_hidden", "selector": "#never-visible"}, Verdict.PASS),
        ({"type": "assert_hidden", "selector": ".absent"}, Verdict.PASS),
        ({"type": "assert_text", "selector": "#message", "text": "private-expected"}, Verdict.FAIL),
        ({"type": "assert_value", "selector": "#name", "value": "private-value"}, Verdict.FAIL),
        ({"type": "assert_count", "selector": "input", "count": 2}, Verdict.FAIL),
        ({"type": "assert_hidden", "selector": "#name"}, Verdict.FAIL),
        ({"type": "assert_text", "selector": "[", "text": "anything"}, Verdict.UNKNOWN),
        ({"type": "assert_count", "selector": "[", "count": 1}, Verdict.UNKNOWN),
        ({"type": "assert_hidden", "selector": "["}, Verdict.UNKNOWN),
        ({"type": "assert_visible", "selector": "["}, Verdict.UNKNOWN),
        ({"type": "assert_value", "selector": "#message", "value": "x"}, Verdict.UNKNOWN),
        ({"type": "assert_text", "selector": "p", "text": "x"}, Verdict.UNKNOWN),
    ]
    criteria = []
    for index, (assertion, _) in enumerate(assertions):
        criteria.append(
            {
                "id": f"AC-{index}",
                "description": "Check an explicit state",
                "procedure": {
                    "type": "browser",
                    "timeout_ms": 1000,
                    "steps": [
                        {"type": "navigate", "path": "/"},
                        {"type": "fill", "selector": "#name", "value": "Ada"},
                        {"type": "click", "selector": "#greet"},
                        assertion,
                    ],
                },
            }
        )
    plan = BrowserVerificationPlanV3.model_validate_json(
        json.dumps(
            {
                "schema_version": 3,
                "task": "Assertions",
                "criteria": criteria,
            }
        )
    )
    store = EvidenceStore(tmp_path)
    executions = BrowserVerifier(local_app_url).verify_with_evidence(plan, evidence_store=store)
    assert [result.verdict for result in executions] == [expected for _, expected in assertions]
    assert all(result.failed_step_index == 3 for result in executions[6:])
    assert executions[6].reason == "assert_text failed at step 4 for selector '#message'"
    manifest = store.build_manifest()
    results = build_browser_verification_results(
        plan=plan,
        executions=executions,
        manifest=manifest,
        evidence_root=tmp_path,
    )
    assert [result.verdict for result in results] == [expected for _, expected in assertions]
    for artifact in manifest.artifacts:
        content = (tmp_path / artifact.relative_path).read_text(encoding="utf-8")
        assert "private-expected" not in content
        assert "private-value" not in content
        assert "Hello, Ada!" not in content
        assert "hunter2" not in content
    # New assertion results still depend on intact evidence; optimization cannot bypass it.
    artifact = manifest.artifacts[0]
    (tmp_path / artifact.relative_path).write_text("tampered", encoding="utf-8")
    results = build_browser_verification_results(
        plan=plan,
        executions=executions,
        manifest=manifest,
        evidence_root=tmp_path,
    )
    assert results[0].verdict is Verdict.UNKNOWN
