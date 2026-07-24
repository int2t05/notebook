# 检查清单

## A. patch 分析清单

- patch 修改了哪些文件
- 是否新增源码文件
- 是否修改 `CMakeLists.txt`
- 是否新增系统变量、状态变量
- 是否修改 prepared statement、optimizer、executor、parser 路径
- 是否新增 `mysql-test` 用例和 `.result`

## B. 版本差异清单

- 目标版本文件是否存在
- 函数签名是否一致
- 类成员是否一致
- helper 是否改名
- include 是否不同
- cleanup / destroy / reset 生命周期是否一致
- SHOW_FUNC / PSI / sysvar 注册方式是否一致

## C. 人工修复优先级

1. 缺 include
2. 缺声明
3. 缺成员
4. 缺 helper
5. 生命周期挂点位置不同
6. 测试基线不同
7. 构建系统差异
8. 运行时库差异

## D. 编译前自检

- 所有 `.rej` 是否已处理
- 是否残留 `.orig`
- 新文件是否已加入构建系统
- 新增符号是否都有声明和定义
- 调整过的 helper 是否与旧版本 API 对齐

## E. 启动前自检

- `LD_LIBRARY_PATH` 是否覆盖编译器运行库
- 是否使用独立 datadir
- socket / port 是否冲突
- `log-error`、`pid-file`、`tmpdir` 是否可写

## F. 功能验证清单

- `mysqld --version`
- `mysqladmin ping`
- `SHOW VARIABLES LIKE 'patch_related%'`
- `SHOW STATUS LIKE 'patch_related%'`
- 至少一条核心 SQL 路径
- 至少一次复用/命中/回归行为验证
- 若用户给出 sysbench 命令，尽量跑缩小版复现路径

## G. patch 产出清单

- 不包含 build 目录
- 不包含二进制
- 不包含临时文件
- patch 名称符合仓库现有编号习惯
- 若替换旧 patch，确认文件名和序号符合分支约定
