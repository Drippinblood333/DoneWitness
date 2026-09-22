# DoneWitness

[![CI](https://github.com/Drippinblood333/DoneWitness/actions/workflows/ci.yml/badge.svg)](https://github.com/Drippinblood333/DoneWitness/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/donewitness?color=2563eb)](https://pypi.org/project/donewitness/)
[![Python](https://img.shields.io/badge/python-3.12%E2%80%933.14-64748b)](https://github.com/Drippinblood333/DoneWitness/blob/main/pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-64748b)](https://github.com/Drippinblood333/DoneWitness/blob/main/LICENSE)

[Quickstart](#try-it) · [Release notes](https://github.com/Drippinblood333/DoneWitness/releases/tag/v0.2.0) · [中文](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/README.zh-CN.md)

**Check what an AI-built web app actually does.** DoneWitness runs a reviewed
acceptance plan against a local application and writes an evidence-backed
`PASS`, `FAIL`, or `UNKNOWN` receipt. No LLM, account, or hosted service is required.

### The page says “Saved”. Did it save?

The included expense demo runs **one acceptance plan against three implementations**:

| Implementation | Input validation | Total & form state | Saved after navigation |
| --- | --- | --- | --- |
| Working app | PASS | PASS | PASS |
| Wrong total | PASS | **FAIL** | PASS |
| Fake save | PASS | PASS | **FAIL** |

These are real Chromium runs against controlled faults. The example uses localStorage;
it demonstrates these covered defects, not backend durability or universal bug detection.

**v0.2.0** adds text, value, count, and hidden-state assertions; offline plan validation;
and lighter CLI startup. Measured help/version startup dropped **69–72%** on one Windows
machine. No new runtime dependencies. [Measurements and limits](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/releases/v0.2.0-evidence.md).

## Try it

Use Python 3.12–3.14 in a virtual environment:

```console
python -m pip install donewitness==0.2.0
python -m playwright install chromium
donewitness --version
```

Get the matching examples (the Python package is already installed):

```console
git clone --depth 1 --branch v0.2.0 https://github.com/Drippinblood333/DoneWitness.git
cd DoneWitness
donewitness validate --plan examples/expenses.plan.json
```

Run the working app and inspect its evidence:

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/expenses --app-command python examples/expenses_app.py
donewitness inspect --run-dir .donewitness/expenses
```

Run the **same plan** against a deliberately broken save implementation:

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/fake-save --app-command python examples/expenses_app.py --fault fake-save
```

The persistence criterion returns `FAIL` (exit 1), even though the page says “Saved”.
Use `--fault wrong-total` with another run directory to try the calculation defect.

Choose a new run directory each time. `--app-command` must be the final DoneWitness
option: everything after it belongs to your application command. `python -m donewitness`
is equivalent to the console command. On Linux, Chromium may need system dependencies;
see the [setup guide](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/CLI_REFERENCE.md).

## Use it on your application

1. Write or review the acceptance criteria **before** verification.
2. Adapt the [example plan](https://github.com/Drippinblood333/DoneWitness/blob/main/examples/expenses.plan.json) to your application.
3. Run `validate --plan ...` to catch format errors without launching anything.
4. Run `verify` with your local URL and startup command.
5. Review the receipt and decide whether the covered behavior is acceptable.

| Exit | Meaning |
| --- | --- |
| 0 | PASS: all declared checks passed with evidence |
| 1 | FAIL: an assertion contradicted expected behavior |
| 2 | Invalid input or invocation |
| 3 | UNKNOWN or incomplete: insufficient execution/evidence |

A PASS covers the reviewed checks only. A valid plan does not prove that its
criteria are complete. Missing requirements remain missing when every check passes.

Runs contain `receipt.txt`, `receipt.json`, `evidence-manifest.json`, and bounded
artifacts. `inspect` checks integrity without rerunning the app. Default observations
record outcomes and step locations; new assertion diagnostics do not copy expected
values or page contents. Screenshots/traces remain opt-in library captures. Hashes
detect inconsistent changes, not forgery by someone who can rewrite the whole bundle.

## Boundaries and details

Direct mode executes the application with your user permissions. Optional Docker
mode reduces exposure but is not a hostile-code security guarantee. This release
stays focused on locally runnable web apps and a CLI.

- [Plan v3 assertions and compatibility](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/PLANS.md)
- [CLI reference, Docker, revisions, and troubleshooting](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/CLI_REFERENCE.md)
- [CI and machine-readable output](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/CI.md)
- [Security and privacy](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/SECURITY_AND_PRIVACY.md)
- [Acceptance criteria](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/V0_2_PLAN.md) · [Architecture](https://github.com/Drippinblood333/DoneWitness/blob/main/docs/ARCHITECTURE.md)
- [Contributing](https://github.com/Drippinblood333/DoneWitness/blob/main/CONTRIBUTING.md) · [Security reporting](https://github.com/Drippinblood333/DoneWitness/blob/main/SECURITY.md)

Trying this on a real app? [Share a small, reproducible issue](https://github.com/Drippinblood333/DoneWitness/issues)
with the expected behavior and a redacted result. Useful failures and unclear UNKNOWNs
are especially welcome. Keep private data and vulnerability details out of public issues.

Licensed under [Apache-2.0](https://github.com/Drippinblood333/DoneWitness/blob/main/LICENSE).
