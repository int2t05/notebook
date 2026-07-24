---
name: e2e-auto-optimize
description: End-to-end autonomous performance optimization for C/C++, system software, and foundational libraries. Use this skill whenever the user wants to optimize a codebase with perf/topdown evidence, remote SSH execution, configured build commands, UT/functest plus perftest comparison, iterative acceptance by an improvement threshold, optimization reports, or local Git commits. This skill should be used for prompts mentioning compilation, build commands, perf, topdown, bottleneck analysis, remote servers, benchmark regressions, perftest, iterative optimization, or automatic performance tuning, even if the user does not explicitly say "skill".
---

# e2e-auto-optimize

Use this skill to run a controlled performance-optimization loop for a software library. The skill is intentionally conservative: it validates the environment first, keeps the user's Git state safe, compares every candidate against a baseline, accepts only changes that compile, pass functional tests, and meet the configured performance threshold, and commits locally without pushing.

## First checks

1. Locate the config file. The default name is `e2e-auto-optimize.config.json`.
2. If the config file is missing, tell the user to create it from `templates/config.example.json` and stop.
3. Run:

```bash
python <skill_dir>/scripts/e2e_optimize.py validate-config --config e2e-auto-optimize.config.json
```

4. If validation reports missing fields, inline passwords, unsupported auth, invalid metric parsing rules, or missing local key/password files, report the exact issues and stop.
5. Run:

```bash
python <skill_dir>/scripts/e2e_optimize.py check-environment --config e2e-auto-optimize.config.json
```

6. If SSH is unreachable, hardware information cannot be collected, the remote repo is missing, or the remote repo is dirty, stop and report the reason. Do not optimize a dirty target repo unless the user explicitly says to allow it.

## Configuration contract

Read `references/config.md` when creating or reviewing a config. The required top-level sections are:

- `software`: software name, remote repo path, optional local repo path, baseline ref.
- `git`: optional Git commit username and email; both default to empty strings.
- `environment`: SSH host, port, user, auth method, private key path or password file path.
- `workspace`: remote working, data, perf/topdown, test report, and summary report directories.
- `commands`: build command, UT/functest command, and perftest command.
- `analysis`: user-provided bottleneck conclusions plus optional perf/topdown file names.
- `optimization`: knowledge base paths, candidate directions, iteration count, threshold percent.
- `metric`: metric name, direction, regex parser, value group, occurrence policy.
- `notes`: compiler, dependency, build, test, optimize and other notes.

Never store or request inline plaintext passwords in the config. A password file may be referenced, but prefer private-key auth.

## Environment workflow

The default target is a remote Linux server. Always confirm the target environment before optimizing:

- SSH reachability.
- `uname`, CPU architecture, CPU model, memory, NUMA information if available.
- Remote Git repo existence and cleanliness.
- Relevant perf/topdown files if the config lists them.

## Knowledge base workflow

Before each optimization attempt:

1. Read the knowledge-base menu from `optimization.kb_menu`, defaulting to `kb/menu.md`.
2. If the menu is empty, record that the run is in autonomous mode and infer candidate changes from the analysis, source code, benchmark profile, and code structure.
3. If the menu lists entries, load only the entries relevant to the current bottleneck, architecture, command, or candidate direction.

The knowledge base starts empty by design. Do not invent missing knowledge-base entries; use the repository and performance data instead.

## Optimization loop

Use `references/workflow.md` for the detailed loop. The short version is:

1. Treat the previous accepted commit as the baseline. For iteration 1, use `software.baseline_ref` or current `HEAD`.
2. Inspect the user analysis, perf/topdown files, benchmark code, and hot code paths.
3. Make one focused candidate change. Keep the blast radius small enough that a failed attempt can be explained clearly.
4. Run the configured build command first for both baseline and optimized versions. If either build fails, reject the candidate.
5. Run UT/functest after a successful build. If it fails, reject the candidate.
6. Run baseline and optimized perftest using the same command, environment, and metric parser.
7. Compute improvement with `scripts/e2e_optimize.py parse-metric` or `run-iteration`.
8. Accept only if build passes, UT/functest passes, and the improvement is at least `optimization.threshold_percent` (default `5`).
9. If accepted, commit immediately as its own local commit. Use the current iteration's `optimization_overview` as the commit message, not a generic template. Each accepted iteration must create a separate commit before the next iteration starts; do not amend, squash, reset back to the original baseline, or wait until the end to commit.

```bash
python <skill_dir>/scripts/e2e_optimize.py run-iteration ... \
  --optimization-overview "Reduce RapidJSON decode allocation overhead" \
  --commit-accepted
```

10. If rejected, return to the previous accepted commit or the baseline commit and continue until `optimization.iterations` is exhausted.

Do not push, create a PR, deploy, or modify production state unless the user explicitly asks after reviewing the local result.

## Reports

Every iteration must produce the four files described in `references/reports.md`:

- `<software>-iterN-base-test-result.md`
- `<software>-iterN-opt-test-result.md`
- `<software>-iterN-base-summary-result.md`
- `<software>-iterN-opt-summary-result.md`

Reports must include:

- Commands run.
- Base and optimized refs/commits.
- Raw test output or a link/path to it.
- Metric values and computed improvement.
- Acceptance or rejection reason.
- Next-iteration direction.
- Brief optimization overview for the optimized summary only; the baseline summary does not need it.

Use:

```bash
python <skill_dir>/scripts/e2e_optimize.py render-reports --help
python <skill_dir>/scripts/e2e_optimize.py run-iteration --help
```

when deterministic report generation or baseline/optimized remote comparison is useful.

## Safety rules

- Do not overwrite unrelated user changes.
- Do not run destructive cleanup outside configured workspace/report directories.
- Do not commit unless the candidate compiles, passes functional tests, and meets the configured threshold.
- Do not use generic accepted-iteration commit messages. The commit message should be the iteration's `optimization_overview`.
- Do not collapse multiple accepted iterations into one commit; commit every accepted iteration separately.
- Do not write Git identity with `git config --global`; use configured `git.username` and `git.email` only as command-scoped Git options.
- Do not push.
- Do not hide failed tests or noisy benchmark output; put it in the report.
- Prefer structured parsing over subjective benchmark interpretation. If the regex cannot parse the metric, stop and fix the config.
