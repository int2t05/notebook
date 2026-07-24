---
name: "governance-content-scanner"
description: "Scans web content for open source governance elements (CLA, SIG, Code of Conduct, etc.). Invoke when user requests governance check, CLA/SIG detection, or open source compliance review for web pages."
---

# Open Source Governance Content Scanner

扫描网页内容，检测开源项目治理相关内容，包括 CLA、SIG、行为准则等治理要素。

## 检测范围

### 1. CLA (Contributor License Agreement) 贡献者许可协议

CLA是贡献者与开源项目之间的重要法律协议，用于明确贡献内容的知识产权归属和使用许可。

#### 1.1 CLA 类型检测

| 检测项 | 关键词 | 说明 |
|--------|--------|------|
| CLA 文档 | `Contributor License Agreement`, `CLA`, `contributor-license-agreement` | 贡献者许可协议 |
| DCO | `Developer Certificate of Origin`, `DCO`, `Signed-off-by` | 开发者原创证书 |
| CLA 签署服务 | `ClaHub`, `CLA Assistant`, `EasyCLA`, `cla-bot` | CLA 自动化工具 |

#### 1.2 签署主体类型检测

| 签署类型 | 关键词 | 说明 |
|----------|--------|------|
| 个人CLA | `Individual CLA`, `ICLA`, `个人贡献者协议` | 以个人身份签署 |
| 企业CLA | `Corporate CLA`, `CCLA`, `企业贡献者协议` | 以企业身份签署 |
| 员工CLA | `Employee CLA`, `员工贡献者协议` | 以企业员工身份签署 |

#### 1.3 CLA 内容完整性检测

检测CLA协议是否包含以下必要条款：

| 条款类型 | 关键词 | 说明 | 必要性 |
|----------|--------|------|--------|
| 签署主体信息 | `signer`, `contributor`, `签署者`, `贡献者` | 明确签署者身份信息 | 必需 |
| 著作权授予 | `copyright`, `著作权`, `版权授予` | 授予著作权给项目拥有者 | 必需 |
| 专利权授予 | `patent`, `专利`, `专利许可` | 授予专利权给项目 | 必需 |
| 授权保证 | `warrant`, `保证`, `有权授予` | 签署者保证有权授予许可 | 必需 |
| 原创保证 | `original`, `原创`, `original work` | 保证贡献为原创作品 | 必需 |
| 免责条款 | `disclaimer`, `warranty`, `免责`, `无担保` | 贡献内容免责声明 | 必需 |
| 非原创处理 | `third-party`, `non-original`, `第三方`, `非原创` | 提交非原创作品的处理方法 | 推荐 |
| 通知义务 | `notify`, `notice`, `通知`, `及时通知` | 不准确事实的通知义务 | 推荐 |
| 开源协议声明 | `license`, `许可协议`, `开源协议` | 阐述项目采用的开源协议 | 必需 |

#### 1.4 CLA 检测评分标准

| 评分 | 条件 |
|------|------|
| ⭐⭐⭐⭐⭐ | 包含所有必需条款 + 推荐条款，区分个人/企业签署 |
| ⭐⭐⭐⭐ | 包含所有必需条款，区分个人/企业签署 |
| ⭐⭐⭐ | 包含大部分必需条款 |
| ⭐⭐ | CLA存在但条款不完整 |
| ⭐ | 仅提及CLA但无具体内容 |

### 2. SIG (Special Interest Group) 特别兴趣小组

| 检测项 | 关键词 | 说明 |
|--------|--------|------|
| SIG 组织 | `Special Interest Group`, `SIG`, `sig-` | 特别兴趣小组 |
| 工作组 | `Working Group`, `WG`, `working-group` | 工作组 |
| 兴趣小组列表 | `SIG list`, `SIGs`, `Active SIGs` | SIG 列表页面 |
| SIG 治理 | `SIG Charter`, `SIG Governance` | SIG 章程/治理 |

### 3. Code of Conduct (CoC) 社区行为准则

