"""Test Case: {CASE_ID}
{CASE_NAME}
Generated from test_cases.json - Strict 1:1 mapping
"""
import pytest
from core.test_runner import TestCaseRunner
from config.config_loader import ConfigLoader


@pytest.mark.omni_operator
@pytest.mark.case_id("{CASE_ID}")
class TestCase{N}:
    """{CASE_NAME} - Case ID: {CASE_ID}"""

    CASE_ID = "{CASE_ID}"
    CASE_NAME = "{CASE_NAME}"

    def setup_method(self):
        self.runner = TestCaseRunner(self.CASE_ID)
        self.config = ConfigLoader()

    def test_{method_name}(self):
        """Execute test case from JSON configuration."""
        case_data = self.config.get_test_case(self.CASE_ID)
        assert case_data['用例_编号'] == self.CASE_ID
        result = self.runner.run_case(self.CASE_ID)
        assert result['passed'] is True, f"Test failed: {result['details']}"

    def teardown_method(self):
        pass