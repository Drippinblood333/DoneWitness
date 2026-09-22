"""Independent acceptance tests for the new versioned assertion vocabulary."""

import json
from pathlib import Path

import pytest

from donewitness.browser_plan_v3 import BrowserVerificationPlanV3
from donewitness.plan import PlanValidationError, load_plan, plan_digest


def payload(step: dict[str, object], *, version: int = 3) -> dict[str, object]:
    return {
        "schema_version": version,
        "task": "Check business state",
        "criteria": [
            {
                "id": "AC-1",
                "description": "The expected business state is observable",
                "procedure": {
                    "type": "browser",
                    "steps": [
                        {"type": "navigate", "path": "/"},
                        step,
                    ],
                },
            }
        ],
    }


@pytest.mark.parametrize(
    "step",
    [
        {"type": "assert_text", "selector": "#total", "text": "12.50"},
        {"type": "assert_value", "selector": "#name", "value": ""},
        {"type": "assert_count", "selector": ".error", "count": 0},
        {"type": "assert_hidden", "selector": "#error"},
    ],
)
def test_v3_assertions_round_trip_and_v2_rejects_them(
    tmp_path: Path,
    step: dict[str, object],
) -> None:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(payload(step)), encoding="utf-8")
    plan = load_plan(path)
    assert isinstance(plan, BrowserVerificationPlanV3)
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    assert load_plan(path) == plan
    assert plan_digest(load_plan(path)) == plan_digest(plan)
    path.write_text(json.dumps(payload(step, version=2)), encoding="utf-8")
    with pytest.raises(PlanValidationError):
        load_plan(path)


@pytest.mark.parametrize(
    "step",
    [
        {"type": "assert_text", "selector": "#total", "text": 12},
        {"type": "assert_value", "selector": "#name", "value": None},
        {"type": "assert_count", "selector": "li", "count": -1},
        {"type": "assert_count", "selector": "li", "count": True},
        {"type": "assert_count", "selector": "li", "count": "1"},
        {"type": "assert_hidden", "selector": " "},
        {"type": "assert_text", "selector": "#total", "text": "12", "regex": True},
        {"type": "execute_javascript", "source": "true"},
        {"type": "click", "selector": "button"},
    ],
)
def test_v3_rejects_invalid_or_assertion_free_plans(
    tmp_path: Path,
    step: dict[str, object],
) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload(step)), encoding="utf-8")
    with pytest.raises(PlanValidationError):
        load_plan(path)


def test_v3_digest_covers_expected_values(tmp_path: Path) -> None:
    path = tmp_path / "plan.json"
    digests = []
    for text in ("12.50", "13.50"):
        path.write_text(
            json.dumps(
                payload(
                    {
                        "type": "assert_text",
                        "selector": "#total",
                        "text": text,
                    }
                )
            ),
            encoding="utf-8",
        )
        digests.append(plan_digest(load_plan(path)))
    assert digests[0] != digests[1]


def test_v3_requires_initial_navigation_and_unique_ids(tmp_path: Path) -> None:
    from pydantic import ValidationError

    original = BrowserVerificationPlanV3.model_validate_json(
        json.dumps(
            payload(
                {
                    "type": "assert_hidden",
                    "selector": "#error",
                }
            )
        )
    )
    with pytest.raises(ValidationError, match="criterion id must be unique"):
        BrowserVerificationPlanV3(
            schema_version=3,
            task=original.task,
            criteria=original.criteria * 2,
        )
    procedure = original.criteria[0].procedure
    with pytest.raises(ValidationError, match="first browser step must be navigate"):
        type(procedure)(type="browser", steps=procedure.steps[1:])
