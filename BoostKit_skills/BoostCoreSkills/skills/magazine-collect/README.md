# magazine-collect

按"月刊收集规则"对**任意技术领域**近 N 个月的动态做汇总，产出中文 digest md。

**设计定位**：LLM-first，零脚本。这个 skill 把"专家阅读流程"封装成 prompt，让 Agent 用 `WebSearch`/`WebFetch` 即可完成抓取-筛选-写作，不依赖任何 Python/Shell 工程产物。

**与领域解耦**：skill 主体不绑定任何具体技术领域。所有领域特定的信息源、筛选关键词、特别关注点、对照对象都在用户提供的规则文件里指定。今天跑编译器，明天换搜推广、数据库、安全、Web3 等任意领域——只换规则文件即可，skill 主体不需要改。

---

## 适用场景

- 给一份规则 md（如 `examples/compiler-magazine-collect.md`，里面分板块写好了信息源 / 筛选类别 / 特别关注点 / 表达方式），让 Agent 按规则做"近 3 个月动态"、"某领域月刊"、"季报"等
- 让 Agent 参照 `examples/llvm-2026-02-23_2026-05-23.md` 的风格做某领域的要闻速览（该示例是编译器领域，但结构与写作 quality bar 适用于任何领域）
- 自己写一份新领域的规则文件时，参照 `examples/compiler-magazine-collect.md` 的字段结构，把每一字段替换为新领域的具体内容

## 使用方式

直接用自然语言调用即可，例如：

```text
按 /home/hxq/workspace/magazine-skills/compiler-magazine-collect.md 的规则跑一遍 LLVM 板块的近 3 个月月刊
```

```text
用 magazine-collect skill，规则文件是 ./recsys-magazine-collect.md，板块只跑"召回"和"排序"
```

```text
做一份数据库领域 2026 Q1 的要闻速览，规则参考 ./db-magazine-collect.md
```

```text
用 magazine-collect 跑一份 2026-05 全板块月刊（mode=magazine），规则文件 ./<your-domain>-magazine-collect.md
```

调用时 Agent 会从你的话里解析以下参数：

| 参数 | 默认值 |
|---|---|
| 规则文件路径 | 必需，问你要 |
| 板块 | 规则文件里的全部板块 |
| 时间窗 | 近 3 个月 |
| 单个源 | 板块下全部源 |
| 模式 | `single`（默认）/ `magazine`（拼月刊）/ `html`（基于已有月刊 md 出 HTML 视觉版） |
| 输出位置 | `<规则文件所在目录>/magazine-collect-output/<领域>-<起始>_<结束>/` |

## 输出位置（领域-窗口 + 板块两级目录）

默认写入 `<规则文件所在目录>/magazine-collect-output/<领域>-<起始>_<结束>/<板块>/<板块-slug>-<起始>_<结束>.md`。

**两级目录的语义**：
- **第一级 `<领域>-<起始>_<结束>/`** 每次跑独立一个"领域+时间窗"根目录——下个月重跑同领域时新窗口自动落到新目录，历史月份产物不会被覆盖，便于跨期对比
- **第二级 `<板块>/`** 把同一领域同一窗口下的多次重跑（`-v2` / `-v3`）聚在同一处

领域 slug 默认从规则文件名 stem 去掉 `-magazine-collect` 后缀推导：
- `compiler-magazine-collect.md` → `magazine-collect-output/compiler-<起始>_<结束>/`
- `recsys-magazine-collect.md` → `magazine-collect-output/recsys-<起始>_<结束>/`
- `db-magazine-collect.md` → `magazine-collect-output/db-<起始>_<结束>/`

调用时可显式指定领域 slug 覆盖默认值。

**重要**：规则文件应该放在仓库根（如 `magazine-skills/<domain>-magazine-collect.md`），这样输出会落在 `magazine-skills/magazine-collect-output/`。**不要**用 skill 自带的 `examples/<...>-magazine-collect.md` 直接跑——那只是字段结构示例，跑起来会把产物写到 skill 内部。

例如跑编译器领域 2026-02-23 ~ 2026-05-23 窗口、用 `mode=magazine`：

```
magazine-skills/magazine-collect-output/compiler-2026-02-23_2026-05-23/
├── llvm/
│   └── llvm-2026-02-23_2026-05-23.md       # 单板块 digest
├── gcc/
│   └── gcc-2026-02-23_2026-05-23.md
├── go/
│   └── go-2026-02-23_2026-05-23.md
├── ai-compiler/
│   └── ai-compiler-2026-02-23_2026-05-23.md
├── ...                                      # 其余 7 个叶子板块
└── magazine-2026-02-23_2026-05-23.md        # 月刊（领域-窗口根下，跨板块汇总）
```

