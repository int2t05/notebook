# 外部数据源识别指南 (External Data Sources Guide)

## 概述

**核心原则：不只是用户输入，所有外部不可控的数据源都有风险。**

任何跨越信任边界的数据都必须视为不可信，需要验证和净化。

---

## 数据源分类

### EXTERNAL (外部不可控) - 高风险 ⚠️

#### 【直接用户输入】

**HTTP请求参数**

Python (Flask/Django):
```python
request.args.get('file')      # GET参数
request.form.get('file')      # POST参数
request.files['file']         # 上传文件
request.data                  # 原始请求体
request.json.get('file')      # JSON体
```

Java (Servlet/Spring):
```java
request.getParameter("file");
request.getInputStream();
@RequestParam String filename
@PathVariable String filename
```

JavaScript (Express):
```javascript
req.query.file          // GET参数
req.body.file           // POST参数
req.params.file         // 路径参数
req.files.file          // 上传文件
```

PHP:
```php
$_GET['file']
$_POST['file']
$_REQUEST['file']
$_FILES['file']['name']
```

Go:
```go
r.URL.Query().Get("file")
r.FormValue("file")
```

**命令行参数**

```python
# Python
sys.argv[1]
argparse.ArgumentParser().parse_args()
```

```java
// Java
args[0]  // main(String[] args)
```

```c
// C
argv[1]  // main(int argc, char *argv[])
getopt(argc, argv, "f:")
```

---

#### 【网络数据】

**Socket接收**

```python
# Python
data = socket.recv(1024)
filename = data.decode()

# TCP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data = sock.recv(4096)

# UDP Socket
data, addr = sock.recvfrom(4096)
```

```java
// Java
InputStream is = socket.getInputStream();
byte[] data = is.readAllBytes();
String filename = new String(data);
```

```c
// C
char buffer[256];
recv(socket_fd, buffer, sizeof(buffer), 0);
```

**RPC响应**

```python
# gRPC
response = stub.getFile(request)
path = response.file_path

# Thrift
client = ThriftClient()
result = client.get_path()

# Dubbo
result = dubbo_service.invoke("getFilePath")
```

```java
// gRPC Java
Response response = stub.getFile(request);
String path = response.getFilePath();
```

**消息队列**

```python
# Kafka
from kafka import KafkaConsumer
consumer = KafkaConsumer('topic')
message = consumer.poll()
filepath = message.value['filename']

# RabbitMQ
import pika
connection = pika.BlockingConnection()
channel = connection.channel()
method, properties, body = channel.basic_get('queue')
data = json.loads(body)

# Redis
import redis
r = redis.Redis()
data = r.get('file_path')
```

**WebSocket**

```python
# Python
from flask_socketio import SocketIO
@socketio.on('message')
def handle_message(data):
    filename = data['path']  # 外部数据！

# JavaScript (Node.js)
ws.on('message', function(data) {
    const filename = JSON.parse(data).path;
});
```

---

#### 【跨信任域数据】

**IPC通信**

```python
# Python multiprocessing
import multiprocessing
queue = multiprocessing.Queue()
data = queue.get()  # 来自其他进程

# Pipe
parent_conn, child_conn = multiprocessing.Pipe()
data = parent_conn.recv()

# Shared memory
import mmap
shared_mem = mmap.mmap(-1, 1024)
data = shared_mem.read(100)
```

```c
// C IPC - Pipe
char buffer[256];
read(pipe_fd, buffer, sizeof(buffer));

// Shared memory
char *shared_data = shmat(shmid, NULL, 0);
// shared_data 可能被其他进程修改

// Message queue
struct msgbuf message;
msgrcv(msqid, &message, sizeof(message), 1, 0);
```

**容器间通信**

```python
# Docker/K8s 共享卷
with open('/shared-volume/config.json') as f:
    config = json.load(f)  # 其他容器写入

# Kubernetes ConfigMap/Secret
with open('/etc/config/app-config.json') as f:
    config = json.load(f)
```

---

#### 【间接受控数据】

**环境变量**

```python
# Python
os.environ.get('FILE_PATH')
os.getenv('FILE_PATH')
```

```c
// C
getenv("FILE_PATH")
```

```go
// Go
os.Getenv("FILE_PATH")
```

**数据库查询结果**

```python
# 如果查询受用户输入影响
user_id = request.args.get('id')  # 用户输入
result = db.query("SELECT path FROM files WHERE id = ?", user_id)
filepath = result['path']  # 间接受用户控制
```

**配置文件内容**

```python
# 如果配置文件可被用户编辑
with open('/home/user/.app/config.json') as f:
    config = json.load(f)  # 用户可编辑
```

**文件系统数据**

```python
# 如果文件内容受外部控制
filename = request.args.get('file')
with open(filename, 'r') as f:
    content = f.read()  # 文件内容可能被外部控制
```

---

### INTERNAL (内部可控) - 低风险 ✓

