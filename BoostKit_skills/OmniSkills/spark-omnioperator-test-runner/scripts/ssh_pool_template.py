"""SSH Connection Pool - Singleton pattern for connection reuse"""
import os
import configparser

def _load_max_pool_size():
    """Load max pool size from environment or pytest.ini"""
    # 1) Environment variable
    v = os.getenv("SSH_POOL_SIZE")
    if v and v.isdigit():
        return int(v)

    # 2) pytest.ini option
    try:
        parser = configparser.ConfigParser()
        parser.read("pytest.ini")
        if parser.has_section("ssh") and parser.has_option("ssh", "pool_size"):
            return parser.getint("ssh", "pool_size")
    except Exception:
        pass

    # 3) Default fallback
    return 30

# Global pool size cached at import time
max_pool_size = _load_max_pool_size()

def get_max_pool_size():
    """Public accessor for configured pool size"""
    return max_pool_size

def _log(msg: str):
    # Lightweight logger to avoid import-time side effects
    import logging
    logging.debug(msg)
import paramiko
import time
import threading
from typing import Dict, Any, Optional
from queue import Queue, Empty


class SSHConnectionPool:
    """Thread-safe singleton SSH connection pool with health checks"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, server_config: Dict[str, Any] = None, max_pool_size: int = 30):
        """Singleton pattern - only one pool instance exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SSHConnectionPool, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, server_config: Dict[str, Any] = None, max_pool_size: int = 30):
        """Initialize pool with server config and max size"""
        if self._initialized:
            return
        
        self.server_config = server_config
        self.max_pool_size = max_pool_size
        self._pool = Queue(maxsize=max_pool_size)
        self._active_connections = 0
        self._pool_lock = threading.Lock()
        self._initialized = True
        
        print(f"[SSH_POOL] Initialized pool with max size {max_pool_size}")
    
    def _create_connection(self) -> paramiko.SSHClient:
        """Create a new SSH connection"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=self.server_config['ip'],
                username=self.server_config['user'],
                password=self.server_config['password'],
                timeout=30,
                banner_timeout=30  # Explicit banner timeout
            )
            print(f"[SSH_POOL] Created new connection to {self.server_config['ip']}")
            return client
        except Exception as e:
            print(f"[SSH_POOL] Connection creation failed: {e}")
            raise
    
    def _is_connection_healthy(self, client: paramiko.SSHClient) -> bool:
        """Check if SSH connection is still alive and usable"""
        try:
            # Check if transport is active
            if client.get_transport() is None:
                return False
            
            transport = client.get_transport()
            if not transport.is_active():
                return False
            
            # Quick test - execute simple command
            stdin, stdout, stderr = client.exec_command("echo 'health_check'", timeout=5)
            stdout.read()
            return True
        except Exception as e:
            print(f"[SSH_POOL] Health check failed: {e}")
            return False
    
    def acquire(self, timeout: int = 60) -> paramiko.SSHClient:
        """Acquire an SSH connection from the pool (or create new one)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Try to get existing connection from pool
            try:
                client = self._pool.get(block=False)
                
                # Health check before returning
                if self._is_connection_healthy(client):
                    print(f"[SSH_POOL] Reused healthy connection from pool")
                    return client
                else:
                    # Connection unhealthy - close it and create new
                    print(f"[SSH_POOL] Discarded unhealthy connection")
                    try:
                        client.close()
                    except:
                        pass
                    with self._pool_lock:
                        self._active_connections -= 1
            except Empty:
                # Pool empty - create new connection if under limit
                pass
            
            # Create new connection if under max limit
            with self._pool_lock:
                if self._active_connections < self.max_pool_size:
                    self._active_connections += 1
                    try:
                        client = self._create_connection()
                        print(f"[SSH_POOL] Acquired new connection (active: {self._active_connections}/{self.max_pool_size})")
                        return client
                    except Exception as e:
                        self._active_connections -= 1
                        print(f"[SSH_POOL] Failed to create connection: {e}")
                        # Wait before retry
                        time.sleep(2)
                        continue
            
            # Pool full and no available connections - wait
            print(f"[SSH_POOL] Pool full ({self._active_connections}/{self.max_pool_size}), waiting...")
            time.sleep(5)
        
        # Timeout exceeded
        raise Exception(f"SSH_POOL: Failed to acquire connection after {timeout}s timeout")
    
    def release(self, client: paramiko.SSHClient):
        """Release SSH connection back to the pool for reuse"""
        try:
            # Health check before returning to pool
            if self._is_connection_healthy(client):
                try:
                    self._pool.put(client, block=False)
                    print(f"[SSH_POOL] Returned healthy connection to pool (pool size: {self._pool.qsize()})")
                    return
                except:
                    # Pool full - close connection
                    pass
            
            # Connection unhealthy or pool full - close it
            print(f"[SSH_POOL] Closing connection (unhealthy or pool full)")
            try:
                client.close()
            except:
                pass
            
            with self._pool_lock:
                self._active_connections -= 1
                print(f"[SSH_POOL] Connection closed (active: {self._active_connections}/{self.max_pool_size})")
        except Exception as e:
            print(f"[SSH_POOL] Error releasing connection: {e}")
            with self._pool_lock:
                self._active_connections -= 1
    
    def close_all(self):
        """Close all connections in the pool"""
        print(f"[SSH_POOL] Closing all connections...")
        
        while not self._pool.empty():
            try:
                client = self._pool.get(block=False)
                try:
                    client.close()
                except:
                    pass
            except Empty:
                break
        
        with self._pool_lock:
            self._active_connections = 0
        
        print(f"[SSH_POOL] All connections closed")
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        return {
            'pool_size': self._pool.qsize(),
            'active_connections': self._active_connections,
            'max_pool_size': self.max_pool_size
        }


# Global pool instance getter
def get_ssh_pool(server_config: Dict[str, Any] = None, max_pool_size: int = None) -> SSHConnectionPool:
    """Get or initialize global SSH connection pool"""
    if max_pool_size is None:
        max_pool_size = get_max_pool_size()
    pool = SSHConnectionPool(server_config, max_pool_size)
    if server_config and not pool.server_config:
        pool.server_config = server_config
        pool.max_pool_size = max_pool_size
    return pool