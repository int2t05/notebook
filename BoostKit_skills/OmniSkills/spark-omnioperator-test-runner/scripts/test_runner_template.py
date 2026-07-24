"""Test Runner - S1/E2 execution logic"""
from typing import Dict, Any, Tuple
from config.config_loader import ConfigLoader
from core.ssh_executor import SSHExecutor, ResultComparator, ExecutionPlanChecker
from core.logger import TestCaseLogger


class TestCaseRunner:
    """Runner for executing test cases with S1 and E2 patterns"""
    __test__ = False  # Prevent pytest collection
    
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.config = ConfigLoader()
        self.logger = TestCaseLogger(case_id)
        self.ssh_executor = SSHExecutor(self.config.get_server_config(), self.logger)
        
    def run_case(self, case_id: str) -> Dict[str, Any]:
        """Run complete test case with all steps"""
        case_data = self.config.get_test_case(case_id)
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Starting test case: {case_id}")
        self.logger.info(f"Test case name: {case_data['用例_名称']}")
        self.logger.info(f"Test case level: {case_data['用例_级别']}")
        self.logger.info(f"{'='*80}\n")
        
        # Connect to SSH
        self.ssh_executor.connect()
        
        results = {
            'case_id': case_id,
            'case_name': case_data['用例_名称'],
            'passed': True,
            'details': [],
            'steps': {}
        }
        
        try:
            # Get test steps
            test_steps = case_data['用例_测试步骤']
            
            # Process each step
            for step_key, step_data in test_steps.items():
                step_result = self._execute_step(step_key, step_data)
                results['steps'][step_key] = step_result
                
                if not step_result['passed']:
                    results['passed'] = False
                    results['details'].append(f"Step {step_key} failed: {step_result['message']}")
        
        except Exception as e:
            import traceback
            results['passed'] = False
            error_details = f"{type(e).__name__}: {str(e)}"
            stacktrace = traceback.format_exc()
            results['details'].append(f"Exception: {error_details}")
            results['details'].append(f"Stacktrace: {stacktrace}")
            self.logger.error(f"Exception occurred: {error_details}")
            self.logger.error(f"Stacktrace:\n{stacktrace}")
            
            # Log worker health info
            self.logger.error(f"SSH executor state: connected={self.ssh_executor.client is not None}")
            if self.ssh_executor.ssh_pool:
                pool_stats = self.ssh_executor.ssh_pool.get_stats()
                self.logger.error(f"Pool stats at failure: {pool_stats}")
        
        finally:
            # Disconnect SSH with robust cleanup
            try:
                if self.ssh_executor:
                    self.ssh_executor.disconnect()
                    self.logger.info("SSH connection cleanup successful")
            except Exception as cleanup_error:
                self.logger.warning(f"SSH cleanup error (non-critical): {cleanup_error}")
                # Force cleanup if disconnect failed
                try:
                    if self.ssh_executor.client:
                        self.ssh_executor.client.close()
                        self.logger.info("Force SSH close executed")
                except:
                    pass
        
        # Log final result with pool stats
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Test case final result: {'PASSED' if results['passed'] else 'FAILED'}")
        
        # Log pool statistics if pool was used
        if self.ssh_executor.ssh_pool:
            pool_stats = self.ssh_executor.ssh_pool.get_stats()
            self.logger.info(f"SSH Pool Stats: {pool_stats}")
        
        self.logger.info(f"{'='*80}\n")
        
        return results
    
    def _execute_step(self, step_key: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual test step"""
        description = step_data['description']
        sql_statement = step_data['sql_statement']
        expected_result = step_data['expected_result']
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Executing step: {step_key}")
        self.logger.info(f"Description: {description}")
        self.logger.info(f"Expected result: {expected_result}")
        self.logger.info(f"{'='*80}\n")
        
        step_result = {
            'step_key': step_key,
            'description': description,
            'passed': False,
            'message': ''
        }
        
        # Determine step type: S1 (result comparison) or E2 (execution plan check)
        if self._is_e2_step(description, sql_statement):
            # E2: Execution plan keyword check
            step_result = self._execute_e2_step(step_key, sql_statement, expected_result)
        elif self._is_s1_step(description):
            # S1: Native vs Omni result comparison
            step_result = self._execute_s1_step(step_key, sql_statement, expected_result)
        else:
            # Generic execution
            step_result = self._execute_generic_step(step_key, sql_statement, expected_result)
        
        return step_result
    
    def _is_s1_step(self, description: str) -> bool:
        """Check if step is S1 (Native vs Omni comparison)"""
        return 'S1' in description or '原生和Omni执行' in description or '原生和Omni' in description
    
    def _is_e2_step(self, description: str, sql_statement: str) -> bool:
        """Check if step is E2 (Execution plan check)"""
        return 'S2' in description or 'E2' in description or '执行计划' in description or 'EXPLAIN' in sql_statement.upper()
    
    def _execute_s1_step(self, step_key: str, sql_statement: str, expected_result: str) -> Dict[str, Any]:
        """Execute S1 step: Native vs Omni result comparison"""
        self.logger.info("Executing S1 pattern: Native vs Omni result comparison")
        
        # Get commands
        native_command = self.config.get_native_spark_command()
        omni_command = self.config.get_omni_spark_command()
        timeout = self.config.get_timeout()
        
        # Execute on Native
        self.logger.info("=== Native Spark Execution ===")
        native_rc, native_stdout, native_stderr = self.ssh_executor.execute_native_spark(
            native_command, sql_statement, timeout
        )
        
        if native_rc != 0:
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"Native Spark execution failed with return code {native_rc}",
                'native_stderr': native_stderr
            }
        
        # Execute on Omni
        self.logger.info("=== Omni Spark Execution ===")
        omni_rc, omni_stdout, omni_stderr = self.ssh_executor.execute_omni_spark(
            omni_command, sql_statement, timeout
        )
        
        if omni_rc != 0:
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"Omni Spark execution failed with return code {omni_rc}",
                'omni_stderr': omni_stderr
            }
        
        # Compare results
        self.logger.info("=== Result Comparison ===")
        match, diff_message = ResultComparator.compare_results(native_stdout, omni_stdout)
        
        if not match:
            self.logger.diff(diff_message)
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"Result comparison failed: {diff_message}",
                'native_output': native_stdout,
                'omni_output': omni_stdout
            }
        
        self.logger.info(f"Result comparison successful: {diff_message}")
        return {
            'step_key': step_key,
            'passed': True,
            'message': "Native and Omni results match perfectly"
        }
    
    def _execute_e2_step(self, step_key: str, sql_statement: str, expected_result: str) -> Dict[str, Any]:
        """Execute E2 step: Execution plan keyword check"""
        self.logger.info("Executing E2 pattern: Execution plan keyword check")
        
        # Get Omni command
        omni_command = self.config.get_omni_spark_command()
        
        # Execute EXPLAIN
        explain_rc, explain_stdout, explain_stderr = self.ssh_executor.execute_explain(
            omni_command, sql_statement, timeout=60
        )
        
        if explain_rc != 0:
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"EXPLAIN execution failed with return code {explain_rc}",
                'explain_stderr': explain_stderr
            }
        
        # Extract expected keywords from expected_result
        expected_keywords = self._extract_expected_keywords(expected_result)
        
        # Check keywords
        self.logger.info("=== Execution Plan Keyword Check ===")
        found, found_keywords = ExecutionPlanChecker.check_keywords(explain_stdout, expected_keywords)
        
        self.logger.plan_check(found_keywords, expected_keywords)
        
        if not found:
            # For case 002 (switch false), we expect NO OmniInsertIntoHadoopFsRelationCommand
            if '无OmniInsertIntoHadoopFsRelationCommand' in expected_result:
                # Check that OmniInsertIntoHadoopFsRelationCommand is NOT present
                if 'OmniInsertIntoHadoopFsRelationCommand' in explain_stdout:
                    return {
                        'step_key': step_key,
                        'passed': False,
                        'message': f"Expected NO OmniInsertIntoHadoopFsRelationCommand, but found it in execution plan",
                        'execution_plan': explain_stdout
                    }
                else:
                    return {
                        'step_key': step_key,
                        'passed': True,
                        'message': "OmniInsertIntoHadoopFsRelationCommand not found (as expected for switch=false)",
                        'found_keywords': found_keywords
                    }
            
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"Expected keywords not found in execution plan. Expected: {expected_keywords}, Found: {found_keywords}",
                'execution_plan': explain_stdout,
                'found_keywords': found_keywords
            }
        
        return {
            'step_key': step_key,
            'passed': True,
            'message': f"Expected Omni keywords found in execution plan: {found_keywords}",
            'found_keywords': found_keywords
        }
    
    def _execute_generic_step(self, step_key: str, sql_statement: str, expected_result: str) -> Dict[str, Any]:
        """Execute generic step (no S1/E2 pattern detected)"""
        self.logger.info("Executing generic step")
        
        # Use Omni command by default
        omni_command = self.config.get_omni_spark_command()
        timeout = self.config.get_timeout()
        
        rc, stdout, stderr = self.ssh_executor.execute_spark_sql_background(
            omni_command, sql_statement, timeout
        )
        
        if rc != 0:
            return {
                'step_key': step_key,
                'passed': False,
                'message': f"Execution failed with return code {rc}",
                'stderr': stderr
            }
        
        return {
            'step_key': step_key,
            'passed': True,
            'message': "Execution successful",
            'output': stdout
        }
    
    def _extract_expected_keywords(self, expected_result: str) -> list:
        """Extract expected Omni keywords from expected_result text"""
        keywords = []
        
        # Check for OmniInsertIntoHadoopFsRelationCommand
        if 'OmniInsertIntoHadoopFsRelationCommand' in expected_result:
            keywords.append('OmniInsertIntoHadoopFsRelationCommand')
        
        # Check for other Omni keywords
        if 'OmniFilter' in expected_result:
            keywords.append('OmniFilter')
        
        if 'OmniProject' in expected_result:
            keywords.append('OmniProject')
        
        if 'OmniSort' in expected_result:
            keywords.append('OmniSort')
        
        if 'OmniAggregate' in expected_result:
            keywords.append('OmniAggregate')
        
        # Default to OmniInsertIntoHadoopFsRelationCommand for TableWrite tests
        if not keywords:
            keywords.append('OmniInsertIntoHadoopFsRelationCommand')
        
        return keywords