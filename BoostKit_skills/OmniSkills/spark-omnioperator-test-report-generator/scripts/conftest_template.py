"""
pytest configuration file for Omni Spark test framework.

Custom HTML report generation (replaces pytest-html):
- pytest-json-report plugin collects results (supports xdist)
- generate_html_from_json.py creates HTML with ALL test cases (47 from test_cases.json)
- Works even if pytest crashes (JSON persisted)
- ERROR logs display bright red (ANSI color support in HTML)
"""

import pytest
import subprocess
import sys
from pathlib import Path


# ============================================
# Custom HTML Report Generation
# ============================================

def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs after pytest session finishes.
    Automatically generate custom HTML report from pytest-json-report results.
    
    Works even if pytest crashed (exitstatus != 0) - pytest-json-report saves JSON incrementally.
    """
    print("\n[CustomHTML] Generating HTML report from JSON results...")
    
    # Generate custom HTML report using generate_html_from_json.py
    try:
        result = subprocess.run(
            [sys.executable, 'generate_html_from_json.py'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        if exitstatus != 0:
            print(f"[CustomHTML] pytest exited with status {exitstatus}, but HTML report generated!")
    except subprocess.CalledProcessError as e:
        print(f"[CustomHTML] Failed to generate HTML report:")
        print(f"  Error: {e.stderr}")
    except Exception as e:
        print(f"[CustomHTML] Unexpected error: {e}")