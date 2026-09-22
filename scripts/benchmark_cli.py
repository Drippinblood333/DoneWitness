"""Compare fresh-process CLI startup with a local Git revision, without network access.

Alternates baseline/current measurements after two warmups. Includes interpreter
startup and import costs, excludes browser/application execution. No CI threshold.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from importlib.metadata import version
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="v0.1.0")
    parser.add_argument("--samples", type=int, default=15)
    args = parser.parse_args()
    if not 3 <= args.samples <= 100:
        parser.error("samples must be from 3 to 100")
    root = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{args.baseline}^{{commit}}"],
        cwd=root, text=True,
    ).strip()
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit, "--", "src/donewitness"],
        cwd=root, text=True,
    ).splitlines()
    measurements: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="donewitness-benchmark-") as temporary:
        baseline = Path(temporary)
        for name in paths:
            if not name.endswith(".py"):
                continue
            destination = (baseline / name).resolve()
            if not destination.is_relative_to(baseline.resolve()):
                raise ValueError("unsafe source path in baseline")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(subprocess.check_output(
                ["git", "show", f"{commit}:{name}"], cwd=root,
            ))
        for command in ("--version", "--help"):
            samples: dict[str, list[float]] = {"baseline": [], "current": []}
            for index in range(args.samples + 2):
                sources = [("baseline", baseline / "src"), ("current", root / "src")]
                if index % 2:
                    sources.reverse()
                for label, source in sources:
                    environment = os.environ.copy()
                    environment["PYTHONPATH"] = str(source)
                    start = time.perf_counter()
                    subprocess.run(
                        [sys.executable, "-m", "donewitness", command], env=environment,
                        cwd=temporary, capture_output=True, check=True, timeout=30,
                    )
                    elapsed = (time.perf_counter() - start) * 1000
                    if index >= 2:
                        samples[label].append(round(elapsed, 3))
            medians = {label: statistics.median(values) for label, values in samples.items()}
            measurements[command] = {
                "samples_ms": samples, "median_ms": medians,
                "median_reduction_percent": round(
                    (1 - medians["current"] / medians["baseline"]) * 100, 2,
                ),
            }
    print(json.dumps({
        "baseline_commit": commit, "python": platform.python_version(),
        "platform": platform.platform(), "playwright": version("playwright"),
        "pydantic": version("pydantic"), "warmups": 2, "measurements": measurements,
    }, indent=2))


if __name__ == "__main__":
    main()