加 `mode=html` 后会在月刊 md 旁多产出一个 `magazine-2026-02-23_2026-05-23.html`（含海报 banner + 边框 + 内联 CSS，可双击浏览器看、复制到邮件正文或上传 wiki）。

换成搜推广领域则是：

```
magazine-skills/magazine-collect-output/recsys-2026-02-23_2026-05-23/
├── recall/
│   └── recall-2026-02-23_2026-05-23.md
├── rank/
│   └── rank-2026-02-23_2026-05-23.md
└── ads/
    └── ads-2026-02-23_2026-05-23.md
```

同名文件存在时自动加 `-v2`、`-v3` 后缀避免覆盖（如 `llvm-2026-02-23_2026-05-23-v2.md`）。月刊 md / HTML 始终落在 `<领域>-<窗口>/` 根下，不进板块子目录。

## 目录结构

```
magazine-collect/
├── SKILL.md                                 # 主入口，Agent 看到的"何时触发 + 工作流"（领域中性）
├── README.md                                # 本文件，人类视角说明
├── references/
│   ├── fetch-strategies.md                  # 各类源抓取策略 + 防爬绕行手册（领域中性的通用策略）
│   ├── output-template.md                   # 输出模板的字段级写作规范（领域中性）
│   ├── aggregate-template.md                # 月刊（mode=magazine）拼接布局规范（领域中性的通用骨架）
│   └── sources-catalog.md                   # 信息源抓取经验沉淀，跑过的源逐步补充，不预设领域占位
└── examples/
    ├── llvm-2026-02-23_2026-05-23.md        # 输出 few-shot：LLVM 板块完整 digest（编译器示例）
    └── compiler-magazine-collect.md         # 输入 few-shot：规则文件结构 + 编译器领域具体填充
```

## 维护建议

- **规则文件不属于 skill 自身**。每个领域一份规则文件（如 `compiler-magazine-collect.md` / `recsys-magazine-collect.md` / `db-magazine-collect.md`），通常放在 `magazine-skills/` 仓库根目录或用户自己的工作目录；`examples/compiler-magazine-collect.md` 仅是字段结构 + 编译器领域示范，新增领域时**新建到仓库根目录**而不是 examples 下，无需改 skill。
- **领域知识沉淀在规则文件**：所有领域特定的关键词（如编译器领域的"鲲鹏 / SVE / Intel / AMD"、搜推广领域的"召回 / 排序 / CTR / 对照平台"）都写在该领域的规则文件"特别关注点"字段里，**不要污染 skill 主体**。
- **新增/修改信息源**：直接编辑领域规则 md。跑完一次后，如果遇到 `references/sources-catalog.md` 没收录的源，回来在最贴近的现有大类下补一行；新领域明显不属任何已有大类，文件末尾新建一个大类即可。
- **抓取策略发现新坑**：更新 `references/fetch-strategies.md`。注意：只往**通用源类型**（项目官方/Weekly/代码仓/邮件列表/学术/公司新闻/技术媒体）里补，不要在该文件里堆具体领域的关键词。
- **输出模板调整**：改 `references/output-template.md` 和 `examples/` 下的样例同步即可。

## 设计取舍

我们刻意**不做**这些事，理由：

| 不做 | 理由 |
|---|---|
| 不写 Python 抓取脚本 | LLM 自带工具够用；脚本一旦写就会面对站点改版/反爬升级，维护成本远大于收益 |
| 不做定时任务 / cron | 月刊频率低（月度/季度），手动触发更可控，没必要自动化 |
| 不发邮件 / 不集成 SMTP | 产物是 md + HTML（`mode=html`），分发由用户自行决定（贴飞书/wiki/邮件均可），skill 不绑死渠道；SMTP 调用是 LLM 工具能力外的事，不做内置 |
| 不做 LLM 评分 / 多档分析流水线 | 同样的目标可以让单次 LLM 综合判断完成，多档分流引入复杂度但收益有限 |
| 不做去重数据库 / 状态持久化 | 月刊是一次性产物，每次重新跑即可；规则文件就是唯一状态 |
| 不为新领域预占位 section / 关键词表 | 领域特定内容应该全部沉淀到该领域的规则文件里，skill 主体只提供领域中性的工作流；预占位会让 skill 主体被特定领域的"既有偏见"污染 |
