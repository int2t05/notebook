---
name: "sensitive-info-scanner"
description: "Scans code for sensitive information leaks (API keys, passwords, tokens, enterprise data). Invoke when user requests sensitive data detection or credential scan."
---

# Sensitive Information Scanner

This skill provides comprehensive sensitive information detection for codebases, focusing on identifying potential data leaks with minimal false positives.

## Detection Categories

### 1. API Keys & Secrets

```regex
# Generic API Key
(?i)(api[_-]?key|apikey|api_secret)['\":\s]*['\"]?[a-zA-Z0-9_\-]{20,}

# AWS Access Key
AKIA[0-9A-Z]{16}

# AWS Secret Key
(?i)aws[_-]?secret[_-]?access[_-]?key['\":\s]*['\"]?[a-zA-Z0-9/+=]{40}

# Azure Key
(?i)azure[_-]?(account[_-]?key|storage[_-]?key)['\":\s]*['\"]?[a-zA-Z0-9+/=]{40,}

# GCP Service Account
(?i)google[_-]?(cloud[_-]?api[_-]?key|service[_-]?account)['\":\s]*['\"]?[a-zA-Z0-9_\-]{20,}

# GitHub Token
ghp_[a-zA-Z0-9]{36}
gho_[a-zA-Z0-9]{36}
ghu_[a-zA-Z0-9]{36}
ghs_[a-zA-Z0-9]{36}
ghr_[a-zA-Z0-9]{36}

# GitLab Token
glpat-[a-zA-Z0-9_\-]{20}

# Slack Token
xox[baprs]-[0-9]{10,13}-[a-zA-Z0-9]{24}

# Stripe Key
sk_live_[a-zA-Z0-9]{24}
rk_live_[a-zA-Z0-9]{24}

# Twilio Account SID
AC[a-f0-9]{32}

# SendGrid API Key
SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}
```

### 2. Authentication Credentials

```regex
# Password in Code
(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{4,}['\"]
(?i)(password|passwd|pwd)\s*:\s*['\"][^'\"]{4,}['\"]

# Database Connection String
(?i)(mysql|postgres|postgresql|mongodb|redis|oracle)://[^\s\"']+
(?i)(jdbc|odbc):[^\s\"']+

# Private Key
-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----

# JWT Token
eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*

# OAuth Token
(?i)(oauth[_-]?token|access[_-]?token|bearer)['\":\s]*['\"]?[a-zA-Z0-9_\-\.]{20,}

# Session Secret
(?i)(session[_-]?secret|secret[_-]?key)['\":\s]*['\"]?[a-zA-Z0-9_\-]{16,}
```

### 3. Encryption Keys & IV/Salt

```regex
# IV Salt (初始化向量/盐值)
(?i)(iv|salt|nonce|initialization[_-]?vector)['\":\s]*['\"]?[a-fA-F0-9]{16,}['\"]?

# Hardcoded Encryption Key
(?i)(secret[_-]?key|encryption[_-]?key|cipher[_-]?key|aes[_-]?key|des[_-]?key)['\":\s]*['\"]?[a-fA-F0-9]{16,}['\"]?

# Key Assignment
(?i)key\s*=\s*['\"][a-fA-F0-9]{16,}['\"]

# PGP Key Block
-----BEGIN PGP (PUBLIC|PRIVATE) KEY BLOCK-----

# SSH Public Key
ssh-rsa [a-zA-Z0-9+/=]+
ssh-ed25519 [a-zA-Z0-9+/=]+
```

### 4. Enterprise-Specific Patterns (Low False Positive)