社区行为准则是开源社区维护健康、包容、安全协作环境的重要文档，明确社区成员的行为规范和违规处理机制。

#### 3.1 行为准则位置检测

| 检测项 | 关键词/路径 | 说明 | 必要性 |
|--------|-------------|------|--------|
| 根目录文件 | `CODE_OF_CONDUCT.md`, `code-of-conduct.md` | 项目根目录，位置显著 | 必需 |
| .github目录 | `.github/CODE_OF_CONDUCT.md` | GitHub标准位置 | 推荐 |
| README链接 | README中包含行为准则链接 | 易于查找 | 必需 |
| 网站导航 | 社区网站导航栏包含链接 | 易于访问 | 推荐 |

#### 3.2 行为准则内容完整性检测

| 检测项 | 关键词 | 说明 | 必要性 |
|--------|--------|------|--------|
| 行为范围 | `行为`, `behavior`, `expected`, ` unacceptable` | 明确适用的行为范围 | 必需 |
| 参与者范围 | `participant`, `member`, `contributor`, `社区成员` | 明确适用的参与者成员范围 | 必需 |
| 违规处罚 | `violation`, `consequence`, `penalty`, `处罚`, `后果` | 明确违规行为如何处罚 | 必需 |
| 举报方式 | `report`, `contact`, `email`, `举报`, `联系方式` | 有合理的举报违规行为的方式 | 必需 |
| 约束措施 | `ban`, `warning`, `timeout`, `kick`, `禁止`, `警告` | 违反准则者的约束措施 | 必需 |
| 回应机制 | `response`, `investigation`, `处理`, `调查` | 社区对举报行为的回应机制 | 必需 |
| 结果公示 | `public`, `announce`, `公示`, `公告` | 对处理结果进行公示 | 推荐 |

#### 3.3 行为准则版本检测

| 版本 | 关键词 | 说明 |
|------|--------|------|
| Contributor Covenant 1.4 | `Contributor Covenant`, `1.4` | 参与者公约1.4版本 |
| Contributor Covenant 2.0 | `Contributor Covenant`, `2.0`, `2.1` | 参与者公约2.0/2.1版本 |
| Mozilla CoC | `Mozilla Community Participation Guidelines` | Mozilla社区参与指南 |
| Ubuntu CoC | `Ubuntu Code of Conduct` | Ubuntu行为准则 |
| Apache Way | `Apache Way`, `Apache Code of Conduct` | Apache行为准则 |

#### 3.4 行为准则评分标准

| 评分 | 条件 |
|------|------|
| ⭐⭐⭐⭐⭐ | 位置显著 + 内容完整 + 使用标准版本 + 有举报和处罚机制 |
| ⭐⭐⭐⭐ | 位置显著 + 内容完整 + 有举报和处罚机制 |
| ⭐⭐⭐ | 位置显著 + 包含基本行为规范 |
| ⭐⭐ | 行为准则存在但位置不显著或内容不完整 |
| ⭐ | 仅提及行为准则但无具体内容 |

### 4. Community Diversity (社区组织多样性)

社区组织多样性是衡量开源项目健康度的重要指标，体现项目的开放性和包容性。主要贡献者来自不同国家或组织，有助于项目获得多元化的视角和更广泛的生态支持。

#### 4.1 贡献者地域多样性检测

| 检测项 | 关键词/指标 | 说明 | 必要性 |
|--------|-------------|------|--------|
| 贡献者国家分布 | `contributors`, `authors`, `地理分布` | 贡献者来自不同国家/地区 | 必需 |
| 时区分布 | `timezone`, `时区`, `地区` | 贡献者时区分布广泛 | 推荐 |
| 语言多样性 | `language`, `语言`, `多语言` | 文档支持多种语言 | 推荐 |

#### 4.2 贡献者组织多样性检测

