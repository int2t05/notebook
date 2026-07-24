# docx 输出格式规范

`scripts/md_to_docx.py` 已把下述约束固化在代码里。本文件解释这些约束,便于排错或按需微调。**不要在未被要求时放宽这些约束。**

## 字体

| 内容 | 字体 | 字号 |
| --- | --- | --- |
| 中文正文 | 宋体 | 五号(10.5pt) |
| 英文 / 数字正文 | Times New Roman | 五号(10.5pt) |
| 嵌入正文的 `代码词` | 与正文同字体(中宋体/英 Times New Roman) | 五号 |
| 完整代码块 | Consolas | 9pt(浅灰底单元格) |
| 标题 | 中宋体 / 英 Times New Roman,加粗 | H1 16 / H2 14 / H3 12 / H4 11 |

要点:
- **嵌入正文的反引号代码词不单独用等宽字体**,与正文统一观感;只有整段 ``` 代码块才用 Consolas。
- 通过同时设置 `w:rFonts` 的 `eastAsia`(宋体)与 `ascii/hAnsi`(Times New Roman),实现"中文宋体、英文 Times New Roman"的混排。

## 颜色与字形

- **字体一律自动黑色**(`RGBColor(0,0,0)`),不得出现彩色字体——包括标题(去掉 Word 默认蓝)、内联代码(去掉红)、题注/引用(去掉灰)。
- **不使用斜体**(所有 run 强制 `italic=False`)。
- 表格表头、代码块底纹是"单元格背景色"(浅灰),不属于"字体颜色",保留;它不违反"字体黑色"约束。

## 段落

- **单倍行距**(`line_spacing=1.0`, rule=SINGLE)。
- **段后 6 磅**,段前 0;标题段前后各 6 磅。
- 这些设在 `Normal` 样式上,所有正文段落继承。

## 校验方法

生成后用 python-docx 自检(应满足:无非黑 run、无斜体 run、正文段落英文仅 Times New Roman、代码块才有 Consolas):

```python
from docx import Document
from docx.oxml.ns import qn
d = Document("out.docx")
bad = italic = 0
for p in d.paragraphs:
    for r in p.runs:
        c = r.font.color
        if c and c.rgb is not None and str(c.rgb) != "000000": bad += 1
        if r.italic: italic += 1
print("non-black:", bad, "italic:", italic)   # 都应为 0
```

## 图片嵌入

- md 里的 `![cap](images/figNN.png)` 会被解析并居中插入对应 PNG,下方加灰底小号题注(题注本身也是黑色)。
- 图片宽度按 PNG 像素自适应到页面宽度(约 6.3 inch 上限);PNG 建议 2x 渲染以保证清晰。
- 图片路径相对 md 所在目录解析;也可用 `--images-base DIR` 指定。