```regex
# 工号 - 字母+00+6个数字组成 (如: A00123456, z01876543)
\b[a-zA-Z]0[01][0-9]{6}\b

# 工号 - 字母+600+5个数字组成 (如: A60012345, q60098765)
\b[a-zA-Z]60[01][0-9]{5}\b

# 工号 - wx+7个数字组成 (如: wx1234567, WX7654321)
\b[wW][xX][0-9]{7}\b

# DTS单号 - DTS+年(4位)+日期(4位)+5个数字
\bDTS(202[0-9]|20[3-9][0-9])(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{5}\b
\bdts(202[0-9]|20[3-9][0-9])(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{5}\b

# HUAWEI 关键字 - 仅在敏感上下文中检测
(?i)(password|passwd|pwd|secret|key|token|credential|api[_-]?key|access[_-]?key).{0,20}huawei
(?i)huawei.{0,20}(password|passwd|pwd|secret|key|token|credential|api[_-]?key|access[_-]?key)

# 华为API/SDK密钥
\b[Hh][Ww][_-]?(ACCESS|SECRET|API|APP)[_-]?(KEY|ID|SECRET)\b
(?i)huawei[_-]?(access|secret|api|app)[_-]?(key|id|secret)\s*[=:]

# 华为云服务端点
https?://[\w-]+\.(obs|evs|ecs|vpc|iam|kms)\.[\w-]+\.myhuaweicloud\.com
https?://[\w-]+\.myhuaweicloud\.com

# 华为内部域名
(?i)(host|url|endpoint|server|domain)\s*[=:]\s*['\"]?https?://[\w-]+\.huawei\.(com|cn)

# 华为邮箱
\b[\w.-]+@(huawei|huaweicloud|hicloud)\.(com|cn|de|jp)\b

# 华为Git仓库
(git@|https?://)(gitlab|git|code)\.huawei\.com[/:][\w/-]+(\.git)?

# 华为认证信息
(?i)(huawei|hwc|hw)[_-]?(username|password|token|credential)\s*[=:]\s*['\"]?[^'\"\s]+
(?i)(huawei|hwc|hw)[_-]?(client[_-]?id|client[_-]?secret|app[_-]?id|app[_-]?secret)\s*[=:]\s*['\"]?[^'\"\s]+
```

### 5. Personal Identifiable Information (PII)

#### 5.1 中国身份证号码

```regex
# 中国居民身份证 - 18位 (含校验位)
# 格式: 6位地区码 + 8位出生日期 + 3位顺序码 + 1位校验码
\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b

# 中国居民身份证 - 15位 (旧版)
# 格式: 6位地区码 + 6位出生日期 + 3位顺序码
\b[1-9]\d{5}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}\b

# 身份证号上下文检测 (降低误报)
(?i)(身份证|id[_-]?card|identity[_-]?card|居民身份证|证件号码)\s*[：:＝=]\s*['\"]?[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]
```

**身份证校验规则**:
```
校验位计算:
1. 前17位分别乘以系数: 7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2
2. 求和后对11取模
3. 对应校验码: 1,0,X,9,8,7,6,5,4,3,2
```

#### 5.2 中国银行卡号

```regex
# 银行卡号通用格式 - 16-19位
\b\d{16,19}\b

# 银行卡号上下文检测 (降低误报)
(?i)(银行卡|卡号|card[_-]?number|bank[_-]?card|账号|account)\s*[：:＝=]\s*['\"]?\d{16,19}

# 各银行BIN码识别
# 工商银行 (ICBC)
\b(622202|622203|622208|620200|620208|621226|621225|621227|621229|621224)\d{10,13}\b

# 农业银行 (ABC)
\b(622848|622849|622845|622846|622847|622840|622841|622842|622843|622844)\d{10,13}\b

# 中国银行 (BOC)
\b(621660|621661|621662|621663|621665|621667|621668|621669|621666|621258)\d{10,13}\b

# 建设银行 (CCB)
\b(622700|622280|622280|622281|622282|622283|622284|622285|622286|622287)\d{10,13}\b

# 交通银行 (BOCOM)
\b(622260|622261|622262|622263|622264|622265|622266|622267|622268|622269)\d{10,13}\b

# 招商银行 (CMB)
\b(622580|622581|622582|622583|622584|622585|622586|622587|622588|622589)\d{10,13}\b

# 民生银行 (CMBC)
\b(622615|622617|622618|622619|622620|622621|622622|622623|622624|622625)\d{10,13}\b

# 浦发银行 (SPDB)
\b(622260|622261|622262|622263|622264|622265|622266|622267|622268|622269)\d{10,13}\b

# 信用卡号 - 16位 (Visa/MasterCard/JCB)
\b4\d{15}\b                                          # Visa
\b5[1-5]\d{14}\b                                     # MasterCard
\b35\d{14}\b                                         # JCB
\b(34|37)\d{13}\b                                    # American Express
\b(6011|65|64[4-9])\d{12,15}\b                       # Discover
\b(62|81)\d{14,17}\b                                 # UnionPay
```

**银行卡Luhn校验**:
```python
def luhn_check(card_number):
    digits = [int(d) for d in str(card_number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        d *= 2
        if d > 9:
            d -= 9
        total += d
    return total % 10 == 0
```

