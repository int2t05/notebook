# TSV110 (TaiShan V110) Software Optimization Guide

> **逆向分析来源**: GCC `gcc/config/aarch64/tsv110.md` pipeline 描述 + `aarch64-cost-tables.h` 调优代价表
> **文档版本**: 基于 GCC 14.3.0 pipeline model 逆向推导
> **ISA**: ARMv8.2-A + Crypto + FP16

---

## 1. 处理器微架构概览

TSV110 是一款高性能 AArch64 乱序执行处理器。GCC 使用 **2 个独立 automaton** 对其建模：

- `tsv110`：整数、分支、Load/Store 域
- `tsv110_fsu`：FP/SIMD 域

这意味着整数/内存操作与 FP/SIMD 操作可以并发发射，但各自域内需要竞争同一组发射槽。

```
                     ┌──────────────────────────────────────────────┐
                     │   Issue Queue (Dispatch) — 2 automata        │
                     │         tsv110  │  tsv110_fsu                │
                     └─────────────────┴────────────────────────────┘
                                          │
        ┌─────────┬─────────┬─────────┬───┴────┬─────────┬─────────┐
        │  ALU1   │  ALU2   │  ALU3   │  MDU   │  BRU1   │   LS    │
        │ (simple)│(simple) │(simple) │(complex)│(on ALU2)│  LS1/2  │
        │  1cy    │  1cy    │  1cy    │ 2-10cy │  0cy    │4cy(L)/0cy(S)
        └─────────┴─────────┴─────────┴────────┴─────────┴─────────┘
                                          │
                              ┌───────────┴───────────┐
                              │    FSU1 (primary)     │    FSU2 (secondary)
                              │  • int mul/shift      │  • int mul/shift
                              │  • fp div             │  • fp sqrt
                              │  • cvti2f             │  • most fp/SIMD
                              │  • crypto             │
                              └───────────────────────┴──────────────────────┘
```

### 关键执行单元

| 单元 | 数量 | 功能 | 备注 |
|------|------|------|------|
| **ALU** (simple) | 3 (ALU1/2/3) | 基本整数运算、逻辑、移位 | 1周期延迟 |
| **MDU** | 1 | 移位+ALU、乘法、除法 | 2-10周期 |
| **BRU** | 2 (复用ALU2/3) | 分支预测执行 | 2 个 BRU 复用 ALU2/3，每条分支占 1 个 slot，无结果延迟 |
| **LS** | 2 (LS1/2) | Load/Store | Load 4周期，Store 0周期 |
| **FSU1** (主要) | 1 | NEON整数乘/移位、FP除、cvtf2i、crypto | 非对称流水线 |
| **FSU2** (次要) | 1 | FP sqrt、大部分FP/SIMD操作 | 非对称流水线 |

---

## 2. 指令延迟与吞吐量

### 2.1 整数指令

| 指令类别 | 延迟 (cycles) | 发射端口 | 备注 |
|----------|--------------|---------|------|
| ALU 基本 (add/sub/and/or/xor/mov) | 1 | ALU1/2/3 | |
| ALU + 立即数移位 (lsl 1-4) | 2 | MDU | extend 类 |
| ALU + 寄存器移位 | 2 | MDU | |
| ALU + flags 设置 (adds/subs/ands) | 1 | ALU2/3 | 仅 ALU2/3 |
| ALUs + 移位 (adds_shift etc.) | 2 | ALU2/3 | |
| 乘法 (32-bit) | 3 | MDU | MUL/MADD/MSUB |
| 乘法 (64-bit) | 3 | MDU | UMULH/SMULH |
| 除法 (32-bit) | 10 | MDU | SDIV/UDIV |
| 除法 (64-bit) | 10 | MDU | |
| CRC | 2 | MDU | |
| CLZ/RBIT/REV | 1 | ALU1/2/3 | |
| BFM/MOVN/MOVZ | 1 | ALU1/2/3 | |
| ADR | 1 | ALU1/2/3 | |

### 2.2 分支指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| 分支 (B/BR/RET) | 0 | ALU2 \| ALU3 | BRU 复用 ALU2/3，每条分支占 1 个 slot，无结果延迟 |
| 调用 (BL/BLR) | 1 | 全部 8 个 issue slot | 阻塞所有发射槽 1 周期 |

