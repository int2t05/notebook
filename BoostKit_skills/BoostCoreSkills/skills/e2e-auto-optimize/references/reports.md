# Report reference

Each iteration writes raw test-result reports and summary reports.

## File names

For iteration `N` and software `<software>`:

- `<software>-iterN-base-test-result.md`
- `<software>-iterN-opt-test-result.md`
- `<software>-iterN-base-summary-result.md`
- `<software>-iterN-opt-summary-result.md`

## Raw test-result report

Include:

- Software name and iteration.
- Variant: baseline or optimized.
- Ref or commit.
- Command.
- Exit code.
- Parsed metric if available.
- Raw stdout/stderr.

## Summary report

Include:

- Baseline metric.
- Optimized metric.
- Improvement percent.
- Threshold percent.
- Accepted/rejected decision.
- Reason.
- Next direction.
- Optimization overview for the optimized summary only. Do not include this field in the baseline summary.

The summary should be short enough to scan, but complete enough that another engineer can reproduce the result.
