# HIP12 Software Optimization Guide

> **逆向分析来源**: GCC `gcc/config/aarch64/hip12.md` pipeline 描述 + `aarch64-cost-tables.h` 调优代价表
> **文档版本**: 基于 GCC 14.3.0 pipeline model (贡献者: liyunfei) 逆向推导
> **ISA**: ARMv9.2-A + SVE2 + SVE2_BITPERM + SVE2_AES + SVE2_SM4 + SVE2_SHA3 + BF16 + DOTPROD + LSE + PAUTH + RDMA + LS64 + RNG
> **HiSilicon Implementer ID**: 0x48, Part: 0xd06

---

## 1. 处理器微架构概览

HIP12 是目前三代中最先进的 AArch64 处理器，采用三个独立 automaton 进行建模（hip12, hip12_ldst, hip12_v），暗示了深度的乱序执行和解耦的流水线设计。

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                  Issue (3 independent queues)             │
                    └──────────────────────────────────────────────────────────┘
                               │                      │
    ┌──────────────────────────┤                      ├────────────────────────┐
    │    hip12 automaton       │    hip12_ldst        │    hip12_v             │
    │                          │    automaton         │    automaton           │
    │  ┌─ ALU0 ─┐ ┌─ ALU2 ─┐  │                      │                        │
    │  │ ALU1   │ │ ALU5   │  │  ┌─ Load0 ─┐         │  ┌─ V0 ─┐ ┌─ V2 ─┐    │
    │  │ ALU3   │ └────────┘  │  │ Load1   │         │  │ V1   │ │ V3   │    │
    │  │ ALU4   │  (complex)  │  │ Load2   │         │  └──────┘ └──────┘    │
    │  └────────┘             │  └─────────┘         │  4 asymmetric SIMD/FP  │
    │  4 simple ALU           │  ┌─ Store0 ─┐        │  /SVE pipelines        │
    │                          │  │ Store1   │        │                        │
    │  ┌─ B0 ───┐             │  └──────────┘        │                        │
    │  │ B1     │             │  ┌─ STD0 ───┐        │                        │
    │  └────────┘             │  │ STD1     │        │                        │
    │  2 branch units         │  └──────────┘        │                        │
    └─────────────────────────┴──────────────────────┴────────────────────────┘