#### 5.3 中国护照号码

```regex
# 中国护照 - 格式: E + 8位数字 或 G + 8位数字
\b[EG][0-9]{8}\b

# 电子护照 - 格式: C + 8位数字 + 1位校验
\bC[0-9]{8}[A-Z]\b

# 公务护照 - 格式: SE + 7位数字 或 P + 7位数字
\b(SE[0-9]{7}|P[0-9]{7})\b

# 护照上下文检测
(?i)(护照|passport|passport[_-]?no|护照号码)\s*[：:＝=]\s*['\"]?[EG][0-9]{8}
```

#### 5.4 中国驾驶证号码

```regex
# 驾驶证号 - 18位 (与身份证号相同)
\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b

# 档案编号 - 12位
\b[0-9]{12}\b

# 驾驶证上下文检测
(?i)(驾驶证|驾照|driving[_-]?license|driver[_-]?license)\s*[：:＝=]\s*['\"]?[1-9]\d{17}[\dXx]
```

#### 5.5 中国社会保障号码

```regex
# 社会保障号 - 18位 (与身份证号相同)
\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b

# 社保卡号 - 各地格式不同，通常9-12位
(?i)(社保|社保卡|social[_-]?security|ssn)\s*[：:＝=]\s*['\"]?\d{9,12}

# 社保上下文检测
(?i)(社会保障号|社保号|社保编号|social[_-]?security[_-]?number)\s*[：:＝=]
```

#### 5.6 中国医保卡号

```regex
# 医保卡号 - 各地格式不同
(?i)(医保|医保卡|medical[_-]?insurance|health[_-]?card)\s*[：:＝=]\s*['\"]?\d{8,18}

# 医保电子凭证码
(?i)(医保凭证|医保电子凭证)\s*[：:＝=]\s*['\"]?\d{16,20}
```

#### 5.7 中国军官证/士兵证

```regex
# 军官证 - 格式: 军字第XXXXXX号 或 简化格式
(?i)(军官证|军官|军字第)\s*[第]?\s*[0-9]{6,8}\s*[号]?

# 士兵证
(?i)(士兵证|士兵)\s*[第]?\s*[0-9]{6,8}\s*[号]?

# 文职干部证
(?i)(文职证|文职干部)\s*[第]?\s*[0-9]{6,8}\s*[号]?

# 军官证上下文检测
(?i)(military[_-]?id|officer[_-]?id)\s*[：:＝=]\s*['\"]?[军字第]?\d{6,8}
```

#### 5.8 港澳通行证/台湾通行证

```regex
# 港澳通行证 - 格式: C + 8位数字 或 K + 8位数字
\b[CK][0-9]{8}\b

# 台湾通行证 - 格式: L + 8位数字 或 M + 8位数字
\b[LM][0-9]{8}\b

# 港澳居民来往内地通行证 - 格式: H + 10位数字 或 M + 10位数字
\b[HM][0-9]{10}\b

# 台湾居民来往大陆通行证 - 格式: 8位数字 或 新版K + 8位数字
\bK?[0-9]{8}\b

# 通行证上下文检测
(?i)(港澳通行证|台湾通行证|回乡证|台胞证|travel[_-]?permit)\s*[：:＝=]\s*['\"]?[CKLM][0-9]{8,10}
```

#### 5.9 中国电话号码

```regex
# 手机号码 - 11位 (中国大陆)
\b1[3-9]\d{9}\b

# 手机号码上下文检测
(?i)(手机|手机号|mobile|phone|电话|联系方式)\s*[：:＝=]\s*['\"]?1[3-9]\d{9}

# 座机号码 - 区号+号码
\b0\d{2,3}-?\d{7,8}\b

# 400/800电话
\b[48]00-?\d{3}-?\d{4}\b

# 国际电话格式
\+86\s*1[3-9]\d{9}
\+?[1-9]\d{6,14}
```

#### 5.10 国际身份证件

