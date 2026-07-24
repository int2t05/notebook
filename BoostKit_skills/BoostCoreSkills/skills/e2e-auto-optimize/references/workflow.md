# Optimization workflow

## Phase 1: Guardrails

Validate the config, confirm SSH reachability, collect hardware information, and ensure the remote Git repo is clean.

If any of these checks fail, stop. A performance optimization loop without a stable baseline produces untrustworthy numbers.

## Phase 2: Baseline

Use `software.baseline_ref` for iteration 1. After an accepted iteration, use that accepted commit as the next baseline.

Record:

- Baseline ref and resolved commit.
- Build command.
- Build/test command.
- Perftest command.
- Parsed metric value.
- Raw output path.
- Brief optimization overview for the optimized summary.

## Phase 3: Candidate

Make one focused candidate change. Prefer changes tied directly to:

- User bottleneck analysis.
- perf/topdown evidence.
- Benchmark hot paths.
- Relevant knowledge-base entries.

Avoid broad refactors during a performance iteration. They make benchmark deltas harder to trust.

## Phase 4: Verification

Run the configured build command first for both baseline and optimized versions. Reject immediately if either side fails to compile.

Run UT/functest after a successful build. Reject immediately if functional tests fail.

Then run the same perftest command against the baseline and optimized version. Parse both outputs with the configured metric rule.

Accept only when:

- Build passes.
- UT/functest passes.
- The metric parser succeeds for both baseline and optimized output.
- The improvement is at least `optimization.threshold_percent`.

## Phase 5: Commit or reject

Accepted candidate:

- Commit immediately after the iteration is accepted.
- Use the iteration's `optimization_overview` as the commit message.
- Create one commit per accepted iteration. If two iterations are accepted, the target repo should contain two new commits in order.
- Do not amend, squash, or defer accepted commits until the end of the run.

If `git.username` or `git.email` is configured, use those values for script-managed Git commands as temporary command-scoped config. Do not change the remote user's global Git config.

Rejected candidate:

- Restore the previous accepted commit or configured baseline.
- Preserve reports explaining why the candidate was rejected.
- Continue with a different focused direction if iterations remain.

Never push automatically.