```

### 关键执行单元

| 单元 | 数量 | automaton | 功能 | 备注 |
|------|------|-----------|------|------|
| **ALU simple** | 4 (0,1,3,4) | hip12 | 单周期整数操作 | ALU2/5为复杂流水线 |
| **ALU complex** | 2 (2,5) | hip12 | 多周期整数（移位/extend/乘/除）| 共享端口 |
| **Branch** | 2 (B0,B1) | hip12 | 分支 | |
| **Load** | 3 (Load0-2) | hip12_ldst | 加载 | 3路load流水线 |
| **Store** | 2 (Store0-1) | hip12_ldst | 存储地址 | |
| **Store Data** | 2 (STD0-1) | hip12_ldst | 存储数据 | |
| **V (FP/SIMD/SVE)** | 4 (V0-3) | hip12_v | FP/SIMD/SVE | 非对称 |

---

## 2. 指令延迟与吞吐量

### 2.1 整数指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| ALU 基本 (add/sub/and/or/xor/adc) | **1** | **全部6路ALU** | 最大发射宽度 |
| ALU flags (adds/subs/adcs) | **1** | ALU1\|4\|2\|5 (hip12_alu1425) | 4路发射 |
| ALUs flags (logics_reg) | 1 | ALU1\|4\|2\|5 | |
| ALUs flags imm (logics_imm) | **2** | ALU2\|5 (hip12_alu25) | flags+imm走复杂流水线！|
| ALU extend (uxtb/sxtb etc.) | **2** | ALU2\|5 | |
| ALU shift (lsl/lsr/asr 1-4/other/reg) | **2** | ALU2\|5 | |
| ALU shift + flags | 2 | ALU2\|5 | |
| logic imm | **1** | **全部6路ALU** | 注意：源码中后定义的 ALU1/4 限制因顺序问题不生效 |
| CSEL | **1** | ALU1\|4 | |
| MOV imm / MOV shift reg | 1 | 全部6路ALU | |
| CLZ | 1 | ALU1\|4 | |
| RBIT/REV | 1 | ALU1\|4 | |
| BFM/BFX | 1 | ALU1\|4 | |
| ADR | 1 | ALU1\|4 | |
| shift reg (variable) | 1 | ALU1\|4 | |
| **乘法 MUL/MULS** | **3** | ALU2\|5 | 2路发射 |
| **乘法 long SMULL/UMULL** | **2** | ALU2\|5 | 比普通乘法快！|
| **乘加 MLA/MLAS** | **4** | ALU2\|5 + **ALU0134** | 占用双资源！|
| **乘加 long SMLAL/UMLAL** | **3** | ALU2\|5 + **ALU0134** | |
| **除法 SDIV/UDIV** | **8** | ALU2\|5 | 32/64-bit统一8周期 |
| CRC | **2** | ALU2\|5 | |

**关键约束**:
- `logic_imm`（无 flags 逻辑立即数，如 `and x0, x1, #imm`）延迟 1 周期，**实际可走全部 6 路 ALU**。GCC 源中虽然后定义了一个 `hip12_alu_logical_imm`（仅 ALU1/4），但它被前面包含 `logic_imm` 的 `hip12_alu_logical`（全部 6 路）覆盖，因此特定限制并不生效。
- `logics_imm`（带 flags 逻辑立即数，如 `ands x0, x1, #imm`）延迟 2 周期，**仅在 ALU2/5 执行（2路）**，走复杂流水线。
- `logics_reg`（带 flags 逻辑寄存器，如 `ands x0, x1, x2`）延迟 1 周期，可在 ALU1/4/2/5 执行（4路）。
- MLA 同时占用复杂 ALU（ALU2/5）和简单 ALU（ALU0/1/3/4）双资源。

> **命名提示**：`logic_imm` 与 `logics_imm` 只差一个 `s`，前者无 flags，后者设置 flags，端口和延迟均不同，请勿混淆。
> **GCC reservation 顺序提示**：当多个 `define_insn_reservation` 匹配同一指令 type 时，其 reservation 取并集。因此 `logic_imm` 实际使用 `hip12_alu`（6路），而不是后面定义的 `hip12_alu14`（2路）。

### 2.2 分支指令

| 指令类别 | 延迟 | 发射端口 | 占用 |
|----------|------|---------|------|
| 分支 (B/BR) | **1** | B0\|1 | 仅BRU |
| 调用 (BL/BLR) | **1** | B0\|1 + ALU1\|4 | BRU + ALU |

**注意**: 分支延迟仅1周期，且简单分支(B/BR)不占用ALU（仅BRU），调用(BL)占用BRU+ALU1/4。

