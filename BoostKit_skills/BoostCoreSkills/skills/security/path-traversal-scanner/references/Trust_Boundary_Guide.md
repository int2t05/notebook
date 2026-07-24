# 信任边界指南 (Trust Boundary Guide)

## 核心概念

**信任边界 (Trust Boundary)** 是安全架构中的关键概念，指不同信任级别之间的边界。

### 定义

```
信任边界 = 内部信任域 ⟂ 外部不可信域
```

**规则：任何跨越信任边界的数据都必须视为不可信，需要验证和净化。**

---

## 信任边界可视化

```
┌──────────────────────────────────────────────────────────┐
│                    信任边界                               │
│  ┌──────────────┐          ┌──────────────┐             │
│  │  内部信任域  │          │  外部不可信域 │             │
│  │              │          │              │             │
│  │ ✓ 应用代码   │ ←─────── │ ✗ 用户输入   │             │
│  │ ✓ 硬编码常量 │   数据流  │ ✗ 网络报文   │             │
│  │ ✓ 内部生成   │          │ ✗ 其他进程   │             │
│  │              │          │ ✗ 远程API    │             │
│  └──────────────┘          └──────────────┘             │
│         ↓                         ↓                      │
│    安全 (低风险)            危险 (高风险)                 │
└──────────────────────────────────────────────────────────┘
```

---

## 信任边界类型

### 1. 网络数据 → 应用代码

**风险级别**: 高危 ⚠️

**数据源**:
- Socket接收数据 (`socket.recv()`)
- RPC响应 (gRPC, Thrift, Dubbo)
- 消息队列 (Kafka, RabbitMQ, Redis)
- WebSocket消息
- HTTP响应体（调用外部API）

**攻击向量**:
- 恶意网络报文注入路径穿越序列
- 伪造RPC响应包含恶意路径
- 消息队列投毒
- 中间人攻击篡改数据

**缓解措施**:
- 协议验证（格式、长度、类型）
- 数据格式检查（JSON Schema, Protobuf验证）
- 路径验证（规范化、边界检查）
- TLS/SSL加密传输
- 消息签名验证

**示例**:
```python
# 漏洞代码
data = socket.recv(1024)
filename = data.decode()  # 直接使用网络数据！
with open(filename, 'r') as f:
    content = f.read()

# 安全代码
data = socket.recv(1024)
try:
    filename = validate_path(data.decode())  # 验证网络数据
    safe_path = resolve_and_check(base_dir, filename)
    with open(safe_path, 'r') as f:
        content = f.read()
except ValidationError as e:
    log_security_event("invalid_network_path", e)
```

---

### 2. 用户输入 → 应用代码

**风险级别**: 高危 ⚠️

**数据源**:
- HTTP请求参数 (GET/POST/PUT/DELETE)
- 命令行参数 (sys.argv, args[])
- 文件上传（文件名、文件内容）
- Cookie值
- HTTP头部
- 表单数据

**攻击向量**:
- 路径穿越序列 (`../`, `..\\`)
- URL编码绕过 (`%2e%2e%2f`)
- 双重编码绕过 (`%252e%252e%252f`)
- UTF-8编码绕过 (`%c0%ae%c0%ae%c0%af`)
- 空字节注入 (`file.txt%00.jpg`)
- 绝对路径 (`/etc/passwd`)

**缓解措施**:
- 输入验证（白名单、格式检查）
- 路径规范化 (`realpath()`, `resolve()`)
- 边界检查（确保在基础目录内）
- 危险字符过滤

**示例**:
```python
# 漏洞代码
filename = request.args.get('file')
with open(filename, 'r') as f:  # 直接用户输入！
    content = f.read()

# 安全代码
from pathlib import Path

def safe_read_file(base_dir, user_input):
    base_path = Path(base_dir).resolve()
    
    # 验证输入
    if '..' in user_input or '/' in user_input:
        raise ValueError("非法路径字符")
    
    target_path = (base_path / user_input).resolve()
    
    # 边界检查
    if not str(target_path).startswith(str(base_path)):
        raise ValueError("路径穿越检测")
    
    return target_path.read_text()
```

---

### 3. 其他进程 → 应用进程

**风险级别**: 高危 ⚠️

**数据源**:
- IPC通信 (管道、消息队列、信号)
- 共享内存 (shm, mmap)
- Unix Domain Socket
- 进程间文件传递
- 容器间通信 (Docker, Kubernetes)

**攻击向量**:
- 恶意进程注入数据
- 共享内存篡改
- 竞态条件利用
- 容器逃逸

**缓解措施**:
- 进程隔离 (namespace, cgroup)
- 权限控制 (最小权限原则)
- 数据签名/加密
- 共享内存保护 (只读、权限控制)
- 容器安全策略

**示例**:
```python
# 漏洞代码 - IPC通信
import multiprocessing
queue = multiprocessing.Queue()
data = queue.get()  # 其他进程的数据
filename = data['path']
with open(filename, 'r') as f:  # 跨信任边界！
    content = f.read()

# 安全代码
import multiprocessing
import hashlib

def safe_ipc_read(queue, shared_secret):
    data = queue.get()
    
    # 验证签名
    expected_sig = hmac.new(
        shared_secret.encode(),
        data['path'].encode(),
        hashlib.sha256
    ).hexdigest()
    
    if data.get('signature') != expected_sig:
        raise ValueError("数据签名验证失败")
    
    # 验证路径
    safe_path = validate_and_resolve(base_dir, data['path'])
    return safe_path.read_text()
```

