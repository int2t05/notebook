# e2e-auto-optimize scripts

Primary entry point:

```bash
python scripts/e2e_optimize.py --help
```

Useful commands:

```bash
python scripts/e2e_optimize.py validate-config --config ../examples/sonic-cpp.config.json
python scripts/e2e_optimize.py check-environment --config ../examples/sonic-cpp.config.json
python scripts/e2e_optimize.py parse-metric --config ../examples/sonic-cpp.config.json --input benchmark-output.txt
python scripts/e2e_optimize.py render-reports --help
python scripts/e2e_optimize.py run-iteration --help
```

`run-iteration` executes `commands.build`, then `commands.ut`, then `commands.perftest` for both baseline and optimized refs.

Pass `--optimization-overview "<brief summary>"` to include a short description of the candidate change in the optimized summary report. Baseline summaries omit this field.

When an accepted iteration should be committed by the helper, pass `--commit-accepted` together with a non-empty `--optimization-overview`. The helper uses that overview as the commit message and creates a separate commit for that accepted iteration.
