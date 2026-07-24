---
name: feature-design-doc
description: 阅读某个性能/优化特性的源码,产出一份图文并茂、可交付的设计文档(Markdown + Word/docx),支持中文、英文或中英双语。适用场景:用户说"读一下 XX 特性/优化的代码并写一份设计文档""为这个 PR/commit 写设计文档""生成含框架图、原理图、时序图、用例图的设计说明""把这个特性整理成 docx 设计文档""再出一份对应英文版的文档和图片""做成中英双语"等。无论用户是否点名"设计文档",只要意图是"理解一段特性代码并系统化产出含架构图/原理图/验证数据/用例的说明文档",都应使用本技能;要英文/双语版时同样用它(图内文字也会译成英文)。它固化了章节骨架、结构图用 SVG 矢量、行为图用 PlantUML 的图示策略、严格的 docx 排版(中文宋体五号/英文 Times New Roman 五号/全黑无斜体/单倍行距段后6磅)、英文版正文全 Times New Roman、以及"图片与文档同级归档、同次提交"的工程规范。
---

# 特性设计文档生成

把"读懂一个特性的源码 → 产出规范、图文并茂、可交付的设计文档"这件事标准化。产物是一份中文 Markdown 设计文档,外加一份排版规范的 Word(.docx),其中所有图都以图片内嵌。

## 何时用本技能

当用户要求"阅读某特性/优化的代码并写设计文档""为某 PR/commit 出设计说明""生成含框架图/原理图/时序图/用例图的文档""把特性整理成 docx"时。核心信号是:**需要先理解一段特性代码,再系统化地把它的需求、方案、详细设计、验证、用法讲清楚。**

## 工作流总览

1. **环境准备**:`bash scripts/setup_env.sh`(装 cairosvg/python-docx/pillow、下载 plantuml.jar 与中英文字体)。
2. **精读源码**:把特性涉及的所有文件读全——构建开关、生成的表/常量、运行时主体、汇编、测试。弄清"改之前 vs 改之后"。
3. **写 Markdown**:按 `references/doc-structure.md` 的骨架写,牢记**黄金原则:每图每代码前有引入、后有解读**。
4. **作图**:按 `references/diagram-guide.md` 选型——结构/分层/组件/内存布局图用 SVG(`scripts/svglib.py` + `assets/svg_example.py`),时序/状态/用例/活动图用 PlantUML。源文件(.svg/.puml)写进文档同级的 `images/`。
5. **渲染**:`python scripts/render_diagrams.py <doc>/images`,把所有 `.puml`/`.svg` 渲成 `.png`。
6. **生成 docx**:`python scripts/md_to_docx.py <doc>.md`,严格遵守 `references/docx-format.md` 的排版。
7. **归档与提交**:md、images/*.png、images/*.{svg,puml} 同级、同次 commit;按目标仓库流程提交并(如需)发 PR。

## 关键规范(必须遵守)

### 文档质量
- **有图、有代码就必有文字**:禁止光秃秃的图或不解释的代码块。详细设计以文字讲原理、讲设计思路为主,图与代码为佐证。详见 `references/doc-structure.md`。
- **详细设计要讲"变换过程"**:重点画清楚数据/内存/状态"从 A 到 B 怎么变"(如 span 怎样被切分、填充、回收、放大),多画原理图,而不是只贴代码。
- **验证要归因**:不能只贴 benchstat 数字,要逐项解释为什么、哪项受益最大/回退,并给总结;基线选择要诚实(对照只差被测特性本身)。
- **与源码交叉验证**:文中常量名/函数名/文件名必须与代码一致,不臆造数据。

### 图示策略(见 `references/diagram-guide.md`)
- **结构类 → SVG**(分层架构、组件/泳道、内存布局、数据流、维度分层):用 `svglib.py` 精确排布,网格对齐、配色统一(参考 sizeclasses_span 风格)。
- **行为类 → PlantUML**(时序、状态、用例、活动、波形):自动布局更合适。
- 自检:SVG 子框不得超出父框/画布,文字不压盖;渲染后用图片查看核对。

### docx 排版(见 `references/docx-format.md`,已固化在 md_to_docx.py)
- 中文宋体五号、英文 Times New Roman 五号;嵌入正文的代码词与正文同字体,仅整块代码用 Consolas。
- 字体一律自动黑色、不用斜体;单倍行距、段后 6 磅。

### 归档规范
- 图片文件夹与文档**同级**(`docs/images/` 紧挨 `docs/xxx.md`),md 用相对引用 `images/figNN.png`。
- **md + 渲染 png + 图源(svg/puml)三者同一次提交**,缺图会导致仓库无法显示图片。

### 英文 / 双语版本(见 `references/bilingual.md`)
当用户要"英文版""对应英文文档""双语"时,产出与中文版**同结构、同图序**的英文版本——**图内文字也要译成英文**(不是只翻正文):
- **布局**:中文在 `docs/<feature>-design.md` + `docs/images/`;英文放 `docs/en/<feature>-design.md` + `docs/en/images/`,两套图各自独立(英文图在 en/images)。
- **图片**:结构图复制 svg 生成器、把标注换成英文重渲染;行为图复制 puml、把文字换成英文重渲染(`render_diagrams.py` 对 en/images 再跑一次)。图序 `figNN` 与中文版一一对应,正文引用同名。
- **docx**:英文版正文全 `Times New Roman` 五号(无中文则宋体不生效),其余排版约束不变;`md_to_docx.py` 直接可用。
- 中英文档互相加一行交叉链接(`> 中文版见 …` / `> English: …`)。

## 目录与脚本

```
feature-design-doc/
├── SKILL.md
├── scripts/
│   ├── setup_env.sh        # 一键装依赖(cairosvg/python-docx/plantuml.jar/CJK 字体)
│   ├── svglib.py           # SVG 原语库(Canvas/rect/cells/arrow/调色板)
│   ├── render_diagrams.py  # images 目录里 *.puml→png(plantuml)、*.svg→png(cairosvg)
│   └── md_to_docx.py       # Markdown→docx,内嵌图片,固化排版规范
├── references/
│   ├── doc-structure.md    # 章节骨架 + 写作黄金原则(先读这个)
│   ├── diagram-guide.md    # SVG vs PlantUML 选型、风格、引用与归档
│   ├── docx-format.md      # docx 字体/颜色/段落/校验细则
│   └── bilingual.md        # 英文/双语版本:图内文字也译英、en/ 布局、交叉链接
└── assets/
    └── svg_example.py      # 用 svglib 画分层架构 / 默认vs优化对比 的起手示例
```

按需读取:动笔前先读 `references/doc-structure.md`;作图时读 `references/diagram-guide.md`;生成 docx 前读 `references/docx-format.md`;做英文/双语版本时读 `references/bilingual.md`。