### 2.3 Load/Store 指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| Load 32/64-bit | 4 | LS1/2 | LDR/LDRSW |
| Store 32/64-bit | 0 | LS1/2 | STR，无结果延迟 |

### 2.4 标量浮点指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| FP move/const | 2 | FSU1/2 | FMOV, FCONST |
| FP abs/neg/minmax | 2 | FSU1/2 | FABS/FNEG/FMIN/FMAX |
| FP add/sub | 5 | FSU1/2 | FADD/FSUB |
| FP multiply | 5 | FSU1/2 | FMUL |
| FP FMA (fused multiply-add) | 7 | FSU1/2 | FMADD/FMSUB/FNMADD/FNMSUB |
| FP divide (single) | 12 | **FSU1 only** | FDIV (S) |
| FP divide (double) | 12 | **FSU1 only** | FDIV (D) |
| FP sqrt (single) | 24 | **FSU2 only** | FSQRT (S) |
| FP sqrt (double) | 24 | **FSU2 only** | FSQRT (D) |
| FP compare | 4 | FSU1/2 | FCMP |
| FP convert (f2f) | 3 | FSU1/2 | FCVT float→float |
| FP convert (f2i) | 4 | **FSU1 only** | FCVTZS/FCVTMS etc. |
| FP convert (i2f) | 5 | ALU1+FSU1\|FSU2 | SCVTF/UCVTF，占用ALU1+FSU |

**关键约束**: FP除法和i2f转换**仅能在FSU1执行**。FP sqrt**仅能在FSU2执行**。混合除法和sqrt可以流水线化（不同端口），但双除法或双sqrt将串行化。

### 2.5 NEON/ASIMD 整数指令

TSV110 使用自定义的 `tsv110_neon_type` 属性进行细致分类：

| 类别 | 指令类型 | 延迟 | 发射端口 |
|------|---------|------|---------|
| **neon_arith_basic** | ADD/SUB/NEG/ABS/CMP/LOGIC/MINMAX (D-form) | 2 | FSU1/2 |
| **neon_arith_complex** | QADD/QSUB/QABS/QNEG (saturating) | 4 | FSU1/2 |
| **neon_arith_acc** | ABD/ABA/ADDL/ADALP | 4 | FSU1/2 |
| **neon_arith_acc_q** | ABD_Q/ABA_Q (128-bit accumulate) | 4 | FSU1/2 |
| **neon_multiply** | MUL/MLA/MLS (D-form, all types) | 4 | **FSU1** |
| **neon_multiply_q** | MUL/MLA/MLS (Q-form, all types) | 8 | **FSU1** |
| **neon_multiply_long** | MUL long (D-form) | 2 | **FSU1** |
| **neon_shift_acc** | SSRA/USRA/SRSRA (shift+acc) | 4 | **FSU1** |
| **neon_shift_imm** | SHL/SSHR/USHR (imm) | 4 | **FSU1** |
| **neon_shift_reg** | SSHL/USHL/RSHL (reg) | 4 | **FSU1** |
| **neon_shift_reg_q** | Shift reg Q-form | 4 | **FSU1** |
| **neon_bitops** | BSL/CLS/CNT/REV/TBL1/2/ZIP/DUP/EXT/MOV (D) | 2 | FSU1/2 |
| **neon_bitops_q** | BSL_Q/CLS_Q/CNT_Q/REV_Q (Q-form bit) | 2 | FSU1/2 |
| **neon_from_gp** | DUP/MOV (from GP→SIMD, D-form) | 2 | FSU1/2 |
| **neon_from_gp_q** | DUP/MOV (from GP→SIMD, Q-form) | 4 | **ALU1+FSU1\|FSU2** |
| **neon_to_gp** | UMOV/SMOV (SIMD→GP) | 3 | **FSU1** |
| **neon_tbl3_tbl4** | TBL3/TBL4 | — | (归入加载类) |

**关键约束**: 
- **所有 NEON 整数乘法、移位在FSU1独占执行** — 这意味着D-form乘法和Q-form乘法互相竞争，且无法与FP除法并行。
- Q-form 乘法延迟为 D-form 的2倍 (8 vs 4 cycles)

### 2.6 NEON/ASIMD 浮点指令

