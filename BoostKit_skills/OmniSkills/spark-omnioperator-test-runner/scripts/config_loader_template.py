"""Configuration loader for JSON-driven test framework."""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigLoader:
    """Singleton class to load and manage configuration from JSON files."""

    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Dict[str, Any]] = None
    _test_cases: Optional[List[Dict[str, Any]]] = None

    def __new__(cls) -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._base_path = Path(__file__).parent.parent

    def load_config(self) -> Dict[str, Any]:
        """Load global configuration from config.json."""
        if self._config is None:
            config_path = self._base_path / 'config.json'
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        return self._config

    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from test_cases.json."""
        if self._test_cases is None:
            test_cases_path = self._base_path / 'test_cases.json'
            if not test_cases_path.exists():
                raise FileNotFoundError(f"Test cases file not found: {test_cases_path}")
            with open(test_cases_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._test_cases = data
                else:
                    self._test_cases = data.get('test_cases', [])
        return self._test_cases

    def get_test_case(self, case_id: str) -> Dict[str, Any]:
        """Get specific test case by 用例_编号."""
        test_cases = self.load_test_cases()
        for case in test_cases:
            if case.get('用例_编号') == case_id:
                return case
        raise ValueError(f"Test case not found: {case_id}")

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return self.get_config().get('server', {})

    def get_spark_commands(self) -> Dict[str, Any]:
        """Get Spark commands configuration."""
        return self.get_config().get('spark_commands', {})

    def get_native_spark_command(self) -> str:
        """Get native Spark SQL command."""
        return self.get_spark_commands().get('原生', '')

    def get_omni_spark_command(self) -> str:
        """Get Omni Spark SQL command."""
        return self.get_spark_commands().get('omni', '')