### 2.3 Load/Store 指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| Load 32/64-bit | **4** | LD0\|1\|2 (hip12_ld) | 3路load |
| Load pair (16-byte) | **4** | LD0\|1\|2 | |
| Store 32/64-bit | **1** | ST0\|1 + STD0\|1 | |
| Store pair (16-byte) | **1** | ST0\|1 + STD0\|1 | |
| FP load (s/d) | **6** | LD0\|1\|2 | |
| FP load vector pair | **6** | ALU + LD | |
| FP store (s/d) | **1** | ST + STD | |
| FP store vector (neon_ldr) | **3** | ALU + ST + STD | GCC 将 vector store 复用 `neon_ldr` type |
| FP store pair | **1** | ST + STD + ALU | `neon_ldp`/`neon_ldp_q` |
| NEON LD1 1/2reg | **6** | LD0\|1\|2 | |
| NEON LD1 3/4reg | **7** | LD0\|1\|2 | |
| NEON LD1 lane/all_lanes | **8** | LD + V | |
| NEON LD2 (2reg/4reg/lane) | **8** | LD + V | |
| NEON LD3 | **8** | LD + V | |
| NEON LD4 reg | **10** | LD + V | |
| NEON LD4 lane | **8** | LD + V | |
| NEON ST1 1/2/4reg (64-bit) | **1** | ST + STD + V | `neon_store1_1/2/4reg` |
| NEON ST1 3reg | **1** | ST + STD + V | |
| NEON ST1 4reg Q (128-bit) | **4** | ST + STD | `neon_store1_4reg_q` |
| NEON ST1 lane / ST2 | **1** | ST + STD | |
| NEON ST3 3reg / ST4 (Q) | **4** | V + ST + STD | |
| NEON ST4 4reg | **4** | V + ST + STD | |

**分析**: 
- 基本 Store（32/64-bit、pair、大多数 NEON ST1/ST2）延迟仅 1 周期，这是很大的改进。
- 3 路 Load 流水线可在高带宽代码中提供更好的内存级并行。
- 注意 `NEON ST1 4reg`（64-bit 形式）走 ST+STD+V，延迟 1；而 `NEON ST1 4reg Q`（128-bit 形式，GCC type `neon_store1_4reg_q`）延迟 4 且不占 V 单元。宽向量存储代价更高。

### 2.4 标量浮点指令

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| FP abs/neg (ffariths/d) | **1** | V0123 | 4路，1周期 |
| FP add (fadd/fsub) | **2** | V0123 | |
| FP min/max | **2** | V0123 | |
| FP multiply (fmul) | **3** | V0123 | |
| FP FMA (ffmad/ffmas) | **4** | V0123 | |
| FP compare (fcmp) | **2** | **V02** + ALU0134 | 仅V0/V2，占用ALU |
| FP CCMP (fccmp) | **4** | ALU14 → V0123 | 双周期级联 |
| FP CSEL (fcsel) | **6** | ALU14 → V0123 | 高延迟！ |
| FP div single | **6** | V0123 | |
| FP div double | **8** | V0123 | |
| FP sqrt single | **6** | V0123 | |
| FP sqrt double | **8** | V0123 | |
| FP convert f2f (fcvt) | **3** | V0123 | |
| FP convert f2i | **5** | V0123 | |
| FP convert i2f | **7** | **ALU14** → V0123 | 重！占用ALU且级联 |
| FP move (fmov) | **2** | V0123 | |
| FP move GP→V (f_mcr) | **4** | ALU14 | |
| FP move 2×GP→V (f_mcrr) | **10** | ALU14 → (3 cycles) → ALU14 → V0123 | 两阶段级联，极重！ |
| FP move V→GP (f_mrc/mrrc) | **2** | V0123 | |

### 2.5 ASIMD/NEON 整数指令

HIP12 直接按GCC标准type属性进行分类，将许多相似指令类型汇总到统一的延迟组：

