# 安全编码示例索引 (Secure Coding Examples Index)

按语言拆分的安全编码示例，扫描时按需加载对应语言文件。

## 语言文件

| 语言 | 文件 | 内容 |
|------|------|------|
| Python | [Secure_Coding_Python.md](./Secure_Coding_Python.md) | 基础路径验证、网络数据验证、用户输入验证、配置文件验证、IPC数据验证、TOCTOU缓解 |
| Java | [Secure_Coding_Java.md](./Secure_Coding_Java.md) | 基础路径验证、用户输入验证、网络数据验证、TOCTOU缓解 |
| C | [Secure_Coding_C.md](./Secure_Coding_C.md) | 基础路径验证、用户输入验证、网络数据验证、TOCTOU缓解 |
| JavaScript | [Secure_Coding_JavaScript.md](./Secure_Coding_JavaScript.md) | 基础路径验证、用户输入验证、网络数据验证 |
| Go | [Secure_Coding_Go.md](./Secure_Coding_Go.md) | 基础路径验证、用户输入验证 |

## 通用验证函数

### 路径穿越检测

```python
def detect_path_traversal(path):
    """检测路径穿越序列"""
    dangerous_patterns = [
        '../',           # Unix父目录
        '..\\',          # Windows父目录
        '..',            # 父目录
        '%2e%2e',        # URL编码
        '%252e%252e',    # 双重URL编码
        '%c0%ae',        # UTF-8编码
        '\x00',          # 空字节
    ]
    
    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in path_lower:
            return True
    
    return False
```

### 路径规范化验证

```python
from pathlib import Path
import os

def validate_path_normalization(base_dir, user_path):
    """验证路径规范化
    
    安全保证：
    1. 使用resolve()规范化路径，解析所有符号链接
    2. 双重边界检查，防止/app/data被/app/data2绕过
    3. 符号链接跳出检测
    """
    base_path = Path(base_dir).resolve()
    target_path = (base_path / user_path).resolve()
    
    base_str = str(base_path)
    target_str = str(target_path)
    
    if target_str != base_str and not target_str.startswith(base_str + os.sep):
        raise ValueError("路径穿越检测")
    
    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError("路径穿越检测")
    
    if target_path.is_symlink():
        real_target = target_path.resolve()
        real_str = str(real_target)
        if real_str != base_str and not real_str.startswith(base_str + os.sep):
            raise ValueError("符号链接跳出基础目录")
    
    return target_path
```

## 安全警告

### TOCTOU竞态条件

所有示例代码都存在Time-of-Check to Time-of-Use (TOCTOU)竞态条件漏洞：

```
时间T1: 程序验证路径 /app/data/file.txt (通过)
时间T2: 攻击者替换 file.txt 为符号链接 -> /etc/passwd
时间T3: 程序读取 /etc/passwd (敏感文件泄露！)
```

各语言的缓解措施见对应语言文件的TOCTOU章节。

### 其他安全注意事项

1. **文件权限**: 验证文件权限，避免权限提升攻击
2. **符号链接**: 始终使用O_NOFOLLOW或检查符号链接
3. **文件描述符泄漏**: 确保在所有路径都关闭文件描述符
4. **错误处理**: 不要泄露敏感信息（如完整路径）在错误消息中
5. **并发访问**: 考虑文件锁定机制
6. **资源限制**: 限制文件大小和读取次数

### 生产环境建议

1. **使用专用安全库**: 如OpenBSD的`openat2()`系统调用
2. **容器化隔离**: 使用容器或沙箱限制文件访问
3. **最小权限原则**: 使用最小必要的文件权限
4. **审计日志**: 记录所有文件访问操作
5. **定期审查**: 定期审查文件访问代码和权限

## 参考资料

- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- CWE-22: Improper Limitation of a Pathname: https://cwe.mitre.org/data/definitions/22.html
- CWE-36: Absolute Path Traversal: https://cwe.mitre.org/data/definitions/36.html
- CWE-59: Improper Link Resolution Before File Access: https://cwe.mitre.org/data/definitions/59.html
- SEI CERT FIO02-C: Canonicalize path names originating from untrusted sources
- SEI CERT FIO05-C: Identify files using their file names only
- TOCTOU Race Conditions: https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use
