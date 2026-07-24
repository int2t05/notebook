# Python 安全编码示例

## 基础路径验证

```python
import os
from pathlib import Path

def safe_read_file(base_dir, filename):
    """安全的文件读取
    
    安全保证：
    1. 使用resolve()规范化路径，解析所有符号链接和相对路径
    2. 严格边界检查，确保路径分隔符匹配
    3. 防止/app/data被/app/data2绕过
    """
    base_path = Path(base_dir).resolve()
    target_path = (base_path / filename).resolve()
    
    base_str = str(base_path)
    target_str = str(target_path)
    
    if target_str != base_str and not target_str.startswith(base_str + os.sep):
        raise ValueError("路径穿越检测！")
    
    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError("路径穿越检测！")
    
    return target_path.read_text()
```

## 网络数据验证

```python
import os
import socket
import logging
from pathlib import Path

def safe_read_from_socket(base_dir, sock):
    """安全处理网络数据
    
    安全保证：
    1. 网络数据被视为不可信的外部输入
    2. 严格的字符验证，拒绝所有路径分隔符和遍历序列
    3. 双重边界检查
    4. 处理数据截断和UTF-8编码问题
    5. Socket超时防止无限阻塞
    """
    original_timeout = sock.gettimeout()
    if original_timeout is None:
        sock.settimeout(30.0)
    
    try:
        chunks = []
        total_size = 0
        MAX_FILENAME_SIZE = 255
        
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                chunks.append(chunk)
                total_size += len(chunk)
                
                if total_size > MAX_FILENAME_SIZE:
                    raise ValueError("文件名过长")
            except socket.timeout:
                raise ValueError("接收数据超时")
        
        data = b''.join(chunks)
        
        try:
            filename = data.decode('utf-8')
        except UnicodeDecodeError as e:
            if 'unexpected end of data' in str(e.reason):
                raise ValueError("数据不完整，可能被截断")
            raise ValueError("无效的UTF-8编码")
        
        dangerous_chars = ['..', '/', '\\', '\x00', '%', '\n', '\r']
        for char in dangerous_chars:
            if char in filename:
                logging.warning(f"检测到非法路径字符: {repr(char)}")
                raise ValueError("文件名包含非法字符")
        
        base_path = Path(base_dir).resolve()
        target_path = (base_path / filename).resolve()
        
        base_str = str(base_path)
        target_str = str(target_path)
        
        if target_str != base_str and not target_str.startswith(base_str + os.sep):
            raise ValueError("路径穿越检测")
        
        try:
            target_path.relative_to(base_path)
        except ValueError:
            raise ValueError("路径穿越检测")
        
        return target_path.read_text()
    finally:
        if original_timeout is None:
            sock.settimeout(original_timeout)
```

## 用户输入验证

```python
import os
from pathlib import Path
import re

def validate_user_filename(filename):
    """验证用户提供的文件名
    
    安全保证：
    1. 严格的白名单验证，仅允许ASCII安全字符
    2. 长度限制防止缓冲区溢出
    3. 禁止隐藏文件和特殊文件
    4. 正确的验证顺序，避免逻辑漏洞
    """
    if not filename or not filename.strip():
        raise ValueError("文件名不能为空")
    
    if len(filename) > 255:
        raise ValueError("文件名过长")
    
    if filename.startswith('.'):
        raise ValueError("不允许隐藏文件")
    
    if not re.match(r'^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)?$', filename):
        raise ValueError("文件名包含非法字符")
    
    return filename

def safe_user_file_access(base_dir, user_input):
    """安全处理用户输入
    
    安全保证：
    1. 输入验证 + 路径规范化 + 边界检查
    2. 双重验证机制
    """
    safe_filename = validate_user_filename(user_input)
    
    base_path = Path(base_dir).resolve()
    target_path = (base_path / safe_filename).resolve()
    
    base_str = str(base_path)
    target_str = str(target_path)
    
    if target_str != base_str and not target_str.startswith(base_str + os.sep):
        raise ValueError("路径穿越检测")
    
    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError("路径穿越检测")
    
    return target_path
```

## 配置文件验证