```regex
# 美国社会安全号 (SSN) - 格式: XXX-XX-XXXX
\b\d{3}-\d{2}-\d{4}\b

# 美国SSN上下文检测
(?i)(ssn|social[_-]?security)\s*[：:＝=]\s*['\"]?\d{3}-\d{2}-\d{4}

# 美国护照 - 9位数字
\b[0-9]{9}\b
(?i)(us[_-]?passport|美国护照)\s*[：:＝=]\s*['\"]?[0-9]{9}

# 英国国家保险号 (NINO) - 格式: AA 12 34 56 A
\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b

# 英国护照 - 9位数字
\b[0-9]{9}\b

# 加拿大社会保险号 (SIN) - 9位数字
\b\d{3}-?\d{3}-?\d{3}\b

# 澳大利亚税号 (TFN) - 8-9位数字
\b\d{3}\s?\d{3}\s?\d{3}\b

# 日本个人番号 (My Number) - 12位数字
\b\d{4}-?\d{4}-?\d{4}\b

# 韩国居民登记号 (RRN) - 13位数字
\b\d{6}-?\d{7}\b

# 新加坡身份证 (NRIC) - 格式: S/T + 7位数字 + 字母
\b[STFG]\d{7}[A-Z]\b

# 香港身份证 - 格式: 字母 + 6-7位数字 + (字母/数字)
\b[A-Z]\d{6,7}\([A-Z0-9]\)\b
```

#### 5.11 其他个人隐私信息

```regex
# 电子邮箱
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

# 邮箱上下文检测
(?i)(邮箱|email|邮件|mail)\s*[：:＝=]\s*['\"]?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

# 姓名 - 中文 (2-4个汉字)
[\u4e00-\u9fa5]{2,4}

# 姓名上下文检测
(?i)(姓名|名字|name)\s*[：:＝=]\s*['\"]?[\u4e00-\u9fa5]{2,4}

# 出生日期
\b(19|20)\d{2}[-/年](0[1-9]|1[0-2])[-/月](0[1-9]|[12]\d|3[01])[日]?\b

# 家庭住址 - 省市区县关键词
(?i)(地址|住址|address|家庭住址)\s*[：:＝=]\s*['\"]?[\u4e00-\u9fa5]+省[\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+

# 车牌号
[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{5,6}

# 车架号 (VIN) - 17位
\b[A-HJ-NPR-Z0-9]{17}\b

# 发动机号 - 6-8位
(?i)(发动机号|发动机)\s*[：:＝=]\s*['\"]?[A-Z0-9]{6,8}
```

---

### 5. PII Detection Summary Table

| 数据类型 | 格式 | 示例 | 风险等级 | 校验方式 |
|----------|------|------|----------|----------|
| **中国身份证(18位)** | 6位地区+8位日期+3位顺序+1位校验 | 110101199001011234 | 严重 | 校验位算法 |
| **中国身份证(15位)** | 6位地区+6位日期+3位顺序 | 110101900101123 | 高危 | 格式验证 |
| **银行卡号** | 16-19位数字 | 6222021234567890123 | 严重 | Luhn算法 |
| **护照号码** | E/G + 8位数字 | E12345678 | 高危 | 格式验证 |
| **驾驶证号** | 18位(同身份证) | 110101199001011234 | 高危 | 校验位算法 |
| **社保号** | 18位(同身份证) | 110101199001011234 | 高危 | 校验位算法 |
| **军官证** | 军字第+6-8位数字 | 军字第123456号 | 高危 | 格式验证 |
| **港澳通行证** | C/K + 8位数字 | C12345678 | 高危 | 格式验证 |
| **台湾通行证** | L/M + 8位数字 | L12345678 | 高危 | 格式验证 |
| **手机号码** | 1 + 10位数字 | 13812345678 | 中危 | 号段验证 |
| **美国SSN** | XXX-XX-XXXX | 123-45-6789 | 严重 | 格式验证 |
| **新加坡NRIC** | S/T + 7位数字 + 字母 | S1234567A | 高危 | 校验位算法 |
| **香港身份证** | 字母+6-7位数字+(校验) | A123456(7) | 高危 | 校验位算法 |

---

### 6. Network & Infrastructure

```regex
# IP Address (Private)
\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b

# IP Address (Public) - with context
(?i)(server|host|ip|address)\s*[=:]\s*['\"]?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}

# Port with Service
(?i)(port|listen)\s*[=:]\s*\d{2,5}

# Domain with Credentials
(?i)(ftp|sftp|ssh|telnet)://[^:]+:[^@]+@[^\s\"']+

# Internal URL
(?i)(internal|intranet|private)[_-]?(url|host|endpoint)
```

### 7. Configuration & Environment

