# Release runbook

Current public release: **v0.2.0**, published to GitHub and PyPI on 2026-09-23
(Asia/Shanghai). See the [publication record](releases/v0.2.0-publication.md)
for exact commit, workflow results, public artifact hashes, and provisioning limits.
The maintainer explicitly authorized publishing this
version and improving its GitHub presentation on 2026-09-23 (Asia/Shanghai).
Public v0.1.0 was observed on GitHub on 2026-09-22.
Repository configuration is not proof of current hosted permissions or publisher state.

## Candidate gates

1. Review the implementation against [V0_2_PLAN.md](V0_2_PLAN.md), including the
   separately documented test/version expectation changes.
2. Run `pytest`, `ruff check .`, and `mypy src tests`. Install managed Chromium first.
3. Build into a new directory, then check and smoke both artifacts:

   ```console
   python -m build --outdir dist/v0.2.0
   python scripts/check_distribution.py dist/v0.2.0
   python scripts/smoke_distribution.py dist/v0.2.0/donewitness-0.2.0-py3-none-any.whl
   python scripts/smoke_distribution.py dist/v0.2.0/donewitness-0.2.0.tar.gz
   ```

4. Review measured startup results and the working/wrong-total/fake-save verdicts.
5. Record exact commit, checks, artifacts, and unverified platform limits in
   [release evidence](releases/v0.2.0-evidence.md). A local Windows pass does not
   qualify Linux, Docker, or other Python versions.

## Public release ceremony

1. Independently review the concrete candidate, merge its PR, and require all CI jobs
   to pass on the exact new main commit. CI covers Python 3.12–3.14 on Linux/Windows,
   required Linux Docker, and clean distributions.
2. Reconfirm the private security reporting channel and authenticated PyPI publisher:
   project `donewitness`, owner `Drippinblood333`, repository `DoneWitness`, workflow
   `release.yml`, environment `pypi`. Verify that version 0.2.0 is not already used.
   Inspect current environment protections; do not infer them from old release notes.
3. Make the explicit publication decision after the candidate and evidence are reviewed.
4. Create annotated tag `v0.2.0` at that exact commit and push only that tag.
5. Dispatch `.github/workflows/release.yml` with input `v0.2.0` at the reviewed commit.
   The workflow checks the exact tag/version, builds once, tests the same artifacts,
   and publishes only after its gates pass. Release actions retain immutable SHA pins.
6. Verify public wheel/sdist bytes, ordinary SHA-256 checksums, PyPI, and GitHub Release.
7. In a fresh environment, install the public package and repeat the sample flow:

   ```console
   python -m pip install donewitness==0.2.0
   python -m playwright install chromium
   donewitness --version
   ```

8. Finalize release date, announcement wording, and evidence using observed results.
   Do not change the already-published artifact bytes.

## Failure and rollback

Build/verification failure publishes nothing. PyPI failure prevents the GitHub
release. If PyPI succeeds but GitHub fails, report a partial release and retry only
GitHub publication with the same verified bytes. Never rebuild or overwrite the
immutable PyPI version. Incorrect published artifacts require a corrective version.

Run manifests and release checksums are integrity indicators, not cryptographic
attestation. The publishing workflow retains `attestations: false`.
