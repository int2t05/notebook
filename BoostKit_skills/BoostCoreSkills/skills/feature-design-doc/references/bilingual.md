# 英文 / 双语版本生成指南

当用户要"英文版""对应英文文档""双语"时,目标是产出一份与中文版**同结构、同图序、同数据**的英文文档,且**图内文字也译成英文**(常见错误:只翻正文、图还是中文)。

## 目录布局

中英分目录,各自带独立的 images(因为图是两套不同语言的 PNG):

```
docs/
├── <feature>-design.md          # 中文,引用 images/figNN.png
├── <feature>-design.docx
├── images/                      # 中文图:figNN.{svg,puml,png}
│   └── ...
└── en/
    ├── <feature>-design.md      # 英文,引用 images/figNN.png(指 en/images)
    ├── <feature>-design.docx
    └── images/                  # 英文图:figNN.{svg,puml,png}
        └── ...
```

- 英文 md 里图片仍写 `![Fig.X-Y ...](images/figNN.png)`,相对 `docs/en/` 解析到 `docs/en/images/`。
- 图序 `figNN` 与中文版严格一一对应(同一张图的中英两版同号),方便对照与维护。

## 图片英文化(关键)

不要把中文 PNG 直接搬过去。对两类图分别处理:

1. **结构图(SVG)**:复制中文的 svg 生成器为 `build_svgs_en.py`,把每个 `text/lines/boxlabel/title` 的中文标注逐一改成英文,输出到 `docs/en/images/`。`svglib.py` 的 `WenQuanYi Micro Hei` 字体同样能渲染纯英文(无需换字体)。
2. **行为图(PlantUML)**:复制中文 `figNN.puml` 到 `docs/en/images/`,把 `title`、participant 名、消息文字、note 全部译英;保留 `skinparam defaultFontName`。

然后对英文图目录跑一次渲染:

```bash
python scripts/render_diagrams.py docs/en/images
```

注意:`.puml` 里若用中文做状态/participant 的**标识符**(如 `空闲页 -->`),英文版要换成 ASCII 标识符(如 `FreePages -->`),否则 PlantUML 状态图可能解析异常;显示文字用 `state "Free pages" as FreePages` 或直接英文标识。

## 正文翻译

- 忠实翻译,不增删技术内容;常量名/函数名/文件名(`pageNumberMultiplier`、`mallocgc`、`sizeclasses.go` 等)保持原样不译。
- 表格、benchstat 数据原样保留(数字不变),仅译表头与说明文字。
- 保持"有图有代码必有文字"的黄金原则:每张英文图前后的引入与解读也要翻译到位。

## docx

英文版正文没有 CJK 字符,`md_to_docx.py` 会让 `Times New Roman` 生效(eastAsia 宋体不命中即可);其余约束(全黑、无斜体、单倍行距段后 6 磅、整块代码 Consolas)不变,直接:

```bash
python scripts/md_to_docx.py docs/en/<feature>-design.md
```

## 交叉链接与提交

- 中文文档顶部加一行 `> English: en/<feature>-design.md`;英文文档加 `> 中文版见 ../<feature>-design.md`。
- 英文 md + docx + en/images 下的 png 与图源(svg/puml)**同一次提交**,与中文版同样遵守"缺图即断"的归档规范。
