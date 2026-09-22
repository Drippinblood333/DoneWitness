# DoneWitness

[![CI](https://github.com/Drippinblood333/DoneWitness/actions/workflows/ci.yml/badge.svg)](https://github.com/Drippinblood333/DoneWitness/actions/workflows/ci.yml)

**Check what an AI-built web app actually does.** DoneWitness runs a reviewed
acceptance plan against a local application and writes an evidence-backed
`PASS`, `FAIL`, or `UNKNOWN` receipt. No LLM, account, or hosted service is required.

This branch prepares **v0.2.0**: business-state assertions, offline plan validation,
and lighter CLI startup. The published release remains v0.1.0 until the second
release is explicitly published. [Changes and upgrade guidance](docs/releases/v0.2.0.md).

## Try the second-release candidate

Use Python 3.12–3.14. From this checkout, preferably in a virtual environment:

```console
python -m pip install -e "."
python -m playwright install chromium
donewitness --version
donewitness validate --plan examples/expenses.plan.json
```

For the currently published package, use `python -m pip install donewitness`.
`python -m donewitness` is equivalent to the console command.

Run the expense-entry example:

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/expenses --app-command python examples/expenses_app.py
donewitness inspect --run-dir .donewitness/expenses
```

The plan checks invalid input, the exact total, form clearing, and persistence
after navigating back to the page. Persistence uses browser localStorage;
it does not demonstrate server/database durability.

Run the **same plan** against a deliberately broken save implementation:

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/fake-save --app-command python examples/expenses_app.py --fault fake-save
```

This should return `FAIL` for persistence, even though the page says “Saved”.
`--fault wrong-total` demonstrates an incorrect calculation. These are controlled
examples, not a claim that every real-world defect can be detected.

Choose a new run directory each time. `--app-command` must be the final DoneWitness
option: everything after it belongs to your application command.

## Use it on your application

1. Write or review the acceptance criteria **before** verification.
2. Adapt the [example plan](examples/expenses.plan.json) to your application.
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

- [Plan v3 assertions and compatibility](docs/PLANS.md)
- [Full CLI reference, Docker, revisions, and troubleshooting](docs/CLI_REFERENCE.md)
- [CI and machine-readable output](docs/CI.md)
- [Security and privacy](docs/SECURITY_AND_PRIVACY.md)
- [Second-release acceptance criteria](docs/V0_2_PLAN.md)
- [Product definition](docs/PRODUCT.md) · [Architecture](docs/ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md)

Licensed under [Apache-2.0](LICENSE).