| 检测项 | 关键词/指标 | 说明 | 必要性 |
|--------|-------------|------|--------|
| 组织分布 | `company`, `organization`, `公司`, `组织` | 贡献者来自不同组织/公司 | 必需 |
| 企业参与度 | `corporate`, `enterprise`, `企业参与` | 多家企业参与贡献 | 推荐 |
| 个人与企业比例 | `individual`, `corporate`, `个人贡献` | 个人与企业贡献者比例合理 | 推荐 |

#### 4.3 多样性指标评估

| 指标 | 计算方式 | 说明 |
|------|----------|------|
| 国家数量 | 统计贡献者所在国家数量 | ≥5个国家为优秀 |
| 组织数量 | 统计贡献者所属组织数量 | ≥3个组织为优秀 |
| 贡献集中度 | 主要贡献者贡献占比 | ≤50%为健康 |
| 新贡献者比例 | 新贡献者占比 | ≥20%为活跃 |

#### 4.4 多样性评分标准

| 评分 | 条件 |
|------|------|
| ⭐⭐⭐⭐⭐ | 贡献者来自≥10个国家 + ≥5个组织 + 贡献集中度≤40% |
| ⭐⭐⭐⭐ | 贡献者来自≥5个国家 + ≥3个组织 + 贡献集中度≤50% |
| ⭐⭐⭐ | 贡献者来自≥3个国家 + ≥2个组织 |
| ⭐⭐ | 贡献者来自≥2个国家或组织 |
| ⭐ | 贡献者主要来自单一国家或组织 |

#### 4.5 多样性数据来源

| 数据来源 | 获取方式 | 说明 |
|----------|----------|------|
| Git提交记录 | 分析提交者邮箱域名 | 推断组织归属 |
| GitHub/GitCode API | 获取用户profile信息 | 包含公司、位置信息 |
| 贡献者文档 | `CONTRIBUTORS`, `AUTHORS` 文件 | 明确列出贡献者信息 |
| 贡献统计页面 | 项目贡献统计页面 | 可视化展示多样性 |

### 5. 其他治理要素

| 检测项 | 关键词 | 说明 |
|--------|--------|------|
| 贡献指南 | `Contributing Guidelines`, `CONTRIBUTING`, `How to Contribute`, `贡献指南`, `贡献路径` | 贡献指南 |

## 扫描工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│           Governance Content Scan Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Fetch Web Content                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 获取网页内容 → 提取文本和链接                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 2: CLA Detection                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 检测 CLA/DCO 相关内容和签署流程                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 3: SIG Detection                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 检测 SIG/工作组 组织结构和活动                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 4: Code of Conduct Detection                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 检测行为准则位置、内容完整性和处罚机制                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 5: Community Diversity Detection                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 检测贡献者地域和组织多样性                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 6: Other Governance Detection                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 检测贡献指南                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 7: Link Analysis                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 分析相关链接 → 检测贡献指南链接                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 8: Generate Report                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 汇总检测结果 → 生成治理要素报告                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 检测模式

### CLA 检测模式

```regex
# CLA 关键词
(?i)(contributor[_-]?license[_-]?agreement|CLA|contributor[_-]?agreement)

# DCO 关键词
(?i)(developer[_-]?certificate[_-]?of[_-]?origin|DCO|signed[_-]?off[_-]?by)

# CLA 服务
(?i)(clahub|cla[_-]?assistant|easycla|cla[_-]?bot|cla[_-]?system)

# 签署主体类型
(?i)(individual[_-]?cla|ICLA|个人贡献者协议|个人CLA)
(?i)(corporate[_-]?cla|CCLA|企业贡献者协议|企业CLA)
(?i)(employee[_-]?cla|员工贡献者协议|员工CLA)

# CLA 必要条款检测
# 签署主体信息
(?i)(signer|contributor|签署者|贡献者信息|签名者)

# 著作权授予
(?i)(copyright|著作权|版权授予|版权许可|grant.*copyright)

# 专利权授予
(?i)(patent|专利权|专利许可|grant.*patent|专利授权)

# 授权保证
(?i)(warrant|保证有权|有权授予|legal.*right|授权权利)

# 原创保证
(?i)(original[_-]?work|原创作品|原创保证|original.*contribution)

# 免责条款
(?i)(disclaimer|warranty|免责声明|无担保|as[_-]?is|no[_-]?warranty)

# 非原创处理
(?i)(third[_-]?party|非原创|第三方代码|external.*code|notice.*required)

# 通知义务
(?i)(notify|notice|及时通知|inform|update.*information)

# 开源协议声明
(?i)(license|许可协议|开源协议|open[_-]?source[_-]?license|under.*license)
```

