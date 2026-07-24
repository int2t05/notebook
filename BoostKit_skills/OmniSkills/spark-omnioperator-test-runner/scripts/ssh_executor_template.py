"""SSH Executor - SSH connection and background execution with connection pooling and retry"""
import paramiko
import time
import uuid
import re
import socket
from typing import Tuple, Dict, Any, List
from core.logger import TestCaseLogger
from core.ssh_pool import get_ssh_pool
from core.ssh_pool import get_max_pool_size


class SSHExecutor:
    """SSH-based remote execution with connection pooling and retry logic"""
    
    def __init__(self, server_config: Dict[str, Any], logger: TestCaseLogger):
        self.server_ip = server_config['ip']
        self.server_user = server_config['user']
        self.server_password = server_config['password']
        self.logger = logger
        self.client = None
        self.ssh_pool = None
        self.use_pool = True  # Enable pooling by default
        
    def connect(self):
        """Establish SSH connection using pool or direct connection"""
        if self.use_pool:
            # Use connection pool
            self.ssh_pool = get_ssh_pool({
                'ip': self.server_ip,
                'user': self.server_user,
                'password': self.server_password
            })  # max_pool_size will be read from config automatically
            
            try:
                # Acquire connection from pool with retry
                self.client = self._retry_operation(
                    lambda: self.ssh_pool.acquire(timeout=60),
                    max_retries=3,
                    operation_name="SSH pool acquire"
                )
                self.logger.info(f"SSH connection acquired from pool to {self.server_ip}")
            except Exception as e:
                self.logger.error(f"Failed to acquire connection from pool: {e}")
                # Fallback to direct connection
                self.logger.warning("Falling back to direct SSH connection")
                self.use_pool = False
                self._connect_direct()
        else:
            # Direct connection (fallback)
            self._connect_direct()
    
    def _connect_direct(self):
        """Direct SSH connection without pool (fallback mode)"""
        max_retries = 3
        retry_delay = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(max_retries):
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(
                    hostname=self.server_ip,
                    username=self.server_user,
                    password=self.server_password,
                    timeout=30,
                    banner_timeout=30
                )
                self.logger.info(f"Direct SSH connection established to {self.server_ip} (attempt {attempt+1})")
                return
            except paramiko.ssh_exception.SSHException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"SSH connection failed (attempt {attempt+1}): {e}, retrying in {retry_delay[attempt]}s...")
                    time.sleep(retry_delay[attempt])
                else:
                    self.logger.error(f"SSH connection failed after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected SSH error: {e}")
                raise
    
    def _retry_operation(self, operation, max_retries: int = 3, operation_name: str = "operation"):
        """Execute operation with exponential backoff retry"""
        retry_delay = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(max_retries):
            try:
                return operation()
            except paramiko.ssh_exception.SSHException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"{operation_name} failed (attempt {attempt+1}): {e}, retrying in {retry_delay[attempt]}s...")
                    time.sleep(retry_delay[attempt])
                else:
                    self.logger.error(f"{operation_name} failed after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error in {operation_name}: {e}")
                raise
    
    def disconnect(self):
        """Close SSH connection (return to pool if using pool)"""
        if self.client:
            if self.use_pool and self.ssh_pool:
                # Return connection to pool
                self.ssh_pool.release(self.client)
                self.logger.info("SSH connection returned to pool")
            else:
                # Direct close
                try:
                    self.client.close()
                    self.logger.info("SSH connection closed")
                except Exception as e:
                    self.logger.warning(f"Error closing SSH connection: {e}")
            self.client = None
    
    def is_sql_execution_success(self, output: str) -> bool:
        """Check if SQL actually executed successfully (ignore startup warnings)"""
        # SQL execution success indicators
        sql_success_indicators = [
            'Time taken:',
            'OK',
            '== Physical Plan ==',
            '== Optimized Logical Plan ==',
            '== Extended Logical Plan ==',
            'spark.sql.',
        ]
        
        # Check for actual data rows
        has_data_rows = False
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or re.match(r'^\d{4}-\d{2}-\d{2}', line):
                continue
            if 'hadoop: command not found' in line or 'Error: A JNI error' in line:
                continue
            if 'Exception in thread' in line or 'java.lang.' in line or 'Caused by:' in line:
                continue
            if line and not line.startswith('Time taken:'):
                has_data_rows = True
        
        for indicator in sql_success_indicators:
            if indicator in output:
                return True
        
        if has_data_rows:
            return True
        
        has_startup_errors = any(err in output for err in [
            'Error: A JNI error',
            'java.lang.NoClassDefFoundError',
            'ClassNotFoundException',
            'Exception in thread "main"'
        ])
        
        if output.strip() and not has_startup_errors:
            return True
        
        return False
    
    def execute_spark_sql_background(self, spark_command: str, sql_statements: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute spark-sql using temporary SQL file approach"""
        # Generate unique file names
        log_file = f"/tmp/omni_test_{uuid.uuid4().hex[:8]}.log"
        pid_file = f"/tmp/omni_pid_{uuid.uuid4().hex[:8]}.pid"
        
        self.logger.command("BACKGROUND EXECUTION", spark_command)
        self.logger.sql(sql_statements)
        
        # CRITICAL FIX: Handle source command prefix properly
        if spark_command.startswith('source '):
            parts = spark_command.split(';', 1)
            source_part = parts[0]
            spark_sql_part = parts[1] if len(parts) > 1 else spark_command
            bg_command = f"source /etc/profile &>/dev/null; {source_part} &>/dev/null; nohup {spark_sql_part} -e \"{sql_statements}\" > {log_file} 2>&1 & echo $! > {pid_file}"
        else:
            full_command = f"{spark_command} -e \"{sql_statements}\""
            inner_bg_command = f"nohup {full_command} > {log_file} 2>&1 & echo $! > {pid_file}"
            bg_command = f"source /etc/profile &>/dev/null; {inner_bg_command}"
        
        self.logger.info(f"Executing: {bg_command}")
        
        # Execute command with retry logic
        stdin, stdout, stderr = self._retry_operation(
            lambda: self.client.exec_command(bg_command, timeout=30),
            max_retries=2,
            operation_name="Background command execution"
        )
        
        try:
            stdout.read()
        except socket.timeout:
            self.logger.warning("Timeout reading stdout, checking PID file anyway...")
        
        # Read PID with retry
        stdin, stdout_pid, stderr_pid = self._retry_operation(
            lambda: self.client.exec_command(f"cat {pid_file}", timeout=10),
            max_retries=2,
            operation_name="PID file read"
        )
        pid = stdout_pid.read().decode('utf-8').strip()
        self.logger.info(f"Background process PID: {pid}")
        
        # Poll for completion
        start_time = time.time()
        poll_interval = 10
        
        while time.time() - start_time < timeout:
            if pid:
                check_cmd = f"ps -p {pid} > /dev/null 2>&1; echo $?"
                stdin, stdout, stderr = self._retry_operation(
                    lambda: self.client.exec_command(check_cmd, timeout=5),
                    max_retries=1,
                    operation_name="Process check"
                )
                ps_rc = stdout.read().decode('utf-8').strip()
                
                if ps_rc == "1":
                    self.logger.info(f"Process {pid} completed")
                    break
            
            time.sleep(poll_interval)
        
        if time.time() - start_time >= timeout:
            self.logger.warning(f"Timeout reached after {timeout}s")
            if pid:
                kill_cmd = f"kill -9 {pid} 2>/dev/null"
                self.client.exec_command(kill_cmd, timeout=5)
                time.sleep(2)
        
        # Read log file with retry
        stdin, stdout, stderr = self._retry_operation(
            lambda: self.client.exec_command(f"cat {log_file}", timeout=timeout),
            max_retries=2,
            operation_name="Log file read"
        )
        log_content = stdout.read().decode('utf-8', errors='replace')
        
        stdout_text = log_content
        stderr_text = ""
        
        sql_success = self.is_sql_execution_success(stdout_text)
        effective_return_code = 0 if sql_success else -1
        
        self.logger.info(f"[SQL EXECUTION STATUS]: {'SUCCESS' if sql_success else 'FAILED'}")
        self.logger.execution_result(effective_return_code, stdout_text, stderr_text)
        
        # Cleanup with error handling
        try:
            self.client.exec_command(f"rm -f {log_file} {pid_file}", timeout=5)
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")
        
        return effective_return_code, stdout_text, stderr_text
    
    def execute_native_spark(self, native_command: str, sql_statements: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute SQL on Native Spark"""
        self.logger.info("Executing on Native Spark...")
        return self.execute_spark_sql_background(native_command, sql_statements, timeout)
    
    def execute_omni_spark(self, omni_command: str, sql_statements: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute SQL on Omni Spark"""
        self.logger.info("Executing on Omni Spark...")
        return self.execute_spark_sql_background(omni_command, sql_statements, timeout)
    
    def execute_explain(self, omni_command: str, explain_sql: str, timeout: int = 60) -> Tuple[int, str, str]:
        """Execute EXPLAIN on Omni Spark"""
        self.logger.info("Executing EXPLAIN on Omni Spark...")
        self.logger.sql(explain_sql)
        return self.execute_spark_sql_background(omni_command, explain_sql, timeout)


class ResultExtractor:
    """Extract query results from log output"""
    
    @staticmethod
    def extract_query_results(output: str) -> List[str]:
        """Extract query result rows - only actual data rows with tab separator"""
        lines = output.strip().split('\n')
        
        result_end_idx = -1
        for i, line in enumerate(lines):
            if 'Time taken:' in line and ('Fetched' in line or 'row(s)' in line):
                result_end_idx = i
        
        data_rows = []
        if result_end_idx >= 0:
            for i in range(result_end_idx - 1, -1, -1):
                line = lines[i].strip()
                
                if not line:
                    continue
                    
                if '\t' in line:
                    data_rows.insert(0, line)
                    continue
                
                if any(skip in line for skip in [
                    'WARN', 'INFO', 'ERROR', 'Setting default',
                    'Spark master', 'Application Id', 
                    'java.', 'Exception', 'hadoop:',
                    'NativeCodeLoader', 'Utils:', 'Client:',
                    'SessionState', 'METASTORE', 'SQLConf',
                    'Time taken:', 'Unable to', 'Your hostname',
                    'Using Scala', 'Branch', 'Compiled by', 'Revision'
                ]):
                    break
        
        return data_rows
    
    @staticmethod
    def extract_execution_plan(output: str) -> str:
        """Extract execution plan from EXPLAIN output"""
        plan_start_markers = ['== Physical Plan ==', '== Optimized Logical Plan ==', '== Extended Logical Plan ==']
        
        for marker in plan_start_markers:
            if marker in output:
                plan_section = output.split(marker)[1]
                next_marker_idx = plan_section.find('==')
                if next_marker_idx > 0:
                    plan_section = plan_section[:next_marker_idx]
                return plan_section.strip()
        
        return output


class ResultComparator:
    """Compare results row-by-row between Native and Omni"""
    
    @staticmethod
    def compare_results(native_output: str, omni_output: str) -> Tuple[bool, str]:
        """Compare Native and Omni results"""
        native_results = ResultExtractor.extract_query_results(native_output)
        omni_results = ResultExtractor.extract_query_results(omni_output)
        
        if len(native_results) != len(omni_results):
            return False, f"Row count mismatch: Native={len(native_results)}, Omni={len(omni_results)}"
        
        differences = []
        for i, (native_row, omni_row) in enumerate(zip(native_results, omni_results)):
            if native_row != omni_row:
                differences.append(f"Row {i+1}:\n  Native: {native_row}\n  Omni:  {omni_row}")
        
        if differences:
            return False, "\n".join(differences)
        
        return True, "Results match perfectly"


class ExecutionPlanChecker:
    """Check execution plan for Omni keywords"""
    
    OMNI_KEYWORDS = [
        'OmniInsertIntoHadoopFsRelationCommand',
        'OmniFilter',
        'OmniProject',
        'OmniSort',
        'OmniAggregate',
        'OmniScan',
        'OmniJoin',
        'OmniBroadcast',
        'OmniUnion',
        'OmniLimit',
        'ColumnarShuffle',
        'Gluten'
    ]
    
    @staticmethod
    def check_keywords(plan_output: str, expected_keywords: List[str] = None) -> Tuple[bool, List[str]]:
        """Check if expected Omni keywords appear in execution plan"""
        if expected_keywords is None:
            expected_keywords = ['OmniInsertIntoHadoopFsRelationCommand']
        
        plan_text = ResultExtractor.extract_execution_plan(plan_output)
        
        found_keywords = [kw for kw in ExecutionPlanChecker.OMNI_KEYWORDS if kw in plan_text]
        expected_found = [kw for kw in expected_keywords if kw in plan_text]
        
        return len(expected_found) > 0, found_keywords