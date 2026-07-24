# HIP09 Software Optimization Guide

> **逆向分析来源**: GCC `gcc/config/aarch64/hip09.md` pipeline 描述 + `aarch64-cost-tables.h` 调优代价表
> **文档版本**: 基于 GCC 14.3.0 pipeline model (贡献者: Yushuai Xing) 逆向推导
> **ISA**: ARMv8.5-A + SVE + I8MM + F32MM + F64MM + Profile + PredRes + RNG
> **HiSilicon Implementer ID**: 0x48, Part: 0xd02

---

## 1. 处理器微架构概览

HIP09 是一款高吞吐量 AArch64 乱序执行处理器，具有显著扩展的执行资源。GCC 模型使用 **3个独立的 automaton** (hip09, hip09_ldst, hip09_fsu)，表明整数/加载存储/SIMD-FP 具有独立的发射队列。

```
                         ┌──────────────────────────────────────────────────┐
                         │               Issue (3 independent queues)        │
                         └──────────────────────────────────────────────────┘
                                    │                     │
    ┌───────────────────────────────┤                     ├───────────────────┐
    │       hip09 automaton         │   hip09_ldst        │   hip09_fsu       │
    │                               │   automaton         │   automaton       │
    │  ┌─ ALUs0 ─┐ ┌─ ALUm0 ─┐     │                     │                   │
    │  │ ALUs1   │ │ ALUm1   │     │  ┌─ Load0 ─┐        │  ┌─ FSU0 ─┐      │
    │  │ ALUs2   │ └─────────┘     │  │ Load1   │        │  │ FSU1   │      │
    │  │ ALUs3   │                 │  └─────────┘        │  │ FSU2   │      │
    │  └─────────┘                 │  ┌─ Store0 ─┐       │  │ FSU3   │      │
    │  ┌─ BRU0 ──┐                 │  │ Store1   │       │  └─────────┘      │
    │  │ BRU1    │                 │  └──────────┘       │  (SVE 与 NEON    │
    │  └─────────┘                 │  ┌─ STD0 ───┐       │   共享 FSU0-3,   │
    │                              │  │ STD1     │       │   AES 用 FSU0/2) │
    │                              │  └──────────┘       │                  │
    │                              │                     │                  │
    └──────────────────────────────┴─────────────────────┴───────────────────┘
```

### 关键执行单元汇总

| 单元 | 数量 | automaton | 功能 |
|------|------|-----------|------|
| **ALUs** (simple) | 4 (ALU0-3) | hip09 | 单周期整数操作 |
| **ALUm** (complex) | 2 (ALU0-1) | hip09 | 多周期整数（移位、乘法）|
| **BRU** | 2 (BRU0-1) | hip09 | 分支 |
| **Load** | 2 | hip09_ldst | 加载 |
| **Store** | 2 | hip09_ldst | 存储地址 |
| **Store Data** | 2 (STD0-1) | hip09_ldst | 存储数据 |
| **FSU** | 4 (FSU0-3) | hip09_fsu | FP/SIMD/SVE（非对称）|

**总发射宽度**: 整数域 4条简单 + 2条复杂 + 2条分支；Load/Store域可同时发射1 Load + 1 Store；SIMD域可发射最多4条操作。

---

## 2. 指令延迟与吞吐量

### 2.1 整数指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| ALU 基本 (add/sub/and/or/xor/mov/imm) | **1** | ALUs0123 | 4路发射 |
| ALU + csel | 1 | ALUs0123 | |
| rotate_imm, bfm, clz, rbit, rev | 1 | ALUs0123 | |
| ALUs (flags设置) + adr | 1 | **ALUs23 only** | flags仅在ALU2/3 |
| ALU extend (uxtb/uxth/sxtb/sxth/sxtw) | 2 | ALUm01 | |
| ALU shift (logic/logics shift imm/reg) | 2 | ALUm01 | |
| 乘法 (32/64-bit) | **3** | ALUm01 | 2路发射 |
| 除法 (32/64-bit) | **10** | **ALUm0 only** | 仅1路！|
| CRC | 2 | ALUm01 | |