### SIG 检测模式

```regex
# SIG 关键词
(?i)(special[_-]?interest[_-]?group|SIG|sig[_-]\w+)

# 工作组
(?i)(working[_-]?group|WG|working[_-]?team|task[_-]?force)

# SIG 治理
(?i)(sig[_-]?charter|sig[_-]?governance|sig[_-]?members|sig[_-]?leaders)
```

### Code of Conduct 检测模式

```regex
# 行为准则文件名
(?i)(code[_-]?of[_-]?conduct|CoC|CODE_OF_CONDUCT)

# 行为准则版本
(?i)(contributor[_-]?covenant|参与者公约)
(?i)(mozilla[_-]?community[_-]?participation|ubuntu[_-]?code[_-]?of[_-]?conduct)
(?i)(apache[_-]?way|apache[_-]?code[_-]?of[_-]?conduct)

# 行为范围
(?i)(expected[_-]?behavior|unacceptable[_-]?behavior|行为规范|不当行为)
(?i)(our[_-]?standards|community[_-]?standards|社区标准)

# 参与者范围
(?i)(participant|member|contributor|社区成员|参与者)
(?i)(who[_-]?this[_-]?applies[_-]?to|适用范围)

# 违规处罚
(?i)(violation|consequence|penalty|处罚|后果|违规)
(?i)(enforcement|执行|强制措施)

# 举报方式
(?i)(report|contact|email|举报|联系方式|reporting)
(?i)(how[_-]?to[_-]?report|reporting[_-]?guidelines)

# 约束措施
(?i)(ban|warning|timeout|kick|禁止|警告|封禁)
(?i)(temporary[_-]?ban|permanent[_-]?ban|临时禁言|永久封禁)

# 回应机制
(?i)(response|investigation|处理|调查|回应)
(?i)(we[_-]?will|community[_-]?will|社区将)

# 结果公示
(?i)(public|announce|公示|公告|公开)
(?i)(transparency|透明|公开处理)
```

### Community Diversity 检测模式

```regex
# 贡献者信息
(?i)(contributors|authors|贡献者|参与者列表)
(?i)(all[_-]?contributors|contributor[_-]?list)

# 地域多样性
(?i)(country|国家|region|地区|location|位置)
(?i)(timezone|时区|geo|地理分布)

# 组织多样性
(?i)(company|公司|organization|组织|employer|雇主)
(?i)(corporate|企业|enterprise|business)

# 多样性指标
(?i)(diversity|多样性|inclusivity|包容性)
(?i)(distribution|分布|statistics|统计)

# 贡献统计
(?i)(contribution[_-]?stats|贡献统计|contributor[_-]?stats)
(?i)(insights|洞察|analytics|分析)
```

### 其他治理模式

```regex
# 贡献指南
(?i)(contributing|how[_-]?to[_-]?contribute|contribution[_-]?guidelines|贡献指南|贡献路径)
```

## 链接检测

检测以下常见贡献指南文档路径：

| 文档类型 | 常见路径 |
|----------|----------|
| CLA | `/cla`, `/CONTRIBUTING`, `/doc/cla`, `/.github/CLA` |
| 行为准则 | `/CODE_OF_CONDUCT`, `/code-of-conduct`, `/.github/CODE_OF_CONDUCT` |
| 贡献指南 | `/CONTRIBUTING`, `/contributing`, `/.github/CONTRIBUTING` |

## 报告格式

