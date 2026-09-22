"""An interrupt before the startup adapter returns must still leave a receipt."""

import socket
import sys
from pathlib import Path
from typing import NoReturn

import pytest

from donewitness.browser_plan import BrowserVerificationPlan
from donewitness.domain import Verdict
from donewitness.inspection import inspect_run_directory
from donewitness.plan import load_plan
from donewitness.run import verify_local_application


def test_interrupt_during_startup_preserves_unknown_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interrupted_start(*args: object, **kwargs: object) -> NoReturn:
        raise KeyboardInterrupt

    monkeypatch.setattr("donewitness.run.ManagedApplication.start", interrupted_start)
    plan_path = Path(__file__).resolve().parents[1] / "examples/greeting.plan.json"
    plan = load_plan(plan_path)
    assert isinstance(plan, BrowserVerificationPlan)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    outcome = verify_local_application(
        plan=plan, base_url=f"http://127.0.0.1:{port}", run_dir=tmp_path / "run",
        app_command=[sys.executable, "unused.py"], invocation_root=tmp_path,
    )
    assert not outcome.receipt.completed
    assert outcome.receipt.overall_verdict is Verdict.UNKNOWN
    assert outcome.receipt.criteria[0].reason == "Verification was interrupted"
    assert "Verification was interrupted during application startup." in outcome.receipt.limitations
    assert inspect_run_directory(outcome.run_root).receipt.overall_verdict is Verdict.UNKNOWN