**约束**: 除法仅在 ALUm0 执行。flags 设置指令只在 ALUs2/3。

### 2.2 分支指令

| 指令类别 | 延迟 | 发射端口 | 占用 |
|----------|------|---------|------|
| 分支 + 调用 | **2** | BRU01 + **ALUs23** | **同时占用BRU和ALU2/3！** |

⚠️ 分支/调用有 **2周期延迟**（非零），且**同时占用BRU和ALUs2/3**。调用密集代码会影响flags计算。

### 2.3 Load/Store 指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| Load 32/64-bit | **4** | LD01 | 2路load |
| Store 32/64-bit | **1** | ST01 + STD01 | 同时占store和store data |
| FP load (s/d) | **7** | LD01 | |
| FP load pair (neon_ldp) | **6** | LD01 + ALUs01 | 额外占ALU |
| FP store (s/d) | **2** | ST01 + STD01 | |
| NEON LD1 1/2/3/4reg | **6** | LD01 | 统一6周期 |
| NEON LD1 lane/all_lanes | **7** | LD01 + FSU0123 | |
| NEON LD2/4 (interleaved) | **8** | LD01 + FSU0123 | |
| NEON LD3 3reg | **9** | LD01 + FSU0123 | |
| NEON LD4 4reg | **13** | LD01 + FSU0123 | 最贵！|
| NEON ST1+ST2 | **1** | ST01 + STD01 | |
| NEON ST1 1reg | **2** | ST01 + STD01 | |
| NEON ST1 2reg | **3** | ST01 + STD01 | |
| NEON ST1 3reg | **4** | ST01 + STD01 | |
| NEON ST1 4reg | **5** | ST01 + STD01 | |
| NEON ST3/4 lane | **4** | FSU0123 + ST01 + STD01 | |
| NEON ST3 3reg | **7** | FSU0123 + ST01 + STD01 | |
| NEON ST4 4reg | **10** | FSU0123 + ST01 + STD01 | |

### 2.4 标量浮点指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| FP abs/neg/cpy (ffariths/d, fmov, fconst) | **1** | FSU0123 | 1周期！快速 |
| FP add/sub (fadd/fsub) | **2** | FSU0123 | |
| FP min/max | 2 | FSU0123 | |
| FP convert f2f (fcvt) | 2 | FSU0123 | |
| FP round int (frint) | 2 | FSU0123 | |
| FP multiply (fmul) | **3** | FSU0123 | |
| FP FMA (fmadd/fmsub) | **4** | FSU0123 | |
| FP compare (fcmp) | **4** | FSU0123 + **ALUs23** | 占用整数流水线！|
| FP CCMP (fccmp) | **7** | ALUs01 + FSU0123 + ALUs23 | 极重！|
| FP CSEL (fcsel) | **4** | ALUs01 + FSU0123 | |
| FP div single | **7** | FSU0123 | |
| FP div double | **10** | FSU0123 | |
| FP sqrt single | **9** | FSU0123 | |
| FP sqrt double | **15** | FSU0123 | |
| FP cvt f2i | **5** | FSU0123 + **ALUs23** | 占ALU |
| FP cvt i2f | **5** | **ALUs01** + FSU0123 | 占ALU |
| FP move GP↔SIMD (f_mcr) | 4 | ALUs01 + FSU0123 | |

### 2.5 ASIMD/NEON 指令

HIP09 使用自定义的 `hip09_type` 属性进行分类：