```markdown
# 开源治理内容扫描报告

## 扫描信息
- **扫描目标**: <URL>
- **扫描时间**: <时间戳>
- **页面标题**: <标题>

## 检测结果摘要

| 治理要素 | 检测状态 | 详情 |
|----------|----------|------|
| CLA/DCO | ✅ 已找到 / ❌ 未找到 | <详情> |
| SIG/工作组 | ✅ 已找到 / ❌ 未找到 | <详情> |
| 行为准则 | ✅ 已找到 / ❌ 未找到 | <详情> |
| 社区多样性 | ✅ 已找到 / ❌ 未找到 | <详情> |
| 贡献指南 | ✅ 已找到 / ❌ 未找到 | <详情> |

## 详细发现

### 1. CLA (Contributor License Agreement)

**状态**: ✅ 已检测到

**评分**: ⭐⭐⭐⭐⭐

**签署类型**:
| 类型 | 状态 | 签署链接 |
|------|------|----------|
| 个人CLA (ICLA) | ✅ 支持 | [签署链接] |
| 企业CLA (CCLA) | ✅ 支持 | [签署链接] |
| 员工CLA | ✅ 支持 | [签署链接] |

**条款完整性检测**:
| 条款类型 | 检测状态 | 说明 |
|----------|----------|------|
| 签署主体信息 | ✅ 已包含 | 明确签署者身份信息 |
| 著作权授予 | ✅ 已包含 | 授予著作权给项目拥有者 |
| 专利权授予 | ✅ 已包含 | 授予专利权给项目 |
| 授权保证 | ✅ 已包含 | 签署者保证有权授予许可 |
| 原创保证 | ✅ 已包含 | 保证贡献为原创作品 |
| 免责条款 | ✅ 已包含 | 贡献内容免责声明 |
| 非原创处理 | ✅ 已包含 | 提交非原创作品的处理方法 |
| 通知义务 | ✅ 已包含 | 不准确事实的通知义务 |
| 开源协议声明 | ✅ 已包含 | 项目采用的开源协议 |

**开源协议**: Apache-2.0 / MIT / GPL-3.0 / ...

**相关链接**: [CLA 文档](...)

### 2. SIG (Special Interest Group)

**状态**: ✅ 已检测到

**发现内容**:
- SIG 数量: X 个
- SIG 列表:
  - sig-architecture: 架构组
  - sig-network: 网络组
  - ...
- 相关链接: [SIG 列表](...)

### 3. Code of Conduct (社区行为准则)

**状态**: ✅ 已检测到

**评分**: ⭐⭐⭐⭐⭐

**位置检测**:
| 检测项 | 状态 | 说明 |
|--------|------|------|
| 根目录文件 | ✅ 已找到 | 位置显著，易于查找 |
| README链接 | ✅ 已包含 | 易于阅读 |
| 网站导航 | ✅ 已包含 | 易于访问 |

**内容完整性检测**:
| 检测项 | 状态 | 说明 |
|--------|------|------|
| 行为范围 | ✅ 已明确 | 明确适用的行为范围 |
| 参与者范围 | ✅ 已明确 | 明确适用的参与者成员范围 |
| 违规处罚 | ✅ 已明确 | 明确违规行为如何处罚 |
| 举报方式 | ✅ 已提供 | 有合理的举报违规行为的方式 |
| 约束措施 | ✅ 已提供 | 违反准则者的约束措施 |
| 回应机制 | ✅ 已明确 | 社区对举报行为的回应机制 |
| 结果公示 | ✅ 已明确 | 对处理结果进行公示 |

**版本信息**:
- 使用版本: Contributor Covenant 2.0
- 版本链接: [https://www.contributor-covenant.org/version/2/0/](https://www.contributor-covenant.org/version/2/0/)

**相关链接**: [CODE_OF_CONDUCT.md](...)

### 4. Community Diversity (社区组织多样性)

**状态**: ✅ 已检测到

**评分**: ⭐⭐⭐⭐⭐

**地域多样性检测**:
| 检测项 | 状态 | 数值 | 说明 |
|--------|------|------|------|
| 贡献者国家数量 | ✅ | 12 | 贡献者来自12个国家 |
| 时区分布 | ✅ | 8个时区 | 覆盖主要时区 |
| 语言支持 | ✅ | 3种语言 | 文档支持多语言 |

**组织多样性检测**:
| 检测项 | 状态 | 数值 | 说明 |
|--------|------|------|------|
| 参与组织数量 | ✅ | 6 | 6个组织参与贡献 |
| 企业参与度 | ✅ | 4家企业 | 多家企业参与 |
| 个人与企业比例 | ✅ | 40:60 | 比例合理 |

**多样性指标**:
| 指标 | 数值 | 评估 | 说明 |
|------|------|------|------|
| 国家数量 | 12 | ⭐⭐⭐⭐⭐ | ≥10个国家，优秀 |
| 组织数量 | 6 | ⭐⭐⭐⭐⭐ | ≥5个组织，优秀 |
| 贡献集中度 | 35% | ⭐⭐⭐⭐⭐ | ≤40%，健康 |
| 新贡献者比例 | 25% | ⭐⭐⭐⭐ | ≥20%，活跃 |

**主要贡献组织**:
| 组织 | 贡献者数量 | 贡献占比 | 国家/地区 |
|------|------------|----------|-----------|
| 组织A | 15 | 30% | 中国 |
| 组织B | 10 | 20% | 美国 |
| 组织C | 8 | 16% | 德国 |
| 个人贡献者 | 17 | 34% | 多国 |

**相关链接**: [Contributors](...), [Insights](...)

### 5. 其他治理要素

| 要素 | 状态 | 位置/链接 |
|------|------|-----------|
| 贡献指南 | ✅ | [CONTRIBUTING.md](...) |

## 治理成熟度评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 贡献流程 | ⭐⭐⭐⭐⭐ | CLA + 贡献指南完善 |
| 社区组织 | ⭐⭐⭐⭐ | SIG 结构清晰 |
| 行为规范 | ⭐⭐⭐⭐⭐ | 行为准则完善 |
| 社区多样性 | ⭐⭐⭐⭐⭐ | 贡献者来自多国家多组织 |

**总体评分**: ⭐⭐⭐⭐ (4/5)

## 建议

1. ✅ CLA 机制完善，建议保持
2. ✅ SIG 组织结构清晰
3. ✅ 社区多样性良好，贡献者来自多个国家和组织
```

