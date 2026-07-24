---
name: spark-omnioperator-test-report-generator
description: "Generate crash-proof HTML test report for Spark OmniOperator testing from pytest-json-report results. Creates expandable/collapsible report with filtering, ERROR red coloring, shows ALL cases (tested + not_tested). Works even if pytest crashed. Trigger when user mentions 'generate report', 'HTML report', 'test report', 'visualization' in the context of Spark OmniOperator. Do NOT trigger for other business scenarios or for script generation/execution."
---

# Omni Spark Test Report Generator

Generate HTML test report for Spark OmniOperator testing from pytest-json-report results.

## Sole Responsibility

**Only generate HTML report.**

- Input: `reports/test_results.json` + `test_cases.json`
- Output: `reports/test_report.html`
- NOT responsible for: script generation, execution, logging

## When to Use

Trigger when user wants to:
- Generate/view HTML report
- Visualize test results
- See passed/failed/not_tested summary

**NOT triggered for:**
- Script generation → use `spark-omnioperator-test-script-generator`
- Test execution → use `spark-omnioperator-test-runner`

## Input Files

Required:
- `reports/test_results.json`: pytest-json-report output
- `test_cases.json`: Test definitions

## Output File

Creates: `reports/test_report.html`

## Features

- **Crash-proof**: Works even if pytest crashed
- **Complete coverage**: Shows ALL cases (tested + not_tested)
- **Expandable rows**: Click for detailed logs
- **Filter buttons**: All / Passed / Failed / Not Tested
- **Correct duration**: Sum of setup + call + teardown
- **ERROR coloring**: Red background
- **localStorage**: Remember state

## Generation

### Auto (via conftest.py)

1. Copy `scripts/conftest_template.py` to project root as `conftest.py`
2. Run pytest — report auto-generated after session ends

### Agent-triggered

When `reports/test_results.json` exists and user asks for a report:

1. Copy `scripts/generate_html_template.py` to project root as `generate_html_from_json.py`
2. Run `python3 generate_html_from_json.py`
3. Output: `reports/test_report.html`

