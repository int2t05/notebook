# e2e-auto-optimize

`e2e-auto-optimize` 是一个用于端到端软件库自主性能优化的 Agent skill。它面向系统软件和基础库场景，支持通过 SSH 在远端环境中编译、测试、运行性能用例、解析性能指标，并按提升阈值判断是否采纳优化。

## 主要能力

- 读取统一 JSON 配置文件，默认文件名为 `e2e-auto-optimize.config.json`。
- 检查远端 SSH 可达性、硬件信息和目标 Git 仓库状态。
- 加载领域知识库，先验的性能瓶颈分析结论，perf/topdown数据和用户其他提示。若知识库为空，由Agent自主优化或根据用户选择的几个方向优化。
- 按顺序执行 `commands.build`、`commands.ut`、`commands.perftest`。
- 使用配置中的正则规则解析性能指标并计算提升比例。
- 每轮生成 baseline/optimized 的测试结果和总结报告。
- 只有在编译、功能测试、性能提升阈值都满足时才允许本地 commit。
- 每个被采纳的优化轮次会单独 commit，commit message 使用该轮的 `optimization_overview`，不会把多轮优化压成最后一个 commit。
- 默认不 push、不创建 PR、不修改远端全局 Git 配置。

## 目录说明

- `SKILL.md`：skill 的主说明和执行规则。
- `scripts/e2e_optimize.py`：配置校验、远端检查、指标解析、报告生成和迭代执行脚本。
- `templates/config.example.json`：配置模板。
- `references/`：配置、报告和迭代流程的补充说明。
- `kb/menu.md`：知识库目录文件，默认可为空。具体知识文件由用户放入kb/。

## 快速安装

```bash
npx skills add https://gitcode.com/boostkit/AcclibSkills.git --skill e2e-auto-optimize
```

## 快速使用

找到skill的安装目录,例如~/.agents/skills/e2e-auto-optimize.

```bash
cd <本地待优化库根目录>
```

先复制配置模板并按目标库实际情况填写：

```bash
cp ~/.agents/skills/e2e-auto-optimize/templates/config.example.json e2e-auto-optimize.config.json
```

若要加载知识库,在skill安装好之后,在skill知识库目录中(如~/.agents/skills/e2e-auto-optimize/kb)放入文档和其目录(menu.md)或在配置文件中指定知识库目录。

**直接调用**
```bash
prompt: /e2e-auto-optimize 基于配置文件,执行自动优化
```

**手工确认环境(LLM默认自动调用,无需手工)**

校验配置：

```bash
python scripts/e2e_optimize.py validate-config --config e2e-auto-optimize.config.json
```

检查远端环境：

```bash
python scripts/e2e_optimize.py check-environment --config e2e-auto-optimize.config.json
```

## 关键配置

配置文件中最重要的部分包括：

- `software`：软件名、远端仓库路径、基线 ref。
- `git`：提交使用的 `username` 和 `email`，默认留空。
- `environment`：远端 SSH 地址、端口、用户和认证方式。
- `workspace`：工作目录，测试目录，数据目录，报告目录等。
- `commands`：编译、功能测试和性能测试命令。
- `metric`：性能指标名称、方向和解析正则。
- `analysis`：先验性能分析结论，perf/topdown结果文件地址。
- `optimization`：迭代次数、提升阈值、预选优化方向和知识库路径。
- `note`：其他用户提示。（如优化注意点，编译器信息等）

详细字段说明见 `references/config.md`。

## 报告输出

每轮迭代会生成四类报告：

- `<software>-iterN-base-test-result.md`
- `<software>-iterN-opt-test-result.md`
- `<software>-iterN-base-summary-result.md`
- `<software>-iterN-opt-summary-result.md`

其中 optimized summary 会包含本轮优化内容概述；baseline summary 不包含该字段。

## 安全边界

- 每次迭代必须满足ut完全通过，判断完全通过的方式是：若ut的**exit code = 0**则算作通过，否则不通过，本轮不继续做性能验证。
- 目标仓库有未提交变更时，默认停止。也可以通过提示LLM忽略脏变更或给e2e_optimize.py增加参数`--allow-dirty`。
- 不自动 push。
- 不写入远端全局 Git 配置。
- 不在配置文件中保存明文密码。
- 不采纳未通过编译、测试或性能阈值的优化。