## 使用示例

### 示例 1: 扫描开源社区页面

```
User: 扫描 https://kubernetes.io/community/ 的治理内容
Action:
1. 获取页面内容
2. 检测 CLA/SIG 等治理要素
3. 分析相关链接
4. 生成治理报告
```

### 示例 2: 扫描项目仓库页面

```
User: 检查 https://github.com/apache/kubernetes 是否有完善的治理结构
Action:
1. 获取 README 和社区页面
2. 检测贡献指南链接
3. 检测 CLA/DCO 配置
4. 生成治理评估报告
```

### 示例 3: 批量扫描多个页面

```
User: 扫描以下项目的治理内容：
- https://openeuler.org/zh/community/
- https://www.openeuler.org/zh/community/committee.html
- https://gitee.com/openeuler/community

Action:
1. 逐个获取页面内容
2. 检测各治理要素
3. 汇总生成综合报告
```

## 常见开源社区治理模式

### Kubernetes 模式
- SIG 组织结构
- KEPC 提案流程
- Contributor Ladder

### Apache 模式
- PMC 治理
- Apache Way
- 投票机制

### CNCF 模式
- TOC (Technical Oversight Committee)
- Sandbox/Incubating/Graduated
- 项目生命周期

### openEuler 模式
- 技术委员会
- SIG 组
- 社区选举

## 注意事项

1. **内容获取**: 使用 WebFetch 工具获取网页内容
2. **编码处理**: 注意处理不同编码的网页
3. **动态内容**: 部分内容可能通过 JavaScript 加载，需要特殊处理
4. **链接验证**: 检测到的链接需要验证是否可访问
5. **误报排除**: 排除示例、测试内容中的误报