```regex
# Environment Variable Assignment
^[A-Z_]+\s*=\s*['\"][^'\"]{8,}['\"]

# .env File Pattern
(?i)(secret|password|token|key|credential)\s*=\s*

# Docker Registry
(?i)(docker[_-]?registry|registry[_-]?url)['\":\s]*['\"]?[^\s\"']+

# Kubernetes Secret
(?i)kind:\s*Secret
(?i)kubectl.*--token

# Terraform Variable
variable\s+['\"]?(password|secret|token|key)['\"]?\s*\{
```

---

## Language-Specific Patterns

### Python

```regex
# Environment Variable
os\.environ\[['\"]\w+['\"]\]\s*=\s*['\"][^'\"]+['\"]
os\.getenv\(['\"]\w+['\"]\)

# Config Assignment
config\[['\"]\w+['\"]\]\s*=\s*['\"][^'\"]+['\"]
settings\.\w+\s*=\s*['\"][^'\"]+['\"]

# Django Secret Key
SECRET_KEY\s*=\s*['\"][^'\"]+['\"]
```

### Java

```regex
# System Property
System\.getenv\(['\"]\w+['\"]\)
System\.setProperty\(['\"]\w+['\"],\s*['\"][^'\"]+['\"]\)

# Properties File
password\s*=\s*[^\s]+
jdbc\.url\s*=\s*[^\s]+

# Spring Boot
@Value\(['\"]\$\{[^}]+\}['\"]\)
```

### JavaScript/TypeScript

```regex
# Process Env
process\.env\.\w+\s*=\s*['\"][^'\"]+['\"]
process\.env\.\w+['\"]\)

# Const Assignment
const\s+(API_KEY|SECRET|PASSWORD|TOKEN)\s*=\s*['\"][^'\"]+['\"]

# Local Storage
localStorage\.setItem\(['\"]\w+['\"],\s*['\"][^'\"]+['\"]\)
sessionStorage\.setItem\(['\"]\w+['\"],\s*['\"][^'\"]+['\"]\)
```

### Go

```regex
# OS Getenv
os\.Getenv\(['\"]\w+['\"]\)

# Const Declaration
const\s+\w+\s*=\s*['\"][^'\"]{16,}['\"]

# Variable Declaration
var\s+\w+\s*=\s*['\"][^'\"]{16,}['\"]
```

### C/C++

```regex
# Define Macro
#define\s+(PASSWORD|SECRET|KEY|TOKEN)\s+['\"][^'\"]+['\"]

# Char Array
char\s+\w+\[\]\s*=\s*['\"][^'\"]+['\"]

# Getenv
getenv\(['\"]\w+['\"]\)
```

### Lua

```regex
# OS Getenv
os\.getenv\(['\"]\w+['\"]\)

# Local Variable
local\s+\w+\s*=\s*['\"][^'\"]{16,}['\"]
```

---

## False Positive Reduction

### Context Constraints

**仅在以下上下文中触发敏感信息检测**:
- 赋值语句 (`=`, `:`, `=>`)
- 配置文件 (`.env`, `.yaml`, `.json`, `.properties`)
- 环境变量设置
- 函数参数中的凭证

### Exclusion Rules

**排除以下情况**:
```regex
# 注释行
^\s*#
^\s*//
^\s*\*

# 示例/文档
example|sample|test|mock|dummy|placeholder|fake

# 变量名声明 (非赋值)
(password|secret|key)\s*:\s*(string|str)

# 空值
(password|secret|key)\s*[=:]\s*['\"]['\"]
(password|secret|key)\s*[=:]\s*null
(password|secret|key)\s*[=:]\s*None
```

### Validation Rules

**验证匹配结果**:
1. 长度检查: 密钥/密码至少8字符
2. 格式检查: 符合预期的格式模式
3. 上下文检查: 排除测试文件和示例代码
4. 重复检查: 同一值多次出现可能是占位符

---

## Scan Commands

### Quick Scan

```bash
# 快速扫描所有源文件
grep -rnE "(password|secret|token|key|credential)" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.go" --include="*.c" --include="*.cpp" . | grep -v "test\|spec\|example\|sample\|mock"
```

### Deep Scan

```bash
# 深度扫描 - 包含所有模式
grep -rnE "(?i)(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.go" --include="*.c" --include="*.cpp" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.properties" --include="*.env" . | grep -v "^\s*#\|^\s*//\|test\|spec\|example"
```

### Enterprise Scan

