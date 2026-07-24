# Custom HTML Report Generation (Replaces pytest-html)

## Why Replace pytest-html?

**Critical Issues with pytest-html:**
1. **Crash vulnerability**: If pytest crashes, no HTML report generated
2. **Incomplete results**: Interrupted pytest → empty "tests: {}" → no report
3. **xdist compatibility**: pytest-html doesn't work well with -n parallelism
4. **JavaScript regex issues**: Complex ANSI color handling fails in browser

**Solution: pytest-json-report + Custom HTML Generator**

## Workflow

1. **pytest-json-report**: Collects results incrementally (supports xdist)
   - Writes JSON in real-time during test execution
   - Each test result saved immediately after completion
   - Supports `-n 8` parallel execution

2. **conftest.py hook**: Auto-generates HTML after pytest finishes
   - `pytest_sessionfinish()` hook runs even if pytest crashed
   - Calls `generate_html_from_json.py` automatically
   - Works for exitstatus != 0 (pytest errors/crashes)

3. **generate_html_from_json.py**: Creates HTML with ALL test cases
   - Merges test_cases.json (47 configs) + test_results.json (pytest output)
   - Shows: passed / failed / not_tested
   - Works even if pytest crashed (JSON persisted)

4. **Crash-proof**: JSON persists even if pytest crashes
   - pytest-json-report saves incrementally, not at end
   - If pytest interrupted at test 35, first 35 results still in JSON
   - HTML generator shows 35 tested + 12 not_tested

## Features

**Expandable/collapsible rows (pytest-html style):**
- Two-row pattern: main row + extras-row (hidden)
- Click row to expand/collapse detailed logs
- JavaScript `toggleRow()` function
- localStorage persistence (expanded state saved)
- Phase-separated logs: Setup / Call / Teardown

**Filter functionality:**
- 4 filter buttons: All / Passed / Failed / Not Tested
- JavaScript `filterTests()` function
- Real-time filtering without page reload
- Counts updated dynamically

**Correct duration display:**
- Duration calculated from setup + call + teardown phases
- pytest-json-report stores duration in each phase, not top level
- Total duration: `setup_duration + call_duration + teardown_duration`
- Example: 0.45s setup + 120.3s call + 0.12s teardown = 120.87s

**ERROR log red coloring:**
- ERROR levelname → `<span class="log-error">` with red background
- INFO/WARNING → default black text (no background color)
- Easy to locate problems in long logs
- Table content has NO background colors (only status column text color)

**Complete test coverage:**
- ALL 47 test cases from test_cases.json shown in HTML
- Tested cases: status = passed/failed (from pytest results)
- Not tested cases: status = not_tested (no pytest result)
- Counts: passed, failed, not_tested, total

## Files

- `conftest.py`: pytest_sessionfinish hook (48 lines)
- `generate_html_from_json.py`: Custom HTML generator (630 lines)
- `reports/test_results.json`: pytest-json-report output
- `reports/test_report.html`: Final HTML report

## HTML Structure

```html
<!-- Main row (visible) -->
<tr class="row-test" onclick="toggleRow('extras-26')">
    <td>26</td>
    <td>Spark_OmniRuntime_Tablewrite_030</td>
    <td class="status-passed">passed</td>
    <td>120.87s</td>
</tr>

<!-- Extras row (hidden, expandable) -->
<tr id="extras-26" class="extras-row" style="display: none;">
    <td colspan="4">
        <div class="log-section">Setup Phase Logs:</div>
        <div class="log-entry log-info">INFO: Initializing...</div>
        <div class="log-entry log-error">ERROR: Connection failed</div>
        <div class="log-section">Call Phase Logs:</div>
        ...
    </td>
</tr>
```

## JavaScript Functions