| hip09_type | 延迟 | 发射端口 | 包含指令 |
|------------|------|---------|---------|
| **hip09_neon_abs** | **1** | FSU0123 | ABS/NEG/ADD/SUB/LOGIC/CMP/BSL/CLS/EXT/TBL1/MOV/FP_ABS/FP_NEG/SHIFT_IMM_NARROW |
| **hip09_neon_fp_arith** | **2** | FSU0123 | ABD/ABA/HALVE/REDUC_ADD/SAT_MUL_B/TBL2/FP_ADDSUB/FP_COMPARE/FP_MINMAX/FP_CVT/FP_ROUND/FP_TO_INT/FP_ABD/SHIFT_IMM |
| **hip09_neon_mul** | **3** | FSU0123 | MUL_H/S/MLA_H/S_long/SHIFT_ACC/SHIFT_REG/SAT_SHIFT/TBL3/FP_REDUC_ADD/FP_REDUC_MINMAX/FP_MUL_S_Q/FP_MUL_D |
| **hip09_neon_mla** | **4** | FSU0123 | MLA_S_Q/REDUC_MINMAX/FRECPS/FRSQRTS/TBL4/FP_MLA_S/FP_MLA_D |
| **hip09_neon_dot** | **6** | FSU0123 | SDOT/UDOT (D + Q) |
| **hip09_neon_fp_div** | **15** | FSU0123 | FDIV (vector) |
| **hip09_neon_fp_sqrt** | **25** | FSU0123 | FSQRT (vector) |
| **hip09_neon_ins** | **4** | **ALUs01** + FSU0123 | DUP/INS (需要整数流水线) |
| **fp_mul_s (neon_fp_mul_s)** | **5** | FSU0123 | 向量FMUL S-form（单独类型）|
| **bfmmla (fp_mla_s_q)** | **9** | FSU0123 | BFMMLA (BF16矩阵乘加) |

### 2.6 SVE 指令

SVE 与 NEON 共享 FSU0-3 流水线；GCC 注释称复用 FSU1/FSU3，但实际 reservation `hip09_fsu02` 定义为 `hip09_fsu0 | hip09_fsu2`，AES 亦使用此 reservation。

| 特性 | 说明 |
|------|------|
| 执行流水线 | 与 NEON 共享 FSU0-3；AES 明确使用 FSU0/FSU2（`hip09_fsu02`） |
| 与 NEON 关系 | SVE 和 NEON 共享 FSU0-3，混合代码注意 FSU 争用 |
| 典型延迟 | SVE load/store 延迟与 NEON 相近；SVE ALU/FMA 延迟参考同类型 NEON 操作 |
| 优化提示 | SVE 与 NEON 共享 FSU，无独立 SVE 专用流水线；尽量与整数/Load-Store 操作交错以利用三个独立 automaton 的并发 |

> 注：GCC `hip09.md` 未为 SVE 单独定义大量 reservation，SVE 指令在调度上复用 NEON/FP 的 FSU reservation。注释“same with fsu1 and fsu3”与 reservation 名 `hip09_fsu02`（FSU0/FSU2）不一致，以 reservation 定义为准。

### 2.7 Crypto 指令

| 指令 | 延迟 | 发射端口 | 备注 |
|------|------|---------|------|
| AES E/MC | **2** | FSU0\|2 (hip09_fsu02) | 双路发射 |
| SHA3 | **1** | **FSU2 only** | 1周期！ |
| SHA1 fast / SHA256 fast / SHA512 / SM3 | **2** | **FSU2 only** | |
| SHA1 slow / SHA256 slow / SM4 | **4** | **FSU2 only** | |
| PMULL | **2** | **FSU2 only** | |

---

## 3. 调优代价模型

> 本节 cost 数值来自 GCC `aarch64-cost-tables.h` 中的 `hip09_extra_costs`，是编译器内部做启发式优化时使用的**相对额外代价**，不等同于 §2 中的流水线延迟。例如 32-bit 整数乘法 cost 为 2，表示在基础指令代价之外额外约 2 个“指令代价单位”，而非 2 个时钟周期。具体延迟请查 §2 指令延迟表。

| 操作 | 32-bit | 64-bit |
|------|--------|--------|
| 整数除法 | 11 | 19 |
| 整数乘法 | 2 | 3 |
| Load | 3 | — |
| Store | 0 | — |
| FP div (S/D) | 10 / 17 | — |
| FP mul (S/D) | 4 / 4 | — |
| FP FMA (S/D) | 4 / 6 | — |
| FP add (S/D) | 4 / 3 | — |
| Vector ALU | 1 | — |
| Vector MUL | 4 | — |

