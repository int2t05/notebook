# 远程单元测试说明

## 执行测试

```bash
./remote_exec.sh -t ut
```

## 测试内容

执行 OmniOperator 全量单元测试，运行二进制 `/home/omni/OmniOperator/build/core/test/omtest`。

## 远程环境要求

- 编译产物已存在：`/home/omni/OmniOperator/build/core/test/omtest`
- 相关动态库已部署到 `$OMNI_HOME/lib`

## 注意事项

- 执行前请先完成编译（`./remote_exec.sh -t compile`）
- 环境变量与编译任务一致（`OMNI_HOME`, `LD_LIBRARY_PATH` 等）
- 测试输出直接打印到终端，失败用例会有详细错误信息
