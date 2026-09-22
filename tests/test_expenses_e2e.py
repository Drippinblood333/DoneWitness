"""One frozen business plan must distinguish working and intentionally broken apps."""

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("fault", "exit_code", "verdicts"),
    [
        ("none", 0, ["PASS", "PASS", "PASS"]),
        ("wrong-total", 1, ["PASS", "FAIL", "PASS"]),
        ("fake-save", 1, ["PASS", "PASS", "FAIL"]),
    ],
)
def test_expense_workflow_detects_business_faults(
    tmp_path: Path,
    fault: str,
    exit_code: int,
    verdicts: list[str],
) -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    run = tmp_path / fault
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "donewitness",
            "verify",
            "--plan",
            str(ROOT / "examples/expenses.plan.json"),
            "--base-url",
            f"http://127.0.0.1:{port}",
            "--run-dir",
            str(run),
            "--output-format",
            "json",
            "--app-command",
            sys.executable,
            str(ROOT / "examples/expenses_app.py"),
            "--port",
            str(port),
            "--fault",
            fault,
        ],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    receipt_path = run / "receipt.json"
    diagnostic = (
        receipt_path.read_text(encoding="utf-8")
        if receipt_path.exists()
        else "No receipt persisted"
    )
    assert result.returncode == exit_code, result.stdout + result.stderr + diagnostic
    summary = json.loads(result.stdout)
    assert summary["exit_code"] == exit_code
    receipt = json.loads(diagnostic)
    assert receipt["schema_version"] == 4
    assert [criterion["verdict"] for criterion in receipt["criteria"]] == verdicts
    inspected = subprocess.run(
        [
            sys.executable,
            "-m",
            "donewitness",
            "inspect",
            "--run-dir",
            str(run),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert inspected.returncode == 0, inspected.stdout + inspected.stderr
    assert "Integrity: OK" in inspected.stdout
