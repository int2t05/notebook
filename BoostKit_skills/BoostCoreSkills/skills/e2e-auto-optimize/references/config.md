# Config reference

Default file name: `e2e-auto-optimize.config.json`.

Use `templates/config.example.json` as the starting point. The helper script applies a few safe defaults, but a real run should keep all paths and commands explicit.

## Top-level fields

```json
{
  "software": {},
  "git": {},
  "environment": {},
  "workspace": {},
  "commands": {},
  "analysis": {},
  "optimization": {},
  "metric": {},
  "notes": ""
}
```

## software

- `name`: Short software name used in report file names.
- `repo_path`: Remote repository path.
- `local_repo_path`: Optional local mirror used for source inspection.
- `baseline_ref`: Optional baseline Git ref. Defaults to `HEAD`.

## git

- `username`: Git `user.name` used by script-managed commits. Defaults to an empty string.
- `email`: Git `user.email` used by script-managed commits. Defaults to an empty string.

Leave both fields empty to use the target repository or remote user's existing Git config. When non-empty, the helper script passes them to Git as temporary `-c user.name=...` and `-c user.email=...` options instead of changing global config.

## environment

- `host`: Remote host or IP.
- `port`: SSH port. Defaults to `22`.
- `user`: SSH user.
- `auth_method`: `private_key` is preferred. `password_file` is allowed only when the local environment has `sshpass`.
- `private_key_path`: Local private key path for `private_key`.
- `password_file_path`: Local file containing the SSH password for `password_file`.
- `connect_timeout_seconds`: Optional SSH connection timeout. Defaults to `10`.

Do not put an inline `password` value in the config. The validator rejects it.

## workspace

All workspace paths are remote paths.

- `work_dir`: Remote working directory. Defaults to `software.repo_path`.
- `test_report_dir`: Directory for raw test-output reports.
- `summary_report_dir`: Directory for summary reports.
- `data_dir`: Directory for temporary worktrees and run data.
- `perf_data_dir`: Directory containing perf/topdown artifacts.

When omitted, report and data directories default outside the target repo under `<parent-of-repo>/e2e-auto-optimize/<software>/`. Keeping run artifacts outside the repo avoids dirtying the worktree.

## commands

- `build`: Bash command for compiling the software.
- `ut`: Bash command for UT/functest.
- `perftest`: Bash command for performance tests.

Commands run from the checked-out worktree root in this order for each baseline and optimized iteration: `build`, `ut`, then `perftest`. Keep commands self-contained and deterministic.

## analysis

- `bottleneck_summary`: User-provided analysis. Empty is allowed, but detailed analysis improves optimization quality.
- `topdown_file`: Optional file name under `workspace.perf_data_dir`.
- `perf_file`: Optional file name under `workspace.perf_data_dir`.

## optimization

- `kb_dir`: Local knowledge-base directory. Defaults to `kb`.
- `kb_menu`: Local knowledge-base menu file. Defaults to `kb/menu.md`.
- `candidate_directions`: Optional list of ideas to try.
- `iterations`: Hard iteration limit. Defaults to `3`.
- `threshold_percent`: Minimum improvement required to accept and commit. Defaults to `5`.

## metric

- `name`: Metric label.
- `direction`: `lower_is_better` or `higher_is_better`.
- `parse_regex`: Regular expression used to extract numeric values from perftest output.
- `value_group`: Regex group name or 1-based group number. Defaults to `1`.
- `occurrence`: Which value to use when the regex matches multiple times: `first`, `last`, `min`, `max`, `mean`, or `median`. Defaults to `last`.
- `repeat`: Optional repeat count for future orchestration. Defaults to `1`.

Improvement is computed as:

- `lower_is_better`: `(base - opt) / abs(base) * 100`
- `higher_is_better`: `(opt - base) / abs(base) * 100`