```bash
# 企业敏感信息扫描
grep -rnE "\b[a-zA-Z]00[0-9]{6}\b|\b[wW][xX][0-9]{7}\b|\bDTS[0-9]{13}\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.go" .

# 华为相关信息扫描
grep -rnE "(?i)(huawei|hwc|hw)[_-]?(password|token|secret|key|credential)" --include="*.py" --include="*.java" --include="*.yaml" --include="*.properties" .

# 华为邮箱扫描
grep -rnE "[\w.-]+@(huawei|huaweicloud|hicloud)\.(com|cn)" --include="*.py" --include="*.java" --include="*.md" .
```

### PII Scan (个人隐私数据扫描)

```bash
# 中国身份证号扫描
grep -rnE "\b[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.go" --include="*.csv" --include="*.json" .

# 银行卡号扫描
grep -rnE "\b[0-9]{16,19}\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" . | grep -iE "(card|bank|account|卡|账号)"

# 手机号码扫描
grep -rnE "\b1[3-9][0-9]{9}\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .

# 护照号码扫描
grep -rnE "\b[EG][0-9]{8}\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .

# 美国SSN扫描
grep -rnE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .

# 邮箱地址扫描
grep -rnE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .

# 车牌号扫描
grep -rnE "[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{5,6}" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .

# 综合PII扫描 (身份证+银行卡+手机号)
grep -rnE "(\b[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]\b|\b1[3-9][0-9]{9}\b|\b[0-9]{16,19}\b)" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.csv" --include="*.json" .
```

### Git History Scan

```bash
# 扫描Git历史中的敏感信息
git log -p | grep -E "(password|secret|token|key).*=.*['\"][^'\"]+['\"]"

# 扫描所有分支
git log --all -p | grep -E "(password|secret|token|key).*=.*['\"][^'\"]+['\"]"
```

---

## Scan Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              Sensitive Information Scan Workflow                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Detect Languages                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Identify file types → Select language-specific patterns  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 2: Universal Pattern Scan                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ API keys, passwords, tokens, private keys                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 3: Enterprise Pattern Scan                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 工号, DTS单号, HUAWEI相关, 企业域名                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 4: PII Pattern Scan                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 身份证, 银行卡, 护照, 手机号, 邮箱, 车牌号                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 5: False Positive Filtering                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Exclude comments, tests, examples, placeholders          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 6: Generate Report                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Categorize findings → Severity rating → Recommendations  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 7: Output Report File                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Save report to file → Naming: 仓仓名_Sensitive_Info_日期 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  Step 8: Cleanup                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Delete downloaded code repository                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Report Output

### Report File Naming

报告文件命名格式：`代码仓库名_Sensitive_Info_年月日.md`

**示例**:
- `KAE_Sensitive_Info_20260402.md`
- `ffmpeg_Sensitive_Info_20260402.md`
- `openclaw_Sensitive_Info_20260402.md`

### Report Output Location

报告输出到当前工作目录：`c:\Users\z00471535\Documents\trae_projects\Security\`

### Report Generation Process

1. 扫描完成后，生成Markdown格式报告
2. 使用当前日期作为文件名后缀
3. 将报告保存为文件
4. 删除下载的代码仓库目录

---

## Report Format

```markdown
# Sensitive Information Scan Report

## Summary
- **Total Files Scanned**: X
- **Total Findings**: X
- **Critical**: X | **High**: X | **Medium**: X | **Low**: X

## Findings by Category

### 1. API Keys & Secrets
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|

### 2. Authentication Credentials
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|

### 3. Enterprise Sensitive Data
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|

### 4. PII - Identity Documents (身份证件)
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|
| file.py | 123 | 中国身份证 | 110101199001011234 | Critical | 脱敏处理 |

### 5. PII - Financial Data (金融数据)
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|
| file.py | 456 | 银行卡号 | 6222021234567890 | Critical | 脱敏处理 |

### 6. PII - Contact Information (联系方式)
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|
| file.py | 789 | 手机号码 | 13812345678 | Medium | 脱敏处理 |
| file.py | 790 | 电子邮箱 | user@example.com | Low | 检查必要性 |

### 7. PII - Other Personal Data (其他个人数据)
| File | Line | Type | Match | Severity | Action |
|------|------|------|-------|----------|--------|
| file.py | 100 | 车牌号 | 京A12345 | Medium | 脱敏处理 |

## PII Compliance Check (隐私合规检查)