| 指令类别 | 延迟 | 发射端口 | 备注 |
|----------|------|---------|------|
| **neon_arith_basic** (ABS/NEG/ADD/SUB) | **1** | V0123 | |
| **neon_arith_long** (ADDL/SUBL) | **2** | V0123 | |
| **neon_arith_wide** (ADDW/SUBW) | **1** | V0123 | 扩展运算也是1周！|
| **neon_arith_complex** (QADD/QSUB/QNEG/QABS) | **2** | V0123 | 饱和运算2周期 |
| **neon_arith_reduce** (ADDP/[SU]ADALP) | **3** | V0123 | |
| **neon_arith_cmp** (CMP/CMP_ZERO/TST) | **2** | V0123 | |
| **neon_logical** (AND/ORR/EOR/BIC) | **1** | V0123 | |
| **neon_abd** (ABD/ABD_LONG) | **2** | V0123 | |
| **neon_dot** (SDOT/UDOT) | **3** | V0123 | 仅3周期，吞吐极高 |
| **neon_minmax** (SMIN/SMAX/UMIN/UMAX) | **2** | V0123 | |
| **neon_reduc_minmax** | **2** | V0123 | |
| **neon_multiply** (MUL/MLA all types) | **3** | V0123 | 统一3周期 |
| **neon_mla** (MLA/MLS all types) | **3** | V0123 | |
| **neon_shift** (SHIFT_IMM/REG all) | **2** | V0123 | 统一2周期 |
| **neon_shift_acc** (SSRA/USRA/SRSRA) | **3** | V0123 | |
| **neon_fp_abs/neg** | **1** | V0123 | |
| **neon_fp_abd** | **2** | V0123 | |
| **neon_fp_arith** (FADD/FSUB) | **2** | V0123 | |
| **neon_fp_compare** | **2** | V0123 | |
| **neon_fp_cvt_narrow** | **4** | V0123 | |
| **neon_fp_cvt_2int** (D) | **3** | V0123 | |
| **neon_fp_cvt_2int_q** | **4** | V0123 | |
| **neon_fp_cvt_from_int** (D) | **3** | V0123 | |
| **neon_fp_cvt_from_int_q** | **4** | V0123 | |
| **neon_fp_div_s** (D/F32) | **6** | V0123 | |
| **neon_fp_div_s_q** (Q/F32) | **7** | V0123 | |
| **neon_fp_div_d** (Q/F64) | **9** | V0123 | |
| **neon_fp_sqrt_s** (D/F32) | **6** | V0123 | |
| **neon_fp_sqrt_s_q** (Q/F32) | **7** | V0123 | |
| **neon_fp_sqrt_d** (Q/F64) | **9** | V0123 | |
| **neon_fp_minmax** | **2** | V0123 | |
| **neon_fp_reduc_minmax** | **3** | V0123 | |
| **neon_fp_multiply** | **3** | V0123 | |
| **neon_fp_mla** | **4** | V0123 | |
| **neon_fp_round** (D) | **3** | V0123 | |
| **neon_fp_round_q** | **4** | V0123 | |
| **neon_fp_recpe/rsqrte** (D) | **3** | V0123 | |
| **neon_fp_recpe/rsqrte_q** | **4** | V0123 | |
| **neon_fp_recpx** | **3** | V0123 | |
| **neon_fp_recps/rsqrts** | **4** | V0123 | |
| **neon_rbit** | **1** | V0123 | |
| **neon_bsl** | **1** | V0123 | |
| **neon_cls** | **1** | V0123 | |
| **neon_cnt** (B/H) | **1** | V0123 | |
| **neon_cnt_q** (S/D) | **2** | V0123 | |
| **neon_dup** | **6** | V0123 + ALU0134 | 重！ |
| **neon_ext** | **2** | V0123 | |
| **neon_ins** | **2** | V0123 | |
| **neon_move** (ORR/MOV/ narrow) | **2** | V0123 | |
| **neon_rev** | **2** | V0123 | |
| **neon_tbl1/tbl2** | **2** | V0123 | |
| **neon_tbl3** | **4** | V0123 | |
| **neon_tbl4** | **4** | V0123 | |
| **neon_zip** | **2** | V0123 | |

### 2.6 Crypto 指令

| 指令 | 延迟 | 发射端口 | 备注 |
|------|------|---------|------|
| AES E/MC | **2** | V0123 | 4路发射 |
| PMULL | **2** | V0123 | |
| SHA1 fast (H/SU1/XOR) | **2** | V0123 | |
| SHA256 fast | **2** | **V02 only** | 有限制 |
| SHA1 slow (C/P/M) | **4** | V0123 | |
| SHA256 slow | **4** | **V02 only** | 有限制 |
| SHA512 | **2** | **V02 only** | |
| SHA3 | **2** | V0123 | |
| SM3 | **2** | **V02 only** | |
| SM4 | **4** | V0123 | |

