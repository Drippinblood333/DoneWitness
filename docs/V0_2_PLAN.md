# v0.2.0: useful checks, small CLI, measured startup

## Product decision and frozen acceptance criteria

The second release keeps the local CLI, deterministic verdicts, independent acceptance
review, and current dependencies. It adds business-state assertions rather than a hosted
platform or autonomous judge. This document is recorded before implementation.

1. Preserve Plan v1/v2 loading, canonical digests, existing step semantics, receipt
   v1-v4 inspection, evidence integrity, exit codes, and machine output schema 1.
2. Introduce explicitly versioned Plan v3 with `assert_text`, `assert_value`,
   `assert_count`, and `assert_hidden`, alongside the four existing actions/assertions.
   Require initial navigation and at least one assertion. Strictly reject unknown
   fields, invalid types/counts, and unsupported steps before application startup.
   Assertions retry within the existing timeout; contradictions are FAIL, execution
   errors are UNKNOWN. Never copy actual page content or expected values into default
   diagnostic output. Keep fresh contexts and all existing integrity checks.
3. Demonstrate a small local expense-entry workflow: required-input rejection,
   correct total, and persistence after navigation. One reviewed plan must pass the
   correct fixture and fail both a wrong-total and a fake-save fixture. These are
   deterministic fault-injection examples, not evidence of external user adoption.
4. Add `donewitness validate --plan PATH` so authors can check format, criteria count,
   and frozen digest without starting the application or browser. Make the new plan
   example and a concise second-release quickstart usable from a clean checkout.
5. Reduce CLI help/version startup overhead by deferring execution-only imports.
   Measure identical fresh-process commands before/after on the same interpreter;
   report raw samples and medians, not an unmeasured full-verification speed claim.
   Help/version must not import Pydantic or Playwright; validate/inspect must not
   import Playwright. No timing threshold in CI.
6. Run pytest, Ruff, mypy, real Chromium fault-injection verification, distribution
   checks, and clean artifact installation. Preserve explicit platform/Docker
   limitations. Prepare v0.2.0 changelog, upgrade guidance, and release evidence.

## Verification asset changes

Add separate v3, CLI startup/validation, and fault-injection tests. Existing v2
tests and golden files remain authoritative. The unsupported-version test moves
its future version from 3 to 4 because version 3 becomes supported; release-version
expectations move from 0.1.0 to 0.2.0 to test the new release. These product-driven
test edits must be reviewed separately from implementation changes. No weakened
assertions, skipped new tests, or relaxed runtime failures are acceptable.

## Release boundary

Public v0.1.0 and main commit 7107aa049f5ffbefaa9e1fcdf1552f974c967185 were
confirmed on 2026-09-22. Work starts from that commit on
`codex/v0.2.0-small-and-useful`. Public publication is a separate final action after
the concrete candidate and release gates are reviewable; development does not imply
that a tag or package has been published.
