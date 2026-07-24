# feature-design-doc

读懂一个性能/优化特性的源码,产出一份**图文并茂、可交付**的中文设计文档(Markdown + Word/docx)。

适合"为某个内核/运行时/编译器特性或某个 PR 写系统化设计说明"的场景:既要把需求背景、总体方案、详细设计原理讲透,又要有规整的架构图/原理图/时序图/用例图,还要有验证数据归因和使用用例,并最终输出排版规范的 docx。

## 能力

- **固定章节骨架**:需求分析(原有机制回顾 → 痛点 → 目标 → 约束)→ 总体方案(核心思路 + 构建模型 + 框架图 + 数据流)→ 详细设计(分模块,讲清数据/内存/状态的变换过程)→ 验证效果(方法 + 数据 + 归因)→ 使用与用例。
- **图示分工**:结构/分层/组件/内存布局图用**手绘 SVG 矢量**(规整、网格对齐、配色统一);时序/状态/用例/活动图用 **PlantUML**。
- **黄金写作原则**:每张图、每段代码前有引入、后有解读,杜绝"光秃秃的图/不解释的代码"。
- **严格 docx 排版**:中文宋体五号、英文 Times New Roman 五号、嵌入代码词随正文、整块代码 Consolas、全黑无斜体、单倍行距段后 6 磅。
- **工程归档规范**:图片与文档同级,md + png + 图源(svg/puml)同次提交。
- **中英双语**:可产出同结构、同图序的英文版本,**图内文字也译成英文**(中文在 `docs/`,英文在 `docs/en/`,各带独立 images),英文 docx 正文全 Times New Roman。

## 快速使用

```bash
# 1. 装依赖(cairosvg / python-docx / plantuml.jar / 中英文字体)
bash scripts/setup_env.sh

# 2. 读源码 + 写 docs/<feature>-design.md(章节见 references/doc-structure.md)
#    结构图写成 docs/images/figNN.svg,行为图写成 docs/images/figNN.puml
#    md 用 ![图X-Y 标题](images/figNN.png) 引用

# 3. 渲染所有图为 png
python scripts/render_diagrams.py docs/images

# 4. 生成 docx(排版规范已固化)
python scripts/md_to_docx.py docs/<feature>-design.md

# 5. md + images/*.png + images/*.{svg,puml} 同次提交
```

## 参考文档

- `references/doc-structure.md` — 章节骨架与写作黄金原则(动笔前先读)
- `references/diagram-guide.md` — SVG vs PlantUML 选型、统一风格、引用与归档
- `references/docx-format.md` — docx 字体/颜色/段落/校验细则
- `references/bilingual.md` — 英文/双语版本:图内文字译英、`docs/en/` 布局、交叉链接

## 由来

本技能从一次真实的"鲲鹏 kpmemopt 内存布局优化"特性设计文档实践中抽象而来:逐步收敛出章节骨架、结构图改用 SVG 矢量(对齐 openeuler/compiler-docs 的图风格)、行为图用 PlantUML、以及成套的 docx 排版与归档约束,沉淀为可复用脚本与规范。