### 2.7 SVE2 指令

SVE/SVE2 操作在 V0-3 流水线上执行，4路发射。SVE2独有的 BITPERM/AES/SM4/SHA3 扩展提供了向量化版本的加密操作。

---

## 3. 数据旁路 (Bypass)

| 生产者 → 消费者 | 旁路延迟 | 说明 |
|----------------|---------|------|
| FMA → FMA | **2** | FMA链可紧密耦合 |
| DOT → DOT | **2** | 点积链快速旁路 |
| MLA → MLA | **2** | 乘加结果2周期后可再乘加 |
| SHIFT_ACC → SHIFT_ACC | **1** | 移位累加最快旁路（仅1周期！）|
| FP_MLA → FP_MLA | **2** | |
| FP_RECPS → FP_RECPS | **2** | Newton-Raphson迭代快速 |

---

## 4. 调优代价模型 (从 hip12_extra_costs)

> 本节 cost 数值来自 GCC `aarch64-cost-tables.h` 中的 `hip12_extra_costs`，是编译器内部做启发式优化时使用的**相对额外代价**，不等同于 §2 中的流水线延迟。例如 32-bit 整数乘法 cost 为 1，表示在基础指令代价之外额外约 1 个“指令代价单位”，总代价约 2。具体延迟请查 §2 指令延迟表。

| 操作 | 32-bit | 64-bit |
|------|--------|--------|
| 整数除法 | **5** | **7** |
| 整数乘法 | 1 | 2 |
| Load | 3 | — |
| Store | 0 | — |
| FP div (S/D) | **5** | **7** |
| FP mul (S/D) | **2** | **2** |
| FP FMA (S/D) | **3** | **3** |
| FP add (S/D) | **1** | **1** |
| Vector ALU | 1 | — |
| Vector MUL | **2** | — |
| Vector MOVI/DUP/EXT | 1 / 1 / 1 | — |

---

## 5. 软件优化建议

### 5.1 整数代码优化

1. **`logics_imm` 注意 ALU2/5 限制**：带 flags 的逻辑立即数（如 `ands x0, x1, #imm`）延迟 2 周期且仅在 ALU2/5 执行（2路）。注意 `tst #imm`/`cmp #imm` 与 `ands #imm` 同属 `logics_imm`/`alus_imm`，同样走复杂流水线，因此简单拆分为 `and #imm + tst #imm` 并不能降低 flags 路径延迟。若需同时得到结果和 flags，应预加载常量到寄存器，用寄存器形式避开立即数瓶颈。

   ```asm
   ;; 推荐: 预加载常量到寄存器，使用寄存器形式
   mov  x2, #mask             ;; 循环外预加载
   and  x0, x1, x2            ;; logic_reg, 1cy, 6路
   tst  x1, x2                ;; logics_reg, 1cy, 4路（与 and 并行发射，优于 tst #imm 的 2cy/2路）

   ;; 避免:
   ands x0, x1, #0xff00ff00  ;; logics_imm, 2cy, 仅ALU2/5
   ```

2. **乘加 MLA 占用双资源**: MLA(4cy)同时占用ALU2/5和ALU0134。这会同时消耗一个复杂ALU和一个简单ALU的发射槽。

   > **不建议无条件拆成 MUL+ADD**：虽然 `MUL(3cy)+ADD(1cy)` 的总延迟也是 4 周期，但它需要 2 条指令、2 个周期才能发完，且 RAW 依赖要求 ADD 必须等待 MUL 结果。MLA 的优势在于指令密度高、发射压力小、占用重命名/解码资源少。只有在简单 ALU（ALU0/1/3/4）或复杂 ALU（ALU2/5）中某一类资源已成为瓶颈时，才考虑拆分，并用 `llvm-mca` 或实测验证。

