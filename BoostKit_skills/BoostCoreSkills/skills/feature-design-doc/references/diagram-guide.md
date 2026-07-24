# 图示形式选择与制作指南

## 核心原则:按图的"性质"选工具

PlantUML 擅长**行为类**图(自动布局对时间轴/泳道友好),但对**结构/分层类**图排版往往松散、不规整。因此:

| 图的性质 | 典型图种 | 用什么 | 原因 |
| --- | --- | --- | --- |
| **行为类** | 时序图、状态图、用例图、活动图、时序波形 | **PlantUML**(`.puml`) | 自动布局适合,改一行就能调 |
| **结构类** | 分层架构、组件/泳道、内存布局、数据流框图、维度分层 | **手绘 SVG**(`.svg`,用 `svglib.py`) | 精确控制坐标,排布规整、网格对齐、配色统一 |

判断口诀:**画的是"谁在什么时间做什么"→ PlantUML;画的是"系统由哪些块组成、内存/数据长什么样"→ SVG。**

## 统一视觉风格(SVG)

参考 openeuler/compiler-docs 的 `sizeclasses_span.png` 风格:白底、网格对齐、对象格用黄色、强调框用蓝/绿/橙、箭头深灰、默认/优化后并排对比。`svglib.py` 已内置这套调色板:

- `NEUTRAL/GRAY` 中性框,`YELLOW` 对象格/高亮,`BLUE/GREEN/ORANGE/PURPLE` 分类强调,`BAND` 泳道底。
- 字体 `WenQuanYi Micro Hei`(中英文 + 标点全覆盖,避免方框)。

## SVG 制作流程

1. 复制 `assets/svg_example.py` 为本文档的 `build_svgs.py`,`import svglib`。
2. 用这些原语拼图:
   - `rect / boxlabel` 画框与带文字的框;`text / lines` 文本;
   - `arrow / plainline` 箭头与线;`cells` 画一排对象格(内存条/sizeclass 条最常用);
   - `Canvas(w,h,title)` 承载,`save(path)` 输出。
3. 把 `.svg` 写进文档的 `images/`,再用 `scripts/render_diagrams.py <images_dir>` 渲染成 `.png`。
4. **布局自检**:子框右/下边界不能超出父框/画布(常见 bug);文字不要互相压盖;留白一致。渲染后务必用图片查看工具核对一遍。

## PlantUML 制作流程

1. 把行为类图写成 `.puml` 文件放进 `images/`(或先内联在草稿 md 里再抽出)。
2. `render_diagrams.py` 会自动给每个 `.puml` 注入 `skinparam defaultFontName "WenQuanYi Micro Hei"` 再渲染,中文不会变方框。
3. 时序图标注每条消息的语义;状态图标清迁移条件;用例图标角色与 `<<include>>`。

## 在文档里如何引用

Markdown 用相对图片引用,且**图片文件夹与文档同级**(否则网页端/本地都断图):

```
docs/
├── <feature>-design.md      # 引用 ![图1-1 ...](images/fig01.png)
└── images/
    ├── fig01.svg  fig01.png   # 结构图:svg 源 + 渲染 png
    ├── fig04.puml fig04.png   # 行为图:puml 源 + 渲染 png
    └── ...
```

- md 里统一写 `![图X-Y 标题](images/figNN.png)`,编号与文档顺序一致。
- **源文件(.svg / .puml)与 .png 一起入库**,保证可复现、可修改。
- 提交时三者(md、images/*.png、images/*.{svg,puml})必须在同一次 commit,缺图会导致仓库无法显示。

## 编号约定

按文档出现顺序 `fig01..figNN`。结构图取 svg、行为图取 puml,但 png 命名连续(便于 `md_to_docx.py` 与正文一一对应)。