```javascript
// Toggle row expansion
function toggleRow(rowId) {
    const row = document.getElementById(rowId);
    const isVisible = row.style.display === 'table-row';
    row.style.display = isVisible ? 'none' : 'table-row';
    
    // Save state to localStorage
    localStorage.setItem(rowId, row.style.display);
}

// Filter tests by status
function filterTests(status) {
    const rows = document.querySelectorAll('.row-test');
    const buttons = document.querySelectorAll('.filter-btn');
    
    // Update button active state
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filter rows
    rows.forEach(row => {
        const rowStatus = row.getAttribute('data-status');
        row.style.display = (status === 'all' || rowStatus === status) ? 'table-row' : 'none';
    });
    
    // Save filter to localStorage
    localStorage.setItem('currentFilter', status);
}

// Restore state on page load
window.onload = function() {
    // Restore expanded rows
    document.querySelectorAll('.extras-row').forEach(row => {
        const savedState = localStorage.getItem(row.id);
        if (savedState) row.style.display = savedState;
    });
    
    // Restore filter
    const savedFilter = localStorage.getItem('currentFilter') || 'all';
    filterTests(savedFilter);
};
```

## Log Color Strategy in HTML

**CSS classes:**
```css
.log-error {
    background-color: #ffebee;  /* Light red background */
    color: #c62828;              /* Dark red text */
    padding: 2px 4px;
    border-radius: 2px;
}

.log-info, .log-warning {
    color: #212121;              /* Black text */
    /* No background color */
}
```

**Mapping:**
- `levelname == 'ERROR'` → `<span class="log-error">...</span>`
- `levelname in ['INFO', 'WARNING']` → `<span class="log-info">...</span>` (default black)

**Visual result:**
- ERROR logs stand out with red background
- Normal logs readable with black text
- No distracting colors on INFO/WARNING logs

## Duration Calculation Fix

**Problem: pytest-json-report stores duration in phases, not top level**

JSON structure:
```json
{
  "tests": [
    {
      "nodeid": "tests/test_xxx.py::TestCase26::test_xxx",
      "outcome": "passed",
      "setup": { "duration": 0.45 },
      "call": { "duration": 120.3 },
      "teardown": { "duration": 0.12 }
    }
  ]
}
```

**Solution: Sum all phases**
```python
setup_duration = test.get('setup', {}).get('duration', 0)
call_duration = test.get('call', {}).get('duration', 0)
teardown_duration = test.get('teardown', {}).get('duration', 0)
duration = setup_duration + call_duration + teardown_duration
```

**Result: Correct duration displayed in HTML (e.g., 120.87s)**

## Comparison: pytest-html vs Custom HTML

| Feature | pytest-html | Custom HTML Generator |
|---------|-------------|----------------------|
| **Crash handling** | No report if pytest crashes | JSON persists → HTML generated |
| **xdist support** | Poor (race conditions) | Excellent (pytest-json-report native) |
| **Test coverage** | Only executed tests | ALL 47 cases (tested + not_tested) |
| **Duration accuracy** | Correct | Correct (sum of phases) |
| **Expandable rows** | Built-in | Implemented (localStorage persistence) |
| **Filter functionality** | None | 4 filters (All/Passed/Failed/Not Tested) |
| **ERROR coloring** | ANSI → HTML (unreliable) | Direct CSS (ERROR = red background) |
| **Log phase separation** | Combined | Setup/Call/Teardown sections |
| **JavaScript regex** | Complex ANSI parsing | Simple log class assignment |

## Implementation

**Step 1: Install pytest-json-report**
```bash
pip install pytest-json-report
```

**Step 2: Update pytest.ini**
```ini
[pytest]
addopts = -v --json-report --json-report-file=reports/test_results.json --json-report-indent=2 -n 8 --dist=loadscope --maxfail=50
```

**Step 3: Copy conftest.py**
```python
# conftest.py - pytest hook for auto HTML generation
def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs after pytest session finishes.
    Automatically generate custom HTML report from pytest-json-report results.
    Works even if pytest crashed (exitstatus != 0).
    """
    import subprocess
    print("\n[CustomHTML] Generating HTML report from JSON results...")
    
    result = subprocess.run(
        ['python', 'generate_html_from_json.py'],
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)
```

**Step 4: Copy generate_html_from_json.py**
```bash
cp scripts/generate_html_template.py generate_html_from_json.py
```

**Step 5: Run tests**
```bash
pytest tests/ -v  # pytest.ini handles --json-report automatically
# After pytest finishes, HTML automatically generated at reports/test_report.html
```