3. **SMULL/UMULL 仅2周期**: 长乘法比标准乘法(3cy)更快。对于需要扩展精度的情况，长乘法更优。

4. **除法仅8周期**: 32-bit和64-bit统一8周期延迟。

5. **分支不阻塞ALU**: 简单分支(B/BR)仅1周期延迟且不占用ALU（仅B0/B1）。调用(BL)占用B0/B1+ALU1/4。分支预测友好代码的开销极低。

### 5.2 浮点/标量代码优化

1. **FP add/sub 仅1-2周期**: FADD/FSUB (2cy) 和 ff ariths (1cy) 极快。HIP12的浮点加法吞吐极高。

2. **FP FMA 4周期**: FFMA 延迟4周期，与标量FMA一致。

3. **FP div (6/8cy) 和 sqrt (6/8cy)**: 标量除法/平方根延迟已显著降低。对于大多数场景可直接使用硬件 FDIV/FSQRT；仅在需要极高吞吐或特定精度时，才考虑 FRECPE/FRSQRTE + Newton-Raphson 近似。

4. **FCMP 仅在V0/V2**: FCMP(2cy)占用V02+ALU0134。**只有一半的V单元能执行比较**。浮点比较密集代码注意V0/V2争用。

5. **FCCMP 和 FCSEL 代价高**:
   - FCCMP: 4cy 级联 (ALU14→V0123)
   - FCSEL: 6cy 级联 (ALU14→V0123)
   避免在循环中使用条件浮点操作。使用位操作或谓词替代。

6. **f_cvti2f 极重 (7cy)**: i2f需要ALU14→V0123级联。在转换密集代码中预留整数和向量资源。

7. **f_mcrr (10cy)**: 传输两个GP寄存器到V寄存器为10cy且级联。尽量减少GP↔SIMD数据传输。

### 5.3 NEON/SIMD 优化

1. **NEON 操作延迟一览**:

   | 延迟 | 操作 |
   |------|------|
   | **1cy** | ABS/NEG/ADD/SUB/LOGIC/WIDE_ADD/FP_ABS/FP_NEG/RBIT/BSL/CLS/CNT |
   | **2cy** | LONG_ADD/QADD/CMP/ABD/MINMAX/FP_ADDSUB/FP_CMP/FP_ABD/SHIFT/REV/TBL1-2/ZIP/MOVE/INS/EXT |
   | **3cy** | REDUC_ADD/DOT/MUL/MLA/SHIFT_ACC/FP_CVT/FP_MUL/FP_MINMAX_REDUC/FP_ROUND(D)/FP_RECPE(D) |
   | **4cy** | FP_MLA/FP_CVT_Q/FP_RECPE_Q/FP_RECPS/TBL3-4 |
   | **6cy** | FP_DIV_S/FP_SQRT_S (D-form) / DUP |
   | **7cy** | FP_DIV_S_Q/FP_SQRT_S_Q |
   | **9cy** | FP_DIV_D_Q/FP_SQRT_D_Q |

2. **点积 DOT 极快 (3cy)**: SDOT/UDOT 仅3周期延迟。AI/ML推理工作负载应大量使用SDOT/UDOT。

3. **NEON 乘加统一3周期**: 所有形式的MUL/MLA均为3周期（除了FP_MLA为4周期）。MUL和MLA延迟相同！这意味着：
   ```c
   // HIP12上MLA与MUL延迟相同，优先使用MLA减少指令数
   c = vmlaq_s32(c, a, b);   // 3周期，2条输入
   // 等价于:
   // t = vmulq_s32(a, b);   // 3周期
   // c = vaddq_s32(c, t);   // 1周期 → 总计4周期
   ```

4. **向量FP除法/平方根相对快**:
   - FDIV_S (6cy): 硬件除法延迟低，直接使用可能优于近似
   - FSQRT_S (6cy): 硬件平方根延迟低，直接使用可能优于近似
   在某些场景下，直接使用硬件除法和sqrt可能比Newton-Raphson近似更优（需要考虑近似所需指令数）。

