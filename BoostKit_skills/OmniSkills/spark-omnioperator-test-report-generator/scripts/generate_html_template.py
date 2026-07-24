"""
Custom HTML report generator from JSON results.
Replaces pytest-html with fully controlled HTML generation.

Features:
- Includes ALL test cases from test_cases.json
- Shows status: passed / failed / not_tested
- Works even if pytest crashed (JSON persisted)
- ANSI color support (ERROR displays red)
- No JavaScript regex issues
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re


def generate_html_report(
    test_cases_json: str = "test_cases.json",
    results_json: str = "reports/test_results.json",
    output_html: str = "reports/test_report.html"
):
    """
    Generate HTML report from JSON files.
    
    Args:
        test_cases_json: Path to test_cases.json
        results_json: Path to test_results.json (pytest-json-report output)
        output_html: Path to output HTML file
    """
    # Load test cases configuration
    test_cases_path = Path(test_cases_json)
    if not test_cases_path.exists():
        print(f"[HTML Generator] Error: {test_cases_json} not found")
        return
    
    with open(test_cases_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    # Load pytest results
    results_path = Path(results_json)
    results = {'tests': [], 'summary': {}}
    
    if results_path.exists():
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except Exception as e:
            print(f"[HTML Generator] Warning: Failed to load {results_json}: {e}")
    
    # Build lookup table: lowercase case_id → original case_id
    case_id_lookup = {}
    for case in test_cases:
        original_id = case.get('用例_编号', '')
        if original_id:
            case_id_lookup[original_id.lower()] = original_id

    # Map test results by test ID
    # pytest-json-report uses 'nodeid' format: "tests/test_xxx.py::TestClass::test_method"
    results_map = {}

    for test in results.get('tests', []):
        nodeid = test.get('nodeid', '')
        outcome = test.get('outcome', 'unknown')

        # Calculate total duration from setup + call + teardown phases
        # pytest-json-report stores duration in each phase, not at top level
        setup_duration = test.get('setup', {}).get('duration', 0)
        call_duration = test.get('call', {}).get('duration', 0)
        teardown_duration = test.get('teardown', {}).get('duration', 0)
        duration = setup_duration + call_duration + teardown_duration

        # Extract test case ID from nodeid using lookup table
        # nodeid format: "tests/test_spark_omniruntime_tablewrite_030.py::TestCase26::test_xxx"
        # Extract: "spark_omniruntime_tablewrite_030" → lookup → "Spark_OmniRuntime_Tablewrite_030"
        match = re.search(r'test_(spark_.*?)\.py', nodeid)
        if match:
            lookup_key = match.group(1).lower()
            test_case_id = case_id_lookup.get(lookup_key, nodeid)
        else:
            test_case_id = nodeid

        results_map[test_case_id] = {
            'status': outcome,
            'duration': duration,
            'setup_logs': test.get('setup', {}).get('log', []),
            'call_logs': test.get('call', {}).get('log', []),
            'teardown_logs': test.get('teardown', {}).get('log', []),
            'nodeid': nodeid
        }
    
    # Generate HTML
    html_content = generate_html_template(test_cases, results_map)
    
    # Write HTML file
    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Statistics
    total_cases = len(test_cases)
    tested_cases = len(results_map)
    passed_cases = sum(1 for r in results_map.values() if r['status'] == 'passed')
    failed_cases = sum(1 for r in results_map.values() if r['status'] == 'failed')
    not_tested_cases = total_cases - tested_cases
    
    print(f"\n[HTML Generator] Report generated: {output_html}")
    print(f"  Total cases in config: {total_cases}")
    print(f"  Tested: {tested_cases} (Passed: {passed_cases}, Failed: {failed_cases})")
    print(f"  Not tested: {not_tested_cases}")
    print(f"  Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def get_css_styles():
    """Return CSS styles for HTML report."""
    return """
        /* Expandable Row Styles */
        .hidden { display: none; }
        .collapsible { cursor: pointer; }
        .collapsible:hover { background: #e8e8e8; }
        .collapsible td:first-child::before { content: '▶ '; color: #666; }
        .collapsible.expanded td:first-child::before { content: '▼ '; color: #666; }
        
        .extras-row td { padding: 0; background: #fafafa; border-top: 2px solid #ddd; }
        
        .log-container { padding: 15px; max-height: 400px; overflow-y: auto; }
        .log-section { margin-bottom: 15px; }
        .log-section-title { 
          font-weight: bold; 
          color: #333; 
          padding: 8px 12px; 
          background: #e0e0e0;
          margin-bottom: 8px;
          border-radius: 4px;
        }
        
        .log-entry { 
          font-family: 'Consolas', monospace; 
          font-size: 12px; 
          padding: 4px 8px; 
          white-space: pre-wrap;
          border-bottom: 1px solid #f0f0f0;
        }
        
        .log-info { color: #2e7d32; }
        .log-warning { color: #FF8F00; font-weight: bold; }
        .log-error { color: #D32F2F; font-weight: bold; background: #ffebee; padding: 6px 8px; }
        
        /* Base Styles */
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        
        h1 { 
            color: #333; 
            margin-bottom: 10px;
            font-size: 24px;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }
        
        .summary { 
            background: white; 
            padding: 20px; 
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .stats-grid { 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .stat-box { 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
            font-size: 18px;
        }
        
        .stat-box strong { font-size: 32px; display: block; margin-bottom: 5px; }
        
        .total { background: #e0e0e0; color: #333; }
        .passed { background: #c8e6c9; color: #2e7d32; }
        .failed { background: #ffcdd2; color: #c62828; }
        .skipped { background: #fff9c4; color: #f57f17; }
        .not-tested { background: #e1bee7; color: #6a1b9a; }
        
        .pass-rate {
            text-align: center;
            padding: 10px;
            background: #e3f2fd;
            border-radius: 8px;
            font-size: 16px;
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        thead { background: #424242; color: white; }
        
        th, td { 
            padding: 12px 15px; 
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th { font-weight: 600; }
        
        tbody tr:hover { background: #f5f5f5; }
        
        .status-passed { 
            color: #2e7d32; 
            font-weight: bold;
        }
        .status-failed { 
            color: #c62828; 
            font-weight: bold;
        }
        .status-skipped { 
            color: #f57f17;
        }
        .status-not-tested { 
            color: #6a1b9a;
        }
        
        .log { 
            background: #f8f8f8; 
            padding: 10px; 
            font-family: 'Consolas', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }
        
        /* ANSI Color Support - ERROR displays bright red */
        .ansi31 { color: #FF0000 !important; font-weight: bold !important; }
        .ansi1.ansi31 { color: #FF0000 !important; font-weight: bold !important; }
        .ansi32 { color: #00aa00 !important; }
        .ansi1.ansi32 { color: #00aa00 !important; font-weight: bold !important; }
        .ansi33 { color: #FFAA00 !important; }
        .ansi1.ansi33 { color: #FFAA00 !important; font-weight: bold !important; }
        
        /* Highlight ERROR lines */
        .log .error-line {
            color: #FF0000;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }
        
        /* Filter buttons */
        .filter-container {
            margin: 20px 0;
            padding: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filter-label {
            font-weight: bold;
            color: #333;
            margin-right: 10px;
        }
        .filter-btn {
            padding: 8px 16px;
            margin-right: 8px;
            border: 2px solid #e0e0e0;
            background: white;
            color: #666;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .filter-btn:hover {
            background: #f5f5f5;
        }
        .filter-btn.active {
            border-color: #424242;
            background: #424242;
            color: white;
            font-weight: bold;
        }
    """


def format_log_entry(entry: Dict) -> str:
    """Format single log entry with color coding and timestamp."""
    levelname = entry.get('levelname', 'INFO')
    msg = entry.get('msg', '')
    asctime = entry.get('asctime', '')
    
    # Escape HTML special characters (order matters: & first, then < and >)
    msg = msg.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Map levelname to color class - only ERROR gets red color, others are black (no class)
    color_class = {
        'ERROR': 'log-error'
    }.get(levelname, '')  # Default: empty string (black color)
    
    # Format: timestamp | level | message
    return f'<div class="log-entry {color_class}">{asctime} | {levelname} | {msg}</div>'


def format_logs(logs: List[Dict]) -> str:
    """Format array of log entries."""
    if not logs:
        return '<div class="log-entry log-info">No logs</div>'
    return '\n'.join(format_log_entry(entry) for entry in logs)


def generate_html_template(test_cases: List[Dict], results_map: Dict) -> str:
    """Generate HTML template with all test cases."""
    
    # Statistics
    total = len(test_cases)
    tested = len(results_map)
    passed = sum(1 for r in results_map.values() if r['status'] == 'passed')
    failed = sum(1 for r in results_map.values() if r['status'] == 'failed')
    skipped = sum(1 for r in results_map.values() if r['status'] == 'skipped')
    not_tested = total - tested
    
    pass_rate = (passed / tested * 100) if tested > 0 else 0
    
    # Get CSS styles
    css_styles = get_css_styles()
    
    # HTML template header
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni Spark Test Report - Custom Generated</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="container">
        <h1>Omni Spark Test Report</h1>
        <div class="timestamp">Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <div class="stats-grid">
                <div class="stat-box total">
                    <strong>{total}</strong>
                    Total Cases
                </div>
                <div class="stat-box passed">
                    <strong>{passed}</strong>
                    Passed
                </div>
                <div class="stat-box failed">
                    <strong>{failed}</strong>
                    Failed
                </div>
                <div class="stat-box skipped">
                    <strong>{skipped}</strong>
                    Skipped
                </div>
                <div class="stat-box not-tested">
                    <strong>{not_tested}</strong>
                    Not Tested
                </div>
            </div>
            <div class="pass-rate">
                <strong>Pass Rate: {pass_rate:.1f}%</strong> (based on tested cases)
            </div>
        </div>
        
        <div class="filter-container">
            <span class="filter-label">筛选：</span>
            <button class="filter-btn active" onclick="filterTests('all')">全部</button>
            <button class="filter-btn" onclick="filterTests('passed')">Passed ({passed})</button>
            <button class="filter-btn" onclick="filterTests('failed')">Failed ({failed})</button>
            <button class="filter-btn" onclick="filterTests('not_tested')">Not Tested ({not_tested})</button>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 5%">序号</th>
                    <th style="width: 20%">用例编号</th>
                    <th style="width: 30%">用例名称</th>
                    <th style="width: 10%">用例级别</th>
                    <th style="width: 10%">状态</th>
                    <th style="width: 15%">执行时间</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add test case rows (two-row pattern: collapsible main row + hidden extras row)
    for index, case in enumerate(test_cases, 1):
        case_id = case.get('用例_编号', 'Unknown')
        case_name = case.get('用例_名称', 'Unknown')
        case_level = case.get('用例_级别', 'Unknown')
        
        # Check if tested
        if case_id in results_map:
            result = results_map[case_id]
            status = result['status']
            duration = f"{result['duration']:.2f}s"
            
            # Get logs by phase
            setup_logs = result.get('setup_logs', [])
            call_logs = result.get('call_logs', [])
            teardown_logs = result.get('teardown_logs', [])
            
            status_class = f"status-{status}"
            status_text = status.upper()
        else:
            status = 'not_tested'
            duration = '-'
            setup_logs = []
            call_logs = []
            teardown_logs = []
            status_class = 'status-not-tested'
            status_text = 'NOT TESTED'
        
        # Row 1: Collapsible main row
        html += f"""
                <tr class="collapsible {status_class}" data-id="{case_id}" onclick="toggleRow('{case_id}')">
                    <td>{index}</td>
                    <td>{case_id}</td>
                    <td>{case_name}</td>
                    <td>{case_level}</td>
                    <td><span class="{status_class}">{status_text}</span></td>
                    <td>{duration}</td>
                </tr>
"""
        
        # Row 2: Hidden extras row with detailed logs by phase
        html += f"""
                <tr class="extras-row hidden" id="extras-{case_id}">
                    <td colspan="6">
                        <div class="log-container">
                            <div class="log-section">
                                <div class="log-section-title">Setup Phase</div>
                                {format_logs(setup_logs)}
                            </div>
                            <div class="log-section">
                                <div class="log-section-title">Call Phase</div>
                                {format_logs(call_logs)}
                            </div>
                            <div class="log-section">
                                <div class="log-section-title">Teardown Phase</div>
                                {format_logs(teardown_logs)}
                            </div>
                        </div>
                    </td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="footer">
            Omni Spark Test Framework - Custom HTML Report Generator<br>
            Powered by pytest-json-report + Custom Python Script
        </div>
    </div>
    
    <script>
function toggleRow(testId) {
  const extrasRow = document.getElementById('extras-' + testId);
  const mainRow = document.querySelector('[data-id="' + testId + '"]');
  
  if (extrasRow.classList.contains('hidden')) {
    extrasRow.classList.remove('hidden');
    mainRow.classList.add('expanded');
    localStorage.setItem('expanded-' + testId, 'true');
  } else {
    extrasRow.classList.add('hidden');
    mainRow.classList.remove('expanded');
    localStorage.removeItem('expanded-' + testId);
  }
}

function filterTests(filterType) {
  // Update button active state
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
  
  // Filter rows
  const rows = document.querySelectorAll('.collapsible');
  rows.forEach(row => {
    const statusClass = row.className.split(' ').find(c => c.startsWith('status-'));
    const status = statusClass ? statusClass.replace('status-', '') : '';
    
    if (filterType === 'all') {
      row.style.display = '';
      // Show corresponding extras-row
      const extrasRow = row.nextElementSibling;
      if (extrasRow) extrasRow.style.display = '';
    } else {
      if (status === filterType) {
        row.style.display = '';
        const extrasRow = row.nextElementSibling;
        if (extrasRow) extrasRow.style.display = '';
      } else {
        row.style.display = 'none';
        const extrasRow = row.nextElementSibling;
        if (extrasRow) extrasRow.style.display = 'none';
      }
    }
  });
  
  // Save filter state
  localStorage.setItem('currentFilter', filterType);
}

// Restore expanded state and filter on page load
window.onload = function() {
  // Restore filter
  const savedFilter = localStorage.getItem('currentFilter') || 'all';
  if (savedFilter !== 'all') {
    const filterBtn = document.querySelector('.filter-btn[onclick*="' + savedFilter + '"]');
    if (filterBtn) {
      filterBtn.click();
    }
  }
  
  // Restore expanded rows
  const expandedRows = Object.keys(localStorage).filter(k => k.startsWith('expanded-'));
  expandedRows.forEach(key => {
    const testId = key.replace('expanded-', '');
    const extrasRow = document.getElementById('extras-' + testId);
    const mainRow = document.querySelector('[data-id="' + testId + '"]');
    if (extrasRow && localStorage.getItem(key) === 'true') {
      extrasRow.classList.remove('hidden');
      mainRow.classList.add('expanded');
    }
  });
};
    </script>
</body>
</html>
"""
    
    return html


def process_ansi_colors(log_text: str) -> str:
    """
    Process ANSI color escape sequences in log text.
    Convert to HTML spans for proper color display.
    
    Args:
        log_text: Raw log text with ANSI escape codes
    
    Returns:
        HTML-formatted log text with color spans
    """
    # Simple ANSI color mapping
    # In reality, pytest output has complex ANSI sequences
    # For simplicity, we highlight ERROR lines
    
    lines = log_text.split('\n')
    processed_lines = []
    
    for line in lines:
        # Highlight lines containing ERROR
        if 'ERROR' in line:
            processed_lines.append(f'<span class="ansi31">{line}</span>')
        # Highlight lines containing WARNING
        elif 'WARNING' in line:
            processed_lines.append(f'<span class="ansi33">{line}</span>')
        # Highlight lines containing FAILED
        elif 'FAILED' in line:
            processed_lines.append(f'<span class="ansi31">{line}</span>')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


# Command-line entry point
if __name__ == '__main__':
    import sys
    
    # Parse command-line arguments
    test_cases_json = sys.argv[1] if len(sys.argv) > 1 else "test_cases.json"
    results_json = sys.argv[2] if len(sys.argv) > 2 else "reports/test_results.json"
    output_html = sys.argv[3] if len(sys.argv) > 3 else "reports/test_report.html"
    
    generate_html_report(test_cases_json, results_json, output_html)