---

## 4. 软件优化建议

### 4.1 整数代码优化

1. **利用4路简单ALU**: HIP09 有4条简单整数流水线（ALUs0-3）。展开循环以填充更多整数指令。

2. **flags指令注意ALU2/3限制**: `adds`/`subs`/`ands` 等只在ALUs2/3上执行（2路而非4路）。对于flags密集型代码，交错简单的非flags指令在ALU0/1上以提升吞吐。

3. **除法仅ALUm0执行**: 32-bit 10周期，64-bit 10周期。双除法将完全串行化。对常除数使用乘法逆。

4. **extend/shift ALU 使用ALUm**: 延迟2周期（ALUm01），2路发射。与简单ALU操作交错可保持吞吐。

5. **乘法 2路发射**: ALUm0和ALUm1均可执行乘法(3cy)，理论上可每1.5周期发射一条乘法指令（双路交替）。

### 4.2 浮点/标量代码优化

1. **FP abs/neg/mov 只需1周期**: FABS/FNEG/FMOV 延迟仅1周期，4路发射。数据移动/符号操作几乎零代价。

2. **FP add/sub 2周期**: 浮点加法吞吐极高，FADD/FSUB 仅2周期延迟，4路发射。

3. **FP mul 3周期, FMA 4周期**: FMA仅比单独mul多1周期，强烈推荐使用FMA：
   ```c
   // HIP09上FMA极有优势
   r = fma(a, b, c);  // 4周期
   // vs mul+add
   t = a * b;         // 3周期
   r = t + c;         // 2周期 + 旁路 = 通常 >5周期
   ```

4. **FP compare 占用整数流水线**: FCMP(4cy)需要 `FSU0123 + ALUs23`。密集的浮点比较会阻塞flags和分支所用的ALU2/3。在关键路径中减少FP比较次数。

5. **fccmp 极重**: 延迟7周期并占用3组资源 (ALUs01+FSU0123+ALUs23)。避免在热循环中使用条件浮点比较。

6. **FP转换需要整数单元**:
   - f2i (5cy): FSU + ALUs23
   - i2f (5cy): ALUs01 + FSU
   在转换密集代码中预留整数流水线。

### 4.3 NEON/SIMD 优化

1. **NEON 基本操作分类与延迟**:

   | 延迟 | 操作类型 |
   |------|---------|
   | **1cy** | ABS/NEG/ADD/SUB/LOGIC/CMP/BSL/TBL1/MOV/FP_ABS/FP_NEG |
   | **2cy** | ABD/ABA/HALVE/REDUC_ADD/FP_ADDSUB/FP_CMP/FP_CVT/FP_ROUND/SHIFT_IMM |
   | **3cy** | MUL/MLA_long/SHIFT_ACC/SHIFT_REG/FP_REDUC/FP_MUL_Q/D |
   | **4cy** | MLA_Q/REDUC_MINMAX/FRECPS/FRSQRTS/TBL4/FP_MLA |
   | **5cy** | 仅 FP_MUL_S (D-form) |
   | **6cy** | SDOT/UDOT |
   | **9cy** | BFMMLA (BF16矩阵乘加) |
   | **15cy** | Vector FP div |
   | **25cy** | Vector FP sqrt |

2. **DOT产品指令 (6cy)**: 比连续mul+add序列有更好的延迟和吞吐。优先使用SDOT/UDOT进行整数点积。

3. **BFMMLA (9cy)**: BF16矩阵乘加为9周期 — 对于AI推理工作负载，这提供了显著的吞吐提升。关键是组织数据为BF16格式以利用此指令。

4. **TBL1/TBL2/TBL3/TBL4 延迟差异**:
   - TBL1: 1周期
   - TBL2: 2周期
   - TBL3: 3周期
   - TBL4: 4周期
   尽量用TBL1/2做查表，避免TBL3/4。

5. **DUP/INS 指令 (4cy)**: 需要ALUs01+FSU0123。频繁的向量插入/提取会影响整数性能。