| 类别 | 指令类型 | 延迟 | 发射端口 |
|------|---------|------|---------|
| **neon_fp_negabs** | FABS/FNEG/FMINMAX (S/D) | 2 | FSU1/2 |
| **neon_fp_arith** | FADD/FSUB/FABD/FRECPS/FRSQRTS/FCMP/FRINT (D) | 4 | FSU1/2 |
| **neon_fp_arith_q** | FADD_Q/FSUB_Q/FABD_Q/FCMP_Q (Q-form) | 4 | FSU1/2 |
| **neon_fp_reductions_q** | FADDP_Q/FMAXNMV_Q/FMINNMV_Q | 4 | FSU1/2 |
| **neon_fp_cvt_int** | FCVT (int↔fp), D + Q | 2 | FSU1/2 |
| **neon_fp_cvt16** | FCVT narrow/widen (16-bit) | — | (归入fp_cvt类) |
| **neon_fp_mul** | FMUL/ FMULX (D-form) | 5 | FSU1/2 |
| **neon_fp_mul_q** | FMUL_Q/ FMULX_Q | 5 | FSU1/2 |
| **neon_fp_mla** | FMLA/FMLS + FRECPS/FRSQRTS (D) | 7 | FSU1/2 |
| **neon_fp_mla_q** | FMLA_Q/FMLS_Q + FRSQRTS_Q (Q) | 7 | FSU1/2 |
| **neon_fp_recpe_rsqrte** | FRECPE/FRSQRTE/FRECPX (D) | 3 | FSU1/2 |
| **neon_fp_recpe_rsqrte_q** | FRECPE_Q/FRSQRTE_Q/FRECPX_Q | 3 | FSU1/2 |
| **neon_fp_recps_rsqrts** | FRECPS/FRSQRTS (D) | 7 | FSU1/2 |
| **neon_fp_recps_rsqrts_q** | FRECPS_Q/FRSQRTS_Q (Q) | 7 | FSU1/2 |
| **fp_minmax_q** | FMINMAX (Q-form) | 2 | FSU1/2 |

**重要**: NEON FP mul 延迟(5)与标量FP mul(5)一致。NEON FP FMA 延迟(7)也与标量一致。但NEON有更高吞吐量的位操作和算术(2-4cy)。

### 2.7 NEON Load/Store 指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| LD1 1reg / f_load | 6 | LS1/2 | 单寄存器加载 |
| LD1 2reg | 6 | LS1/2 | 双寄存器加载，1个发射 |
| LD1 3reg | 7 | LS1/2 | 三寄存器加载 |
| LD1 4reg | 7 | LS1/2 | 四寄存器加载 |
| LD1 lane / LD1 all_lanes | 8 | **LS+FSU** | 需要LS+FSU联合发射 |
| LD2 (2reg) | 8 | **LS+FSU** | |
| LD3 (3reg) | 9 | **LS+FSU** | |
| LD4 lane | 9 | **LS+FSU** | |
| LD4 reg | 11 | **LS+FSU** | |
| ST1 1reg | 0 | FSU1/2 | GCC model 将简单 vector store 归入 FSU reservation |
| ST1 2reg | 0 | FSU1/2 | 同上 |
| ST complex (3/4reg, lane) | 0 | **阻塞全部端口2周期** | 高代价！|

> **关于 vector store 走 FSU 的说明**：TSV110 GCC pipeline model 把 `neon_store_a/b` 这类简单 vector store 的 reservation 放在 `tsv110_fsu` automaton 中（延迟 0）。这表示调度器认为它们占用 FP/SIMD 域的发射资源，**不等于** store 数据实际经过浮点执行单元。复杂 store（ST3/ST4 等）则通过 `tsv110_block` 阻塞全部 8 个 issue slot。

### 2.8 Crypto 指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| AES E/MC | 3 | **FSU1** | AESE/AESMC |
| SHA1 fast (H/SU1) | 2 | FSU1/2 | |
| SHA256 fast (H/SU0) | 2 | **FSU1** | |
| SHA1 slow (C/P/M) | 5 | **FSU1** | |
| SHA256 slow | 5 | **FSU1** | |

---

## 3. 数据旁路 (Bypass)

| 生产者 → 消费者 | 旁路延迟 | 说明 |
|----------------|---------|------|
| ALU → ALU/ALU_shift | **1** | 整数ALU结果可在1周期后使用 |
| ALU_shift → ALU/ALU_shift | **2** | 移位结果需2周期旁路 |
| NEON MLA/MUL → MLA | **3** | 乘加结果可快速馈入下一次乘加 |
| 通用 → BRANCH/CALL | **1** | 分支预测正确时无需额外延迟 |