### 数据类型统计
| 数据类型 | 数量 | 合规状态 | 备注 |
|----------|------|----------|------|
| 身份证号 | X | ❌ 需整改 | 需脱敏或加密存储 |
| 银行卡号 | X | ❌ 需整改 | 需脱敏或加密存储 |
| 手机号码 | X | ⚠️ 需评估 | 检查收集必要性 |
| 邮箱地址 | X | ⚠️ 需评估 | 检查收集必要性 |

### 合规建议
1. 敏感数据脱敏: 身份证、银行卡等敏感数据需脱敏存储
2. 数据最小化: 仅收集必要的个人信息
3. 加密存储: 敏感数据应加密存储
4. 访问控制: 限制敏感数据的访问权限
5. 审计日志: 记录敏感数据的访问日志

## Recommendations
1. Move secrets to environment variables
2. Use secret management tools (Vault, AWS Secrets Manager)
3. Add sensitive files to .gitignore
4. Rotate exposed credentials immediately
5. Implement pre-commit hooks for secret detection
6. PII data masking and encryption
7. Data minimization review

## Files to Review
- [ ] .env files
- [ ] Configuration files
- [ ] Source code with hardcoded values
- [ ] Database files
- [ ] Log files
- [ ] Git history
```

---

## Severity Classification

| 级别 | 描述 | 示例 |
|------|------|------|
| **Critical** | 可直接导致系统被入侵或严重隐私泄露 | AWS密钥、私钥、数据库密码、身份证号、银行卡号 |
| **High** | 可导致敏感数据泄露 | API密钥、用户密码、Token、护照号、驾驶证号 |
| **Medium** | 可能泄露内部信息或个人隐私 | 内网IP、内部域名、工号、手机号、车牌号 |
| **Low** | 信息泄露风险较低 | 邮箱地址、公网IP、姓名 |

---

## Remediation Actions

### For API Keys
```bash
# 1. 撤销泄露的密钥
# 2. 使用环境变量
export API_KEY="your-key-here"

# 3. 使用配置文件 (不提交到Git)
# config.local.yaml
api_key: ${API_KEY}
```

### For Passwords
```bash
# 1. 使用密钥管理服务
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id my-secret

# 2. 使用Vault
vault kv get secret/myapp/password
```

### For Enterprise Data
```bash
# 1. 数据脱敏
echo "A00123456" | sed 's/[0-9]/X/g'  # A00XXXXXX

# 2. 使用占位符
employee_id: ${EMPLOYEE_ID}
dts_number: ${DTS_NUMBER}
```

### For PII Data (个人隐私数据脱敏)

```python
# Python 数据脱敏示例

# 身份证号脱敏 - 保留前6位和后4位
def mask_id_card(id_card):
    if len(id_card) == 18:
        return id_card[:6] + '********' + id_card[-4:]
    return id_card
# 示例: 110101199001011234 -> 110101********1234

# 银行卡号脱敏 - 保留前4位和后4位
def mask_bank_card(card_number):
    if len(card_number) >= 16:
        return card_number[:4] + '******' + card_number[-4:]
    return card_number
# 示例: 6222021234567890 -> 6222******7890

# 手机号脱敏 - 保留前3位和后4位
def mask_phone(phone):
    if len(phone) == 11:
        return phone[:3] + '****' + phone[-4:]
    return phone
# 示例: 13812345678 -> 138****5678

# 邮箱脱敏 - 保留前2位和@后的域名
def mask_email(email):
    if '@' in email:
        parts = email.split('@')
        if len(parts[0]) > 2:
            return parts[0][:2] + '***@' + parts[1]
    return email
# 示例: user@example.com -> us***@example.com

# 姓名脱敏 - 保留姓氏
def mask_name(name):
    if len(name) >= 2:
        return name[0] + '*' * (len(name) - 1)
    return name
# 示例: 张三 -> 张*

# 地址脱敏 - 隐藏详细地址
def mask_address(address):
    # 只保留省市区，隐藏详细地址
    import re
    match = re.match(r'(.{2,3}省.{2,3}市.{2,3}区)', address)
    if match:
        return match.group(1) + '***'
    return address[:10] + '***'
# 示例: 广东省深圳市南山区科技园路123号 -> 广东省深圳市南山区***

# 车牌号脱敏 - 隐藏中间部分
def mask_license_plate(plate):
    if len(plate) >= 7:
        return plate[:2] + '***' + plate[-2:]
    return plate
# 示例: 粤B12345 -> 粤B***45
```

```javascript
// JavaScript 数据脱敏示例