6. **NEON Load 优化**:
   - **LD1 1-4reg 统一6周期**: LD1 无论加载1个还是4个寄存器统一为6周期延迟
   - **LD4 4reg 13周期**: 最昂贵的交错加载
   - 尽量使用连续加载(LD1)替代交错加载(LD2/3/4)

7. **NEON Store 优化**:
   - ST1 1reg (2cy) → ST1 4reg (5cy): 存储代价随寄存器数线性增长
   - ST3/ST4 需要额外FSU资源
   - 解交织存储用多个ST1代替ST3/ST4可减少FSU争用

### 4.4 SVE 优化

1. **SVE 与 NEON 共享 FSU0-3**: GCC `hip09.md` 未为 SVE 定义独立流水线，SVE 指令复用 NEON/FP 的 FSU reservation。实际可执行的 SVE 吞吐受 FSU0-3 争用限制，尽量与整数/Load-Store 操作交错以利用三个独立 automaton 的并发。

2. **SVE 与 NEON 的关系**: SVE和NEON共享FSU0-3。混合使用SVE和NEON时注意FSU资源争用。

3. **向量长度不可知**: SVE的优势在于向量长度不可知(agnostic)编程。优化代码应使用SVE谓词和while循环结构，而非固定长度循环。

### 4.5 Crypto 优化

- **FSU2 是主要Crypto流水线**: SHA1/SHA256/SHA512/SM3/SM4/PMULL都在FSU2独占
- **AES 在FSU0\|2双路**: AES可在FSU0或FSU2发射
- **SHA3 仅1周期** (FSU2): SHA3哈希运算极快
- **Crypto与SIMD的并行**: AES用FSU0，SHA用FSU2，SIMD mul/shift用其他FSU单元 — 可以实现crypto+SIMD并行

### 4.6 循环优化

1. **展开因子**: 
   - 整数: 4路ALU → 展开4-8x
   - SIMD: 4路FSU → 展开4-8x  
   - Load/Store: 2路LS → 考虑每周期1 load + 1 store

2. **软件流水**: Load延迟4-7周期（取决于类型），预取距离为4-7条指令。

3. **Load/Store 并行**: hip09_ldst automaton独立于hip09/hip09_fsu，可同时进行整数运算、SIMD运算和内存访问。

---

## 5. 调度总结

| 资源 | 每周期吞吐 | 关键独占指令 |
|------|----------|------------|
| ALUs0-3 | 4 | 简单整数 |
| ALUm0-1 | 2 | 移位ALU / 乘法 / CRC |
| ALUm0 only | 1 | **除法** |
| BRU0-1 | 2 | 分支 (+占用ALUs2/3) |
| Load0-1 | 2 | 加载 |
| Store0-1 + STD0-1 | 2 | 存储 |
| FSU0-3 | 4 | FP/SIMD/SVE |
| FSU0\|2 | 2 | AES |
| FSU2 only | 1 | SHA/SM3/SM4/PMULL |

**独立Automaton并发**: hip09 (整数+分支) ‖ hip09_ldst (加载存储) ‖ hip09_fsu (SIMD/FP/SVE)

---

## 6. 性能陷阱

1. ❌ **FCMP/FCVT占用整数流水线**: FCMP需要ALUs23，fcvt需要ALUs01或ALUs23 — FP密度高时整数性能下降
2. ❌ **FCCMP (7cy, 3组资源)**: 避免在热路径使用
3. ❌ **LD4 4reg (13cy)**: 尽可能改用LD1多寄存器或交错LD1
4. ❌ **NEON vector FP div (15cy) / sqrt (25cy)**: 代价极高，用近似指令或查表替代
5. ❌ **ST3/ST4 (7-10cy + FSU)**: 使用多个 ST1 单寄存器存储替代
6. ❌ **分支+调用占用ALUs23**: 调用密集循环中flags计算会受影响
7. ❌ **除法仅在ALUm0**: 双除法完全串行

---

> **参考文件**: `gcc/config/aarch64/hip09.md`, `gcc/config/aarch64/aarch64-cost-tables.h` (`hip09_extra_costs`)