---

## 4. 调优代价模型 (Cost Model)

从 `aarch64-cost-tables.h` 的 `tsv110_extra_costs` 表提取：

| 操作 | 32-bit代价 | 64-bit代价 |
|------|-----------|-----------|
| 整数除法 | 11 | 19 |
| 整数乘法 | 2 | 3 |
| Load | 3 | — |
| Store | 0 | — |
| FP div (S/D) | 10 / 17 | — |
| FP mul (S/D) | 4 / 4 | — |
| FP FMA (S/D) | 4 / 6 | — |
| FP add/sub (S/D) | 4 / 3 | — |
| Vector ALU | 1 | — |
| Vector MUL | 4 | — |
| Vector MOVI/DUP/EXT | 1 / 2 / 2 | — |

---

## 5. 软件优化建议

### 5.1 整数代码优化

1. **ALU移位链最小化**: 带移位的ALU操作延迟为2周期（通过MDU），而简单ALU操作为1周期。尽可能用简单ALU + 独立移位代替 ALU-with-shift。

   ```asm
   ;; 推荐: 分离移位和运算
   lsl  x1, x0, #3      ;; 1cy on ALU
   add  x2, x1, x3      ;; 1cy on ALU  → 总计2cy，但双发射友好

   ;; 避免: 合并移位ALU (若不必要)
   add  x2, x3, x0, lsl #3  ;; 2cy on MDU → 占用MDU资源
   ```

2. **flags设置指令优先放ALU2/3**: `adds`/`subs`/`ands` 等flags设置指令只能在ALU2/3执行（不能发到ALU1）。若有密集的flags计算，注意ALU1无法参与。

3. **除法代价极高**: 32-bit除法10周期，64-bit除法10周期。对于编译时常量除数，使用乘法逆替换。对于循环中除数不变的情况，将除法提升到循环外。

4. **乘法吞吐**: 所有乘法通过单一MDU流水线。连续乘法将串行化。必要时交错其他MDU操作（移位+ALU等）以利用旁路。

5. **CRC与CLZ/REV**: CRC为2周期（MDU），CLZ/REV为1周期（ALU）。CRC密集型代码要注意MDU拥塞。

### 5.2 浮点/标量代码优化

1. **FP FMA优先**: 虽FMA延迟(7)高于独立mul(5)+add(5)，但FMA精度更高、指令数更少，且避免中间舍入。对于关键循环中的乘加序列，FMA是更优选择。

   ```c
   // 推荐: 使用 fma()
   r = fma(a, b, c);   // 1条fma指令，7周期

   // 避免: 分离乘加 (除非有并行工作填充延迟)
   t = a * b;           // 5周期
   r = t + c;           // 5周期 → 总计10周期（无旁路）
   ```

2. **FP除法与sqrt流水线化**: FP除法(12cy, FSU1)和FP sqrt(24cy, FSU2)使用不同端口。可以并行发射除法和sqrt指令！

3. **FP转换代价不对称**:
   - f2i (cvtf2i): 4周期，FSU1独占
   - i2f (cvti2f): 5周期，**还占用ALU1**！对i2f密集代码要预留ALU1

4. **FP比较相对慢**: FCMP为4周期，而整数比较为1周期。减少不必要的FP比较，或尽早将FP值转为整数再比较。

### 5.3 NEON/SIMD 优化

1. **D-form优先于Q-form**: Q-form整数乘法(8cy)是D-form(4cy)的2倍。对于可以拆分为两个64-bit操作的数据并行任务，优先使用D-form指令序列，特别是当FSU1资源空闲时。

2. **FSU1/FSU2非对称性利用**:
   | FSU1专属 | FSU2专属 | 共享 |
   |----------|----------|------|
   | NEON 整数乘/移位 | FP sqrt | NEON arith/logic |
   | FP div | | FP mul/FMA |
   | cvti2f | | bitops |
   | crypto AES/SHA | SHA1 fast | |

   **策略**: 将整数乘法和FP sqrt交叠调度，它们使用不同端口，可并行执行。

3. **乘加链优化**: MUL→MLA旁路为3周期。连续MLA指令的发射间隔可缩短至3周期而非4周期。组织乘加序列以利用此旁路。

