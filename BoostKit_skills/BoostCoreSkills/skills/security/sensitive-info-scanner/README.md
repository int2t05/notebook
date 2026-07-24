# sensitive-info-scanner

`sensitive-info-scanner` 是一个用于代码敏感信息泄露检测的 Agent skill。它面向代码安全审计场景，支持扫描代码仓库中的 API 密钥、密码、令牌、企业内部数据和个人隐私信息（PII），并提供低误报率的检测结果。

## 主要能力

- **API 密钥与凭证检测**：识别 AWS、Azure、GCP、GitHub、GitLab、Slack、Stripe 等主流平台的 API Key 和 Secret。
- **认证凭证检测**：发现硬编码密码、数据库连接串、私钥、JWT Token、OAuth Token、Session Secret。
- **加密密钥与 IV/Salt 检测**：识别硬编码的加密密钥、初始化向量、盐值、PGP 密钥块和 SSH 公钥。
- **企业专属模式检测**：识别工号、DTS 单号、华为关键字/邮箱/内部域名/Git 仓库/认证信息等企业内部敏感数据。
- **个人隐私信息（PII）检测**：覆盖中国身份证、银行卡、护照、驾驶证、社保、医保、军官证、港澳/台湾通行证、手机号等证件信息，以及美国 SSN、英国 NINO、日本 My Number、韩国 RRN、新加坡 NRIC、香港身份证等国际证件。
- **网络与基础设施检测**：识别内网 IP、带凭证的 URL、内部服务端点。
- **配置与环境变量检测**：发现 `.env` 文件、Docker Registry、Kubernetes Secret、Terraform 变量中的敏感信息。
- **多语言特定模式**：针对 Python、Java、JavaScript/TypeScript、Go、C/C++、Lua 提供语言级别的敏感信息检测模式。
- **Git 历史扫描**：扫描 Git 提交历史中泄露的敏感信息。
- **误报抑制**：通过上下文约束、排除规则和验证规则（长度/格式/上下文/重复检查）降低误报率。

## 目录说明

- `SKILL.md`：skill 的主说明，包含全部检测规则、扫描命令和工作流程。

## 快速安装

```bash
npx skills add https://gitcode.com/boostkit/AcclibSkills.git --skill sensitive-info-scanner
```

## 快速使用

找到 skill 的安装目录，例如 `~/.agents/skills/sensitive-info-scanner`。

**直接调用**

```
prompt: /sensitive-info-scanner 扫描当前代码仓库中的敏感信息
```

**指定扫描目标**

```
prompt: /sensitive-info-scanner 扫描 /path/to/project 目录下的敏感信息泄露
```

## 检测类别一览

| 类别 | 检测内容 | 典型模式 |
|------|----------|----------|
| API 密钥与凭证 | AWS/Azure/GCP/GitHub/GitLab/Slack/Stripe 等 | `AKIA...`, `ghp_...`, `glpat-...`, `sk_live_...` |
| 认证凭证 | 密码、连接串、私钥、JWT、OAuth | `password=...`, `-----BEGIN PRIVATE KEY-----`, `eyJ...` |
| 加密密钥 | AES/DES 密钥、IV/Salt、PGP/SSH 密钥 | `secret_key=...`, `-----BEGIN PGP...` |
| 企业专属 | 工号、DTS 单号、华为邮箱/域名/Git/认证 | `A00123456`, `@huawei.com`, `git.huawei.com` |
| 个人隐私（中国） | 身份证、银行卡、护照、驾驶证、社保、医保、军官证、通行证、手机号 | `110101199001011234`, `622202...`, `E12345678` |
| 个人隐私（国际） | 美国 SSN、英国 NINO、日本 My Number、韩国 RRN、新加坡 NRIC、香港身份证 | `123-45-6789`, `S1234567A` |
| 网络与基础设施 | 内网 IP、带凭证 URL、内部端点 | `192.168.x.x`, `ftp://user:pass@...` |
| 配置与环境 | .env、Docker Registry、K8s Secret、Terraform | `SECRET=...`, `kind: Secret` |

## 扫描模式

### 快速扫描

扫描所有源文件中的密码、密钥、令牌等关键词：

```bash
grep -rnE "(password|secret|token|key|credential)" \
  --include="*.py" --include="*.java" --include="*.js" --include="*.ts" \
  --include="*.go" --include="*.c" --include="*.cpp" . \
  | grep -v "test\|spec\|example\|sample\|mock"
```

