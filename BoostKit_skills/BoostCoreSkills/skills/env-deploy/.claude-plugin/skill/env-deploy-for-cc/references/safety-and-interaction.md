# Safety And Interaction Rules

Use this reference before any high-risk operation, ambiguity, or unresolved failure.

## Default Safety Policy

Preserve the existing host environment. Prefer version-compatible installation, isolation, wrappers, virtual environments, or independent runtime paths. Do not remove, overwrite, or downgrade system-level components unless the user explicitly confirms the action.

## Must Ask Before Continuing

| Scenario | What To Show | Allowed User Decisions |
|----------|--------------|------------------------|
| Driver or CUDA/cuDNN conflict | Current version, required version, conflict impact, rollback risk | Continue or skip |
| Unit tests fail and cannot be repaired safely | Failing command, likely cause, attempted fix, residual risk | Continue by skipping UT or terminate |
| Project type ambiguity | Candidate project types and markers found | User selects type/component |
| Java Maven and Gradle both present | Markers, wrappers, README evidence | User selects Maven or Gradle |
| Required credentials missing | Dependency source, credential type, safe retry command | User provides credential/config or skips |
| Runtime unavailable and install path is unsafe | Required version, current version, possible installation methods | User installs manually, accepts install, or skips |

## Unit Test Failure Flow

1. Capture the exact failing command and output in `deploy.log`.
2. Classify the likely cause: missing dependency, environment variable, network/private repo, runtime mismatch, or code failure.
3. If the cause is clearly environment-related, apply one narrow fix and rerun the test.
4. If the same failure persists or the cause is code-related, pause and ask the user whether to skip or terminate.
5. Record skipped tests in the final report under "Skipped".

## Dependency And Build Failure Flow

1. Read the error carefully and identify the missing package, tool, header, library, runtime, or repository configuration.
2. Install or configure only the missing piece.
3. Rerun the failed command once.
4. If the problem repeats, use a different diagnostic path instead of repeating the same command blindly.
5. After three unresolved attempts, stop and ask the user for guidance.

## Command Execution Rules

- Print or log commands as they run.
- Use noninteractive flags only when they are safe and predictable.
- Avoid destructive package-manager operations such as autoremove, purge, or forced downgrades.
- Do not store secrets in `deploy.log`, `setup.sh`, or the final report. Redact tokens and passwords.
- Any command added to `setup.sh` must be safe to repeat or guarded by an existence/version check.
