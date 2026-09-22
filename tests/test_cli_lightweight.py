"""CLI startup and offline plan checks, independently of browser availability."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("args", [["--help"], ["--version"], ["verify", "--help"]])
def test_help_and_version_do_not_import_execution_dependencies(args: list[str]) -> None:
    script = """
import sys
from donewitness.cli import main
try:
    main(sys.argv[1:])
except SystemExit as error:
    assert error.code == 0
assert 'pydantic' not in sys.modules
assert 'playwright' not in sys.modules
assert 'donewitness.run' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", script, *args], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_validate_reports_format_without_importing_browser(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = """
import sys
from donewitness.cli import main
assert main(sys.argv[1:]) == 0
assert 'playwright' not in sys.modules
assert 'donewitness.run' not in sys.modules
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            "validate",
            "--plan",
            str(root / "examples/expenses.plan.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Plan: v3" in result.stdout
    assert "Criteria: 3" in result.stdout
    assert "Digest: sha256:" in result.stdout
    assert "application behavior has not been verified" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_validate_invalid_plan_is_usage_error(tmp_path: Path) -> None:
    plan = tmp_path / "invalid.json"
    plan.write_text(json.dumps({"schema_version": 3, "task": "Empty", "criteria": []}))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "donewitness",
            "validate",
            "--plan",
            str(plan),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "criteria" in result.stderr
    assert "Traceback" not in result.stderr


def test_inspect_does_not_import_playwright(tmp_path: Path) -> None:
    script = """
import sys
from donewitness.cli import main
assert main(sys.argv[1:]) == 2
assert 'playwright' not in sys.modules
assert 'donewitness.run' not in sys.modules
"""
    result = subprocess.run([
        sys.executable, "-c", script, "inspect", "--run-dir", str(tmp_path / "missing"),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_validate_v1_explains_non_executable_format() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([
        sys.executable, "-m", "donewitness", "validate", "--plan",
        str(root / "examples/password-reset.plan.json"),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "Criteria-only plan; execution requires Plan v2 or v3." in result.stdout


def test_invalid_v3_count_does_not_start_application(tmp_path: Path) -> None:
    from test_browser_plan_v3 import payload

    plan = tmp_path / "invalid.json"
    plan.write_text(json.dumps(payload({
        "type": "assert_count", "selector": "li", "count": True,
    })), encoding="utf-8")
    marker = tmp_path / "started"
    result = subprocess.run([
        sys.executable, "-m", "donewitness", "verify", "--plan", str(plan),
        "--base-url", "http://127.0.0.1:8765", "--run-dir", str(tmp_path / "run"),
        "--app-command", sys.executable, "-c",
        f"from pathlib import Path; Path({str(marker)!r}).touch()",
    ], capture_output=True, text=True)
    assert result.returncode == 2, result.stdout + result.stderr
    assert not marker.exists()
    assert not (tmp_path / "run").exists()