4. **NEON Load/Store 策略**:
   - **LD1 1reg/2reg** (6cy) 是最快的向量加载方式
   - **LD2/LD3/LD4** 需要LS+FSU联合资源，延迟更高(8-11cy)
   - **Store complex** (多寄存器/交叉存储)会*阻塞所有发射槽2周期* — 这是最重要的性能陷阱！
   - 考虑用多个 ST1 1reg 代替 ST2/ST3/ST4

   ```asm
   ;; 推荐: 分开 ST1
   st1  {v0.4s}, [x0]        ;; 0cy，仅FSU
   st1  {v1.4s}, [x0, #16]   ;; 0cy，仅FSU

   ;; 避免: 多寄存器store（阻塞所有端口）
   st2  {v0.4s, v1.4s}, [x0]  ;; 0cy，但阻塞全部端口×2！
   ```

5. **TBL指令优化**: TBL1/TBL2归类为bitops（2cy），相对快。TBL3/TBL4归入复杂加载（高延迟）。尽量使用TBL1/TBL2置换。

6. **SIMD→GP传输代价**: NEON→GP (UMOV/SMOV) 延迟3周期且FSU1独占。GP→SIMD Q-form (DUP Q) 延迟4周期且占用ALU1。尽量减少向量-标量寄存器间的数据传输。

### 5.4 Crypto 优化

- **AES**: 3周期(FSU1)，适合流水线化AES轮函数
- **SHA256 fast**: 2周期但FSU1独占 — 不能与乘法/除法的SHA并行
- **SHA1 slow** (5周期): 尽可能地使用SHA1 fast路径
- AES和SHA可以交替（都在FSU1但可能不同周期交错）

### 5.5 循环优化

1. **展开因子**: `tsv110` 与 `tsv110_fsu` 独立调度，每周期可并发发射整数/LS 域指令（最多 3 ALU + 1 MDU + 2 LS）和 FP/SIMD 域指令（2 FSU）。最小展开因子建议 4-6 以填满两域发射槽。

2. **软件流水**: Load延迟4周期，对于数组遍历，至少提前4次迭代预取。

3. **Load/Store平衡**: 2个LS单元可每周期发出1个load + 1个store。

---

## 6. 调度总结

| 资源 | 每周期吞吐 | 关键指令 |
|------|----------|---------|
| ALU1 | 1 | 简单整数 |
| ALU2 | 1 | 简单整数 + flags + 分支 |
| ALU3 | 1 | 简单整数 + flags + 分支 |
| MDU | 1 | 移位ALU / 乘法 / 除法 / CRC |
| FSU1 | 1 | NEON mul/shift / FP div / AES / SHA |
| FSU2 | 1 | NEON arith / FP sqrt / SHA1 fast |
| LS1 | 1 | Load 或 Store |
| LS2 | 1 | Load 或 Store |

**总发射宽度**: 由于 `tsv110` 和 `tsv110_fsu` 是两个独立 automaton，两域可并发：

- 整数/LS 域（`tsv110`）：最多可同时使用 3 ALU + 1 MDU + 2 LS = **6 个 issue slot**（BRU 复用 ALU2/3 的 slot）
- FP/SIMD 域（`tsv110_fsu`）：最多可同时使用 **2 FSU**
- 理论峰值：整数/LS 域 6 + FP/SIMD 域 2 = **8 个 issue slot/周期**

> 注：复杂 store（ST2/ST3/ST4/lane）通过 `tsv110_block` 同时占用全部 8 个 issue slot，因此§7称为“阻塞全部8个端口”。

实际指令吞吐 = min(指令延迟链, 端口冲突, 发射宽度)。

---

## 7. 性能陷阱 (Performance Pitfalls)

1. ❌ **NEON Complex Store (ST2/ST3/ST4/ST-lane)**: 阻塞**全部8个端口** 2周期 — 绝对的调度障碍
2. ❌ **双FP除法**: 都需FSU1，完全串行化（12+12=24周期）
3. ❌ **NEON Q-form乘法链**: 8周期延迟 + FSU1独占
4. ❌ **i2f转换密集**: 占用ALU1+FSU，影响整数运算
5. ❌ **MDU拥塞**: 乘法和带移位ALU共享MDU，连续乘法会阻塞后续移位操作
6. ❌ **LD3/LD4 加载**: 9-11周期 + 占用LS+FSU双资源

---

> **参考文件**: `gcc/config/aarch64/tsv110.md`, `gcc/config/aarch64/aarch64-cost-tables.h` (`tsv110_extra_costs`)
