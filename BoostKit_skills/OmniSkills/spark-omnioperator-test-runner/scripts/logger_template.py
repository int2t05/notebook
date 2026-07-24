"""Logging utility - complete, clear, no truncation."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class TestLogger:
    """Per-case logger with duplicate prevention."""

    _instances: Dict[str, 'TestLogger'] = {}
    _history: Dict[str, List[Dict[str, Any]]] = {}

    def __new__(cls, case_id: str = 'default') -> 'TestLogger':
        if case_id not in cls._instances:
            cls._instances[case_id] = super().__new__(cls)
        return cls._instances[case_id]

    def __init__(self, case_id: str = 'default'):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._case_id = case_id
        logs_path = Path(__file__).parent.parent / 'logs'
        logs_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._log_file = logs_path / f"{case_id.lower()}_{timestamp}.log"
        
        self.logger = logging.getLogger(f'OmniTest_{case_id}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        file_handler = logging.FileHandler(self._log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
        self.logger.addHandler(file_handler)
        
        self._initialized = True
        self.logger.info("=" * 80)
        self.logger.info(f"Test Case: {case_id}")
        self.logger.info("=" * 80)

    def info(self, case_id: str, message: str):
        self.logger.info(f"[{case_id}] {message}")

    def debug(self, case_id: str, message: str):
        self.logger.debug(f"[{case_id}] {message}")

    def error(self, case_id: str, message: str):
        self.logger.error(f"[{case_id}] ERROR: {message}")

    def warning(self, case_id: str, message: str):
        self.logger.warning(f"[{case_id}] WARNING: {message}")

    def step(self, case_id: str, step_num: int, step_desc: str):
        self.info(case_id, f"Step {step_num}: {step_desc}")

    def result(self, case_id: str, passed: bool, details: str):
        status = "PASSED" if passed else "FAILED"
        self.info(case_id, f"Result: {status} | {details}")

    def sql(self, case_id: str, sql_type: str, sql_content: str):
        self.debug(case_id, f"SQL Type: {sql_type}")
        self.debug(case_id, f"SQL:\n{sql_content}")

    def output(self, case_id: str, output_type: str, content: str):
        self.debug(case_id, f"{output_type}:\n{content}")

    def diff(self, case_id: str, differences: List[str]):
        if differences:
            self.error(case_id, f"Found {len(differences)} differences:")
            for d in differences:
                self.error(case_id, f"  - {d}")
        else:
            self.info(case_id, "No differences found")

    def plan_check(self, case_id: str, expected: str, found: List[str]):
        if expected in found:
            self.info(case_id, f"Plan check PASSED: Found '{expected}'")
        else:
            self.error(case_id, f"Plan check FAILED: '{expected}' NOT found")

    def command(self, case_id: str, command_type: str, command_str: str):
        self.info(case_id, f"Command Type: {command_type}")
        self.info(case_id, f"Command String: {command_str}")

    def execution_result(self, case_id: str, return_code: int, stdout: str = '', stderr: str = '':
        self.info(case_id, f"Return Code: {return_code}")
        if stdout:
            self.debug(case_id, f"STDOUT Preview: {stdout[:500]}")
        if stderr:
            self.warning(case_id, f"STDERR Preview: {stderr[:500]}")