// 身份证号脱敏
function maskIdCard(idCard) {
    if (idCard.length === 18) {
        return idCard.substring(0, 6) + '********' + idCard.substring(14);
    }
    return idCard;
}

// 银行卡号脱敏
function maskBankCard(cardNumber) {
    if (cardNumber.length >= 16) {
        return cardNumber.substring(0, 4) + '******' + cardNumber.substring(cardNumber.length - 4);
    }
    return cardNumber;
}

// 手机号脱敏
function maskPhone(phone) {
    if (phone.length === 11) {
        return phone.substring(0, 3) + '****' + phone.substring(7);
    }
    return phone;
}

// 邮箱脱敏
function maskEmail(email) {
    const parts = email.split('@');
    if (parts.length === 2 && parts[0].length > 2) {
        return parts[0].substring(0, 2) + '***@' + parts[1];
    }
    return email;
}
```

```java
// Java 数据脱敏示例

public class DataMasker {
    
    // 身份证号脱敏
    public static String maskIdCard(String idCard) {
        if (idCard != null && idCard.length() == 18) {
            return idCard.substring(0, 6) + "********" + idCard.substring(14);
        }
        return idCard;
    }
    
    // 银行卡号脱敏
    public static String maskBankCard(String cardNumber) {
        if (cardNumber != null && cardNumber.length() >= 16) {
            return cardNumber.substring(0, 4) + "******" + cardNumber.substring(cardNumber.length() - 4);
        }
        return cardNumber;
    }
    
    // 手机号脱敏
    public static String maskPhone(String phone) {
        if (phone != null && phone.length() == 11) {
            return phone.substring(0, 3) + "****" + phone.substring(7);
        }
        return phone;
    }
    
    // 邮箱脱敏
    public static String maskEmail(String email) {
        if (email != null && email.contains("@")) {
            String[] parts = email.split("@");
            if (parts[0].length() > 2) {
                return parts[0].substring(0, 2) + "***@" + parts[1];
            }
        }
        return email;
    }
}
```

---

## Usage Examples

### Example 1: Quick Scan
```
User: "Scan this project for sensitive information"
Action:
1. Detect languages
2. Run universal pattern scan
3. Filter false positives
4. Generate summary report
5. Save report to file: 仓库名_Sensitive_Info_年月日.md
6. Cleanup downloaded code
```

### Example 2: Enterprise Scan
```
User: "Check for enterprise sensitive data leaks"
Action:
1. Scan for 工号, DTS单号
2. Scan for HUAWEI-related credentials
3. Check internal domains and emails
4. Generate enterprise-specific report
5. Save report to file: 仓库名_Sensitive_Info_年月日.md
6. Cleanup downloaded code
```

### Example 3: PII Scan
```
User: "Scan for personal identifiable information"
Action:
1. Scan for 身份证号, 银行卡号
2. Scan for 手机号, 邮箱, 护照号
3. Check for 车牌号, 驾驶证号
4. Generate PII compliance report
5. Save report to file: 仓库名_Sensitive_Info_年月日.md
6. Cleanup downloaded code
```

### Example 4: Deep Scan with Git History
```
User: "Deep scan including git history"
Action:
1. Scan current codebase
2. Scan git history for committed secrets
3. Check all branches
4. Generate comprehensive report
5. Save report to file: 仓库名_Sensitive_Info_年月日.md
6. Cleanup downloaded code
```

### Example 5: Remote Repository Scan
```
User: "Scan https://gitcode.com/boostkit/KAE.git for sensitive information"
Action:
1. Clone repository to temp directory (仓库名-scan/)
2. Detect languages
3. Run all pattern scans (API keys, credentials, enterprise, PII)
4. Filter false positives
5. Generate comprehensive report
6. Save report to file: KAE_Sensitive_Info_20260402.md
7. Delete temp directory (KAE-scan/)
```

---

## Best Practices

1. **Scan Early** - Integrate into CI/CD pipeline
2. **Scan Often** - Run on every commit
3. **Use Pre-commit Hooks** - Prevent secrets from being committed
4. **Rotate Regularly** - Change credentials periodically
5. **Least Privilege** - Use minimal required permissions
6. **Audit Access** - Log all secret access
7. **Encrypt at Rest** - Never store secrets in plain text
8. **Use Secret Managers** - Centralize secret management
9. **PII Masking** - Always mask sensitive PII data
10. **Data Minimization** - Only collect necessary personal data
11. **Compliance Check** - Ensure GDPR/PIPL compliance