5. **NEON DUP 代价高 (6cy)**: DUP需要V0123+ALU0134。频繁的向量填充操作会阻塞整数流水线。尝试将DUP提升到循环外，或使用向量加载替代。

6. **TBL3/TBL4 延迟为TBL1/TBL2的2倍**: 4cy vs 2cy。大型查表考虑拆分为多个TBL1/TBL2。

7. **fp_mla 旁路为2周期**: FP FMA链（Newton-Raphson迭代等）可紧密耦合。

8. **shift_acc 旁路仅1周期**: SSRA/USRA链是最快的累加路径。

### 5.4 SVE2 优化

1. **SVE2 4路发射**: SVE2利用全部4条V流水线（V0-3），提供极高的向量吞吐。

2. **SVE2 BITPERM**: 位排列指令可用于高效的表查找和数据处理。

3. **SVE2 AES/SM4/SHA3**: 加密操作可向量化处理。将加密工作负载映射到SVE2可显著提升吞吐。

4. **向量长度不可知编程**: 充分利用SVE的while循环和谓词，使同一代码在不同向量宽度上高效运行。

### 5.5 Crypto 优化

- **AES 4路发射 (V0123)**: AES可在所有4条V流水线上发射 — AES吞吐极高
- **SHA256/SHA512/SM3 仅在V0/V2**: 注意半吞吐限制
- **Crypto与SIMD的并行**: AES/SHA1/SHA3/SM4可在V0-V3任意发射，与SIMD共享但资源充足

### 5.6 循环优化

1. **展开因子**:
   - 整数: 4-6路ALU → 展开6-8x
   - SIMD: 4路V → 展开4-8x
   - Load: 3路 → 每周期最多3次加载

2. **Load 带宽**: 3路Load流水线。内存带宽敏感代码可更高效地利用预取和数据并行。

3. **Store 优化**: 基本Store仅1周期延迟。交错Store(ST3/ST4)为4周期。

---

## 6. 调度总结

| 资源 | 每周期吞吐 | 关键独占指令 |
|------|----------|------------|
| ALU all (0-5) | 6 | 简单ALU，mov |
| ALU1\|4 | 2 | CSEL, CLZ, REV, BFM, shift_reg |
| ALU2\|5 | 2 | ALU extend/shift, 乘法, 除法, CRC, logics_imm |
| ALU1\|4\|2\|5 | 4 | ALU flags |
| B0\|1 | 2 | 分支 |
| Load0-2 | 3 | 加载 |
| Store0-1 + STD0-1 | 2 | 存储 |
| V0-3 | 4 | FP/SIMD/SVE |
| V0\|2 | 2 | SHA256/SHA512/SM3, FCMP |

**三级并发**: hip12 ‖ hip12_ldst ‖ hip12_v — 三个独立发射队列可同时发射。

---

## 7. 性能陷阱

1. ❌ **`logics_imm` 2周期+仅2路**: 带 flags 逻辑立即数（如 `ands #imm`）延迟 2 周期且仅在 ALU2/5
2. ❌ **f_cvti2f 7周期**: i2f转换级联延迟显著
3. ❌ **f_mcrr 10周期**: GP→V双寄存器传输极重
4. ❌ **FCSEL 6周期**: 条件浮点选择代价高
5. ❌ **NEON DUP 6周期**: 向量填充占用V+ALU
6. ❌ **MLA占用双资源**: 乘加同时占复杂和简单ALU
7. ❌ **FCMP仅在V0/V2**: 浮点比较仅有2路

---

---

> **参考文件**: `gcc/config/aarch64/hip12.md`, `gcc/config/aarch64/aarch64-cost-tables.h` (`hip12_extra_costs`), `gcc/config/aarch64/aarch64-cores.def`