**硬编码字符串**

```python
filename = "/etc/passwd"  # 硬编码
config_file = "config.json"  # 常量
```

**随机生成值**

```python
import secrets
import uuid

# 密码学安全的随机
token = secrets.token_urlsafe(32)
uid = uuid.uuid4()
```

**编译时常量**

```c
#define CONFIG_PATH "/etc/app/config.json"
const char *filename = CONFIG_PATH;
```

**内部函数返回值**

```python
# 如果函数内部无外部数据依赖
def get_internal_path():
    return "/var/data/internal.json"

filename = get_internal_path()  # 内部生成
```

---

### CONFIGURATION (配置/管理) - 中风险 ⚡

**管理员控制的配置**

```python
# 仅管理员可修改
with open('/etc/app/config.json') as f:  # 权限: 600, owner: root
    config = json.load(f)
```

**系统级环境变量**

```bash
# /etc/environment
export APP_CONFIG_PATH="/etc/app/config.json"
```

**部署时确定的参数**

```yaml
# docker-compose.yml
environment:
  - CONFIG_PATH=/etc/app/config.json
```

**⚠️ 注意：如果配置可被普通用户修改，应升级为 EXTERNAL**

---

## 数据源识别流程

### 步骤1：识别数据入口点

```
检查所有数据来源：
├─ HTTP请求？ → EXTERNAL
├─ CLI参数？ → EXTERNAL
├─ Socket接收？ → EXTERNAL
├─ RPC响应？ → EXTERNAL
├─ 消息队列？ → EXTERNAL
├─ IPC通信？ → EXTERNAL
├─ 环境变量？ → EXTERNAL/CONFIGURATION
├─ 配置文件？ → CONFIGURATION
└─ 硬编码？ → INTERNAL
```

### 步骤2：确定信任边界

```
对每个数据源：
├─ 是否跨信任边界？
│   ├─ 网络 → 应用：是
│   ├─ 用户 → 应用：是
│   ├─ 其他进程 → 应用：是
│   ├─ 配置 → 应用：取决于权限
│   └─ 内部 → 应用：否
│
└─ 是否可被外部控制？
    ├─ 可控制 → EXTERNAL
    ├─ 部分控制 → CONFIGURATION
    └─ 不可控制 → INTERNAL
```

### 步骤3：评估风险级别

```
EXTERNAL → 高风险 → 必须验证
CONFIGURATION → 中风险 → 需验证权限
INTERNAL → 低风险 → 可选验证
```

---

## 常见数据源识别错误

### ❌ 错误1：忽略网络数据

```python
# 错误：只验证HTTP参数，忽略Socket数据
filename = validate(request.args.get('file'))  # 验证了
data = socket.recv(1024)                        # 没验证！
path = data.decode()
```

### ✅ 正确：验证所有外部数据

```python
filename = validate(request.args.get('file'))
data = validate_network(socket.recv(1024))  # 验证网络数据
path = data.decode()
```

### ❌ 错误2：假设环境变量安全

```python
# 错误：环境变量可能被攻击者设置
path = os.getenv('FILE_PATH')  # 攻击者可设置
with open(path, 'r') as f:
    content = f.read()
```

### ✅ 正确：验证环境变量

```python
# 正确：白名单验证环境变量
allowed_paths = {'/etc/app/config.json', '/var/data/config.json'}
path = os.getenv('FILE_PATH', '/etc/app/config.json')

if path not in allowed_paths:
    raise ValueError("非法路径")

with open(path, 'r') as f:
    content = f.read()
```

### ❌ 错误3：忽略跨进程数据

```python
# 错误：假设IPC数据可信
data = ipc_queue.get()
filename = data['path']  # 其他进程可能被攻陷
```

### ✅ 正确：验证跨进程数据

```python
data = ipc_queue.get()
verify_signature(data)  # 验证签名
filename = validate_path(data['path'])
```

---

## 数据源检查清单

```
□ 已识别所有数据入口点
  □ HTTP请求参数
  □ 命令行参数
  □ Socket接收数据
  □ RPC响应
  □ 消息队列
  □ WebSocket消息
  □ IPC通信
  □ 共享内存
  □ 环境变量
  □ 配置文件
  □ 数据库查询

□ 已确定每个数据源的信任边界
  □ 是否跨信任边界？
  □ 是否可被外部控制？
  □ 风险级别？

□ 已实施验证措施
  □ 格式验证
  □ 类型验证
  □ 范围验证
  □ 白名单验证

□ 已记录数据流
  □ 数据源 → 处理 → 使用
  □ 所有中间转换
  □ 所有验证点
```

---

## 参考资料

- OWASP Input Validation: https://owasp.org/www-community/vulnerabilities/Improper_Data_Validation
- CWE-20: Improper Input Validation: https://cwe.mitre.org/data/definitions/20.html
- SEI CERT: Validate Inputs from All Untrusted Sources
