# Patch-Validator 设计文档

## 目录

- [1. 设计概述](#1-设计概述)
- [2. 架构驱动因素](#2-架构驱动因素)
- [3. 分层架构](#3-分层架构)
- [4. 组件模型与交互](#4-组件模型与交互)
- [5. 时序与流程](#5-时序与流程)
- [6. 匹配与比较模型](#6-匹配与比较模型)
- [7. 脚本职责说明](#7-脚本职责说明)
- [8. 数据契约](#8-数据契约)
- [9. 测试与运维说明](#9-测试与运维说明)

## 1. 设计概述

`patch-validator` 是一个用于分析 `git format-patch` 结果的校验器，支持两类问题：

1. 这些 patch 还能否应用到目标分支。
2. 这些 patch 是否已经以等价 diff 的形式合入目标仓库。

系统既可单独用于 patch 预检查，也可作为 `kernel-patch` 批量迁移后的复核组件。

### 1.1 双模式定位图

```mermaid
flowchart LR
    P[patches_dir/*.patch] --> CLI[validate_patches.py]
    CLI --> A[applicability]
    CLI --> M[merged-diff]

    A --> AOUT[能否应用 / hunk 状态]
    M --> MOUT[是否已等价合入 / diff 状态]

    AOUT --> JSON[validation_result.json]
    MOUT --> JSON
    JSON --> REP[generate_report.py]
    REP --> MD[Markdown 报告]
```

### 1.2 当前实现边界

- 单一主脚本 `scripts/validate_patches.py` 承载解析、匹配、比较和 CLI
- 报告渲染与校验计算分离
- 目标提交匹配顺序固定为 `subject-strict -> subject-fuzzy -> diff`
- 对二进制 / 非 UTF-8 diff 不做文本逐行比较，而是显式降级

## 2. 架构驱动因素

### 2.1 业务驱动

- patch 迁移前需要尽早判断可应用性
- patch 迁移后需要判断“已合入”是否真等价，而不是只比标题
- 大批量 patch 审查需要结构化 JSON 和可读报告双产物
- 用户提供的 patch 文件名可能截断，匹配逻辑必须更稳健

### 2.2 技术驱动

- 解析层要同时支持 `unidiff` 和手工解析兜底
- 匹配层要能限制搜索范围，避免全历史扫描成本过高
- 比较层要能识别新增缺失、额外新增和删除侧不一致
- 输出层要为自动化和人工审查分别提供 JSON 与 Markdown

### 2.3 约束图

```mermaid
flowchart TD
    A[patch 文件可能不规范] --> B[解析需支持 metadata + diff body]
    B --> C[匹配要避免只依赖文件名]
    C --> D[比较要支持文本和二进制降级]
    D --> E[结果要能直接生成报告]
```

## 3. 分层架构

### 3.1 分层图

```mermaid
flowchart TB
    subgraph L1[CLI 层]
        CLI1[validate_patches.py]
        CLI2[generate_report.py]
    end

    subgraph L2[解析层]
        META[parse_patch_metadata]
        PARSE[parse_patch_text]
    end

    subgraph L3[校验与匹配层]
        APP[validate_patch_applicability]
        IDX1[build_local_patch_index]
        IDX2[build_target_commit_index]
        MAP[map_local_patch_to_target_commit]
    end

    subgraph L4[比较层]
        CMP1[compare_patch_to_commit]
        CMP2[compare_file_diffs]
        CMP3[compare_hunk_pair]
    end

    subgraph L5[输出层]
        RES[ValidationResult]
        MD[Markdown Report]
    end

    CLI1 --> META
    CLI1 --> PARSE
    CLI1 --> APP
    CLI1 --> IDX1
    CLI1 --> IDX2
    CLI1 --> MAP
    MAP --> CMP1
    CMP1 --> CMP2
    CMP2 --> CMP3
    APP --> RES
    CMP1 --> RES
    CLI2 --> RES
    CLI2 --> MD
```

### 3.2 分层职责

- CLI 层：参数解析、模式切换、输出落盘
- 解析层：提取 patch metadata、文件 diff 和 hunk
- 校验与匹配层：执行 applicability 校验或构建本地/目标索引并匹配提交
- 比较层：做文件级和 hunk 级差异分析
- 输出层：聚合统计并生成 JSON / Markdown

## 4. 组件模型与交互

### 4.1 核心组件图

```mermaid
flowchart LR
    U[用户 / Agent] --> CLI[validate_patches.py]
    CLI --> LP[本地 patch 索引]
    CLI --> TC[目标提交索引]
    CLI --> AP[Applicability 校验器]
    LP --> MAP[提交匹配器]
    TC --> MAP
    MAP --> DIFF[Diff 比较器]
    AP --> RES[(ValidationResult)]
    DIFF --> RES
    RES --> REP[generate_report.py]
    REP --> OUT[Markdown 报告]
```

### 4.2 Applicability 子系统图

```mermaid
flowchart TD
    P[patch text] --> PARSE[parse_patch_text]
    PARSE --> FILE[validate_file]
    FILE --> HUNK[validate_hunk]
    HUNK --> READ[read_file_lines]
    HUNK --> GIT[git apply --check]
    HUNK --> SCORE[calculate_similarity / find_best_match]
    SCORE --> STATUS[CLEAN / VARIATION / FAILED]
```

### 4.3 Merged-Diff 子系统图

```mermaid
flowchart TD
    PATCH[本地 patch] --> LIDX[build_local_patch_index]
    REPO[目标 repo] --> TIDX[build_target_commit_index]
    LIDX --> MAP[map_local_patch_to_target_commit]
    TIDX --> MAP
    MAP --> CMP[compare_patch_to_commit]
    CMP --> OUT[IDENTICAL / DIFFERENT / UNMATCHED / AMBIGUOUS]
```

## 5. 时序与流程

### 5.1 Applicability 时序图

```mermaid
sequenceDiagram
    autonumber
    participant User as 用户/Agent
    participant CLI as validate_patches.py
    participant Parser as parse_patch_text
    participant Repo as 目标仓库

    User->>CLI: --mode applicability
    CLI->>CLI: 遍历 patch 文件
    loop 每个 patch
        CLI->>Parser: 解析文件和 hunk
        Parser-->>CLI: file_info / hunk_info
        loop 每个 hunk
            CLI->>Repo: 读取目标文件
            CLI->>Repo: 可选 git apply --check
            CLI->>CLI: 计算 similarity / offset
            CLI->>CLI: 生成 HunkResult
        end
        CLI->>CLI: 汇总 PatchResult
    end
    CLI->>CLI: 汇总 ValidationResult
```

### 5.2 Merged-Diff 时序图

```mermaid
sequenceDiagram
    autonumber
    participant User as 用户/Agent
    participant CLI as validate_patches.py
    participant L as LocalPatchIndex
    participant T as TargetCommitIndex
    participant M as Matcher
    participant C as Comparator

    User->>CLI: --mode merged-diff
    CLI->>L: build_local_patch_index()
    CLI->>T: build_target_commit_index()

    loop 每个 local patch
        CLI->>M: map_local_patch_to_target_commit()
        M-->>CLI: MATCHED / UNMATCHED / AMBIGUOUS

        alt MATCHED
            CLI->>C: compare_patch_to_commit()
            C-->>CLI: file_differences
        else 未匹配或歧义
            CLI->>CLI: 直接构造 PatchResult
        end
    end

    CLI->>CLI: 汇总 ValidationResult
```

### 5.3 搜索范围流程图

```mermaid
flowchart TD
    START[build_target_commit_index] --> C1{explicit_commit?}
    C1 -->|yes| E[search_scope=explicit]
    C1 -->|no| C2{global_search?}
    C2 -->|yes| G[search_scope=global]
    C2 -->|no| S[detect upstream]
    S --> C3{找到 upstream?}
    C3 -->|yes| SC[search_scope=scoped]
    C3 -->|no| ERR[抛出 ValueError]
```

### 5.4 报告生成流程图

```mermaid
flowchart LR
    JSON[validation_result.json] --> LOAD[load_validation_result]
    LOAD --> SUM[generate_summary_section]
    LOAD --> DETAIL[生成 patch / file / hunk 详情]
    SUM --> REPORT[generate_report]
    DETAIL --> REPORT
    REPORT --> MD[patch_validation_report.md]
```

## 6. 匹配与比较模型

### 6.1 状态模型

#### Applicability 状态

```mermaid
flowchart LR
    H[单个 hunk] --> C1{匹配结果}
    C1 -->|精确匹配| CLEAN[CLEAN]
    C1 -->|容忍范围内近似匹配| VAR[VARIATION]
    C1 -->|无法匹配| FAIL[FAILED]
```

#### Merged-Diff 状态

```mermaid
flowchart LR
    P[单个 patch] --> M1{目标提交匹配}
    M1 -->|唯一匹配且 diff 一致| ID[IDENTICAL]
    M1 -->|唯一匹配但 diff 不同| DIFF[DIFFERENT]
    M1 -->|找不到提交| UNM[UNMATCHED]
    M1 -->|多个候选| AMB[AMBIGUOUS]
```

### 6.2 匹配优先级图

```mermaid
flowchart LR
    A[local patch] --> B[subject-strict]
    B -->|命中唯一候选| OK1[MATCHED]
    B -->|无候选| C[subject-fuzzy]
    C -->|命中唯一候选| OK2[MATCHED]
    C -->|无候选| D[diff patch-id]
    D -->|命中唯一候选| OK3[MATCHED]
    D -->|无候选| U[UNMATCHED]
    B -->|多个候选| X1[AMBIGUOUS]
    C -->|多个候选| X2[AMBIGUOUS]
    D -->|多个候选| X3[AMBIGUOUS]
```

### 6.3 本地 patch 身份提取图

```mermaid
flowchart TD
    PATCH[patch file] --> META[parse_patch_metadata]
    PATCH --> NAME[split_filename_metadata]
    PATCH --> BODY[extract_diff_body]
    META --> ID[LocalPatchIndexEntry]
    NAME --> ID
    BODY --> PID[compute_patch_id]
    PID --> ID
```

### 6.4 差异比较图

```mermaid
flowchart TD
    LOCAL[local patch diff] --> FILEALIGN[按文件对齐]
    MERGED[target commit diff] --> FILEALIGN
    FILEALIGN --> HUNKALIGN[align_hunks]
    HUNKALIGN --> HUNKCMP[compare_hunk_pair]
    HUNKCMP --> FILECMP[compare_file_diffs]
    FILECMP --> RES[file_differences]
```

### 6.5 特殊场景说明

- `Subject:` 折行时会拼接 continuation line，避免截断匹配失败
- 文件名明显截断时，不直接判定“文件不存在”，而是优先走 `Subject -> From hash -> diff`
- 二进制或非 UTF-8 diff 会返回 `skipped` 文件级状态，不做文本逐行比较

## 7. 脚本职责说明

### 7.1 脚本矩阵

| 脚本 | 职责 |
|------|------|
| `scripts/validate_patches.py` | 主 CLI、patch 解析、适用性校验、提交匹配、diff 比较 |
| `scripts/generate_report.py` | 将 JSON 结果转成 Markdown 报告 |
| `references/report_template.md` | 报告阅读模板与术语说明 |

### 7.2 主脚本内部模块关系

```mermaid
flowchart TD
    VP[validate_patches.py]
    VP --> P1[parse_patch_metadata / parse_patch_text]
    VP --> P2[validate_patch_applicability]
    VP --> P3[build_local_patch_index]
    VP --> P4[build_target_commit_index]
    VP --> P5[map_local_patch_to_target_commit]
    VP --> P6[compare_patch_to_commit]
    VP --> P7[ValidationResult 聚合]
```

## 8. 数据契约

### 8.1 CLI 输入图

```mermaid
flowchart TD
    IN[CLI 参数]
    IN --> I1[--patches]
    IN --> I2[--repo]
    IN --> I3[--branch]
    IN --> I4[--mode]
    IN --> I5[--tolerance / --threshold]
    IN --> I6[--commit / --upstream-branch / --global-search]
    IN --> I7[--output]
```

### 8.2 结果模型图

```mermaid
flowchart TD
    VR[ValidationResult]
    VR --> V1[repository / branch / mode]
    VR --> V2[match_strategy / search_scope / upstream_branch]
    VR --> V3[patches[]]
    VR --> V4[total_patches / total_hunks]
    VR --> V5[identical / different / unmatched / ambiguous]

    V3 --> PR[PatchResult]
    PR --> P1[patch_file / commit_subject / commit_hash]
    PR --> P2[files / file_differences]
    PR --> P3[overall_status / diff_status]
    PR --> P4[target_match_status / target_match_method]
```

### 8.3 JSON 输出示例

```json
{
  "repository": "/path/to/repo",
  "branch": "main",
  "mode": "merged-diff",
  "match_strategy": "subject-strict->subject-fuzzy->diff",
  "search_scope": "global",
  "patches": [
    {
      "patch_file": "0001-demo.patch",
      "commit_subject": "demo subject",
      "diff_status": "IDENTICAL",
      "target_match_status": "MATCHED",
      "target_match_method": "subject-strict"
    }
  ],
  "total_patches": 1,
  "identical_patches": 1,
  "different_patches": 0,
  "unmatched_patches": 0,
  "ambiguous_patches": 0
}
```

### 8.4 报告产物图

```mermaid
flowchart LR
    ValidationResult --> Summary[执行摘要]
    ValidationResult --> Detail[补丁 / 文件 / hunk 详情]
    Summary --> Report[Markdown Report]
    Detail --> Report
```

## 9. 测试与运维说明

### 9.1 测试覆盖

| 测试类别 | 覆盖重点 |
|---------|---------|
| Binary diff | `get_commit_diff_bytes()`、`compute_patch_id()`、`compare_patch_to_commit()` |
| Search scope | `explicit`、`scoped`、`global` 搜索范围 |
| Matching | `subject-strict`、`subject-fuzzy`、`diff` 三段式匹配 |

运行命令：

```bash
cd patch-validator
python3 -m unittest discover -s tests -p 'test_*.py'
```

### 9.2 运维建议

- merged-diff 默认优先 scoped 搜索，只有必要时再开 `--global-search`
- 当 patch 标题可能被截断时，先信任 patch 头，不要只看文件名
- 对 `DIFFERENT` 结果应结合 `file_differences` 与报告一起判断
- 对 `UNMATCHED` 和 `AMBIGUOUS` 结果要优先检查搜索范围是否过窄

### 9.3 总结

当前实现的 `patch-validator` 架构有三个重点：

1. 双模式分离清晰，分别服务“可应用性”与“等价合入性”两个问题。
2. 匹配与比较链路可解释，便于人工复核误判来源。
3. JSON 与 Markdown 双产物让它既能嵌入自动化流程，也能直接服务人工审查。