---

### 4. 配置数据 → 应用代码

**风险级别**: 中危 ⚡ (取决于配置权限)

**数据源**:
- 配置文件 (JSON, YAML, INI, XML)
- 环境变量
- 命令行选项
- 数据库配置表
- 远程配置中心 (Consul, etcd)

**攻击向量**:
- 配置文件篡改
- 环境变量注入
- 配置中心攻击
- 默认配置漏洞

**缓解措施**:
- 配置文件权限控制 (chmod 600)
- 配置完整性校验 (SHA256, 签名)
- 环境变量白名单
- 配置变更审计
- 敏感配置加密

**示例**:
```python
# 漏洞代码
import os
config_path = os.getenv('CONFIG_PATH')  # 环境变量可控
with open(config_path, 'r') as f:  # 可能跨信任边界
    config = json.load(f)

# 安全代码
import os
from pathlib import Path

def load_config_safely():
    # 白名单验证
    allowed_config_paths = {
        '/etc/app/config.json',
        '/var/lib/app/config.json'
    }
    
    config_path = os.getenv('CONFIG_PATH', '/etc/app/config.json')
    
    if config_path not in allowed_config_paths:
        raise ValueError("非法配置路径")
    
    # 权限检查
    config_file = Path(config_path)
    stat_info = config_file.stat()
    
    if stat_info.st_mode & 0o077:  # 检查其他用户权限
        raise ValueError("配置文件权限过于宽松")
    
    # 完整性校验
    content = config_file.read_text()
    expected_hash = os.getenv('CONFIG_HASH')
    
    if expected_hash:
        actual_hash = hashlib.sha256(content.encode()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError("配置文件完整性校验失败")
    
    return json.loads(content)
```

---

## 信任边界决策树

```
数据进入应用
    │
    ├─ 是否来自网络？
    │   ├─ 是 → 信任边界1 → 高风险 → 必须验证
    │   └─ 否 ↓
    │
    ├─ 是否来自用户输入？
    │   ├─ 是 → 信任边界2 → 高风险 → 必须验证
    │   └─ 否 ↓
    │
    ├─ 是否来自其他进程？
    │   ├─ 是 → 信任边界3 → 高风险 → 必须验证
    │   └─ 否 ↓
    │
    ├─ 是否来自配置？
    │   ├─ 是 → 信任边界4 → 中风险 → 需验证权限
    │   └─ 否 ↓
    │
    └─ 内部信任域 → 低风险 → 可选验证
```

---

## 信任边界识别清单

```
□ 已识别所有数据入口点
  □ 网络数据入口：socket, RPC, WebSocket, 消息队列
  □ 用户输入入口：HTTP参数, CLI参数, 文件上传
  □ 跨进程入口：IPC, 共享内存, 管道
  □ 配置入口：配置文件, 环境变量

□ 已确定每个入口的信任边界
  □ 数据源是否跨信任边界？
  □ 数据是否可被外部控制？
  □ 数据是否可被篡改？

□ 已实施验证措施
  □ 格式验证
  □ 路径验证
  □ 签名验证
  □ 权限检查

□ 已建立监控机制
  □ 跨信任边界数据流监控
  □ 异常检测和告警
  □ 审计日志
```

---

## 常见错误

### ❌ 错误1：仅验证用户输入

```python
# 错误：只验证HTTP参数，忽略网络数据
filename = request.args.get('file')  # 验证了
data = socket.recv(1024)              # 没验证！
config = json.load(open(env_config))  # 没验证！
```

### ✅ 正确：验证所有跨信任边界数据

```python
# 正确：验证所有外部数据
filename = validate_user_input(request.args.get('file'))
data = validate_network_data(socket.recv(1024))
config = validate_config(json.load(open(validate_config_path(env_config))))
```

### ❌ 错误2：假设配置安全

```python
# 错误：假设配置文件不会被篡改
config_path = "/etc/app/config.json"
with open(config_path, 'r') as f:  # 如果配置文件被篡改？
    config = json.load(f)
```

### ✅ 正确：验证配置完整性

```python
# 正确：验证配置来源和完整性
config_path = validate_config_path("/etc/app/config.json")
check_file_permissions(config_path, 0o600)  # 仅所有者可读写
verify_file_integrity(config_path, expected_hash)
config = json.load(open(config_path, 'r'))
```

### ❌ 错误3：忽略进程间通信

```python
# 错误：假设IPC数据可信
data = ipc_queue.get()
filename = data['path']  # 其他进程可能被攻陷！
```

### ✅ 正确：验证跨进程数据

```python
# 正确：验证IPC数据签名
data = ipc_queue.get()
verify_data_signature(data, shared_secret)
filename = validate_path(data['path'])
```

---

## 参考资料

- OWASP Trust Boundary: https://owasp.org/www-community/Trust_Boundary
- CWE-20: Improper Input Validation: https://cwe.mitre.org/data/definitions/20.html
- NIST SP 800-160: Systems Security Engineering
- SEI CERT: Validate Inputs from Untrusted Sources