### 深度扫描

包含所有模式的全面扫描，覆盖配置文件和环境变量：

```bash
grep -rnE "(?i)(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)" \
  --include="*.py" --include="*.java" --include="*.js" --include="*.ts" \
  --include="*.go" --include="*.c" --include="*.cpp" --include="*.yaml" \
  --include="*.yml" --include="*.json" --include="*.properties" --include="*.env" . \
  | grep -v "^\s*#\|^\s*//\|test\|spec\|example"
```

### 企业敏感信息扫描

针对企业内部工号、邮箱、域名等：

```bash
# 工号扫描
grep -rnE "\b[a-zA-Z]00[0-9]{6}\b|\b[wW][xX][0-9]{7}\b|\bDTS[0-9]{13}\b" \
  --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.go" .

# 华为相关信息扫描
grep -rnE "(?i)(huawei|hwc|hw)[_-]?(password|token|secret|key|credential)" \
  --include="*.py" --include="*.java" --include="*.yaml" --include="*.properties" .

# 华为邮箱扫描
grep -rnE "[\w.-]+@(huawei|huaweicloud|hicloud)\.(com|cn)" \
  --include="*.py" --include="*.java" --include="*.md" .
```

### PII 扫描

针对个人隐私数据的专项扫描：

```bash
# 中国身份证号
grep -rnE "\b[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]\b" \
  --include="*.py" --include="*.java" --include="*.csv" --include="*.json" .

# 银行卡号
grep -rnE "\b[0-9]{16,19}\b" --include="*.csv" --include="*.json" . | grep -iE "(card|bank|account|卡|账号)"

# 手机号码
grep -rnE "\b1[3-9][0-9]{9}\b" --include="*.py" --include="*.java" --include="*.csv" --include="*.json" .

# 综合PII扫描（身份证+银行卡+手机号）
grep -rnE "(\b[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]\b|\b1[3-9][0-9]{9}\b|\b[0-9]{16,19}\b)" \
  --include="*.py" --include="*.java" --include="*.csv" --include="*.json" .
```

### Git 历史扫描

扫描 Git 提交历史中泄露的敏感信息：

```bash
# 扫描当前分支历史
git log -p | grep -E "(password|secret|token|key).*=.*['\"][^'\"]+['\"]"

# 扫描所有分支
git log --all -p | grep -E "(password|secret|token|key).*=.*['\"][^'\"]+['\"]"
```

## 误报抑制策略

### 上下文约束

仅在以下上下文中触发检测：
- 赋值语句（`=`, `:`, `=>`）
- 配置文件（`.env`, `.yaml`, `.json`, `.properties`）
- 环境变量设置
- 函数参数中的凭证

### 排除规则

自动排除以下情况：
- 注释行（`#`, `//`, `*`）
- 示例/文档（`example`, `sample`, `test`, `mock`, `dummy`, `placeholder`）
- 变量名声明（非赋值）
- 空值（`null`, `None`, `""`）

### 验证规则

对匹配结果进行四重验证：
1. **长度检查**：密钥/密码至少 8 字符
2. **格式检查**：符合预期的格式模式
3. **上下文检查**：排除测试文件和示例代码
4. **重复检查**：同一值多次出现可能是占位符

## 扫描工作流程

```
Step 1: 语言检测 → 识别文件类型，选择语言特定模式
    ↓
Step 2: 通用模式扫描 → API Key、密码、令牌、私钥等
    ↓
Step 3: 企业模式扫描 → 工号、内部域名、企业邮箱等
    ↓
Step 4: PII 模式扫描 → 身份证、银行卡、护照、手机号等
    ↓
Step 5: 语言特定扫描 → Python/Java/JS/Go/C++/Lua 专属模式
    ↓
Step 6: 误报过滤 → 上下文约束 + 排除规则 + 验证规则
    ↓
Step 7: 结果分类 → 按类别和风险等级整理
    ↓
Step 8: 报告生成 → 输出结构化扫描报告
```

## 安全边界

- 扫描过程只读取代码文件，不修改任何文件内容。
- 检测结果中敏感值会被脱敏显示（如 `AKIA****1234`）。
- 不自动提交修复，仅提供建议。
- 不联网验证检测到的密钥是否有效。
- 遵循 GDPR/PIPL 合规要求处理个人隐私数据。
