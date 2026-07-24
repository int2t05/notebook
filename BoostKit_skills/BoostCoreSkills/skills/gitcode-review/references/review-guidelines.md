# 代码审查最佳实践指南

本文档提供详细的代码审查指南，帮助进行高质量的代码审查。

## 审查重点领域

### 1. 代码正确性

**检查项**：
- 逻辑是否正确实现了需求
- 边界条件是否处理妥当
- 错误处理是否完善
- 空值/null 检查是否充分

**常见问题**：
- 数组越界
- 空指针引用
- 整数溢出
- 并发竞态条件

### 2. 代码风格和可读性

**检查项**：
- 命名是否清晰有意义
- 代码格式是否一致
- 注释是否必要且准确
- 函数/方法长度是否合理

**最佳实践**：
- 变量名应描述其用途
- 函数名应使用动词
- 避免魔法数字，使用常量
- 复杂逻辑应添加注释

### 3. 性能考虑

**检查项**：
- 算法复杂度是否合理
- 是否有不必要的循环嵌套
- 数据库查询是否优化
- 是否有内存泄漏风险

**常见优化**：
- 使用合适的数据结构
- 避免重复计算
- 批量操作代替单个操作
- 适当使用缓存

### 4. 安全性

**检查项**：
- 输入验证是否充分
- SQL 注入防护
- XSS 防护
- 敏感信息是否加密
- 权限检查是否完善

**安全清单**：
- [ ] 所有用户输入都经过验证
- [ ] 使用参数化查询
- [ ] 输出进行适当转义
- [ ] 敏感数据不在日志中
- [ ] 使用 HTTPS 传输敏感信息

### 5. 测试覆盖

**检查项**：
- 是否有单元测试
- 测试覆盖率是否足够
- 边界条件是否测试
- 错误场景是否测试

**测试建议**：
- 新功能应有对应测试
- Bug 修复应有回归测试
- 关键路径应有集成测试
- 性能敏感代码应有基准测试

## 审查流程建议

### 第一遍：整体理解
- 阅读 PR 描述和相关 Issue
- 了解变更的目的和背景
- 查看整体架构变化

### 第二遍：详细审查
- 逐文件审查代码变更
- 检查逻辑正确性
- 评估代码质量

### 第三遍：交叉检查
- 验证测试覆盖
- 检查文档更新
- 确认无遗漏问题

## 提供反馈的技巧

### 建设性反馈

**好的反馈**：
```
建议使用 `empty()` 替代 `size() > 0`，这更符合 C++ 最佳实践，
且语义更清晰。

// 建议改为
if (!container.empty()) {
    // ...
}
```

**避免的反馈**：
```
这个写法不对。
```

### 分级反馈

使用标签区分问题严重程度：

- **🔴 必须修复**：安全漏洞、严重 bug、破坏性变更
- **🟡 建议修复**：代码质量问题、性能优化、最佳实践
- **🟢 可选优化**：代码风格、微小改进、个人偏好

### 认可优点

不要只指出问题，也要认可做得好的地方：

```
✅ 错误处理很完善，考虑了各种边界情况
✅ 测试覆盖率很好，包含了正常和异常场景
✅ 代码结构清晰，易于理解和维护
```

## 常见代码问题模式

### 1. 资源泄漏

```cpp
// 问题代码
FILE* file = fopen("data.txt", "r");
if (error_condition) {
    return;  // 文件未关闭
}
fclose(file);

// 改进代码
FILE* file = fopen("data.txt", "r");
if (!file) return;

if (error_condition) {
    fclose(file);
    return;
}
fclose(file);

// 更好的方式：使用 RAII
std::ifstream file("data.txt");
if (error_condition) {
    return;  // 自动关闭
}
```

### 2. 并发问题

```python
# 问题代码
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1  # 非原子操作

# 改进代码
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1
```

### 3. SQL 注入

```python
# 问题代码
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# 改进代码
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

### 4. 内存效率

```python
# 问题代码
def process_large_file(filename):
    data = open(filename).read()  # 一次性读取全部
    return process(data)

# 改进代码
def process_large_file(filename):
    with open(filename) as f:
        for line in f:  # 逐行处理
            process(line)
```

## 审查清单

使用此清单确保全面审查：

- [ ] 代码逻辑正确
- [ ] 错误处理完善
- [ ] 命名清晰有意义
- [ ] 代码风格一致
- [ ] 无安全漏洞
- [ ] 性能可接受
- [ ] 有适当的测试
- [ ] 文档已更新
- [ ] 无代码重复
- [ ] 遵循项目约定
- [ ] 向后兼容（如适用）
- [ ] 无调试代码残留

## 特定语言注意事项

### C/C++
- 内存管理（malloc/free, new/delete）
- 指针安全
- 缓冲区溢出
- 未定义行为

### Python
- 异常处理
- 资源管理（with 语句）
- 类型提示
- PEP 8 风格

### JavaScript/TypeScript
- 异步处理（Promise, async/await）
- 类型安全（TypeScript）
- 闭包和作用域
- 事件监听器清理

### Java
- 异常处理
- 资源管理（try-with-resources）
- 并发安全
- 空指针检查

## 总结

高质量的代码审查应该：
1. **全面**：覆盖所有重要方面
2. **建设性**：提供具体改进建议
3. **及时**：尽快完成审查
4. **尊重**：保持专业和友好
5. **教育性**：帮助团队成长