```python
import os
import hashlib
import hmac
from pathlib import Path

def load_config_safely(config_path, expected_owner=None, expected_group=None, expected_hash=None):
    """安全加载配置文件
    
    安全保证：
    1. 白名单验证确保只加载允许的配置文件
    2. 符号链接检查防止符号链接攻击
    3. 所有者验证确保文件归属正确
    4. 权限检查防止权限过宽
    5. 完整性校验确保文件未被篡改
    """
    config_file = Path(config_path)
    
    allowed_configs = {
        '/etc/app/config.json',
        '/var/lib/app/config.json'
    }
    
    resolved_path = str(config_file.resolve())
    if resolved_path not in allowed_configs:
        raise ValueError("非法配置路径")
    
    if config_file.is_symlink():
        raise ValueError("不允许符号链接")
    
    stat_info = config_file.stat()
    
    if expected_owner:
        try:
            import pwd
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            if owner != expected_owner:
                raise ValueError(f"文件所有者不是预期的用户: {expected_owner}")
        except ImportError:
            pass
    
    if expected_group:
        try:
            import grp
            group = grp.getgrgid(stat_info.st_gid).gr_name
            if group != expected_group:
                raise ValueError(f"文件所属组不是预期的组: {expected_group}")
        except ImportError:
            pass
    
    if stat_info.st_mode & 0o007:
        raise ValueError("配置文件权限过于宽松")
    
    content = config_file.read_text()
    
    if expected_hash:
        actual_hash = hashlib.sha256(content.encode()).hexdigest()
        if not hmac.compare_digest(actual_hash, expected_hash):
            raise ValueError("配置文件完整性校验失败")
    
    import json
    return json.loads(content)
```

## IPC数据验证

```python
import os
import hmac
import hashlib
import json
from pathlib import Path

def safe_ipc_file_access(ipc_data, shared_secret, base_dir):
    """安全处理IPC数据
    
    安全保证：
    1. IPC数据格式验证确保数据结构正确
    2. HMAC签名验证确保数据完整性
    3. 使用常量时间比较防止时序攻击
    4. 双重边界检查防止路径穿越
    5. 防止/app/data被/app/data2绕过
    """
    if not isinstance(ipc_data, dict):
        raise ValueError("IPC数据格式错误")
    
    if 'path' not in ipc_data:
        raise ValueError("IPC数据缺少'path'字段")
    
    if 'signature' not in ipc_data:
        raise ValueError("IPC数据缺少'signature'字段")
    
    if not isinstance(ipc_data['path'], str):
        raise ValueError("IPC数据'path'字段必须是字符串")
    
    if not isinstance(ipc_data['signature'], str):
        raise ValueError("IPC数据'signature'字段必须是字符串")
    
    expected_sig = hmac.new(
        shared_secret.encode(),
        ipc_data['path'].encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(ipc_data.get('signature', ''), expected_sig):
        raise ValueError("IPC数据签名验证失败")
    
    filename = ipc_data['path']
    base_path = Path(base_dir).resolve()
    target_path = (base_path / filename).resolve()
    
    base_str = str(base_path)
    target_str = str(target_path)
    
    if target_str != base_str and not target_str.startswith(base_str + os.sep):
        raise ValueError("路径穿越检测")
    
    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError("路径穿越检测")
    
    return target_path
```

## TOCTOU竞态条件缓解（Python）

```python
import os
from pathlib import Path

def safe_read_file_no_race(base_dir, filename):
    """无竞态条件的安全文件读取（Linux/Unix）"""
    base_path = Path(base_dir).resolve()
    target_path = (base_path / filename).resolve()
    
    base_str = str(base_path)
    target_str = str(target_path)
    
    if target_str != base_str and not target_str.startswith(base_str + os.sep):
        raise ValueError("路径穿越检测！")
    
    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError("路径穿越检测！")
    
    try:
        fd = os.open(str(target_path), os.O_RDONLY | os.O_NOFOLLOW)
        try:
            fd_path = os.readlink(f"/proc/self/fd/{fd}")
            if not fd_path.startswith(base_str):
                os.close(fd)
                raise ValueError("路径穿越检测！")
            
            with os.fdopen(fd, 'r') as f:
                return f.read()
        except:
            os.close(fd)
            raise
    except OSError as e:
        if e.errno == 40:
            raise ValueError("检测到符号链接攻击")
        raise
```
