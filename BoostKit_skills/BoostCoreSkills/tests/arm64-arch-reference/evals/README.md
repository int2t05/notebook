# evals — arm64-arch-reference 的评测文件

本目录存放该 skill 的评测用例与结果记录。两类评测：

## 1. 输出正确性评测 — `evals.json`

4 个真实编译器开发场景的查询，每条带可程序化校验的断言（版本/可选强制/汇编模板/门控特性）。
用于确认"用了 skill 后能否从表里给出正确答案"。配套结果见 `benchmark.md`。

| 用例 | 考点 |
| --- | --- |
| bf16-bfdot | FEAT_BF16 版本/可选 + SVE BFDOT 汇编模板与门控 |
| lse-ldadd | LSE LDADD 内存序变体 + 汇编模板 + FEAT_LSE/版本 |
| sve2-match | 由指令反查门控特性 FEAT_SVE2 + 版本 + 汇编模板 |
| sme-fmopa | SME FMOPA 汇编模板 + 门控特性 + SME 版本 |

## 2. 触发评测 — `trigger_evals.json`

20 条查询（10 应触发 / 10 不应触发），用于校准 SKILL.md 的 `description`，
确保真实查询能触发本 skill、而相邻近似请求（写代码、跑测试、其他架构、翻译等）不误触发。

## 3. 结果记录 — `benchmark.md` / `benchmark.json`

输出正确性评测的量化对比（with-skill vs 无 skill 基线）：通过率、耗时、token。

## 如何复跑

> 注：以下脚本来自 skill-creator 插件；评测依赖本机 `claude` CLI（触发评测）。

```bash
SC=~/.claude/plugins/cache/claude-plugins-official/skill-creator/*/skills/skill-creator

# 触发评测（直接用 claude -p 测真实 skill 更准；run_eval 的代理命令在本机已安装同名 skill 时会测不准）
python3 -m scripts.run_eval --eval-set trigger_evals.json \
  --skill-path ~/.claude/skills/arm64-arch-reference --runs-per-query 3

# 输出正确性评测：见 docs/arm64-arch-reference/DESIGN.md 的"验证"一节（with-skill / baseline 子代理对跑 + 聚合）
```

实测结论（详见 `docs/arm64-arch-reference/DESIGN.md`）：触发直测 4/4 正确；输出正确性 with-skill 100% vs 基线 88%。
