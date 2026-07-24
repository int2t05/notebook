# 远程编译说明

## 执行编译

```bash
./remote_exec.sh -t compile
```

## 编译内容

该任务编译 OmniOperator 和 Gluten 两个组件：

1. **OmniOperator (C++ + Java)**
   - 执行 `bash build_scripts/build.sh release:java`
   - 进入 `bindings/java` 目录执行 Maven 构建

2. **清理旧产物**
   - 删除 `$OMNI_HOME/lib` 下的旧编译产物（`libboostkit-omniop-*`, `boostkit-omniop-*`, `include`）

## 远程环境要求

- CMake、GCC
- Maven（用于 Java 绑定编译）
- 目标路径：`/home/omni/OmniOperator`

## 注意事项

- 编译时间较长，请耐心等待
- 编译完成后会输出耗时统计
- 如果编译失败，检查远程服务器的依赖是否完整
