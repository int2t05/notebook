# A64 指令 — SVE 可伸缩向量指令

> 数据源：ARM 官方 A64 ISA 机器可读规范（2026-03_rel），共 938 条。汇编模板列即官方 `asmtemplate`（Encoding）。
> 源数据下载：https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz

| 指令名 | 英文简述 | 中文简介 | 汇编模板（Encoding） | 关联特性 |
| --- | --- | --- | --- | --- |
| `ABS` | Absolute value (predicated) | 取绝对值（有谓词） | `ABS <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`ABS <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `ADCLB` | Add with carry long (bottom) | 带进位长加法（低位） | `ADCLB <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `ADCLT` | Add with carry long (top) | 带进位长加法（高位） | `ADCLT <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `ADD (immediate)` | Add immediate (unpredicated) | 加立即数（无谓词） | `ADD <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `ADD (vectors, predicated)` | Add (predicated) | 向量加法（有谓词） | `ADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `ADD (vectors, unpredicated)` | Add (unpredicated) | 向量加法（无谓词） | `ADD <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `ADDHNB` | Add narrow high part (bottom) | 加法取高位窄化（低位） | `ADDHNB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `ADDHNT` | Add narrow high part (top) | 加法取高位窄化（高位） | `ADDHNT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `ADDP` | Add pairwise | 成对加法 | `ADDP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `ADDPL` | Add multiple of predicate register size to scalar register | 将谓词寄存器大小的倍数加到标量寄存器 | `ADDPL <Xd\|SP>, <Xn\|SP>, #<imm>` | FEAT_SME, FEAT_SVE |
| `ADDPT (predicated)` | Add checked pointer vectors (predicated) | 经检查指针向量加法（有谓词） | `ADDPT <Zdn>.D, <Pg>/M, <Zdn>.D, <Zm>.D` | FEAT_CPA, FEAT_SVE |
| `ADDPT (unpredicated)` | Add checked pointer vectors (unpredicated) | 经检查指针向量加法（无谓词） | `ADDPT <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_CPA, FEAT_SVE |
| `ADDQV` | Add reduction of quadword vector segments | 四字向量段的加法归约 | `ADDQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ADDVL` | Add multiple of vector register size to scalar register | 将向量寄存器大小的倍数加到标量寄存器 | `ADDVL <Xd\|SP>, <Xn\|SP>, #<imm>` | FEAT_SME, FEAT_SVE |
| `ADR` | Calculate vector address | 计算向量地址 | `ADR <Zd>.<T>, [<Zn>.<T>, <Zm>.<T>{, <mod> <amount>}]`<br>`ADR <Zd>.D, [<Zn>.D, <Zm>.D, SXTW{<amount>}]`<br>`ADR <Zd>.D, [<Zn>.D, <Zm>.D, UXTW{<amount>}]` | FEAT_SVE |
| `AESD (indexed)` | Multi-vector AES single round decryption | 多向量 AES 单轮解密（索引） | `AESD { <Zdn1>.B-<Zdn2>.B }, { <Zdn1>.B-<Zdn2>.B }, <Zm>.Q[<index>]`<br>`AESD { <Zdn1>.B-<Zdn4>.B }, { <Zdn1>.B-<Zdn4>.B }, <Zm>.Q[<index>]` | FEAT_SVE_AES2 |
| `AESD (vectors)` | AES single round decryption | AES 单轮解密 | `AESD <Zdn>.B, <Zdn>.B, <Zm>.B` | FEAT_SVE_AES |
| `AESDIMC` | Multi-vector AES single round decryption and inverse mix columns | 多向量 AES 单轮解密并逆混列 | `AESDIMC { <Zdn1>.B-<Zdn2>.B }, { <Zdn1>.B-<Zdn2>.B }, <Zm>.Q[<index>]`<br>`AESDIMC { <Zdn1>.B-<Zdn4>.B }, { <Zdn1>.B-<Zdn4>.B }, <Zm>.Q[<index>]` | FEAT_SVE_AES2 |
| `AESE (indexed)` | Multi-vector AES single round encryption | 多向量 AES 单轮加密（索引） | `AESE { <Zdn1>.B-<Zdn2>.B }, { <Zdn1>.B-<Zdn2>.B }, <Zm>.Q[<index>]`<br>`AESE { <Zdn1>.B-<Zdn4>.B }, { <Zdn1>.B-<Zdn4>.B }, <Zm>.Q[<index>]` | FEAT_SVE_AES2 |
| `AESE (vectors)` | AES single round encryption | AES 单轮加密 | `AESE <Zdn>.B, <Zdn>.B, <Zm>.B` | FEAT_SVE_AES |
| `AESEMC` | Multi-vector AES single round encryption and mix columns | 多向量 AES 单轮加密并混列 | `AESEMC { <Zdn1>.B-<Zdn2>.B }, { <Zdn1>.B-<Zdn2>.B }, <Zm>.Q[<index>]`<br>`AESEMC { <Zdn1>.B-<Zdn4>.B }, { <Zdn1>.B-<Zdn4>.B }, <Zm>.Q[<index>]` | FEAT_SVE_AES2 |
| `AESIMC` | AES inverse mix columns | AES 逆混列 | `AESIMC <Zdn>.B, <Zdn>.B` | FEAT_SVE_AES |
| `AESMC` | AES mix columns | AES 混列 | `AESMC <Zdn>.B, <Zdn>.B` | FEAT_SVE_AES |
| `AND (immediate)` | Bitwise AND with immediate (unpredicated) | 按位与立即数（无谓词） | `AND <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `AND (predicates)` | Bitwise AND predicates | 谓词按位与 | `AND <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `AND (vectors, predicated)` | Bitwise AND (predicated) | 向量按位与（有谓词） | `AND <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `AND (vectors, unpredicated)` | Bitwise AND (unpredicated) | 向量按位与（无谓词） | `AND <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `ANDQV` | Bitwise AND reduction of quadword vector segments | 四字向量段按位与归约 | `ANDQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ANDS` | Bitwise AND predicates, setting the condition flags | 谓词按位与并设置条件标志 | `ANDS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `ANDV` | Bitwise AND reduction to scalar | 向量按位与归约到标量 | `ANDV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `ASR (immediate, predicated)` | Arithmetic shift right by immediate (predicated) | 算术右移立即数（有谓词） | `ASR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `ASR (immediate, unpredicated)` | Arithmetic shift right by immediate (unpredicated) | 算术右移立即数（无谓词） | `ASR <Zd>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `ASR (vectors)` | Arithmetic shift right by vector (predicated) | 按向量算术右移（有谓词） | `ASR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `ASR (wide elements, predicated)` | Arithmetic shift right by 64-bit wide elements (predicated) | 按 64 位宽元素算术右移（有谓词） | `ASR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `ASR (wide elements, unpredicated)` | Arithmetic shift right by 64-bit wide elements (unpredicated) | 按 64 位宽元素算术右移（无谓词） | `ASR <Zd>.<T>, <Zn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `ASRD` | Arithmetic shift right for divide by immediate (predicated) | 算术右移用于除以立即数（有谓词） | `ASRD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `ASRR` | Reversed arithmetic shift right by vector (predicated) | 反向按向量算术右移（有谓词） | `ASRR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `BCAX` | Bitwise clear and exclusive-OR | 按位清除并异或 | `BCAX <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `BDEP` | Scatter lower bits into positions selected by bitmask | 将低位按位掩码所选位置分散 | `BDEP <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE_BitPerm |
| `BEXT` | Gather lower bits from positions selected by bitmask | 从位掩码所选位置收集低位 | `BEXT <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE_BitPerm |
| `BF1CVT, BF2CVT` | 8-bit floating-point convert to BFloat16 | 8 位浮点转换为 BFloat16 | `BF1CVT <Zd>.H, <Zn>.B`<br>`BF2CVT <Zd>.H, <Zn>.B` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `BF1CVTLT, BF2CVTLT` | 8-bit floating-point convert to BFloat16 (top) | 8 位浮点转换为 BFloat16（高位） | `BF1CVTLT <Zd>.H, <Zn>.B`<br>`BF2CVTLT <Zd>.H, <Zn>.B` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `BFADD (predicated)` | BFloat16 add (predicated) | BFloat16 加法（有谓词） | `BFADD <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFADD (unpredicated)` | BFloat16 add (unpredicated) | BFloat16 加法（无谓词） | `BFADD <Zd>.H, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFCLAMP` | BFloat16 clamp to minimum/maximum number | BFloat16 钳位到最小/最大值 | `BFCLAMP <Zd>.H, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFCVT` | Single-precision convert to BFloat16 (predicated) | 单精度转换为 BFloat16（有谓词） | `BFCVT <Zd>.H, <Pg>/M, <Zn>.S`<br>`BFCVT <Zd>.H, <Pg>/Z, <Zn>.S` | FEAT_BF16, FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `BFCVTN` | BFloat16 convert to interleaved 8-bit floating-point | BFloat16 转换为交错 8 位浮点 | `BFCVTN <Zd>.B, { <Zn1>.H-<Zn2>.H }` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `BFCVTNT` | Single-precision convert to BFloat16 (top, predicated) | 单精度转换为 BFloat16（高位，有谓词） | `BFCVTNT <Zd>.H, <Pg>/M, <Zn>.S`<br>`BFCVTNT <Zd>.H, <Pg>/Z, <Zn>.S` | FEAT_BF16, FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `BFDOT (indexed)` | BFloat16 dot product by indexed element to single-precision | BFloat16 点积（索引元素）累加到单精度 | `BFDOT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFDOT (vectors)` | BFloat16 dot product to single-precision | BFloat16 点积累加到单精度 | `BFDOT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFMAX` | BFloat16 maximum (predicated) | BFloat16 最大值（有谓词） | `BFMAX <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMAXNM` | BFloat16 maximum number (predicated) | BFloat16 数值最大值（有谓词） | `BFMAXNM <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMIN` | BFloat16 minimum (predicated) | BFloat16 最小值（有谓词） | `BFMIN <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMINNM` | BFloat16 minimum number (predicated) | BFloat16 数值最小值（有谓词） | `BFMINNM <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMLA (indexed)` | BFloat16 fused multiply-add by indexed element | BFloat16 融合乘加（索引元素） | `BFMLA <Zda>.H, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SVE_B16B16 |
| `BFMLA (vectors)` | BFloat16 fused multiply-add | BFloat16 融合乘加（向量） | `BFMLA <Zda>.H, <Pg>/M, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMLALB (indexed)` | BFloat16 multiply-add by indexed element to single-precision (bottom) | BFloat16 乘加到单精度（索引，低位） | `BFMLALB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFMLALB (vectors)` | BFloat16 multiply-add to single-precision (bottom) | BFloat16 乘加到单精度（低位） | `BFMLALB <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFMLALT (indexed)` | BFloat16 multiply-add by indexed element to single-precision (top) | BFloat16 乘加到单精度（索引，高位） | `BFMLALT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFMLALT (vectors)` | BFloat16 multiply-add to single-precision (top) | BFloat16 乘加到单精度（高位） | `BFMLALT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_BF16, FEAT_SME, FEAT_SVE |
| `BFMLS (indexed)` | BFloat16 fused multiply-subtract by indexed element | BFloat16 融合乘减（索引元素） | `BFMLS <Zda>.H, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SVE_B16B16 |
| `BFMLS (vectors)` | BFloat16 fused multiply-subtract | BFloat16 融合乘减（向量） | `BFMLS <Zda>.H, <Pg>/M, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMLSLB (indexed)` | BFloat16 multiply-subtract by indexed element from single-precision (bottom) | BFloat16 乘减自单精度（索引，低位） | `BFMLSLB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `BFMLSLB (vectors)` | BFloat16 multiply-subtract from single-precision (bottom) | BFloat16 乘减自单精度（低位） | `BFMLSLB <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME2, FEAT_SVE2p1 |
| `BFMLSLT (indexed)` | BFloat16 multiply-subtract by indexed element from single-precision (top) | BFloat16 乘减自单精度（索引，高位） | `BFMLSLT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `BFMLSLT (vectors)` | BFloat16 multiply-subtract from single-precision (top) | BFloat16 乘减自单精度（高位） | `BFMLSLT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME2, FEAT_SVE2p1 |
| `BFMMLA (widening)` | BFloat16 matrix multiply-accumulate to single-precision | BFloat16 矩阵乘累加到单精度 | `BFMMLA <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_BF16, FEAT_SVE |
| `BFMUL (indexed)` | BFloat16 multiply by indexed element | BFloat16 乘以索引元素 | `BFMUL <Zd>.H, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SVE_B16B16 |
| `BFMUL (vectors, predicated)` | BFloat16 multiply (predicated) | BFloat16 乘法（有谓词） | `BFMUL <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFMUL (vectors, unpredicated)` | BFloat16 multiply (unpredicated) | BFloat16 乘法（无谓词） | `BFMUL <Zd>.H, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFSCALE` | BFloat16 adjust exponent (predicated) | BFloat16 调整指数（有谓词） | `BFSCALE <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_BFSCALE |
| `BFSUB (predicated)` | BFloat16 subtract (predicated) | BFloat16 减法（有谓词） | `BFSUB <Zdn>.H, <Pg>/M, <Zdn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BFSUB (unpredicated)` | BFloat16 subtract (unpredicated) | BFloat16 减法（无谓词） | `BFSUB <Zd>.H, <Zn>.H, <Zm>.H` | FEAT_SVE_B16B16 |
| `BGRP` | Group bits to right or left as selected by bitmask | 按位掩码将位分组到右侧或左侧 | `BGRP <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE_BitPerm |
| `BIC (immediate)` | Bitwise clear bits using immediate (unpredicated): an alias of AND (immediate) | 用立即数按位清除（无谓词，AND 立即数的别名） | `BIC <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `BIC (predicates)` | Bitwise clear predicates | 谓词按位清除 | `BIC <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BIC (vectors, predicated)` | Bitwise clear (predicated) | 向量按位清除（有谓词） | `BIC <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `BIC (vectors, unpredicated)` | Bitwise clear (unpredicated) | 向量按位清除（无谓词） | `BIC <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `BICS` | Bitwise clear predicates, setting the condition flags | 谓词按位清除并设置条件标志 | `BICS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BRKA` | Break after first true condition | 在首个真条件后中断 | `BRKA <Pd>.B, <Pg>/<ZM>, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `BRKAS` | Break after first true condition, setting the condition flags | 在首个真条件后中断并设置条件标志 | `BRKAS <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `BRKB` | Break before first true condition | 在首个真条件前中断 | `BRKB <Pd>.B, <Pg>/<ZM>, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `BRKBS` | Break before first true condition, setting the condition flags | 在首个真条件前中断并设置条件标志 | `BRKBS <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `BRKN` | Propagate break to next partition | 将中断传播到下一分区 | `BRKN <Pdm>.B, <Pg>/Z, <Pn>.B, <Pdm>.B` | FEAT_SME, FEAT_SVE |
| `BRKNS` | Propagate break to next partition, setting the condition flags | 将中断传播到下一分区并设置条件标志 | `BRKNS <Pdm>.B, <Pg>/Z, <Pn>.B, <Pdm>.B` | FEAT_SME, FEAT_SVE |
| `BRKPA` | Break after first true condition, propagating from previous partition | 从前一分区传播后在首个真条件后中断 | `BRKPA <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BRKPAS` | Break after first true condition, propagating from previous partition and setting the condition flags | 从前一分区传播后在首个真条件后中断并设置条件标志 | `BRKPAS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BRKPB` | Break before first true condition, propagating from previous partition | 从前一分区传播后在首个真条件前中断 | `BRKPB <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BRKPBS` | Break before first true condition, propagating from previous partition and setting the condition flags | 从前一分区传播后在首个真条件前中断并设置条件标志 | `BRKPBS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `BSL` | Bitwise select | 按位选择 | `BSL <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `BSL1N` | Bitwise select with first input inverted | 按位选择（第一输入取反） | `BSL1N <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `BSL2N` | Bitwise select with second input inverted | 按位选择（第二输入取反） | `BSL2N <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `CADD` | Complex integer add | 复数整数加法 | `CADD <Zdn>.<T>, <Zdn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE2 |
| `CDOT (indexed)` | Complex integer dot product by indexed element | 复数整数点积（索引元素） | `CDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>], <const>`<br>`CDOT <Zda>.D, <Zn>.H, <Zm>.H[<imm>], <const>` | FEAT_SME, FEAT_SVE2 |
| `CDOT (vectors)` | Complex integer dot product | 复数整数点积 | `CDOT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>, <const>` | FEAT_SME, FEAT_SVE2 |
| `CLASTA (scalar)` | Conditionally extract element after last to general-purpose register | 按条件提取末位后元素到通用寄存器 | `CLASTA <R><dn>, <Pg>, <R><dn>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLASTA (SIMD&FP scalar)` | Conditionally extract element after last to SIMD&FP scalar register | 按条件提取末位后元素到 SIMD&FP 标量寄存器 | `CLASTA <V><dn>, <Pg>, <V><dn>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLASTA (vectors)` | Conditionally extract element after last to vector register | 按条件提取末位后元素到向量寄存器 | `CLASTA <Zdn>.<T>, <Pg>, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLASTB (scalar)` | Conditionally extract last element to general-purpose register | 按条件提取最后元素到通用寄存器 | `CLASTB <R><dn>, <Pg>, <R><dn>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLASTB (SIMD&FP scalar)` | Conditionally extract last element to SIMD&FP scalar register | 按条件提取最后元素到 SIMD&FP 标量寄存器 | `CLASTB <V><dn>, <Pg>, <V><dn>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLASTB (vectors)` | Conditionally extract last element to vector register | 按条件提取最后元素到向量寄存器 | `CLASTB <Zdn>.<T>, <Pg>, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CLS` | Count leading sign bits (predicated) | 计算前导符号位数（有谓词） | `CLS <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`CLS <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `CLZ` | Count leading zero bits (predicated) | 计算前导零位数（有谓词） | `CLZ <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`CLZ <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `CMLA (indexed)` | Complex integer multiply-add by indexed element | 复数整数乘加（索引元素） | `CMLA <Zda>.H, <Zn>.H, <Zm>.H[<imm>], <const>`<br>`CMLA <Zda>.S, <Zn>.S, <Zm>.S[<imm>], <const>` | FEAT_SME, FEAT_SVE2 |
| `CMLA (vectors)` | Complex integer multiply-add | 复数整数乘加 | `CMLA <Zda>.<T>, <Zn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE2 |
| `CMP<cc> (immediate)` | Compare vector to immediate | 向量与立即数比较 | `CMPEQ <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPHI <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPHS <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPLT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPLE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPLO <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPLS <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>`<br>`CMPNE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `CMP<cc> (vectors)` | Compare vectors | 向量比较 | `CMPEQ <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`CMPGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`CMPGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`CMPHI <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`CMPHS <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`CMPNE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `CMP<cc> (wide elements)` | Compare vector to 64-bit wide elements | 向量与 64 位宽元素比较 | `CMPEQ <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPHI <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPHS <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPLT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPLE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPLO <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPLS <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D`<br>`CMPNE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `CMPLE (vectors)` | Compare signed less than or equal to vector, setting the condition flags: an alias of CMP<cc> (vectors) | 有符号小于等于向量比较（CMP<cc> 向量的别名） | `CMPLE <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `CMPLO (vectors)` | Compare unsigned lower than vector, setting the condition flags: an alias of CMP<cc> (vectors) | 无符号低于向量比较（CMP<cc> 向量的别名） | `CMPLO <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `CMPLS (vectors)` | Compare unsigned lower than or same as vector, setting the condition flags: an alias of CMP<cc> (vectors) | 比较向量（无符号小于等于），设置条件标志（CMP<cc>（向量）的别名） | `CMPLS <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `CMPLT (vectors)` | Compare signed less than vector, setting the condition flags: an alias of CMP<cc> (vectors) | 比较向量（有符号小于），设置条件标志（CMP<cc>（向量）的别名） | `CMPLT <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `CNOT` | Logically invert boolean condition (predicated) | 逻辑取反布尔条件（有谓词） | `CNOT <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`CNOT <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `CNT` | Count non-zero bits (predicated) | 统计非零位数（有谓词） | `CNT <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`CNT <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `CNTB, CNTD, CNTH, CNTW` | Set scalar to multiple of predicate constraint element count | 将标量设为谓词约束元素计数的倍数 | `CNTB <Xd>{, <pattern>{, MUL #<imm>}}`<br>`CNTD <Xd>{, <pattern>{, MUL #<imm>}}`<br>`CNTH <Xd>{, <pattern>{, MUL #<imm>}}`<br>`CNTW <Xd>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `CNTP (predicate as counter)` | Set scalar to count from predicate-as-counter | 将标量设为谓词计数器中的计数 | `CNTP <Xd>, <PNn>.<T>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `CNTP (predicate)` | Set scalar to count of true predicate elements | 将标量设为谓词中真元素的数量 | `CNTP <Xd>, <Pg>, <Pn>.<T>` | FEAT_SME, FEAT_SVE |
| `COMPACT` | Copy Active vector elements to lower-numbered elements | 将活跃向量元素复制到低编号元素位置 | `COMPACT <Zd>.<T>, <Pg>, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `CPY (immediate, merging)` | Copy signed integer immediate to vector elements (merging) | 将有符号整数立即数复制到向量元素（合并） | `CPY <Zd>.<T>, <Pg>/M, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `CPY (immediate, zeroing)` | Copy signed integer immediate to vector elements (zeroing) | 将有符号整数立即数复制到向量元素（清零） | `CPY <Zd>.<T>, <Pg>/Z, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `CPY (scalar)` | Copy general-purpose register to vector elements (predicated) | 将通用寄存器复制到向量元素（有谓词） | `CPY <Zd>.<T>, <Pg>/M, <R><n\|SP>` | FEAT_SME, FEAT_SVE |
| `CPY (SIMD&FP scalar)` | Copy SIMD&FP scalar register to vector elements (predicated) | 将 SIMD&FP 标量寄存器复制到向量元素（有谓词） | `CPY <Zd>.<T>, <Pg>/M, <V><n>` | FEAT_SME, FEAT_SVE |
| `CTERMEQ, CTERMNE` | Compare and terminate loop | 比较并终止循环 | `CTERMEQ <R><n>, <R><m>`<br>`CTERMNE <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `DECB, DECD, DECH, DECW (scalar)` | Decrement scalar by multiple of predicate constraint element count | 将标量减去谓词约束元素计数的倍数 | `DECB <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`DECD <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`DECH <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`DECW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `DECD, DECH, DECW (vector)` | Decrement vector by multiple of predicate constraint element count | 将向量减去谓词约束元素计数的倍数 | `DECD <Zdn>.D{, <pattern>{, MUL #<imm>}}`<br>`DECH <Zdn>.H{, <pattern>{, MUL #<imm>}}`<br>`DECW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `DECP (scalar)` | Decrement scalar by count of true predicate elements | 将标量减去谓词中真元素的数量 | `DECP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `DECP (vector)` | Decrement vector by count of true predicate elements | 将向量减去谓词中真元素的数量 | `DECP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `DUP (immediate)` | Broadcast signed immediate to vector elements (unpredicated) | 将有符号立即数广播到向量所有元素（无谓词） | `DUP <Zd>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `DUP (indexed)` | Broadcast indexed element to vector (unpredicated) | 将索引元素广播到整个向量（无谓词） | `DUP <Zd>.<T>, <Zn>.<T>[<imm>]` | FEAT_SME, FEAT_SVE |
| `DUP (scalar)` | Broadcast general-purpose register to vector elements (unpredicated) | 将通用寄存器广播到向量所有元素（无谓词） | `DUP <Zd>.<T>, <R><n\|SP>` | FEAT_SME, FEAT_SVE |
| `DUPM` | Broadcast logical bitmask immediate to vector (unpredicated) | 将逻辑位掩码立即数广播到向量（无谓词） | `DUPM <Zd>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `DUPQ` | Broadcast indexed element within each quadword vector segment (unpredicated) | 在每个四字向量段内广播索引元素（无谓词） | `DUPQ <Zd>.<T>, <Zn>.<T>[<imm>]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `EON` | Bitwise exclusive-OR with inverted immediate (unpredicated): an alias of EOR (immediate) | 与取反立即数按位异或（无谓词）（EOR（立即数）的别名） | `EON <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `EOR (immediate)` | Bitwise exclusive-OR with immediate (unpredicated) | 与立即数按位异或（无谓词） | `EOR <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `EOR (predicates)` | Bitwise exclusive-OR predicates | 谓词按位异或 | `EOR <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `EOR (vectors, predicated)` | Bitwise exclusive-OR (predicated) | 向量按位异或（有谓词） | `EOR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `EOR (vectors, unpredicated)` | Bitwise exclusive-OR (unpredicated) | 向量按位异或（无谓词） | `EOR <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `EOR3` | Bitwise exclusive-OR between three vectors | 三个向量之间按位异或 | `EOR3 <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `EORBT` | Interleaving exclusive-OR (bottom, top) | 交错按位异或（低半部分与高半部分） | `EORBT <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `EORQV` | Bitwise exclusive-OR reduction of quadword vector segments | 四字向量段的按位异或归约 | `EORQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `EORS` | Bitwise exclusive-OR predicates, setting the condition flags | 谓词按位异或并设置条件标志 | `EORS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `EORTB` | Interleaving exclusive-OR (top, bottom) | 交错按位异或（高半部分与低半部分） | `EORTB <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `EORV` | Bitwise exclusive-OR reduction to scalar | 向量按位异或归约到标量 | `EORV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `EXPAND` | Copy lower-numbered vector elements to Active elements | 将低编号向量元素复制到活跃元素位置 | `EXPAND <Zd>.<T>, <Pg>, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `EXT` | Extract vector from pair of vectors | 从两个向量中提取向量片段 | `EXT <Zd>.B, { <Zn1>.B, <Zn2>.B }, #<imm>`<br>`EXT <Zdn>.B, <Zdn>.B, <Zm>.B, #<imm>` | FEAT_SME, FEAT_SVE, FEAT_SVE2 |
| `EXTQ` | Extract vector segment from each pair of quadword vector segments | 从每对四字向量段中提取向量段 | `EXTQ <Zdn>.B, <Zdn>.B, <Zm>.B, #<imm>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `F1CVT, F2CVT` | 8-bit floating-point convert to half-precision | 8位浮点数转换为半精度浮点数 | `F1CVT <Zd>.H, <Zn>.B`<br>`F2CVT <Zd>.H, <Zn>.B` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `F1CVTLT, F2CVTLT` | 8-bit floating-point convert to half-precision (top) | 8位浮点数转换为半精度浮点数（高半部分） | `F1CVTLT <Zd>.H, <Zn>.B`<br>`F2CVTLT <Zd>.H, <Zn>.B` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `FABD` | Floating-point absolute difference (predicated) | 浮点绝对差（有谓词） | `FABD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FABS` | Floating-point absolute value (predicated) | 浮点绝对值（有谓词） | `FABS <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FABS <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FAC<cc>` | Floating-point absolute compare | 浮点绝对值比较 | `FACGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`FACGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FACLE` | Floating-point absolute compare less than or equal: an alias of FAC<cc> | 浮点绝对值比较（小于等于）（FAC<cc> 的别名） | `FACLE <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FACLT` | Floating-point absolute compare less than: an alias of FAC<cc> | 浮点绝对值比较（小于）（FAC<cc> 的别名） | `FACLT <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FADD (immediate)` | Floating-point add immediate (predicated) | 浮点加立即数（有谓词） | `FADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FADD (vectors, predicated)` | Floating-point add (predicated) | 浮点加法（有谓词） | `FADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FADD (vectors, unpredicated)` | Floating-point add (unpredicated) | 浮点加法（无谓词） | `FADD <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FADDA` | Floating-point add strictly-ordered reduction, accumulating in scalar | 浮点严格顺序累加归约到标量 | `FADDA <V><dn>, <Pg>, <V><dn>, <Zm>.<T>` | FEAT_SVE |
| `FADDP` | Floating-point add pairwise | 浮点相邻元素加法 | `FADDP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `FADDQV` | Floating-point add recursive reduction of quadword vector segments | 四字向量段浮点加法递归归约 | `FADDQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `FADDV` | Floating-point add recursive reduction to scalar | 浮点加法递归归约到标量 | `FADDV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FAMAX` | Floating-point absolute maximum (predicated) | 浮点绝对值最大值（有谓词） | `FAMAX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_FAMINMAX, FEAT_SME2, FEAT_SVE2 |
| `FAMIN` | Floating-point absolute minimum (predicated) | 浮点绝对值最小值（有谓词） | `FAMIN <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_FAMINMAX, FEAT_SME2, FEAT_SVE2 |
| `FCADD` | Floating-point complex add (predicated) | 浮点复数加法（有谓词） | `FCADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FCLAMP` | Floating-point clamp to minimum/maximum number | 浮点数钳制到最小/最大数 | `FCLAMP <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2, FEAT_SVE2p1 |
| `FCM<cc> (vectors)` | Floating-point compare | 浮点向量比较 | `FCMEQ <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`FCMGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`FCMGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`FCMNE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>`<br>`FCMUO <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FCM<cc> (zero)` | Floating-point compare with zero | 浮点与零比较 | `FCMEQ <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0`<br>`FCMGT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0`<br>`FCMGE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0`<br>`FCMLT <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0`<br>`FCMLE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0`<br>`FCMNE <Pd>.<T>, <Pg>/Z, <Zn>.<T>, #0.0` | FEAT_SME, FEAT_SVE |
| `FCMLA (indexed)` | Floating-point complex multiply-add by indexed element | 浮点复数乘加（按索引元素，有谓词） | `FCMLA <Zda>.H, <Zn>.H, <Zm>.H[<imm>], <const>`<br>`FCMLA <Zda>.S, <Zn>.S, <Zm>.S[<imm>], <const>` | FEAT_SME, FEAT_SVE |
| `FCMLA (vectors)` | Floating-point complex multiply-add (predicated) | 浮点复数乘加（有谓词） | `FCMLA <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FCMLE (vectors)` | Floating-point compare less than or equal to vector: an alias of FCM<cc> (vectors) | 浮点向量比较（小于等于）（FCM<cc>（向量）的别名） | `FCMLE <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FCMLT (vectors)` | Floating-point compare less than vector: an alias of FCM<cc> (vectors) | 浮点向量比较（小于）（FCM<cc>（向量）的别名） | `FCMLT <Pd>.<T>, <Pg>/Z, <Zm>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FCPY` | Copy floating-point immediate to vector elements (predicated) | 将浮点立即数复制到向量元素（有谓词） | `FCPY <Zd>.<T>, <Pg>/M, #<const>` | FEAT_SME, FEAT_SVE |
| `FCVT` | Floating-point convert (predicated) | 浮点格式转换（有谓词） | `FCVT <Zd>.S, <Pg>/M, <Zn>.H`<br>`FCVT <Zd>.S, <Pg>/Z, <Zn>.H`<br>`FCVT <Zd>.D, <Pg>/M, <Zn>.H`<br>`FCVT <Zd>.D, <Pg>/Z, <Zn>.H`<br>`FCVT <Zd>.H, <Pg>/M, <Zn>.S`<br>`FCVT <Zd>.H, <Pg>/Z, <Zn>.S`<br>`FCVT <Zd>.D, <Pg>/M, <Zn>.S`<br>`FCVT <Zd>.D, <Pg>/Z, <Zn>.S`<br>`FCVT <Zd>.H, <Pg>/M, <Zn>.D`<br>`FCVT <Zd>.H, <Pg>/Z, <Zn>.D`<br>`FCVT <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVT <Zd>.S, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FCVTLT` | Floating-point widening convert (top, predicated) | 浮点扩展转换（高半部分，有谓词） | `FCVTLT <Zd>.S, <Pg>/M, <Zn>.H`<br>`FCVTLT <Zd>.S, <Pg>/Z, <Zn>.H`<br>`FCVTLT <Zd>.D, <Pg>/M, <Zn>.S`<br>`FCVTLT <Zd>.D, <Pg>/Z, <Zn>.S` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `FCVTN` | Half-precision convert to interleaved 8-bit floating-point | 半精度转换为交错8位浮点数 | `FCVTN <Zd>.B, { <Zn1>.H-<Zn2>.H }` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `FCVTNB` | Single-precision convert to interleaved 8-bit floating-point (bottom) | 单精度转换为交错8位浮点数（低半部分） | `FCVTNB <Zd>.B, { <Zn1>.S-<Zn2>.S }` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `FCVTNT (predicated)` | Floating-point narrowing convert (top, predicated) | 浮点窄化转换（高半部分，有谓词） | `FCVTNT <Zd>.H, <Pg>/M, <Zn>.S`<br>`FCVTNT <Zd>.H, <Pg>/Z, <Zn>.S`<br>`FCVTNT <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVTNT <Zd>.S, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `FCVTNT (unpredicated)` | Single-precision convert to interleaved 8-bit floating-point (top) | 单精度转换为交错8位浮点数（高半部分） | `FCVTNT <Zd>.B, { <Zn1>.S-<Zn2>.S }` | FEAT_FP8, FEAT_SME2, FEAT_SVE2 |
| `FCVTX` | Double-precision convert to single-precision, rounding to odd (predicated) | 双精度转换为单精度，取奇数舍入（有谓词） | `FCVTX <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVTX <Zd>.S, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `FCVTXNT` | Double-precision convert to single-precision, rounding to odd (top, predicated) | 双精度转换为单精度，取奇数舍入（高半部分，有谓词） | `FCVTXNT <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVTXNT <Zd>.S, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `FCVTZS` | Floating-point convert to signed integer, rounding toward zero (predicated) | 浮点转换为有符号整数，向零舍入（有谓词） | `FCVTZS <Zd>.H, <Pg>/M, <Zn>.H`<br>`FCVTZS <Zd>.H, <Pg>/Z, <Zn>.H`<br>`FCVTZS <Zd>.S, <Pg>/M, <Zn>.H`<br>`FCVTZS <Zd>.S, <Pg>/Z, <Zn>.H`<br>`FCVTZS <Zd>.D, <Pg>/M, <Zn>.H`<br>`FCVTZS <Zd>.D, <Pg>/Z, <Zn>.H`<br>`FCVTZS <Zd>.S, <Pg>/M, <Zn>.S`<br>`FCVTZS <Zd>.S, <Pg>/Z, <Zn>.S`<br>`FCVTZS <Zd>.D, <Pg>/M, <Zn>.S`<br>`FCVTZS <Zd>.D, <Pg>/Z, <Zn>.S`<br>`FCVTZS <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVTZS <Zd>.S, <Pg>/Z, <Zn>.D`<br>`FCVTZS <Zd>.D, <Pg>/M, <Zn>.D`<br>`FCVTZS <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FCVTZU` | Floating-point convert to unsigned integer, rounding toward zero (predicated) | 浮点转换为无符号整数，向零舍入（有谓词） | `FCVTZU <Zd>.H, <Pg>/M, <Zn>.H`<br>`FCVTZU <Zd>.H, <Pg>/Z, <Zn>.H`<br>`FCVTZU <Zd>.S, <Pg>/M, <Zn>.H`<br>`FCVTZU <Zd>.S, <Pg>/Z, <Zn>.H`<br>`FCVTZU <Zd>.D, <Pg>/M, <Zn>.H`<br>`FCVTZU <Zd>.D, <Pg>/Z, <Zn>.H`<br>`FCVTZU <Zd>.S, <Pg>/M, <Zn>.S`<br>`FCVTZU <Zd>.S, <Pg>/Z, <Zn>.S`<br>`FCVTZU <Zd>.D, <Pg>/M, <Zn>.S`<br>`FCVTZU <Zd>.D, <Pg>/Z, <Zn>.S`<br>`FCVTZU <Zd>.S, <Pg>/M, <Zn>.D`<br>`FCVTZU <Zd>.S, <Pg>/Z, <Zn>.D`<br>`FCVTZU <Zd>.D, <Pg>/M, <Zn>.D`<br>`FCVTZU <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FDIV` | Floating-point divide (predicated) | 浮点除法（有谓词） | `FDIV <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FDIVR` | Floating-point reversed divide (predicated) | 浮点反向除法（有谓词） | `FDIVR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FDOT (2-way, indexed, FP16 to FP32)` | Half-precision dot product by indexed element to single-precision | 半精度按索引元素点积到单精度（2路） | `FDOT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `FDOT (2-way, indexed, FP8 to FP16)` | 8-bit floating-point dot product by indexed element to half-precision | 8位浮点按索引元素点积到半精度（2路） | `FDOT <Zda>.H, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8DOT2, FEAT_SSVE_FP8DOT2, FEAT_SVE2 |
| `FDOT (2-way, vectors, FP16 to FP32)` | Half-precision dot product to single-precision | 半精度点积到单精度（2路） | `FDOT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME2, FEAT_SVE2p1 |
| `FDOT (2-way, vectors, FP8 to FP16)` | 8-bit floating-point dot product to half-precision | 8位浮点点积到半精度（2路） | `FDOT <Zda>.H, <Zn>.B, <Zm>.B` | FEAT_FP8DOT2, FEAT_SSVE_FP8DOT2, FEAT_SVE2 |
| `FDOT (4-way, indexed)` | 8-bit floating-point dot product by indexed element to single-precision | 8位浮点按索引元素点积到单精度（4路） | `FDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8DOT4, FEAT_SSVE_FP8DOT4, FEAT_SVE2 |
| `FDOT (4-way, vectors)` | 8-bit floating-point dot product to single-precision | 8位浮点点积到单精度（4路） | `FDOT <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_FP8DOT4, FEAT_SSVE_FP8DOT4, FEAT_SVE2 |
| `FDUP` | Broadcast floating-point immediate to vector elements (unpredicated) | 将浮点立即数广播到向量所有元素（无谓词） | `FDUP <Zd>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `FEXPA` | Floating-point exponential accelerator | 浮点指数加速器 | `FEXPA <Zd>.<T>, <Zn>.<T>` | FEAT_SSVE_FEXPA, FEAT_SVE |
| `FIRSTP` | Scalar index of first true predicate element (predicated) | 获取第一个真谓词元素的标量索引（有谓词） | `FIRSTP <Xd>, <Pg>, <Pn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `FLOGB` | Floating-point base 2 logarithm as integer | 浮点以2为底的对数（整数结果） | `FLOGB <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FLOGB <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `FMAD` | Floating-point fused multiply-add to multiplicand (predicated) | 浮点融合乘加到被乘数（有谓词） | `FMAD <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `FMAX (immediate)` | Floating-point maximum with immediate (predicated) | 浮点与立即数取最大值（有谓词） | `FMAX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FMAX (vectors)` | Floating-point maximum (predicated) | 浮点向量取最大值（有谓词） | `FMAX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMAXNM (immediate)` | Floating-point maximum number with immediate (predicated) | 浮点与立即数取最大数（有谓词） | `FMAXNM <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FMAXNM (vectors)` | Floating-point maximum number (predicated) | 浮点向量取最大数（有谓词） | `FMAXNM <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMAXNMP` | Floating-point maximum number pairwise | 浮点相邻元素取最大数 | `FMAXNMP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `FMAXNMQV` | Floating-point maximum number recursive reduction of quadword vector segments | 四字向量段浮点最大数递归归约 | `FMAXNMQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `FMAXNMV` | Floating-point maximum number recursive reduction to scalar | 浮点最大数递归归约到标量 | `FMAXNMV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FMAXP` | Floating-point maximum pairwise | 浮点相邻元素取最大值 | `FMAXP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `FMAXQV` | Floating-point maximum reduction of quadword vector segments | 四字向量段浮点最大值归约 | `FMAXQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `FMAXV` | Floating-point maximum recursive reduction to scalar | 浮点最大值递归归约到标量 | `FMAXV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FMIN (immediate)` | Floating-point minimum with immediate (predicated) | 浮点与立即数取最小值（有谓词） | `FMIN <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FMIN (vectors)` | Floating-point minimum (predicated) | 浮点向量取最小值（有谓词） | `FMIN <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMINNM (immediate)` | Floating-point minimum number with immediate (predicated) | 浮点与立即数取最小数（有谓词） | `FMINNM <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FMINNM (vectors)` | Floating-point minimum number (predicated) | 浮点向量取最小数（有谓词） | `FMINNM <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMINNMP` | Floating-point minimum number pairwise | 浮点相邻元素取最小数 | `FMINNMP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `FMINNMQV` | Floating-point minimum number recursive reduction of quadword vector segments | 四字向量段浮点最小数递归归约 | `FMINNMQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `FMINNMV` | Floating-point minimum number recursive reduction to scalar | 浮点最小数递归归约到标量 | `FMINNMV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FMINP` | Floating-point minimum pairwise | 浮点相邻元素取最小值 | `FMINP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `FMINQV` | Floating-point minimum recursive reduction of quadword vector segments | 四字向量段浮点最小值递归归约 | `FMINQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `FMINV` | Floating-point minimum recursive reduction to scalar | 浮点最小值递归归约到标量 | `FMINV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FMLA (indexed)` | Floating-point fused multiply-add by indexed element | 浮点融合乘加（按索引元素） | `FMLA <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`FMLA <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`FMLA <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE |
| `FMLA (vectors)` | Floating-point fused multiply-add (predicated) | 浮点融合乘加（有谓词） | `FMLA <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMLALB (indexed, FP16 to FP32)` | Half-precision multiply-add by indexed element to single-precision (bottom) | 半精度按索引元素乘加到单精度（低半部分） | `FMLALB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `FMLALB (indexed, FP8 to FP16)` | 8-bit floating-point multiply-add by indexed element to half-precision (bottom) | 8位浮点按索引元素乘加到半精度（低半部分） | `FMLALB <Zda>.H, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALB (vectors, FP16 to FP32)` | Half-precision multiply-add to single-precision (bottom) | 半精度乘加到单精度（低半部分） | `FMLALB <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME, FEAT_SVE2 |
| `FMLALB (vectors, FP8 to FP16)` | 8-bit floating-point multiply-add to half-precision (bottom) | 8位浮点乘加到半精度（低半部分） | `FMLALB <Zda>.H, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLBB (indexed)` | 8-bit floating-point multiply-add by indexed element to single-precision (bottom bottom) | 8位浮点按索引元素乘加到单精度（底底） | `FMLALLBB <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLBB (vectors)` | 8-bit floating-point multiply-add to single-precision (bottom bottom) | 8位浮点乘加到单精度（底底） | `FMLALLBB <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLBT (indexed)` | 8-bit floating-point multiply-add by indexed element to single-precision (bottom top) | 8位浮点按索引元素乘加到单精度（底顶） | `FMLALLBT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLBT (vectors)` | 8-bit floating-point multiply-add to single-precision (bottom top) | 8位浮点乘加到单精度（底顶） | `FMLALLBT <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLTB (indexed)` | 8-bit floating-point multiply-add by indexed element to single-precision (top bottom) | 8位浮点按索引元素乘加到单精度（顶底） | `FMLALLTB <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLTB (vectors)` | 8-bit floating-point multiply-add to single-precision (top bottom) | 8位浮点乘加到单精度（顶底） | `FMLALLTB <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLTT (indexed)` | 8-bit floating-point multiply-add by indexed element to single-precision (top top) | 8位浮点按索引元素乘加到单精度（顶顶） | `FMLALLTT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALLTT (vectors)` | 8-bit floating-point multiply-add to single-precision (top top) | 8位浮点乘加到单精度（顶顶） | `FMLALLTT <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALT (indexed, FP16 to FP32)` | Half-precision multiply-add by indexed element to single-precision (top) | 半精度按索引元素乘加到单精度（高半部分） | `FMLALT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `FMLALT (indexed, FP8 to FP16)` | 8-bit floating-point multiply-add by indexed element to half-precision (top) | 8位浮点按索引元素乘加到半精度（高半部分） | `FMLALT <Zda>.H, <Zn>.B, <Zm>.B[<imm>]` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLALT (vectors, FP16 to FP32)` | Half-precision multiply-add to single-precision (top) | 半精度乘加到单精度（高半部，FP16→FP32） | `FMLALT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME, FEAT_SVE2 |
| `FMLALT (vectors, FP8 to FP16)` | 8-bit floating-point multiply-add to half-precision (top) | 8位浮点乘加到半精度（高半部，FP8→FP16） | `FMLALT <Zda>.H, <Zn>.B, <Zm>.B` | FEAT_FP8FMA, FEAT_SSVE_FP8FMA, FEAT_SVE2 |
| `FMLS (indexed)` | Floating-point fused multiply-subtract by indexed element | 浮点融合乘减，乘以索引元素 | `FMLS <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`FMLS <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`FMLS <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE |
| `FMLS (vectors)` | Floating-point fused multiply-subtract (predicated) | 浮点融合乘减（有谓词） | `FMLS <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMLSLB (indexed)` | Half-precision multiply-subtract by indexed element from single-precision (bottom) | 半精度乘减单精度，乘以索引元素（低半部，FP16→FP32） | `FMLSLB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `FMLSLB (vectors)` | Half-precision multiply-subtract from single-precision (bottom) | 半精度乘减单精度（低半部，FP16→FP32） | `FMLSLB <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME, FEAT_SVE2 |
| `FMLSLT (indexed)` | Half-precision multiply-subtract by indexed element from single-precision (top) | 半精度乘减单精度，乘以索引元素（高半部，FP16→FP32） | `FMLSLT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `FMLSLT (vectors)` | Half-precision multiply-subtract from single-precision (top) | 半精度乘减单精度（高半部，FP16→FP32） | `FMLSLT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME, FEAT_SVE2 |
| `FMMLA (non-widening)` | Floating-point matrix multiply-accumulate | 浮点矩阵乘累加（非扩宽） | `FMMLA <Zda>.S, <Zn>.S, <Zm>.S`<br>`FMMLA <Zda>.D, <Zn>.D, <Zm>.D` | FEAT_F32MM, FEAT_F64MM |
| `FMMLA (widening, FP16 to FP32)` | Half-precision matrix multiply-accumulate to single-precision | 半精度矩阵乘累加到单精度（FP16→FP32） | `FMMLA <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SVE_F16F32MM |
| `FMMLA (widening, FP8 to FP16)` | 8-bit floating-point matrix multiply-accumulate to half-precision | 8位浮点矩阵乘累加到半精度（FP8→FP16） | `FMMLA <Zda>.H, <Zn>.B, <Zm>.B` | FEAT_F8F16MM, FEAT_SVE2 |
| `FMMLA (widening, FP8 to FP32)` | 8-bit floating-point matrix multiply-accumulate to single-precision | 8位浮点矩阵乘累加到单精度（FP8→FP32） | `FMMLA <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_F8F32MM, FEAT_SVE2 |
| `FMOV (immediate, predicated)` | Move floating-point immediate to vector elements (predicated): an alias of FCPY | 将浮点立即数移入向量各元素（有谓词，FCPY 的别名） | `FMOV <Zd>.<T>, <Pg>/M, #<const>` | FEAT_SME, FEAT_SVE |
| `FMOV (immediate, unpredicated)` | Move floating-point immediate to vector elements (unpredicated): an alias of FDUP | 将浮点立即数移入向量各元素（无谓词，FDUP 的别名） | `FMOV <Zd>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `FMOV (zero, predicated)` | Move floating-point +0.0 to vector elements (predicated): an alias of CPY (immediate, merging) | 将浮点+0.0移入向量各元素（有谓词，CPY 立即数合并的别名） | `FMOV <Zd>.<T>, <Pg>/M, #0.0` | FEAT_SME, FEAT_SVE |
| `FMOV (zero, unpredicated)` | Move floating-point +0.0 to vector elements (unpredicated): an alias of DUP (immediate) | 将浮点+0.0移入向量各元素（无谓词，DUP 立即数的别名） | `FMOV <Zd>.<T>, #0.0` | FEAT_SME, FEAT_SVE |
| `FMSB` | Floating-point fused multiply-subtract to multiplicand (predicated) | 浮点融合乘减，结果写回被乘数（有谓词） | `FMSB <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `FMUL (immediate)` | Floating-point multiply by immediate (predicated) | 浮点乘以立即数（有谓词） | `FMUL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FMUL (indexed)` | Floating-point multiply by indexed element | 浮点乘以索引元素 | `FMUL <Zd>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`FMUL <Zd>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`FMUL <Zd>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE |
| `FMUL (vectors, predicated)` | Floating-point multiply (predicated) | 浮点向量乘法（有谓词） | `FMUL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMUL (vectors, unpredicated)` | Floating-point multiply (unpredicated) | 浮点向量乘法（无谓词） | `FMUL <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FMULX` | Floating-point multiply extended (predicated) | 浮点扩展乘法（有谓词） | `FMULX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FNEG` | Floating-point negate (predicated) | 浮点取反（有谓词） | `FNEG <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FNEG <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FNMAD` | Floating-point negated fused multiply-add to multiplicand (predicated) | 浮点取负融合乘加，结果写回被乘数（有谓词） | `FNMAD <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `FNMLA` | Floating-point negated fused multiply-add (predicated) | 浮点取负融合乘加（有谓词） | `FNMLA <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FNMLS` | Floating-point negated fused multiply-subtract (predicated) | 浮点取负融合乘减（有谓词） | `FNMLS <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FNMSB` | Floating-point negated fused multiply-subtract to multiplicand (predicated) | 浮点取负融合乘减，结果写回被乘数（有谓词） | `FNMSB <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `FRECPE` | Floating-point reciprocal estimate (unpredicated) | 浮点倒数估算（无谓词） | `FRECPE <Zd>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FRECPS` | Floating-point reciprocal step (unpredicated) | 浮点倒数迭代步进（无谓词） | `FRECPS <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FRECPX` | Floating-point reciprocal exponent (predicated) | 浮点倒数指数（有谓词） | `FRECPX <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRECPX <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FRINT32X` | Floating-point round to 32-bit integer (predicated) | 浮点舍入为32位整数（有谓词） | `FRINT32X <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINT32X <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `FRINT32Z` | Floating-point round to 32-bit integer, rounding toward zero (predicated) | 浮点向零舍入为32位整数（有谓词） | `FRINT32Z <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINT32Z <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `FRINT64X` | Floating-point round to 64-bit integer (predicated) | 浮点舍入为64位整数（有谓词） | `FRINT64X <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINT64X <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `FRINT64Z` | Floating-point round to 64-bit integer, rounding toward zero (predicated) | 浮点向零舍入为64位整数（有谓词） | `FRINT64Z <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINT64Z <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `FRINT<r>` | Floating-point round to integral value (predicated) | 浮点舍入为整数值（有谓词） | `FRINTX <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTX <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTI <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTI <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTA <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTA <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTN <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTN <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTZ <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTZ <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTM <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTM <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`FRINTP <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FRINTP <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FRSQRTE` | Floating-point reciprocal square root estimate (unpredicated) | 浮点倒数平方根估算（无谓词） | `FRSQRTE <Zd>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `FRSQRTS` | Floating-point reciprocal square root step (unpredicated) | 浮点倒数平方根迭代步进（无谓词） | `FRSQRTS <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FSCALE` | Floating-point adjust exponent (predicated) | 浮点调整指数（有谓词） | `FSCALE <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FSQRT` | Floating-point square root (predicated) | 浮点平方根（有谓词） | `FSQRT <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`FSQRT <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `FSUB (immediate)` | Floating-point subtract immediate (predicated) | 浮点减立即数（有谓词） | `FSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FSUB (vectors, predicated)` | Floating-point subtract (predicated) | 浮点向量减法（有谓词） | `FSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FSUB (vectors, unpredicated)` | Floating-point subtract (unpredicated) | 浮点向量减法（无谓词） | `FSUB <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FSUBR (immediate)` | Floating-point reversed subtract from immediate (predicated) | 浮点反向减立即数（有谓词） | `FSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <const>` | FEAT_SME, FEAT_SVE |
| `FSUBR (vectors)` | Floating-point reversed subtract (predicated) | 浮点反向减法（有谓词） | `FSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `FTMAD` | Floating-point trigonometric multiply-add coefficient | 浮点三角函数乘加系数 | `FTMAD <Zdn>.<T>, <Zdn>.<T>, <Zm>.<T>, #<imm>` | FEAT_SVE |
| `FTSMUL` | Floating-point trigonometric starting value | 浮点三角函数起始值计算 | `FTSMUL <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE |
| `FTSSEL` | Floating-point trigonometric select coefficient | 浮点三角函数系数选择 | `FTSSEL <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE |
| `HISTCNT` | Count matching elements in vector | 统计向量中匹配元素的个数 | `HISTCNT <Zd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE2 |
| `HISTSEG` | Count matching elements in vector segments | 统计向量分段中匹配元素的个数 | `HISTSEG <Zd>.B, <Zn>.B, <Zm>.B` | FEAT_SVE2 |
| `INCB, INCD, INCH, INCW (scalar)` | Increment scalar by multiple of predicate constraint element count | 按谓词约束元素计数的倍数递增标量寄存器 | `INCB <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`INCD <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`INCH <Xdn>{, <pattern>{, MUL #<imm>}}`<br>`INCW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `INCD, INCH, INCW (vector)` | Increment vector by multiple of predicate constraint element count | 按谓词约束元素计数的倍数递增向量寄存器 | `INCD <Zdn>.D{, <pattern>{, MUL #<imm>}}`<br>`INCH <Zdn>.H{, <pattern>{, MUL #<imm>}}`<br>`INCW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `INCP (scalar)` | Increment scalar by count of true predicate elements | 按谓词真元素个数递增标量寄存器 | `INCP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `INCP (vector)` | Increment vector by count of true predicate elements | 按谓词真元素个数递增向量寄存器 | `INCP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `INDEX (immediate, scalar)` | Create index starting from immediate and incremented by general-purpose register | 从立即数起始、以通用寄存器为步长创建索引向量 | `INDEX <Zd>.<T>, #<imm>, <R><m>` | FEAT_SME, FEAT_SVE |
| `INDEX (immediates)` | Create index starting from and incremented by immediate | 从立即数起始、以立即数为步长创建索引向量 | `INDEX <Zd>.<T>, #<imm1>, #<imm2>` | FEAT_SME, FEAT_SVE |
| `INDEX (scalar, immediate)` | Create index starting from general-purpose register and incremented by immediate | 从通用寄存器起始、以立即数为步长创建索引向量 | `INDEX <Zd>.<T>, <R><n>, #<imm>` | FEAT_SME, FEAT_SVE |
| `INDEX (scalars)` | Create index starting from and incremented by general-purpose register | 从通用寄存器起始、以寄存器为步长创建索引向量 | `INDEX <Zd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `INSR (scalar)` | Insert general-purpose register in shifted vector | 将通用寄存器值插入右移后的向量首位 | `INSR <Zdn>.<T>, <R><m>` | FEAT_SME, FEAT_SVE |
| `INSR (SIMD&FP scalar)` | Insert SIMD&FP scalar register in shifted vector | 将SIMD&FP标量寄存器值插入右移后的向量首位 | `INSR <Zdn>.<T>, <V><m>` | FEAT_SME, FEAT_SVE |
| `LASTA (scalar)` | Extract element after last to general-purpose register | 提取末个真谓词元素之后的元素到通用寄存器 | `LASTA <R><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `LASTA (SIMD&FP scalar)` | Extract element after last to SIMD&FP scalar register | 提取末个真谓词元素之后的元素到SIMD&FP标量寄存器 | `LASTA <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `LASTB (scalar)` | Extract last element to general-purpose register | 提取最后一个真谓词元素到通用寄存器 | `LASTB <R><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `LASTB (SIMD&FP scalar)` | Extract last element to SIMD&FP scalar register | 提取最后一个真谓词元素到SIMD&FP标量寄存器 | `LASTB <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `LASTP` | Scalar index of last true predicate element (predicated) | 获取最后一个真谓词元素的标量索引（有谓词） | `LASTP <Xd>, <Pg>, <Pn>.<T>` | FEAT_SME2p2, FEAT_SVE2p2 |
| `LD1B (scalar plus immediate, consecutive registers)` | Contiguous load of bytes to multiple consecutive vectors (immediate index) | 连续加载字节到多个连续向量（立即数索引） | `LD1B { <Zt1>.B-<Zt2>.B }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1B { <Zt1>.B-<Zt4>.B }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1B (scalar plus immediate, single register)` | Contiguous load unsigned bytes to vector (immediate index) | 连续加载无符号字节到向量（立即数索引） | `LD1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1B { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD1B (scalar plus scalar, consecutive registers)` | Contiguous load of bytes to multiple consecutive vectors (scalar index) | 连续加载字节到多个连续向量（标量索引） | `LD1B { <Zt1>.B-<Zt2>.B }, <PNg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1B { <Zt1>.B-<Zt4>.B }, <PNg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1B (scalar plus scalar, single register)` | Contiguous load unsigned bytes to vector (scalar index) | 连续加载无符号字节到向量（标量索引） | `LD1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1B { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD1B (scalar plus vector)` | Gather load unsigned bytes to vector (vector index) | 聚集加载无符号字节到向量（向量索引） | `LD1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LD1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1B (vector plus immediate)` | Gather load unsigned bytes to vector (immediate index) | 聚集加载无符号字节到向量（立即数索引） | `LD1B { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LD1B { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1D (scalar plus immediate, consecutive registers)` | Contiguous load of doublewords to multiple consecutive vectors (immediate index) | 连续加载双字到多个连续向量（立即数索引） | `LD1D { <Zt1>.D-<Zt2>.D }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1D { <Zt1>.D-<Zt4>.D }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1D (scalar plus immediate, single register)` | Contiguous load unsigned doublewords to vector (immediate index) | 连续加载无符号双字到向量（立即数索引） | `LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1D { <Zt>.Q }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `LD1D (scalar plus scalar, consecutive registers)` | Contiguous load of doublewords to multiple consecutive vectors (scalar index) | 连续加载双字到多个连续向量（标量索引） | `LD1D { <Zt1>.D-<Zt2>.D }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #3]`<br>`LD1D { <Zt1>.D-<Zt4>.D }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1D (scalar plus scalar, single register)` | Contiguous load unsigned doublewords to vector (scalar index) | 连续加载无符号双字到向量（标量索引） | `LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]`<br>`LD1D { <Zt>.Q }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `LD1D (scalar plus vector)` | Gather load doublewords to vector (vector index) | 聚集加载双字到向量（向量索引） | `LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #3]`<br>`LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #3]`<br>`LD1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1D (vector plus immediate)` | Gather load doublewords to vector (immediate index) | 聚集加载双字到向量（立即数索引） | `LD1D { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1H (scalar plus immediate, consecutive registers)` | Contiguous load of halfwords to multiple consecutive vectors (immediate index) | 连续加载半字到多个连续向量（立即数索引） | `LD1H { <Zt1>.H-<Zt2>.H }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1H { <Zt1>.H-<Zt4>.H }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1H (scalar plus immediate, single register)` | Contiguous load unsigned halfwords to vector (immediate index) | 连续加载无符号半字到向量（立即数索引） | `LD1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD1H (scalar plus scalar, consecutive registers)` | Contiguous load of halfwords to multiple consecutive vectors (scalar index) | 连续加载半字到多个连续向量（标量索引） | `LD1H { <Zt1>.H-<Zt2>.H }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #1]`<br>`LD1H { <Zt1>.H-<Zt4>.H }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1H (scalar plus scalar, single register)` | Contiguous load unsigned halfwords to vector (scalar index) | 连续加载无符号半字到向量（标量索引） | `LD1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]`<br>`LD1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD1H (scalar plus vector)` | Gather load unsigned halfwords to vector (vector index) | 聚集加载无符号半字到向量（向量索引） | `LD1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #1]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1H (vector plus immediate)` | Gather load unsigned halfwords to vector (immediate index) | 聚集加载无符号半字到向量（立即数索引） | `LD1H { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LD1H { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1Q` | Gather load quadwords | 聚集加载四字到向量 | `LD1Q { <Zt>.Q }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2p1 |
| `LD1RB` | Load and broadcast unsigned byte to vector | 加载并广播无符号字节到向量 | `LD1RB { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RD` | Load and broadcast doubleword to vector | 加载并广播双字到向量 | `LD1RD { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RH` | Load and broadcast unsigned halfword to vector | 加载并广播无符号半字到向量 | `LD1RH { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1ROB (scalar plus immediate)` | Contiguous load and replicate thirty-two bytes (immediate index) | 连续加载并复制32字节到向量（立即数索引） | `LD1ROB { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_F64MM |
| `LD1ROB (scalar plus scalar)` | Contiguous load and replicate thirty-two bytes (scalar index) | 连续加载并复制32字节到向量（标量索引） | `LD1ROB { <Zt>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_F64MM |
| `LD1ROD (scalar plus immediate)` | Contiguous load and replicate four doublewords (immediate index) | 连续加载并复制4个双字到向量（立即数索引） | `LD1ROD { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_F64MM |
| `LD1ROD (scalar plus scalar)` | Contiguous load and replicate four doublewords (scalar index) | 连续加载并复制4个双字到向量（标量索引） | `LD1ROD { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_F64MM |
| `LD1ROH (scalar plus immediate)` | Contiguous load and replicate sixteen halfwords (immediate index) | 连续加载并复制16个半字到向量（立即数索引） | `LD1ROH { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_F64MM |
| `LD1ROH (scalar plus scalar)` | Contiguous load and replicate sixteen halfwords (scalar index) | 连续加载并复制16个半字到向量（标量索引） | `LD1ROH { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_F64MM |
| `LD1ROW (scalar plus immediate)` | Contiguous load and replicate eight words (immediate index) | 连续加载并复制8个字到向量（立即数索引） | `LD1ROW { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_F64MM |
| `LD1ROW (scalar plus scalar)` | Contiguous load and replicate eight words (scalar index) | 连续加载并复制8个字到向量（标量索引） | `LD1ROW { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_F64MM |
| `LD1RQB (scalar plus immediate)` | Contiguous load and replicate sixteen bytes (immediate index) | 连续加载并复制16字节到向量（立即数索引） | `LD1RQB { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RQB (scalar plus scalar)` | Contiguous load and replicate sixteen bytes (scalar index) | 连续加载并复制16字节到向量（标量索引） | `LD1RQB { <Zt>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD1RQD (scalar plus immediate)` | Contiguous load and replicate two doublewords (immediate index) | 连续加载并复制2个双字到向量（立即数索引） | `LD1RQD { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RQD (scalar plus scalar)` | Contiguous load and replicate two doublewords (scalar index) | 连续加载并复制2个双字到向量（标量索引） | `LD1RQD { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `LD1RQH (scalar plus immediate)` | Contiguous load and replicate eight halfwords (immediate index) | 连续加载并复制8个半字到向量（立即数索引） | `LD1RQH { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RQH (scalar plus scalar)` | Contiguous load and replicate eight halfwords (scalar index) | 连续加载并复制8个半字到向量（标量索引） | `LD1RQH { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD1RQW (scalar plus immediate)` | Contiguous load and replicate four words (immediate index) | 连续加载并复制4个字到向量（立即数索引） | `LD1RQW { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RQW (scalar plus scalar)` | Contiguous load and replicate four words (scalar index) | 连续加载并复制4个字到向量（标量索引） | `LD1RQW { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LD1RSB` | Load and broadcast signed byte to vector | 加载并广播有符号字节到向量 | `LD1RSB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RSB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RSB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RSH` | Load and broadcast signed halfword to vector | 加载并广播有符号半字到向量 | `LD1RSH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RSH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RSW` | Load and broadcast signed word to vector | 加载并广播有符号字到向量 | `LD1RSW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1RW` | Load and broadcast unsigned word to vector | 加载并广播无符号字到向量 | `LD1RW { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]`<br>`LD1RW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>}]` | FEAT_SME, FEAT_SVE |
| `LD1SB (scalar plus immediate)` | Contiguous load signed bytes to vector (immediate index) | 连续加载有符号字节到向量（立即数索引） | `LD1SB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD1SB (scalar plus scalar)` | Contiguous load signed bytes to vector (scalar index) | 连续加载有符号字节到向量（标量索引） | `LD1SB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>]`<br>`LD1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD1SB (scalar plus vector)` | Gather load signed bytes to vector (vector index) | 聚集加载有符号字节到向量（向量索引） | `LD1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LD1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1SB (vector plus immediate)` | Gather load signed bytes to vector (immediate index) | 聚集加载有符号字节到向量（立即数索引） | `LD1SB { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LD1SB { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1SH (scalar plus immediate)` | Contiguous load signed halfwords to vector (immediate index) | 连续加载有符号半字到向量（立即数索引） | `LD1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD1SH (scalar plus scalar)` | Contiguous load signed halfwords to vector (scalar index) | 连续加载有符号半字到向量（标量索引） | `LD1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD1SH (scalar plus vector)` | Gather load signed halfwords to vector (vector index) | 聚集加载有符号半字到向量（向量索引） | `LD1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #1]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1SH (vector plus immediate)` | Gather load signed halfwords to vector (immediate index) | 聚集加载有符号半字到向量（立即数索引） | `LD1SH { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LD1SH { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1SW (scalar plus immediate)` | Contiguous load signed words to vector (immediate index) | 连续加载有符号字到向量（立即数索引） | `LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD1SW (scalar plus scalar)` | Contiguous load signed words to vector (scalar index) | 连续加载有符号字到向量（标量索引） | `LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LD1SW (scalar plus vector)` | Gather load signed words to vector (vector index) | 聚集加载有符号字到向量（向量索引） | `LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #2]`<br>`LD1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1SW (vector plus immediate)` | Gather load signed words to vector (immediate index) | 聚集加载有符号字到向量（立即数索引） | `LD1SW { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD1W (scalar plus immediate, consecutive registers)` | Contiguous load of words to multiple consecutive vectors (immediate index) | 连续加载字到多个连续向量（立即数索引） | `LD1W { <Zt1>.S-<Zt2>.S }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1W { <Zt1>.S-<Zt4>.S }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1W (scalar plus immediate, single register)` | Contiguous load unsigned words to vector (immediate index) | 连续加载无符号字到向量（立即数索引） | `LD1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LD1W { <Zt>.Q }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `LD1W (scalar plus scalar, consecutive registers)` | Contiguous load of words to multiple consecutive vectors (scalar index) | 连续加载字到多个连续SVE向量寄存器（标量索引） | `LD1W { <Zt1>.S-<Zt2>.S }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #2]`<br>`LD1W { <Zt1>.S-<Zt4>.S }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME2, FEAT_SVE2p1 |
| `LD1W (scalar plus scalar, single register)` | Contiguous load unsigned words to vector (scalar index) | 连续加载无符号字到SVE向量寄存器（标量索引） | `LD1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]`<br>`LD1W { <Zt>.Q }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `LD1W (scalar plus vector)` | Gather load unsigned words to vector (vector index) | 聚集加载无符号字到SVE向量寄存器（向量索引） | `LD1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #2]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LD1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #2]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LD1W (vector plus immediate)` | Gather load unsigned words to vector (immediate index) | 聚集加载无符号字到SVE向量寄存器（立即数索引） | `LD1W { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LD1W { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LD2B (scalar plus immediate)` | Contiguous load two-byte structures to two vectors (immediate index) | 连续加载双字节结构体到两个SVE向量寄存器（立即数索引） | `LD2B { <Zt1>.B, <Zt2>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD2B (scalar plus scalar)` | Contiguous load two-byte structures to two vectors (scalar index) | 连续加载双字节结构体到两个SVE向量寄存器（标量索引） | `LD2B { <Zt1>.B, <Zt2>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD2D (scalar plus immediate)` | Contiguous load two-doubleword structures to two vectors (immediate index) | 连续加载双双字结构体到两个SVE向量寄存器（立即数索引） | `LD2D { <Zt1>.D, <Zt2>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD2D (scalar plus scalar)` | Contiguous load two-doubleword structures to two vectors (scalar index) | 连续加载双双字结构体到两个SVE向量寄存器（标量索引） | `LD2D { <Zt1>.D, <Zt2>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `LD2H (scalar plus immediate)` | Contiguous load two-halfword structures to two vectors (immediate index) | 连续加载双半字结构体到两个SVE向量寄存器（立即数索引） | `LD2H { <Zt1>.H, <Zt2>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD2H (scalar plus scalar)` | Contiguous load two-halfword structures to two vectors (scalar index) | 连续加载双半字结构体到两个SVE向量寄存器（标量索引） | `LD2H { <Zt1>.H, <Zt2>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD2Q (scalar plus immediate)` | Contiguous load two-quadword structures to two vectors (immediate index) | 连续加载双四字结构体到两个SVE向量寄存器（立即数索引） | `LD2Q { <Zt1>.Q, <Zt2>.Q }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD2Q (scalar plus scalar)` | Contiguous load two-quadword structures to two vectors (scalar index) | 连续加载双四字结构体到两个SVE向量寄存器（标量索引） | `LD2Q { <Zt1>.Q, <Zt2>.Q }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD2W (scalar plus immediate)` | Contiguous load two-word structures to two vectors (immediate index) | 连续加载双字结构体到两个SVE向量寄存器（立即数索引） | `LD2W { <Zt1>.S, <Zt2>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD2W (scalar plus scalar)` | Contiguous load two-word structures to two vectors (scalar index) | 连续加载双字结构体到两个SVE向量寄存器（标量索引） | `LD2W { <Zt1>.S, <Zt2>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LD3B (scalar plus immediate)` | Contiguous load three-byte structures to three vectors (immediate index) | 连续加载三字节结构体到三个SVE向量寄存器（立即数索引） | `LD3B { <Zt1>.B, <Zt2>.B, <Zt3>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD3B (scalar plus scalar)` | Contiguous load three-byte structures to three vectors (scalar index) | 连续加载三字节结构体到三个SVE向量寄存器（标量索引） | `LD3B { <Zt1>.B, <Zt2>.B, <Zt3>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD3D (scalar plus immediate)` | Contiguous load three-doubleword structures to three vectors (immediate index) | 连续加载三双字结构体到三个SVE向量寄存器（立即数索引） | `LD3D { <Zt1>.D, <Zt2>.D, <Zt3>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD3D (scalar plus scalar)` | Contiguous load three-doubleword structures to three vectors (scalar index) | 连续加载三双字结构体到三个SVE向量寄存器（标量索引） | `LD3D { <Zt1>.D, <Zt2>.D, <Zt3>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `LD3H (scalar plus immediate)` | Contiguous load three-halfword structures to three vectors (immediate index) | 连续加载三半字结构体到三个SVE向量寄存器（立即数索引） | `LD3H { <Zt1>.H, <Zt2>.H, <Zt3>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD3H (scalar plus scalar)` | Contiguous load three-halfword structures to three vectors (scalar index) | 连续加载三半字结构体到三个SVE向量寄存器（标量索引） | `LD3H { <Zt1>.H, <Zt2>.H, <Zt3>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD3Q (scalar plus immediate)` | Contiguous load three-quadword structures to three vectors (immediate index) | 连续加载三四字结构体到三个SVE向量寄存器（立即数索引） | `LD3Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD3Q (scalar plus scalar)` | Contiguous load three-quadword structures to three vectors (scalar index) | 连续加载三四字结构体到三个SVE向量寄存器（标量索引） | `LD3Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD3W (scalar plus immediate)` | Contiguous load three-word structures to three vectors (immediate index) | 连续加载三字结构体到三个SVE向量寄存器（立即数索引） | `LD3W { <Zt1>.S, <Zt2>.S, <Zt3>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD3W (scalar plus scalar)` | Contiguous load three-word structures to three vectors (scalar index) | 连续加载三字结构体到三个SVE向量寄存器（标量索引） | `LD3W { <Zt1>.S, <Zt2>.S, <Zt3>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LD4B (scalar plus immediate)` | Contiguous load four-byte structures to four vectors (immediate index) | 连续加载四字节结构体到四个SVE向量寄存器（立即数索引） | `LD4B { <Zt1>.B, <Zt2>.B, <Zt3>.B, <Zt4>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD4B (scalar plus scalar)` | Contiguous load four-byte structures to four vectors (scalar index) | 连续加载四字节结构体到四个SVE向量寄存器（标量索引） | `LD4B { <Zt1>.B, <Zt2>.B, <Zt3>.B, <Zt4>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LD4D (scalar plus immediate)` | Contiguous load four-doubleword structures to four vectors (immediate index) | 连续加载四双字结构体到四个SVE向量寄存器（立即数索引） | `LD4D { <Zt1>.D, <Zt2>.D, <Zt3>.D, <Zt4>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD4D (scalar plus scalar)` | Contiguous load four-doubleword structures to four vectors (scalar index) | 连续加载四双字结构体到四个SVE向量寄存器（标量索引） | `LD4D { <Zt1>.D, <Zt2>.D, <Zt3>.D, <Zt4>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `LD4H (scalar plus immediate)` | Contiguous load four-halfword structures to four vectors (immediate index) | 连续加载四半字结构体到四个SVE向量寄存器（立即数索引） | `LD4H { <Zt1>.H, <Zt2>.H, <Zt3>.H, <Zt4>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD4H (scalar plus scalar)` | Contiguous load four-halfword structures to four vectors (scalar index) | 连续加载四半字结构体到四个SVE向量寄存器（标量索引） | `LD4H { <Zt1>.H, <Zt2>.H, <Zt3>.H, <Zt4>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LD4Q (scalar plus immediate)` | Contiguous load four-quadword structures to four vectors (immediate index) | 连续加载四四字结构体到四个SVE向量寄存器（立即数索引） | `LD4Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q, <Zt4>.Q }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD4Q (scalar plus scalar)` | Contiguous load four-quadword structures to four vectors (scalar index) | 连续加载四四字结构体到四个SVE向量寄存器（标量索引） | `LD4Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q, <Zt4>.Q }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `LD4W (scalar plus immediate)` | Contiguous load four-word structures to four vectors (immediate index) | 连续加载四字结构体到四个SVE向量寄存器（立即数索引） | `LD4W { <Zt1>.S, <Zt2>.S, <Zt3>.S, <Zt4>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LD4W (scalar plus scalar)` | Contiguous load four-word structures to four vectors (scalar index) | 连续加载四字结构体到四个SVE向量寄存器（标量索引） | `LD4W { <Zt1>.S, <Zt2>.S, <Zt3>.S, <Zt4>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LDFF1B (scalar plus scalar)` | Contiguous load first-fault unsigned bytes to vector (scalar index) | 连续首错误加载无符号字节到SVE向量寄存器（标量索引） | `LDFF1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]`<br>`LDFF1B { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]`<br>`LDFF1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]`<br>`LDFF1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]` | FEAT_SVE |
| `LDFF1B (scalar plus vector)` | Gather load first-fault unsigned bytes to vector (vector index) | 聚集首错误加载无符号字节到SVE向量寄存器（向量索引） | `LDFF1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LDFF1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1B (vector plus immediate)` | Gather load first-fault unsigned bytes to vector (immediate index) | 聚集首错误加载无符号字节到SVE向量寄存器（立即数索引） | `LDFF1B { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LDFF1B { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1D (scalar plus scalar)` | Contiguous load first-fault doublewords to vector (scalar index) | 连续首错误加载双字到SVE向量寄存器（标量索引） | `LDFF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #3}]` | FEAT_SVE |
| `LDFF1D (scalar plus vector)` | Gather load first-fault doublewords to vector (vector index) | 聚集首错误加载双字到SVE向量寄存器（向量索引） | `LDFF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #3]`<br>`LDFF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #3]`<br>`LDFF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1D (vector plus immediate)` | Gather load first-fault doublewords to vector (immediate index) | 聚集首错误加载双字到SVE向量寄存器（立即数索引） | `LDFF1D { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1H (scalar plus scalar)` | Contiguous load first-fault unsigned halfwords to vector (scalar index) | 连续首错误加载无符号半字到SVE向量寄存器（标量索引） | `LDFF1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #1}]`<br>`LDFF1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #1}]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #1}]` | FEAT_SVE |
| `LDFF1H (scalar plus vector)` | Gather load first-fault unsigned halfwords to vector (vector index) | 聚集首错误加载无符号半字到SVE向量寄存器（向量索引） | `LDFF1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #1]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1H (vector plus immediate)` | Gather load first-fault unsigned halfwords to vector (immediate index) | 聚集首错误加载无符号半字到SVE向量寄存器（立即数索引） | `LDFF1H { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LDFF1H { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1SB (scalar plus scalar)` | Contiguous load first-fault signed bytes to vector (scalar index) | 连续首错误加载有符号字节到SVE向量寄存器（标量索引） | `LDFF1SB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]`<br>`LDFF1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]`<br>`LDFF1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>}]` | FEAT_SVE |
| `LDFF1SB (scalar plus vector)` | Gather load first-fault signed bytes to vector (vector index) | 聚集首错误加载有符号字节到SVE向量寄存器（向量索引） | `LDFF1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LDFF1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1SB (vector plus immediate)` | Gather load first-fault signed bytes to vector (immediate index) | 聚集首错误加载有符号字节到SVE向量寄存器（立即数索引） | `LDFF1SB { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LDFF1SB { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1SH (scalar plus scalar)` | Contiguous load first-fault signed halfwords to vector (scalar index) | 连续首错误加载有符号半字到SVE向量寄存器（标量索引） | `LDFF1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #1}]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #1}]` | FEAT_SVE |
| `LDFF1SH (scalar plus vector)` | Gather load first-fault signed halfwords to vector (vector index) | 聚集首错误加载有符号半字到SVE向量寄存器（向量索引） | `LDFF1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #1]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1SH (vector plus immediate)` | Gather load first-fault signed halfwords to vector (immediate index) | 聚集首错误加载有符号半字到SVE向量寄存器（立即数索引） | `LDFF1SH { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LDFF1SH { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1SW (scalar plus scalar)` | Contiguous load first-fault signed words to vector (scalar index) | 连续首错误加载有符号字到SVE向量寄存器（标量索引） | `LDFF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #2}]` | FEAT_SVE |
| `LDFF1SW (scalar plus vector)` | Gather load first-fault signed words to vector (vector index) | 聚集首错误加载有符号字到SVE向量寄存器（向量索引） | `LDFF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`LDFF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #2]`<br>`LDFF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1SW (vector plus immediate)` | Gather load first-fault signed words to vector (immediate index) | 聚集首错误加载有符号字到SVE向量寄存器（立即数索引） | `LDFF1SW { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDFF1W (scalar plus scalar)` | Contiguous load first-fault unsigned words to vector (scalar index) | 连续首错误加载无符号字到SVE向量寄存器（标量索引） | `LDFF1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #2}]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, <Xm>, LSL #2}]` | FEAT_SVE |
| `LDFF1W (scalar plus vector)` | Gather load first-fault unsigned words to vector (vector index) | 聚集首错误加载无符号字到SVE向量寄存器（向量索引） | `LDFF1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod> #2]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`LDFF1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D, LSL #2]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `LDFF1W (vector plus immediate)` | Gather load first-fault unsigned words to vector (immediate index) | 聚集首错误加载无符号字到SVE向量寄存器（立即数索引） | `LDFF1W { <Zt>.S }, <Pg>/Z, [<Zn>.S{, #<imm>}]`<br>`LDFF1W { <Zt>.D }, <Pg>/Z, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `LDNF1B` | Contiguous load non-fault unsigned bytes to vector (immediate index) | 连续非错误加载无符号字节到SVE向量寄存器（立即数索引） | `LDNF1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1B { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1B { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1B { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1D` | Contiguous load non-fault doublewords to vector (immediate index) | 连续非错误加载双字到SVE向量寄存器（立即数索引） | `LDNF1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1H` | Contiguous load non-fault unsigned halfwords to vector (immediate index) | 连续非错误加载无符号半字到SVE向量寄存器（立即数索引） | `LDNF1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1H { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1H { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1SB` | Contiguous load non-fault signed bytes to vector (immediate index) | 连续非错误加载有符号字节到SVE向量寄存器（立即数索引） | `LDNF1SB { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1SB { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1SB { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1SH` | Contiguous load non-fault signed halfwords to vector (immediate index) | 连续非错误加载有符号半字到SVE向量寄存器（立即数索引） | `LDNF1SH { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1SH { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1SW` | Contiguous load non-fault signed words to vector (immediate index) | 连续非错误加载有符号字到SVE向量寄存器（立即数索引） | `LDNF1SW { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNF1W` | Contiguous load non-fault unsigned words to vector (immediate index) | 连续非错误加载无符号字到SVE向量寄存器（立即数索引） | `LDNF1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNF1W { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SVE |
| `LDNT1B (scalar plus immediate, consecutive registers)` | Contiguous load non-temporal of bytes to multiple consecutive vectors (immediate index) | 连续非临时加载字节到多个连续SVE向量寄存器（立即数索引） | `LDNT1B { <Zt1>.B-<Zt2>.B }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNT1B { <Zt1>.B-<Zt4>.B }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1B (scalar plus immediate, single register)` | Contiguous load non-temporal bytes to vector (immediate index) | 连续非临时加载字节到SVE向量寄存器（立即数索引） | `LDNT1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LDNT1B (scalar plus scalar, consecutive registers)` | Contiguous load non-temporal of bytes to multiple consecutive vectors (scalar index) | 连续非临时加载字节到多个连续SVE向量寄存器（标量索引） | `LDNT1B { <Zt1>.B-<Zt2>.B }, <PNg>/Z, [<Xn\|SP>, <Xm>]`<br>`LDNT1B { <Zt1>.B-<Zt4>.B }, <PNg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1B (scalar plus scalar, single register)` | Contiguous load non-temporal bytes to vector (scalar index) | 连续非临时加载字节到SVE向量寄存器（标量索引） | `LDNT1B { <Zt>.B }, <Pg>/Z, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `LDNT1B (vector plus scalar)` | Gather load non-temporal unsigned bytes | 聚集非临时加载无符号字节到SVE向量寄存器 | `LDNT1B { <Zt>.S }, <Pg>/Z, [<Zn>.S{, <Xm>}]`<br>`LDNT1B { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1D (scalar plus immediate, consecutive registers)` | Contiguous load non-temporal of doublewords to multiple consecutive vectors (immediate index) | 连续非临时加载双字到多个连续SVE向量寄存器（立即数索引） | `LDNT1D { <Zt1>.D-<Zt2>.D }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNT1D { <Zt1>.D-<Zt4>.D }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1D (scalar plus immediate, single register)` | Contiguous load non-temporal doublewords to vector (immediate index) | 连续非临时加载双字到SVE向量寄存器（立即数索引） | `LDNT1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LDNT1D (scalar plus scalar, consecutive registers)` | Contiguous load non-temporal of doublewords to multiple consecutive vectors (scalar index) | 连续非临时加载双字到多个连续SVE向量寄存器（标量索引） | `LDNT1D { <Zt1>.D-<Zt2>.D }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #3]`<br>`LDNT1D { <Zt1>.D-<Zt4>.D }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1D (scalar plus scalar, single register)` | Contiguous load non-temporal doublewords to vector (scalar index) | 连续非临时加载双字到SVE向量寄存器（标量索引） | `LDNT1D { <Zt>.D }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `LDNT1D (vector plus scalar)` | Gather load non-temporal unsigned doublewords | 聚集非临时加载无符号双字到SVE向量寄存器 | `LDNT1D { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1H (scalar plus immediate, consecutive registers)` | Contiguous load non-temporal of halfwords to multiple consecutive vectors (immediate index) | 连续非临时加载半字到多个连续SVE向量寄存器（立即数索引） | `LDNT1H { <Zt1>.H-<Zt2>.H }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNT1H { <Zt1>.H-<Zt4>.H }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1H (scalar plus immediate, single register)` | Contiguous load non-temporal halfwords to vector (immediate index) | 连续非临时加载半字到SVE向量寄存器（立即数索引） | `LDNT1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LDNT1H (scalar plus scalar, consecutive registers)` | Contiguous load non-temporal of halfwords to multiple consecutive vectors (scalar index) | 连续非临时加载半字到多个连续SVE向量寄存器（标量索引） | `LDNT1H { <Zt1>.H-<Zt2>.H }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #1]`<br>`LDNT1H { <Zt1>.H-<Zt4>.H }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1H (scalar plus scalar, single register)` | Contiguous load non-temporal halfwords to vector (scalar index) | 连续非临时加载半字到SVE向量寄存器（标量索引） | `LDNT1H { <Zt>.H }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `LDNT1H (vector plus scalar)` | Gather load non-temporal unsigned halfwords | 聚集非临时加载无符号半字到SVE向量寄存器 | `LDNT1H { <Zt>.S }, <Pg>/Z, [<Zn>.S{, <Xm>}]`<br>`LDNT1H { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1SB` | Gather load non-temporal signed bytes | 聚集非临时加载有符号字节到SVE向量寄存器 | `LDNT1SB { <Zt>.S }, <Pg>/Z, [<Zn>.S{, <Xm>}]`<br>`LDNT1SB { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1SH` | Gather load non-temporal signed halfwords | 聚集非临时加载有符号半字到SVE向量寄存器 | `LDNT1SH { <Zt>.S }, <Pg>/Z, [<Zn>.S{, <Xm>}]`<br>`LDNT1SH { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1SW` | Gather load non-temporal signed words | 聚集非临时加载有符号字到SVE向量寄存器 | `LDNT1SW { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDNT1W (scalar plus immediate, consecutive registers)` | Contiguous load non-temporal of words to multiple consecutive vectors (immediate index) | 连续非临时加载字到多个连续SVE向量寄存器（立即数索引） | `LDNT1W { <Zt1>.S-<Zt2>.S }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`LDNT1W { <Zt1>.S-<Zt4>.S }, <PNg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1W (scalar plus immediate, single register)` | Contiguous load non-temporal words to vector (immediate index) | 连续非临时加载字到SVE向量寄存器（立即数索引） | `LDNT1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LDNT1W (scalar plus scalar, consecutive registers)` | Contiguous load non-temporal of words to multiple consecutive vectors (scalar index) | 连续非临时加载字到多个连续SVE向量寄存器（标量索引） | `LDNT1W { <Zt1>.S-<Zt2>.S }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #2]`<br>`LDNT1W { <Zt1>.S-<Zt4>.S }, <PNg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME2, FEAT_SVE2p1 |
| `LDNT1W (scalar plus scalar, single register)` | Contiguous load non-temporal words to vector (scalar index) | 连续非临时加载字到SVE向量寄存器（标量索引） | `LDNT1W { <Zt>.S }, <Pg>/Z, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `LDNT1W (vector plus scalar)` | Gather load non-temporal unsigned words | 聚集非临时加载无符号字到SVE向量寄存器 | `LDNT1W { <Zt>.S }, <Pg>/Z, [<Zn>.S{, <Xm>}]`<br>`LDNT1W { <Zt>.D }, <Pg>/Z, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `LDR (predicate)` | Load predicate register | 加载SVE谓词寄存器 | `LDR <Pt>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LDR (vector)` | Load vector register | 加载SVE向量寄存器 | `LDR <Zt>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `LSL (immediate, predicated)` | Logical shift left by immediate (predicated) | SVE向量元素逻辑左移立即数（有谓词） | `LSL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `LSL (immediate, unpredicated)` | Logical shift left by immediate (unpredicated) | SVE向量元素逻辑左移立即数（无谓词） | `LSL <Zd>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `LSL (vectors)` | Logical shift left by vector (predicated) | SVE向量元素按向量逻辑左移（有谓词） | `LSL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `LSL (wide elements, predicated)` | Logical shift left by 64-bit wide elements (predicated) | SVE向量元素按64位宽元素逻辑左移（有谓词） | `LSL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `LSL (wide elements, unpredicated)` | Logical shift left by 64-bit wide elements (unpredicated) | SVE向量元素按64位宽元素逻辑左移（无谓词） | `LSL <Zd>.<T>, <Zn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `LSLR` | Reversed logical shift left by vector (predicated) | SVE向量元素反向逻辑左移（有谓词） | `LSLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `LSR (immediate, predicated)` | Logical shift right by immediate (predicated) | SVE向量元素逻辑右移立即数（有谓词） | `LSR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `LSR (immediate, unpredicated)` | Logical shift right by immediate (unpredicated) | SVE向量元素逻辑右移立即数（无谓词） | `LSR <Zd>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `LSR (vectors)` | Logical shift right by vector (predicated) | SVE向量元素按向量逻辑右移（有谓词） | `LSR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `LSR (wide elements, predicated)` | Logical shift right by 64-bit wide elements (predicated) | SVE向量元素按64位宽元素逻辑右移（有谓词） | `LSR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `LSR (wide elements, unpredicated)` | Logical shift right by 64-bit wide elements (unpredicated) | SVE向量元素按64位宽元素逻辑右移（无谓词） | `LSR <Zd>.<T>, <Zn>.<T>, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `LSRR` | Reversed logical shift right by vector (predicated) | SVE向量元素反向逻辑右移（有谓词） | `LSRR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `LUTI2 (8-bit and 16-bit)` | Lookup table read with 2-bit indices (8-bit and 16-bit) | SVE查找表读取，使用2位索引（8位和16位元素） | `LUTI2 <Zd>.B, { <Zn>.B }, <Zm>[<index>]`<br>`LUTI2 <Zd>.H, { <Zn>.H }, <Zm>[<index>]` | FEAT_LUT, FEAT_SME2, FEAT_SVE2 |
| `LUTI4 (8-bit and 16-bit)` | Lookup table read with 4-bit indices (8-bit and 16-bit) | SVE查找表读取，使用4位索引（8位和16位元素） | `LUTI4 <Zd>.B, { <Zn>.B }, <Zm>[<index>]`<br>`LUTI4 <Zd>.H, { <Zn1>.H, <Zn2>.H }, <Zm>[<index>]`<br>`LUTI4 <Zd>.H, { <Zn>.H }, <Zm>[<index>]` | FEAT_LUT, FEAT_SME2, FEAT_SVE2 |
| `MAD` | Multiply-add to multiplicand (predicated) | SVE向量乘加到被乘数（有谓词） | `MAD <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `MADPT` | Multiply-add checked pointer vectors to multiplicand | SVE检查指针向量乘加到被乘数 | `MADPT <Zdn>.D, <Zm>.D, <Za>.D` | FEAT_CPA, FEAT_SVE |
| `MATCH` | Detect any matching elements, setting the condition flags | SVE检测匹配元素并设置条件标志 | `MATCH <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE2 |
| `MLA (indexed)` | Multiply-add by indexed element | SVE向量元素乘加索引元素 | `MLA <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`MLA <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`MLA <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `MLA (vectors)` | Multiply-add (predicated) | SVE向量元素乘加（有谓词） | `MLA <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `MLAPT` | Multiply-add checked pointer vectors | SVE检查指针向量乘加 | `MLAPT <Zda>.D, <Zn>.D, <Zm>.D` | FEAT_CPA, FEAT_SVE |
| `MLS (indexed)` | Multiply-subtract by indexed element | SVE向量元素乘减索引元素 | `MLS <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`MLS <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`MLS <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `MLS (vectors)` | Multiply-subtract (predicated) | SVE向量元素乘减（有谓词） | `MLS <Zda>.<T>, <Pg>/M, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `MOV` | Move logical bitmask immediate to vector (unpredicated): an alias of DUPM | 将逻辑位掩码立即数移入SVE向量（无谓词，DUPM的别名） | `MOV <Zd>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `MOV` | Move predicate (unpredicated): an alias of ORR (predicates) | 移动谓词（无谓词，ORR谓词版别名） | `MOV <Pd>.B, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `MOV (immediate, merging)` | Move signed integer immediate to vector elements (merging): an alias of CPY (immediate, merging) | 将有符号整数立即数移入SVE向量元素（合并，CPY立即数合并版别名） | `MOV <Zd>.<T>, <Pg>/M, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `MOV (immediate, unpredicated)` | Move signed immediate to vector elements (unpredicated): an alias of DUP (immediate) | 将有符号立即数移入SVE向量元素（无谓词，DUP立即数别名） | `MOV <Zd>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `MOV (immediate, zeroing)` | Move signed integer immediate to vector elements (zeroing): an alias of CPY (immediate, zeroing) | 将有符号整数立即数移入SVE向量元素（清零，CPY立即数清零版别名） | `MOV <Zd>.<T>, <Pg>/Z, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `MOV (predicate, merging)` | Move predicates (merging): an alias of SEL (predicates) | 移动谓词（合并，SEL谓词版别名） | `MOV <Pd>.B, <Pg>/M, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `MOV (predicate, zeroing)` | Move predicates (zeroing): an alias of AND (predicates) | 移动谓词（清零，AND谓词版别名） | `MOV <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `MOV (scalar, predicated)` | Move general-purpose register to vector elements (predicated): an alias of CPY (scalar) | 将通用寄存器移入SVE向量元素（有谓词，CPY标量版别名） | `MOV <Zd>.<T>, <Pg>/M, <R><n\|SP>` | FEAT_SME, FEAT_SVE |
| `MOV (scalar, unpredicated)` | Move general-purpose register to vector elements (unpredicated): an alias of DUP (scalar) | 将通用寄存器移入SVE向量元素（无谓词，DUP标量版别名） | `MOV <Zd>.<T>, <R><n\|SP>` | FEAT_SME, FEAT_SVE |
| `MOV (SIMD&FP scalar, predicated)` | Move SIMD&FP scalar register to vector elements (predicated): an alias of CPY (SIMD&FP scalar) | 将SIMD&FP标量寄存器移入SVE向量元素（有谓词，CPY SIMD&FP版别名） | `MOV <Zd>.<T>, <Pg>/M, <V><n>` | FEAT_SME, FEAT_SVE |
| `MOV (SIMD&FP scalar, unpredicated)` | Move indexed element or SIMD&FP scalar to vector (unpredicated): an alias of DUP (indexed) | 将索引元素或SIMD&FP标量移入SVE向量（无谓词，DUP索引版别名） | `MOV <Zd>.<T>, <V><n>`<br>`MOV <Zd>.<T>, <Zn>.<T>[<imm>]` | FEAT_SME, FEAT_SVE |
| `MOV (vector, predicated)` | Move vector elements (predicated): an alias of SEL (vectors) | 按谓词条件移动向量元素（SEL 向量的别名） | `MOV <Zd>.<T>, <Pv>/M, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `MOV (vector, unpredicated)` | Move vector register (unpredicated): an alias of ORR (vectors, unpredicated) | 无谓词移动向量寄存器（ORR 向量无谓词的别名） | `MOV <Zd>.D, <Zn>.D` | FEAT_SME, FEAT_SVE |
| `MOVPRFX (predicated)` | Move prefix (predicated) | 带谓词的移动前缀指令 | `MOVPRFX <Zd>.<T>, <Pg>/<ZM>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `MOVPRFX (unpredicated)` | Move prefix (unpredicated) | 不带谓词的移动前缀指令 | `MOVPRFX <Zd>, <Zn>` | FEAT_SME, FEAT_SVE |
| `MOVS (predicated)` | Move predicates (zeroing), setting the condition flags: an alias of ANDS | 归零移动谓词并设置条件标志（ANDS 的别名） | `MOVS <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `MOVS (unpredicated)` | Move predicate (unpredicated), setting the condition flags: an alias of ORRS | 无谓词移动谓词并设置条件标志（ORRS 的别名） | `MOVS <Pd>.B, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `MSB` | Multiply-subtract to multiplicand | 将乘积从被乘数中减去（带谓词乘减） | `MSB <Zdn>.<T>, <Pg>/M, <Zm>.<T>, <Za>.<T>` | FEAT_SME, FEAT_SVE |
| `MUL (immediate)` | Multiply by immediate (unpredicated) | 向量元素乘以立即数（无谓词） | `MUL <Zdn>.<T>, <Zdn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `MUL (indexed)` | Multiply by indexed element | 向量元素乘以索引元素 | `MUL <Zd>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`MUL <Zd>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`MUL <Zd>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `MUL (vectors, predicated)` | Multiply (predicated) | 向量元素相乘（带谓词） | `MUL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `MUL (vectors, unpredicated)` | Multiply (unpredicated) | 向量元素相乘（无谓词） | `MUL <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `NAND` | Bitwise NAND predicates | 谓词按位与非（NAND） | `NAND <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `NANDS` | Bitwise NAND predicates, setting the condition flags | 谓词按位与非并设置条件标志 | `NANDS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `NBSL` | Bitwise inverted select | 按位反转选择（Bitwise inverted select） | `NBSL <Zdn>.D, <Zdn>.D, <Zm>.D, <Zk>.D` | FEAT_SME, FEAT_SVE2 |
| `NEG` | Negate (predicated) | 向量元素取反（带谓词） | `NEG <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`NEG <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `NMATCH` | Detect no matching elements, setting the condition flags | 检测无匹配元素并设置条件标志 | `NMATCH <Pd>.<T>, <Pg>/Z, <Zn>.<T>, <Zm>.<T>` | FEAT_SVE2 |
| `NOR` | Bitwise NOR predicates | 谓词按位或非（NOR） | `NOR <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `NORS` | Bitwise NOR predicates, setting the condition flags | 谓词按位或非并设置条件标志 | `NORS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `NOT (predicate)` | Bitwise invert predicate: an alias of EOR (predicates) | 按位取反谓词（EOR 谓词的别名） | `NOT <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `NOT (vector)` | Bitwise invert (predicated) | 向量元素按位取反（带谓词） | `NOT <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`NOT <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `NOTS` | Bitwise invert predicate, setting the condition flags: an alias of EORS | 按位取反谓词并设置条件标志（EORS 的别名） | `NOTS <Pd>.B, <Pg>/Z, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `ORN (immediate)` | Bitwise inclusive OR with inverted immediate (unpredicated): an alias of ORR (immediate) | 向量与立即数取反后按位或（ORR 立即数的别名） | `ORN <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `ORN (predicates)` | Bitwise inclusive OR inverted predicate | 谓词按位或取反（OR NOT） | `ORN <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `ORNS` | Bitwise inclusive OR inverted predicate, setting the condition flags | 谓词按位或取反并设置条件标志 | `ORNS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `ORQV` | Bitwise inclusive OR reduction of quadword vector segments | 按四字（128位）段对向量进行按位或归约 | `ORQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ORR (immediate)` | Bitwise inclusive OR with immediate (unpredicated) | 向量元素与立即数按位或（无谓词） | `ORR <Zdn>.<T>, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE |
| `ORR (predicates)` | Bitwise inclusive OR predicates | 谓词按位或 | `ORR <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `ORR (vectors, predicated)` | Bitwise inclusive OR (predicated) | 向量元素按位或（带谓词） | `ORR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `ORR (vectors, unpredicated)` | Bitwise inclusive OR (unpredicated) | 向量元素按位或（无谓词） | `ORR <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE |
| `ORRS` | Bitwise inclusive OR predicates, setting the condition flags | 谓词按位或并设置条件标志 | `ORRS <Pd>.B, <Pg>/Z, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `ORV` | Bitwise inclusive OR reduction to scalar | 向量元素按位或归约到标量 | `ORV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `PEXT (predicate pair)` | Predicate extract pair from predicate-as-counter | 从计数器形式谓词中提取谓词对 | `PEXT { <Pd1>.<T>, <Pd2>.<T> }, <PNn>[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `PEXT (predicate)` | Predicate extract from predicate-as-counter | 从计数器形式谓词中提取单个谓词 | `PEXT <Pd>.<T>, <PNn>[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `PFALSE` | Set all predicate elements to false | 将谓词寄存器所有元素设为假 | `PFALSE <Pd>.B` | FEAT_SME, FEAT_SVE |
| `PFIRST` | Set the First active predicate element to true | 将第一个活跃谓词元素置为真 | `PFIRST <Pdn>.B, <Pg>, <Pdn>.B` | FEAT_SME, FEAT_SVE |
| `PMLAL` | Multi-vector polynomial multiply long and accumulate | 多向量多项式乘长并累加 | `PMLAL { <Zda1>.Q-<Zda2>.Q }, <Zn>.D, <Zm>.D` | FEAT_SVE_AES2 |
| `PMOV (to predicate)` | Move predicate from vector | 从向量中提取位并写入谓词寄存器 | `PMOV <Pd>.B, <Zn>`<br>`PMOV <Pd>.D, <Zn>{[<imm>]}`<br>`PMOV <Pd>.H, <Zn>{[<imm>]}`<br>`PMOV <Pd>.S, <Zn>{[<imm>]}` | FEAT_SME2p1, FEAT_SVE2p1 |
| `PMOV (to vector)` | Move predicate to vector | 将谓词寄存器位扩展写入向量 | `PMOV <Zd>, <Pn>.B`<br>`PMOV <Zd>{[<imm>]}, <Pn>.D`<br>`PMOV <Zd>{[<imm>]}, <Pn>.H`<br>`PMOV <Zd>{[<imm>]}, <Pn>.S` | FEAT_SME2p1, FEAT_SVE2p1 |
| `PMUL` | Polynomial multiply (unpredicated) | 向量元素多项式相乘（无谓词） | `PMUL <Zd>.B, <Zn>.B, <Zm>.B` | FEAT_SME, FEAT_SVE2 |
| `PMULL` | Multi-vector polynomial multiply long | 多向量多项式乘长 | `PMULL { <Zd1>.Q-<Zd2>.Q }, <Zn>.D, <Zm>.D` | FEAT_SVE_AES2 |
| `PMULLB` | Polynomial multiply long (bottom) | 多项式长乘（取低半部分元素） | `PMULLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>`<br>`PMULLB <Zd>.Q, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE2, FEAT_SVE_PMULL128 |
| `PMULLT` | Polynomial multiply long (top) | 多项式长乘（取高半部分元素） | `PMULLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>`<br>`PMULLT <Zd>.Q, <Zn>.D, <Zm>.D` | FEAT_SME, FEAT_SVE2, FEAT_SVE_PMULL128 |
| `PNEXT` | Find next active predicate | 查找下一个活跃谓词 | `PNEXT <Pdn>.<T>, <Pv>, <Pdn>.<T>` | FEAT_SME, FEAT_SVE |
| `PRFB (scalar plus immediate)` | Contiguous prefetch bytes (immediate index) | 连续预取字节（立即数偏移） | `PRFB <prfop>, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `PRFB (scalar plus scalar)` | Contiguous prefetch bytes (scalar index) | 连续预取字节（标量索引） | `PRFB <prfop>, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `PRFB (scalar plus vector)` | Gather prefetch bytes (scalar plus vector) | 聚集预取字节（标量加向量） | `PRFB <prfop>, <Pg>, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`PRFB <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`PRFB <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `PRFB (vector plus immediate)` | Gather prefetch bytes (vector plus immediate) | 聚集预取字节（向量加立即数） | `PRFB <prfop>, <Pg>, [<Zn>.S{, #<imm>}]`<br>`PRFB <prfop>, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `PRFD (scalar plus immediate)` | Contiguous prefetch doublewords (immediate index) | 连续预取双字（立即数偏移） | `PRFD <prfop>, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `PRFD (scalar plus scalar)` | Contiguous prefetch doublewords (scalar index) | 连续预取双字（标量索引） | `PRFD <prfop>, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `PRFD (scalar plus vector)` | Gather prefetch doublewords (scalar plus vector) | 聚集预取双字（标量加向量） | `PRFD <prfop>, <Pg>, [<Xn\|SP>, <Zm>.S, <mod> #3]`<br>`PRFD <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #3]`<br>`PRFD <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #3]` | FEAT_SVE |
| `PRFD (vector plus immediate)` | Gather prefetch doublewords (vector plus immediate) | 聚集预取双字（向量加立即数） | `PRFD <prfop>, <Pg>, [<Zn>.S{, #<imm>}]`<br>`PRFD <prfop>, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `PRFH (scalar plus immediate)` | Contiguous prefetch halfwords (immediate index) | 连续预取半字（立即数偏移） | `PRFH <prfop>, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `PRFH (scalar plus scalar)` | Contiguous prefetch halfwords (scalar index) | 连续预取半字（标量索引） | `PRFH <prfop>, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `PRFH (scalar plus vector)` | Gather prefetch halfwords (scalar plus vector) | 聚集预取半字（标量加向量） | `PRFH <prfop>, <Pg>, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`PRFH <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`PRFH <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #1]` | FEAT_SVE |
| `PRFH (vector plus immediate)` | Gather prefetch halfwords (vector plus immediate) | 聚集预取半字（向量加立即数） | `PRFH <prfop>, <Pg>, [<Zn>.S{, #<imm>}]`<br>`PRFH <prfop>, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `PRFW (scalar plus immediate)` | Contiguous prefetch words (immediate index) | 连续预取字（立即数偏移） | `PRFW <prfop>, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `PRFW (scalar plus scalar)` | Contiguous prefetch words (scalar index) | 连续预取字（标量索引） | `PRFW <prfop>, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `PRFW (scalar plus vector)` | Gather prefetch words (scalar plus vector) | 聚集预取字（标量加向量） | `PRFW <prfop>, <Pg>, [<Xn\|SP>, <Zm>.S, <mod> #2]`<br>`PRFW <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`PRFW <prfop>, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #2]` | FEAT_SVE |
| `PRFW (vector plus immediate)` | Gather prefetch words (vector plus immediate) | 聚集预取字（向量加立即数） | `PRFW <prfop>, <Pg>, [<Zn>.S{, #<imm>}]`<br>`PRFW <prfop>, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `PSEL` | Predicate select between predicate register or all-false | 从谓词寄存器或全假值中按条件选择谓词 | `PSEL <Pd>, <Pn>, <Pm>.<T>[<Wv>, <imm>]` | FEAT_SME, FEAT_SVE2p1 |
| `PTEST` | Set condition flags for predicate | 根据谓词设置条件标志 | `PTEST <Pg>, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `PTRUE (predicate as counter)` | Initialize predicate-as-counter to all active | 将计数器形式谓词初始化为全活跃 | `PTRUE <PNd>.<T>` | FEAT_SME2, FEAT_SVE2p1 |
| `PTRUE (predicate)` | Initialize predicate from named constraint | 按命名约束初始化谓词寄存器 | `PTRUE <Pd>.<T>{, <pattern>}` | FEAT_SME, FEAT_SVE |
| `PTRUES` | Initialize predicate from named constraint and set the condition flags | 按命名约束初始化谓词并设置条件标志 | `PTRUES <Pd>.<T>{, <pattern>}` | FEAT_SME, FEAT_SVE |
| `PUNPKHI, PUNPKLO` | Unpack and widen half of predicate | 将谓词高半部解包并宽展 | `PUNPKHI <Pd>.H, <Pn>.B`<br>`PUNPKLO <Pd>.H, <Pn>.B` | FEAT_SME, FEAT_SVE |
| `RADDHNB` | Rounding add narrow high part (bottom) | 舍入加法取高位窄化（存低半元素） | `RADDHNB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `RADDHNT` | Rounding add narrow high part (top) | 舍入加法取高位窄化（存高半元素） | `RADDHNT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `RAX1` | Bitwise rotate left by 1 and exclusive-OR | 向左循环移位1位并与另一向量异或 | `RAX1 <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_SVE_SHA3 |
| `RBIT` | Reverse bits (predicated) | 按位反转各元素的位序（带谓词） | `RBIT <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`RBIT <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `RDFFR (predicated)` | Return predicate of successfully loaded elements | 返回成功加载元素的谓词（带谓词） | `RDFFR <Pd>.B, <Pg>/Z` | FEAT_SVE |
| `RDFFR (unpredicated)` | Read the first-fault register | 读取首次错误寄存器（FFR） | `RDFFR <Pd>.B` | FEAT_SVE |
| `RDFFRS` | Return predicate of successfully loaded elements, setting the condition flags | 返回成功加载元素的谓词并设置条件标志 | `RDFFRS <Pd>.B, <Pg>/Z` | FEAT_SVE |
| `RDVL` | Read multiple of vector register size to scalar register | 将向量寄存器长度的倍数读入标量寄存器 | `RDVL <Xd>, #<imm>` | FEAT_SME, FEAT_SVE |
| `REV (predicate)` | Reverse all elements in a predicate | 反转谓词寄存器中所有元素的顺序 | `REV <Pd>.<T>, <Pn>.<T>` | FEAT_SME, FEAT_SVE |
| `REV (vector)` | Reverse all elements in a vector (unpredicated) | 反转向量中所有元素的顺序（无谓词） | `REV <Zd>.<T>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `REVB, REVH, REVW` | Reverse bytes / halfwords / words within elements (predicated) | 在元素内反转字节/半字/字的顺序（带谓词） | `REVB <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`REVB <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`REVH <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`REVH <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`REVW <Zd>.D, <Pg>/M, <Zn>.D`<br>`REVW <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `REVD` | Reverse 64-bit doublewords in elements (predicated) | 在元素内反转64位双字顺序（带谓词） | `REVD <Zd>.Q, <Pg>/M, <Zn>.Q`<br>`REVD <Zd>.Q, <Pg>/Z, <Zn>.Q` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2p1, FEAT_SVE2p2 |
| `RSHRNB` | Rounding shift right narrow by immediate (bottom) | 按立即数舍入右移并窄化（存低半元素） | `RSHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `RSHRNT` | Rounding shift right narrow by immediate (top) | 按立即数舍入右移并窄化（存高半元素） | `RSHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `RSUBHNB` | Rounding subtract narrow high part (bottom) | 舍入减法取高位窄化（存低半元素） | `RSUBHNB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `RSUBHNT` | Rounding subtract narrow high part (top) | 舍入减法取高位窄化（存高半元素） | `RSUBHNT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SABA` | Signed absolute difference and accumulate | 有符号绝对差并累加 | `SABA <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SABALB` | Signed absolute difference and accumulate long (bottom) | 有符号绝对差长累加（取低半元素） | `SABALB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SABALT` | Signed absolute difference and accumulate long (top) | 有符号绝对差长累加（取高半元素） | `SABALT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SABD` | Signed absolute difference (predicated) | 有符号绝对差（带谓词） | `SABD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SABDLB` | Signed absolute difference long (bottom) | 有符号长绝对差（取低半元素） | `SABDLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SABDLT` | Signed absolute difference long (top) | 有符号长绝对差（取高半元素） | `SABDLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADALP` | Signed add and accumulate long pairwise | 有符号成对相加并长累加（带谓词） | `SADALP <Zda>.<T>, <Pg>/M, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADDLB` | Signed add long (bottom) | 有符号长加法（取低半元素） | `SADDLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADDLBT` | Signed add long (bottom + top) | 有符号长加法（低半加高半元素） | `SADDLBT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADDLT` | Signed add long (top) | 有符号长加法（取高半元素） | `SADDLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADDV` | Signed add reduction to scalar | 有符号向量元素归约求和到标量 | `SADDV <Dd>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `SADDWB` | Signed add wide (bottom) | 有符号宽加法（取低半元素） | `SADDWB <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SADDWT` | Signed add wide (top) | 有符号宽加法（取高半元素） | `SADDWT <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SBCLB` | Subtract with carry long (bottom) | 有符号带借位长减法（存低半元素） | `SBCLB <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SBCLT` | Subtract with carry long (top) | 有符号带借位长减法（存高半元素） | `SBCLT <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SCLAMP` | Signed clamp to minimum/maximum | 有符号钳位到最小值/最大值范围 | `SCLAMP <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2p1 |
| `SCVTF (predicated)` | Signed integer convert to floating-point (predicated) | 有符号整数转浮点数（带谓词） | `SCVTF <Zd>.H, <Pg>/M, <Zn>.H`<br>`SCVTF <Zd>.H, <Pg>/Z, <Zn>.H`<br>`SCVTF <Zd>.H, <Pg>/M, <Zn>.S`<br>`SCVTF <Zd>.H, <Pg>/Z, <Zn>.S`<br>`SCVTF <Zd>.S, <Pg>/M, <Zn>.S`<br>`SCVTF <Zd>.S, <Pg>/Z, <Zn>.S`<br>`SCVTF <Zd>.D, <Pg>/M, <Zn>.S`<br>`SCVTF <Zd>.D, <Pg>/Z, <Zn>.S`<br>`SCVTF <Zd>.H, <Pg>/M, <Zn>.D`<br>`SCVTF <Zd>.H, <Pg>/Z, <Zn>.D`<br>`SCVTF <Zd>.S, <Pg>/M, <Zn>.D`<br>`SCVTF <Zd>.S, <Pg>/Z, <Zn>.D`<br>`SCVTF <Zd>.D, <Pg>/M, <Zn>.D`<br>`SCVTF <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `SDIV` | Signed divide (predicated) | 有符号整数除法（带谓词） | `SDIV <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SDIVR` | Signed reversed divide (predicated) | 有符号整数反向除法（带谓词） | `SDIVR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SDOT (2-way, indexed)` | Signed integer dot product by indexed element (two-way) | 有符号整数点积（双路，索引元素） | `SDOT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `SDOT (2-way, vectors)` | Signed integer dot product (two-way) | 有符号整数点积（双路，向量） | `SDOT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME2, FEAT_SVE2p1 |
| `SDOT (4-way, indexed)` | Signed integer dot product by indexed element (four-way) | 有符号整数点积（四路，索引元素） | `SDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]`<br>`SDOT <Zda>.D, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE |
| `SDOT (4-way, vectors)` | Signed integer dot product (four-way) | 有符号整数点积（四路，向量） | `SDOT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE |
| `SEL (predicates)` | Conditionally select elements from two predicates | 按条件从两个谓词中选取元素 | `SEL <Pd>.B, <Pg>, <Pn>.B, <Pm>.B` | FEAT_SME, FEAT_SVE |
| `SEL (vectors)` | Conditionally select elements from two vectors | 按谓词从两个向量中条件选取元素 | `SEL <Zd>.<T>, <Pv>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SETFFR` | Initialize the first-fault register to all true | 将首次错误寄存器（FFR）初始化为全真 | `SETFFR` | FEAT_SVE |
| `SHADD` | Signed halving add | 有符号折半加法（带谓词） | `SHADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SHRNB` | Shift right narrow by immediate (bottom) | 按立即数右移并窄化（存低半元素） | `SHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SHRNT` | Shift right narrow by immediate (top) | 按立即数右移并窄化（存高半元素） | `SHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SHSUB` | Signed halving subtract | 有符号折半减法（带谓词） | `SHSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SHSUBR` | Signed halving subtract reversed | 有符号折半反向减法（带谓词） | `SHSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SLI` | Shift left and insert (immediate) | 向量元素左移并插入（立即数位移） | `SLI <Zd>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SM4E` | SM4 encryption and decryption | SM4 加密/解密轮操作 | `SM4E <Zdn>.S, <Zdn>.S, <Zm>.S` | FEAT_SVE_SM4 |
| `SM4EKEY` | SM4 key updates | SM4 密钥扩展轮操作 | `SM4EKEY <Zd>.S, <Zn>.S, <Zm>.S` | FEAT_SVE_SM4 |
| `SMAX (immediate)` | Signed maximum with immediate (unpredicated) | 有符号最大值与立即数比较（无谓词） | `SMAX <Zdn>.<T>, <Zdn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `SMAX (vectors)` | Signed maximum (predicated) | 有符号向量元素最大值（带谓词） | `SMAX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SMAXP` | Signed maximum pairwise | 有符号成对最大值（带谓词） | `SMAXP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SMAXQV` | Signed maximum reduction of quadword vector segments | 按四字段对向量进行有符号最大归约 | `SMAXQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `SMAXV` | Signed maximum reduction to scalar | 有符号向量元素最大值归约到标量 | `SMAXV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `SMIN (immediate)` | Signed minimum with immediate (unpredicated) | 有符号立即数最小值（无谓词） | `SMIN <Zdn>.<T>, <Zdn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `SMIN (vectors)` | Signed minimum (predicated) | 有符号向量最小值（有谓词） | `SMIN <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SMINP` | Signed minimum pairwise | 有符号成对最小值 | `SMINP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SMINQV` | Signed minimum reduction of quadword vector segments | 有符号四字向量段最小值规约 | `SMINQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `SMINV` | Signed minimum reduction to scalar | 有符号向量元素最小值规约到标量 | `SMINV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `SMLALB (indexed)` | Signed multiply-add long by indexed element (bottom) | 有符号按索引元素乘加长（低半） | `SMLALB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMLALB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMLALB (vectors)` | Signed multiply-add long (bottom) | 有符号向量乘加长（低半） | `SMLALB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SMLALT (indexed)` | Signed multiply-add long by indexed element (top) | 有符号按索引元素乘加长（高半） | `SMLALT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMLALT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMLALT (vectors)` | Signed multiply-add long (top) | 有符号向量乘加长（高半） | `SMLALT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SMLSLB (indexed)` | Signed multiply-subtract long by indexed element (bottom) | 有符号按索引元素乘减长（低半） | `SMLSLB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMLSLB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMLSLB (vectors)` | Signed multiply-subtract long (bottom) | 有符号向量乘减长（低半） | `SMLSLB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SMLSLT (indexed)` | Signed multiply-subtract long by indexed element (top) | 有符号按索引元素乘减长（高半） | `SMLSLT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMLSLT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMLSLT (vectors)` | Signed multiply-subtract long (top) | 有符号向量乘减长（高半） | `SMLSLT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SMMLA` | Signed 8-bit integer matrix multiply-accumulate to 32-bit integer | 有符号8位整数矩阵乘累加到32位整数 | `SMMLA <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_I8MM, FEAT_SVE |
| `SMULH (predicated)` | Signed multiply returning high half (predicated) | 有符号乘法取高半结果（有谓词） | `SMULH <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SMULH (unpredicated)` | Signed multiply returning high half (unpredicated) | 有符号乘法取高半结果（无谓词） | `SMULH <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SMULLB (indexed)` | Signed multiply long by indexed element (bottom) | 有符号按索引元素乘长（低半） | `SMULLB <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMULLB <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMULLB (vectors)` | Signed multiply long (bottom) | 有符号向量乘长（低半） | `SMULLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SMULLT (indexed)` | Signed multiply long by indexed element (top) | 有符号按索引元素乘长（高半） | `SMULLT <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SMULLT <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SMULLT (vectors)` | Signed multiply long (top) | 有符号向量乘长（高半） | `SMULLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SPLICE` | Splice two vectors under predicate control | 在谓词控制下拼接两个向量 | `SPLICE <Zd>.<T>, <Pv>, { <Zn1>.<T>, <Zn2>.<T> }`<br>`SPLICE <Zdn>.<T>, <Pv>, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE, FEAT_SVE2 |
| `SQABS` | Signed saturating absolute value | 有符号饱和绝对值 | `SQABS <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`SQABS <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `SQADD (immediate)` | Signed saturating add immediate (unpredicated) | 有符号饱和加立即数（无谓词） | `SQADD <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `SQADD (vectors, predicated)` | Signed saturating add (predicated) | 有符号饱和向量加法（有谓词） | `SQADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQADD (vectors, unpredicated)` | Signed saturating add (unpredicated) | 有符号饱和向量加法（无谓词） | `SQADD <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQCADD` | Saturating complex integer add | 饱和复数整数加法 | `SQCADD <Zdn>.<T>, <Zdn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE2 |
| `SQCVTN` | Signed 32-bit integer saturating extract narrow to interleaved 16-bit integer | 有符号32位整数饱和窄化提取为交错16位整数 | `SQCVTN <Zd>.H, { <Zn1>.S-<Zn2>.S }` | FEAT_SME2, FEAT_SVE2p1 |
| `SQCVTUN` | Signed 32-bit integer saturating extract narrow to interleaved unsigned 16-bit integer | 有符号32位整数饱和窄化提取为交错无符号16位整数 | `SQCVTUN <Zd>.H, { <Zn1>.S-<Zn2>.S }` | FEAT_SME2, FEAT_SVE2p1 |
| `SQDECB` | Signed saturating decrement scalar by multiple of 8-bit predicate constraint element count | 有符号饱和标量减去8位谓词约束元素数倍数 | `SQDECB <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQDECB <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECD (scalar)` | Signed saturating decrement scalar by multiple of 64-bit predicate constraint element count | 有符号饱和标量减去64位谓词约束元素数倍数 | `SQDECD <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQDECD <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECD (vector)` | Signed saturating decrement vector by multiple of 64-bit predicate constraint element count | 有符号饱和向量减去64位谓词约束元素数倍数 | `SQDECD <Zdn>.D{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECH (scalar)` | Signed saturating decrement scalar by multiple of 16-bit predicate constraint element count | 有符号饱和标量减去16位谓词约束元素数倍数 | `SQDECH <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQDECH <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECH (vector)` | Signed saturating decrement vector by multiple of 16-bit predicate constraint element count | 有符号饱和向量减去16位谓词约束元素数倍数 | `SQDECH <Zdn>.H{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECP (scalar)` | Signed saturating decrement scalar by count of true predicate elements | 有符号饱和标量减去真谓词元素数 | `SQDECP <Xdn>, <Pm>.<T>, <Wdn>`<br>`SQDECP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQDECP (vector)` | Signed saturating decrement vector by count of true predicate elements | 有符号饱和向量减去真谓词元素数 | `SQDECP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQDECW (scalar)` | Signed saturating decrement scalar by multiple of 32-bit predicate constraint element count | 有符号饱和标量减去32位谓词约束元素数倍数 | `SQDECW <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQDECW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDECW (vector)` | Signed saturating decrement vector by multiple of 32-bit predicate constraint element count | 有符号饱和向量减去32位谓词约束元素数倍数 | `SQDECW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQDMLALB (indexed)` | Signed saturating doubling multiply-add by indexed element (bottom) | 有符号饱和倍增乘加按索引元素（低半） | `SQDMLALB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMLALB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMLALB (vectors)` | Signed saturating doubling multiply-add (bottom) | 有符号饱和倍增乘加向量（低半） | `SQDMLALB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMLALBT` | Signed saturating doubling multiply-add (bottom × top) | 有符号饱和倍增乘加向量（低半×高半） | `SQDMLALBT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMLALT (indexed)` | Signed saturating doubling multiply-add by indexed element (top) | 有符号饱和倍增乘加按索引元素（高半） | `SQDMLALT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMLALT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMLALT (vectors)` | Signed saturating doubling multiply-add (top) | 有符号饱和倍增乘加向量（高半） | `SQDMLALT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMLSLB (indexed)` | Signed saturating doubling multiply-subtract by indexed element (bottom) | 有符号饱和倍增乘减按索引元素（低半） | `SQDMLSLB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMLSLB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMLSLB (vectors)` | Signed saturating doubling multiply-subtract (bottom) | 有符号饱和倍增乘减向量（低半） | `SQDMLSLB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMLSLBT` | Signed saturating doubling multiply-subtract (bottom × top) | 有符号饱和倍增乘减向量（低半×高半） | `SQDMLSLBT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMLSLT (indexed)` | Signed saturating doubling multiply-subtract by indexed element (top) | 有符号饱和倍增乘减按索引元素（高半） | `SQDMLSLT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMLSLT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMLSLT (vectors)` | Signed saturating doubling multiply-subtract (top) | 有符号饱和倍增乘减向量（高半） | `SQDMLSLT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMULH (indexed)` | Signed saturating doubling multiply high by indexed element | 有符号饱和倍增乘高按索引元素 | `SQDMULH <Zd>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMULH <Zd>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`SQDMULH <Zd>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMULH (vectors)` | Signed saturating doubling multiply high (unpredicated) | 有符号饱和倍增乘高（无谓词） | `SQDMULH <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQDMULLB (indexed)` | Signed saturating doubling multiply by indexed element (bottom) | 有符号饱和倍增乘长按索引元素（低半） | `SQDMULLB <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMULLB <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMULLB (vectors)` | Signed saturating doubling multiply (bottom) | 有符号饱和倍增乘长（低半） | `SQDMULLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQDMULLT (indexed)` | Signed saturating doubling multiply by indexed element (top) | 有符号饱和倍增乘长按索引元素（高半） | `SQDMULLT <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`SQDMULLT <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQDMULLT (vectors)` | Signed saturating doubling multiply (top) | 有符号饱和倍增乘长（高半） | `SQDMULLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQINCB` | Signed saturating increment scalar by multiple of 8-bit predicate constraint element count | 有符号饱和标量加上8位谓词约束元素数倍数 | `SQINCB <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQINCB <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCD (scalar)` | Signed saturating increment scalar by multiple of 64-bit predicate constraint element count | 有符号饱和标量加上64位谓词约束元素数倍数 | `SQINCD <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQINCD <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCD (vector)` | Signed saturating increment vector by multiple of 64-bit predicate constraint element count | 有符号饱和向量加上64位谓词约束元素数倍数 | `SQINCD <Zdn>.D{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCH (scalar)` | Signed saturating increment scalar by multiple of 16-bit predicate constraint element count | 有符号饱和标量加上16位谓词约束元素数倍数 | `SQINCH <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQINCH <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCH (vector)` | Signed saturating increment vector by multiple of 16-bit predicate constraint element count | 有符号饱和向量加上16位谓词约束元素数倍数 | `SQINCH <Zdn>.H{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCP (scalar)` | Signed saturating increment scalar by count of true predicate elements | 有符号饱和标量加上真谓词元素数 | `SQINCP <Xdn>, <Pm>.<T>, <Wdn>`<br>`SQINCP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQINCP (vector)` | Signed saturating increment vector by count of true predicate elements | 有符号饱和向量加上真谓词元素数 | `SQINCP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQINCW (scalar)` | Signed saturating increment scalar by multiple of 32-bit predicate constraint element count | 有符号饱和标量加上32位谓词约束元素数倍数 | `SQINCW <Xdn>, <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`SQINCW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQINCW (vector)` | Signed saturating increment vector by multiple of 32-bit predicate constraint element count | 有符号饱和向量加上32位谓词约束元素数倍数 | `SQINCW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `SQNEG` | Signed saturating negate | 有符号饱和取反 | `SQNEG <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`SQNEG <Zd>.<T>, <Pg>/Z, <Zn>.<T>` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `SQRDCMLAH (indexed)` | Saturating rounding doubling complex integer multiply-add high by indexed element | 饱和舍入倍增复数整数乘加高按索引元素 | `SQRDCMLAH <Zda>.H, <Zn>.H, <Zm>.H[<imm>], <const>`<br>`SQRDCMLAH <Zda>.S, <Zn>.S, <Zm>.S[<imm>], <const>` | FEAT_SME, FEAT_SVE2 |
| `SQRDCMLAH (vectors)` | Saturating rounding doubling complex integer multiply-add high | 饱和舍入倍增复数整数乘加高 | `SQRDCMLAH <Zda>.<T>, <Zn>.<T>, <Zm>.<T>, <const>` | FEAT_SME, FEAT_SVE2 |
| `SQRDMLAH (indexed)` | Signed saturating rounding doubling multiply-add high by indexed element | 有符号饱和舍入倍增乘加高按索引元素 | `SQRDMLAH <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`SQRDMLAH <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`SQRDMLAH <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQRDMLAH (vectors)` | Signed saturating rounding doubling multiply-add high (unpredicated) | 有符号饱和舍入倍增乘加高（无谓词） | `SQRDMLAH <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQRDMLSH (indexed)` | Signed saturating rounding doubling multiply-subtract high by indexed element | 有符号饱和舍入倍增乘减高按索引元素 | `SQRDMLSH <Zda>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`SQRDMLSH <Zda>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`SQRDMLSH <Zda>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQRDMLSH (vectors)` | Signed saturating rounding doubling multiply-subtract high (unpredicated) | 有符号饱和舍入倍增乘减高（无谓词） | `SQRDMLSH <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQRDMULH (indexed)` | Signed saturating rounding doubling multiply high by indexed element | 有符号饱和舍入倍增乘高按索引元素 | `SQRDMULH <Zd>.H, <Zn>.H, <Zm>.H[<imm>]`<br>`SQRDMULH <Zd>.S, <Zn>.S, <Zm>.S[<imm>]`<br>`SQRDMULH <Zd>.D, <Zn>.D, <Zm>.D[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `SQRDMULH (vectors)` | Signed saturating rounding doubling multiply high (unpredicated) | 有符号饱和舍入倍增乘高（无谓词） | `SQRDMULH <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHL` | Signed saturating rounding shift left (predicated) | 有符号饱和舍入左移（有谓词） | `SQRSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHLR` | Signed saturating rounding shift left reversed (predicated) | 有符号饱和舍入左移（反转，有谓词） | `SQRSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHRN` | Signed saturating rounding shift right narrow by immediate to interleaved integer | 有符号饱和舍入右移窄化为交错整数（立即数） | `SQRSHRN <Zd>.H, { <Zn1>.S-<Zn2>.S }, #<const>` | FEAT_SME2, FEAT_SVE2p1 |
| `SQRSHRNB` | Signed saturating rounding shift right narrow by immediate (bottom) | 有符号饱和舍入右移窄化立即数（低半） | `SQRSHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHRNT` | Signed saturating rounding shift right narrow by immediate (top) | 有符号饱和舍入右移窄化立即数（高半） | `SQRSHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHRUN` | Signed saturating rounding shift right unsigned narrow by immediate and interleave | 有符号饱和舍入右移无符号窄化并交错（立即数） | `SQRSHRUN <Zd>.H, { <Zn1>.S-<Zn2>.S }, #<const>` | FEAT_SME2, FEAT_SVE2p1 |
| `SQRSHRUNB` | Signed saturating rounding shift right narrow by immediate to unsigned integer (bottom) | 有符号饱和舍入右移窄化为无符号整数（低半） | `SQRSHRUNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQRSHRUNT` | Signed saturating rounding shift right narrow by immediate to unsigned integer (top) | 有符号饱和舍入右移窄化为无符号整数（高半） | `SQRSHRUNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHL (immediate)` | Signed saturating shift left by immediate | 有符号饱和左移立即数 | `SQSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHL (vectors)` | Signed saturating shift left (predicated) | 有符号饱和向量左移（有谓词） | `SQSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQSHLR` | Signed saturating shift left reversed (predicated) | 有符号饱和左移（反转，有谓词） | `SQSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQSHLU` | Signed saturating shift left unsigned by immediate | 有符号饱和左移为无符号（立即数） | `SQSHLU <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHRNB` | Signed saturating shift right narrow by immediate (bottom) | 有符号饱和右移窄化立即数（低半） | `SQSHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHRNT` | Signed saturating shift right narrow by immediate (top) | 有符号饱和右移窄化立即数（高半） | `SQSHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHRUNB` | Signed saturating shift right narrow by immediate to unsigned integer (bottom) | 有符号饱和右移窄化为无符号整数（低半） | `SQSHRUNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSHRUNT` | Signed saturating shift right narrow by immediate to unsigned integer (top) | 有符号饱和右移窄化为无符号整数（高半） | `SQSHRUNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SQSUB (immediate)` | Signed saturating subtract immediate (unpredicated) | 有符号饱和减立即数（无谓词） | `SQSUB <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `SQSUB (vectors, predicated)` | Signed saturating subtract (predicated) | 有符号饱和向量减法（有谓词） | `SQSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQSUB (vectors, unpredicated)` | Signed saturating subtract (unpredicated) | 有符号饱和向量减法（无谓词） | `SQSUB <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SQSUBR` | Signed saturating subtract reversed (predicated) | 有符号饱和减法（反转，有谓词） | `SQSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SQXTNB` | Signed saturating extract narrow (bottom) | 有符号饱和窄化提取（低半） | `SQXTNB <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQXTNT` | Signed saturating extract narrow (top) | 有符号饱和窄化提取（高半） | `SQXTNT <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQXTUNB` | Signed saturating extract narrow to unsigned integer (bottom) | 有符号饱和窄化提取为无符号整数（低半） | `SQXTUNB <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SQXTUNT` | Signed saturating extract narrow to unsigned integer (top) | 有符号饱和窄化提取为无符号整数（高半） | `SQXTUNT <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SRHADD` | Signed rounding halving add | 有符号舍入折半加法 | `SRHADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SRI` | Shift right and insert (immediate) | 右移并插入（立即数） | `SRI <Zd>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SRSHL` | Signed rounding shift left (predicated) | 有符号舍入左移（有谓词） | `SRSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SRSHLR` | Signed rounding shift left reversed (predicated) | 有符号舍入左移（反转，有谓词） | `SRSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SRSHR` | Signed rounding shift right by immediate | 有符号舍入右移立即数 | `SRSHR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SRSRA` | Signed rounding shift right and accumulate (immediate) | 有符号舍入右移并累加（立即数） | `SRSRA <Zda>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SSHLLB` | Signed shift left long by immediate (bottom) | 有符号长左移立即数（低半） | `SSHLLB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SSHLLT` | Signed shift left long by immediate (top) | 有符号长左移立即数（高半） | `SSHLLT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SSRA` | Signed shift right and accumulate (immediate) | 有符号右移并累加（立即数） | `SSRA <Zda>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `SSUBLB` | Signed subtract long (bottom) | 有符号长减法（低半） | `SSUBLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SSUBLBT` | Signed subtract long (bottom - top) | 有符号长减法（低半减高半） | `SSUBLBT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SSUBLT` | Signed subtract long (top) | 有符号长减法（高半） | `SSUBLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SSUBLTB` | Signed subtract long (top - bottom) | 有符号长减法（高半减低半） | `SSUBLTB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SSUBWB` | Signed subtract wide (bottom) | 有符号宽减法（低半） | `SSUBWB <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SSUBWT` | Signed subtract wide (top) | 有符号宽减法（高半） | `SSUBWT <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `ST1B (scalar plus immediate, consecutive registers)` | Contiguous store of bytes from multiple consecutive vectors (immediate index) | 连续存储多寄存器字节到内存（立即数索引） | `ST1B { <Zt1>.B-<Zt2>.B }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1B { <Zt1>.B-<Zt4>.B }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1B (scalar plus immediate, single register)` | Contiguous store bytes from vector (immediate index) | 连续存储向量字节到内存（立即数索引） | `ST1B { <Zt>.<T> }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST1B (scalar plus scalar, consecutive registers)` | Contiguous store of bytes from multiple consecutive vectors (scalar index) | 连续存储多寄存器字节到内存（标量索引） | `ST1B { <Zt1>.B-<Zt2>.B }, <PNg>, [<Xn\|SP>, <Xm>]`<br>`ST1B { <Zt1>.B-<Zt4>.B }, <PNg>, [<Xn\|SP>, <Xm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1B (scalar plus scalar, single register)` | Contiguous store bytes from vector (scalar index) | 连续存储向量字节到内存（标量索引） | `ST1B { <Zt>.<T> }, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `ST1B (scalar plus vector)` | Scatter store bytes from a vector (vector index) | 散布存储向量字节到内存（向量索引） | `ST1B { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`ST1B { <Zt>.S }, <Pg>, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`ST1B { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `ST1B (vector plus immediate)` | Scatter store bytes from a vector (immediate index) | 散布存储向量字节到内存（立即数索引） | `ST1B { <Zt>.S }, <Pg>, [<Zn>.S{, #<imm>}]`<br>`ST1B { <Zt>.D }, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `ST1D (scalar plus immediate, consecutive registers)` | Contiguous store of doublewords from multiple consecutive vectors (immediate index) | 连续存储多寄存器双字到内存（立即数索引） | `ST1D { <Zt1>.D-<Zt2>.D }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1D { <Zt1>.D-<Zt4>.D }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1D (scalar plus immediate, single register)` | Contiguous store doublewords from vector (immediate index) | 连续存储向量双字到内存（立即数索引） | `ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1D { <Zt>.Q }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `ST1D (scalar plus scalar, consecutive registers)` | Contiguous store of doublewords from multiple consecutive vectors (scalar index) | 连续存储多寄存器双字到内存（标量索引） | `ST1D { <Zt1>.D-<Zt2>.D }, <PNg>, [<Xn\|SP>, <Xm>, LSL #3]`<br>`ST1D { <Zt1>.D-<Zt4>.D }, <PNg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1D (scalar plus scalar, single register)` | Contiguous store doublewords from vector (scalar index) | 连续存储向量双字到内存（标量索引） | `ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]`<br>`ST1D { <Zt>.Q }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `ST1D (scalar plus vector)` | Scatter store doublewords from a vector (vector index) | SVE 向量散射存储双字（向量索引） | `ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #3]`<br>`ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #3]`<br>`ST1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `ST1D (vector plus immediate)` | Scatter store doublewords from a vector (immediate index) | SVE 向量散射存储双字（立即数索引） | `ST1D { <Zt>.D }, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `ST1H (scalar plus immediate, consecutive registers)` | Contiguous store of halfwords from multiple consecutive vectors (immediate index) | SVE 多连续向量连续存储半字（立即数索引） | `ST1H { <Zt1>.H-<Zt2>.H }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1H { <Zt1>.H-<Zt4>.H }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1H (scalar plus immediate, single register)` | Contiguous store halfwords from vector (immediate index) | SVE 向量连续存储半字（立即数索引） | `ST1H { <Zt>.<T> }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST1H (scalar plus scalar, consecutive registers)` | Contiguous store of halfwords from multiple consecutive vectors (scalar index) | SVE 多连续向量连续存储半字（标量索引） | `ST1H { <Zt1>.H-<Zt2>.H }, <PNg>, [<Xn\|SP>, <Xm>, LSL #1]`<br>`ST1H { <Zt1>.H-<Zt4>.H }, <PNg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1H (scalar plus scalar, single register)` | Contiguous store halfwords from vector (scalar index) | SVE 向量连续存储半字（标量索引） | `ST1H { <Zt>.<T> }, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `ST1H (scalar plus vector)` | Scatter store halfwords from a vector (vector index) | SVE 向量散射存储半字（向量索引） | `ST1H { <Zt>.S }, <Pg>, [<Xn\|SP>, <Zm>.S, <mod> #1]`<br>`ST1H { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #1]`<br>`ST1H { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`ST1H { <Zt>.S }, <Pg>, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`ST1H { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #1]`<br>`ST1H { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `ST1H (vector plus immediate)` | Scatter store halfwords from a vector (immediate index) | SVE 向量散射存储半字（立即数索引） | `ST1H { <Zt>.S }, <Pg>, [<Zn>.S{, #<imm>}]`<br>`ST1H { <Zt>.D }, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `ST1Q` | Scatter store quadwords | SVE 向量散射存储四字 | `ST1Q { <Zt>.Q }, <Pg>, [<Zn>.D{, <Xm>}]` | FEAT_SVE2p1 |
| `ST1W (scalar plus immediate, consecutive registers)` | Contiguous store of words from multiple consecutive vectors (immediate index) | SVE 多连续向量连续存储字（立即数索引） | `ST1W { <Zt1>.S-<Zt2>.S }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1W { <Zt1>.S-<Zt4>.S }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1W (scalar plus immediate, single register)` | Contiguous store words from vector (immediate index) | SVE 向量连续存储字（立即数索引） | `ST1W { <Zt>.<T> }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`ST1W { <Zt>.Q }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `ST1W (scalar plus scalar, consecutive registers)` | Contiguous store of words from multiple consecutive vectors (scalar index) | SVE 多连续向量连续存储字（标量索引） | `ST1W { <Zt1>.S-<Zt2>.S }, <PNg>, [<Xn\|SP>, <Xm>, LSL #2]`<br>`ST1W { <Zt1>.S-<Zt4>.S }, <PNg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME2, FEAT_SVE2p1 |
| `ST1W (scalar plus scalar, single register)` | Contiguous store words from vector (scalar index) | SVE 向量连续存储字（标量索引） | `ST1W { <Zt>.<T> }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]`<br>`ST1W { <Zt>.Q }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE, FEAT_SVE2p1 |
| `ST1W (scalar plus vector)` | Scatter store words from a vector (vector index) | SVE 向量散射存储字（向量索引） | `ST1W { <Zt>.S }, <Pg>, [<Xn\|SP>, <Zm>.S, <mod> #2]`<br>`ST1W { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod> #2]`<br>`ST1W { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, <mod>]`<br>`ST1W { <Zt>.S }, <Pg>, [<Xn\|SP>, <Zm>.S, <mod>]`<br>`ST1W { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D, LSL #2]`<br>`ST1W { <Zt>.D }, <Pg>, [<Xn\|SP>, <Zm>.D]` | FEAT_SVE |
| `ST1W (vector plus immediate)` | Scatter store words from a vector (immediate index) | SVE 向量散射存储字（立即数索引） | `ST1W { <Zt>.S }, <Pg>, [<Zn>.S{, #<imm>}]`<br>`ST1W { <Zt>.D }, <Pg>, [<Zn>.D{, #<imm>}]` | FEAT_SVE |
| `ST2B (scalar plus immediate)` | Contiguous store two-byte structures from two vectors (immediate index) | SVE 两向量连续存储两字节结构（立即数索引） | `ST2B { <Zt1>.B, <Zt2>.B }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST2B (scalar plus scalar)` | Contiguous store two-byte structures from two vectors (scalar index) | SVE 两向量连续存储两字节结构（标量索引） | `ST2B { <Zt1>.B, <Zt2>.B }, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `ST2D (scalar plus immediate)` | Contiguous store two-doubleword structures from two vectors (immediate index) | SVE 两向量连续存储两双字结构（立即数索引） | `ST2D { <Zt1>.D, <Zt2>.D }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST2D (scalar plus scalar)` | Contiguous store two-doubleword structures from two vectors (scalar index) | SVE 两向量连续存储两双字结构（标量索引） | `ST2D { <Zt1>.D, <Zt2>.D }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `ST2H (scalar plus immediate)` | Contiguous store two-halfword structures from two vectors (immediate index) | SVE 两向量连续存储两半字结构（立即数索引） | `ST2H { <Zt1>.H, <Zt2>.H }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST2H (scalar plus scalar)` | Contiguous store two-halfword structures from two vectors (scalar index) | SVE 两向量连续存储两半字结构（标量索引） | `ST2H { <Zt1>.H, <Zt2>.H }, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `ST2Q (scalar plus immediate)` | Contiguous store two-quadword structures from two vectors (immediate index) | SVE 两向量连续存储两四字结构（立即数索引） | `ST2Q { <Zt1>.Q, <Zt2>.Q }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST2Q (scalar plus scalar)` | Contiguous store two-quadword structures from two vectors (scalar index) | SVE 两向量连续存储两四字结构（标量索引） | `ST2Q { <Zt1>.Q, <Zt2>.Q }, <Pg>, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST2W (scalar plus immediate)` | Contiguous store two-word structures from two vectors (immediate index) | SVE 两向量连续存储两字结构（立即数索引） | `ST2W { <Zt1>.S, <Zt2>.S }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST2W (scalar plus scalar)` | Contiguous store two-word structures from two vectors (scalar index) | SVE 两向量连续存储两字结构（标量索引） | `ST2W { <Zt1>.S, <Zt2>.S }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `ST3B (scalar plus immediate)` | Contiguous store three-byte structures from three vectors (immediate index) | SVE 三向量连续存储三字节结构（立即数索引） | `ST3B { <Zt1>.B, <Zt2>.B, <Zt3>.B }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST3B (scalar plus scalar)` | Contiguous store three-byte structures from three vectors (scalar index) | SVE 三向量连续存储三字节结构（标量索引） | `ST3B { <Zt1>.B, <Zt2>.B, <Zt3>.B }, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `ST3D (scalar plus immediate)` | Contiguous store three-doubleword structures from three vectors (immediate index) | SVE 三向量连续存储三双字结构（立即数索引） | `ST3D { <Zt1>.D, <Zt2>.D, <Zt3>.D }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST3D (scalar plus scalar)` | Contiguous store three-doubleword structures from three vectors (scalar index) | SVE 三向量连续存储三双字结构（标量索引） | `ST3D { <Zt1>.D, <Zt2>.D, <Zt3>.D }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `ST3H (scalar plus immediate)` | Contiguous store three-halfword structures from three vectors (immediate index) | SVE 三向量连续存储三半字结构（立即数索引） | `ST3H { <Zt1>.H, <Zt2>.H, <Zt3>.H }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST3H (scalar plus scalar)` | Contiguous store three-halfword structures from three vectors (scalar index) | SVE 三向量连续存储三半字结构（标量索引） | `ST3H { <Zt1>.H, <Zt2>.H, <Zt3>.H }, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `ST3Q (scalar plus immediate)` | Contiguous store three-quadword structures from three vectors (immediate index) | SVE 三向量连续存储三四字结构（立即数索引） | `ST3Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST3Q (scalar plus scalar)` | Contiguous store three-quadword structures from three vectors (scalar index) | SVE 三向量连续存储三四字结构（标量索引） | `ST3Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q }, <Pg>, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST3W (scalar plus immediate)` | Contiguous store three-word structures from three vectors (immediate index) | SVE 三向量连续存储三字结构（立即数索引） | `ST3W { <Zt1>.S, <Zt2>.S, <Zt3>.S }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST3W (scalar plus scalar)` | Contiguous store three-word structures from three vectors (scalar index) | SVE 三向量连续存储三字结构（标量索引） | `ST3W { <Zt1>.S, <Zt2>.S, <Zt3>.S }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `ST4B (scalar plus immediate)` | Contiguous store four-byte structures from four vectors (immediate index) | SVE 四向量连续存储四字节结构（立即数索引） | `ST4B { <Zt1>.B, <Zt2>.B, <Zt3>.B, <Zt4>.B }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST4B (scalar plus scalar)` | Contiguous store four-byte structures from four vectors (scalar index) | SVE 四向量连续存储四字节结构（标量索引） | `ST4B { <Zt1>.B, <Zt2>.B, <Zt3>.B, <Zt4>.B }, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `ST4D (scalar plus immediate)` | Contiguous store four-doubleword structures from four vectors (immediate index) | SVE 四向量连续存储四双字结构（立即数索引） | `ST4D { <Zt1>.D, <Zt2>.D, <Zt3>.D, <Zt4>.D }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST4D (scalar plus scalar)` | Contiguous store four-doubleword structures from four vectors (scalar index) | SVE 四向量连续存储四双字结构（标量索引） | `ST4D { <Zt1>.D, <Zt2>.D, <Zt3>.D, <Zt4>.D }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `ST4H (scalar plus immediate)` | Contiguous store four-halfword structures from four vectors (immediate index) | SVE 四向量连续存储四半字结构（立即数索引） | `ST4H { <Zt1>.H, <Zt2>.H, <Zt3>.H, <Zt4>.H }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST4H (scalar plus scalar)` | Contiguous store four-halfword structures from four vectors (scalar index) | SVE 四向量连续存储四半字结构（标量索引） | `ST4H { <Zt1>.H, <Zt2>.H, <Zt3>.H, <Zt4>.H }, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `ST4Q (scalar plus immediate)` | Contiguous store four-quadword structures from four vectors (immediate index) | SVE 四向量连续存储四四字结构（立即数索引） | `ST4Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q, <Zt4>.Q }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST4Q (scalar plus scalar)` | Contiguous store four-quadword structures from four vectors (scalar index) | SVE 四向量连续存储四四字结构（标量索引） | `ST4Q { <Zt1>.Q, <Zt2>.Q, <Zt3>.Q, <Zt4>.Q }, <Pg>, [<Xn\|SP>, <Xm>, LSL #4]` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ST4W (scalar plus immediate)` | Contiguous store four-word structures from four vectors (immediate index) | SVE 四向量连续存储四字结构（立即数索引） | `ST4W { <Zt1>.S, <Zt2>.S, <Zt3>.S, <Zt4>.S }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `ST4W (scalar plus scalar)` | Contiguous store four-word structures from four vectors (scalar index) | SVE 四向量连续存储四字结构（标量索引） | `ST4W { <Zt1>.S, <Zt2>.S, <Zt3>.S, <Zt4>.S }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `STNT1B (scalar plus immediate, consecutive registers)` | Contiguous store non-temporal of bytes from multiple consecutive vectors (immediate index) | SVE 多连续向量连续非时态存储字节（立即数索引） | `STNT1B { <Zt1>.B-<Zt2>.B }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`STNT1B { <Zt1>.B-<Zt4>.B }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1B (scalar plus immediate, single register)` | Contiguous store non-temporal bytes from vector (immediate index) | SVE 向量连续非时态存储字节（立即数索引） | `STNT1B { <Zt>.B }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `STNT1B (scalar plus scalar, consecutive registers)` | Contiguous store non-temporal of bytes from multiple consecutive vectors (scalar index) | SVE 多连续向量连续非时态存储字节（标量索引） | `STNT1B { <Zt1>.B-<Zt2>.B }, <PNg>, [<Xn\|SP>, <Xm>]`<br>`STNT1B { <Zt1>.B-<Zt4>.B }, <PNg>, [<Xn\|SP>, <Xm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1B (scalar plus scalar, single register)` | Contiguous store non-temporal bytes from vector (scalar index) | SVE 向量连续非时态存储字节（标量索引） | `STNT1B { <Zt>.B }, <Pg>, [<Xn\|SP>, <Xm>]` | FEAT_SME, FEAT_SVE |
| `STNT1B (vector plus scalar)` | Scatter store non-temporal bytes | SVE 向量散射非时态存储字节 | `STNT1B { <Zt>.S }, <Pg>, [<Zn>.S{, <Xm>}]`<br>`STNT1B { <Zt>.D }, <Pg>, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `STNT1D (scalar plus immediate, consecutive registers)` | Contiguous store non-temporal of doublewords from multiple consecutive vectors (immediate index) | SVE 多连续向量连续非时态存储双字（立即数索引） | `STNT1D { <Zt1>.D-<Zt2>.D }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`STNT1D { <Zt1>.D-<Zt4>.D }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1D (scalar plus immediate, single register)` | Contiguous store non-temporal doublewords from vector (immediate index) | SVE 向量连续非时态存储双字（立即数索引） | `STNT1D { <Zt>.D }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `STNT1D (scalar plus scalar, consecutive registers)` | Contiguous store non-temporal of doublewords from multiple consecutive vectors (scalar index) | SVE 多连续向量连续非时态存储双字（标量索引） | `STNT1D { <Zt1>.D-<Zt2>.D }, <PNg>, [<Xn\|SP>, <Xm>, LSL #3]`<br>`STNT1D { <Zt1>.D-<Zt4>.D }, <PNg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1D (scalar plus scalar, single register)` | Contiguous store non-temporal doublewords from vector (scalar index) | SVE 向量连续非时态存储双字（标量索引） | `STNT1D { <Zt>.D }, <Pg>, [<Xn\|SP>, <Xm>, LSL #3]` | FEAT_SME, FEAT_SVE |
| `STNT1D (vector plus scalar)` | Scatter store non-temporal doublewords | SVE 向量散射非时态存储双字 | `STNT1D { <Zt>.D }, <Pg>, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `STNT1H (scalar plus immediate, consecutive registers)` | Contiguous store non-temporal of halfwords from multiple consecutive vectors (immediate index) | SVE 多连续向量连续非时态存储半字（立即数索引） | `STNT1H { <Zt1>.H-<Zt2>.H }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`STNT1H { <Zt1>.H-<Zt4>.H }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1H (scalar plus immediate, single register)` | Contiguous store non-temporal halfwords from vector (immediate index) | SVE 向量连续非时态存储半字（立即数索引） | `STNT1H { <Zt>.H }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `STNT1H (scalar plus scalar, consecutive registers)` | Contiguous store non-temporal of halfwords from multiple consecutive vectors (scalar index) | SVE 多连续向量连续非时态存储半字（标量索引） | `STNT1H { <Zt1>.H-<Zt2>.H }, <PNg>, [<Xn\|SP>, <Xm>, LSL #1]`<br>`STNT1H { <Zt1>.H-<Zt4>.H }, <PNg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1H (scalar plus scalar, single register)` | Contiguous store non-temporal halfwords from vector (scalar index) | SVE 向量连续非时态存储半字（标量索引） | `STNT1H { <Zt>.H }, <Pg>, [<Xn\|SP>, <Xm>, LSL #1]` | FEAT_SME, FEAT_SVE |
| `STNT1H (vector plus scalar)` | Scatter store non-temporal halfwords | SVE 向量散射非时态存储半字 | `STNT1H { <Zt>.S }, <Pg>, [<Zn>.S{, <Xm>}]`<br>`STNT1H { <Zt>.D }, <Pg>, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `STNT1W (scalar plus immediate, consecutive registers)` | Contiguous store non-temporal of words from multiple consecutive vectors (immediate index) | SVE 多连续向量连续非时态存储字（立即数索引） | `STNT1W { <Zt1>.S-<Zt2>.S }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]`<br>`STNT1W { <Zt1>.S-<Zt4>.S }, <PNg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1W (scalar plus immediate, single register)` | Contiguous store non-temporal words from vector (immediate index) | SVE 向量连续非时态存储字（立即数索引） | `STNT1W { <Zt>.S }, <Pg>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `STNT1W (scalar plus scalar, consecutive registers)` | Contiguous store non-temporal of words from multiple consecutive vectors (scalar index) | SVE 多连续向量连续非时态存储字（标量索引） | `STNT1W { <Zt1>.S-<Zt2>.S }, <PNg>, [<Xn\|SP>, <Xm>, LSL #2]`<br>`STNT1W { <Zt1>.S-<Zt4>.S }, <PNg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME2, FEAT_SVE2p1 |
| `STNT1W (scalar plus scalar, single register)` | Contiguous store non-temporal words from vector (scalar index) | SVE 向量连续非时态存储字（标量索引） | `STNT1W { <Zt>.S }, <Pg>, [<Xn\|SP>, <Xm>, LSL #2]` | FEAT_SME, FEAT_SVE |
| `STNT1W (vector plus scalar)` | Scatter store non-temporal words | SVE 向量散射非时态存储字 | `STNT1W { <Zt>.S }, <Pg>, [<Zn>.S{, <Xm>}]`<br>`STNT1W { <Zt>.D }, <Pg>, [<Zn>.D{, <Xm>}]` | FEAT_SVE2 |
| `STR (predicate)` | Store predicate register | SVE 存储谓词寄存器 | `STR <Pt>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `STR (vector)` | Store vector register | SVE 存储向量寄存器 | `STR <Zt>, [<Xn\|SP>{, #<imm>, MUL VL}]` | FEAT_SME, FEAT_SVE |
| `SUB (immediate)` | Subtract immediate (unpredicated) | SVE 向量减立即数（无谓词） | `SUB <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `SUB (vectors, predicated)` | Subtract (predicated) | SVE 向量减法（有谓词） | `SUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SUB (vectors, unpredicated)` | Subtract (unpredicated) | SVE 向量减法（无谓词） | `SUB <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SUBHNB` | Subtract narrow high part (bottom) | SVE 减法窄化取高位结果（写下半部分） | `SUBHNB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SUBHNT` | Subtract narrow high part (top) | SVE 减法窄化取高位结果（写上半部分） | `SUBHNT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `SUBPT (predicated)` | Subtract checked pointer vectors (predicated) | SVE 校验指针向量相减（有谓词） | `SUBPT <Zdn>.D, <Pg>/M, <Zdn>.D, <Zm>.D` | FEAT_CPA, FEAT_SVE |
| `SUBPT (unpredicated)` | Subtract checked pointer vectors (unpredicated) | SVE 校验指针向量相减（无谓词） | `SUBPT <Zd>.D, <Zn>.D, <Zm>.D` | FEAT_CPA, FEAT_SVE |
| `SUBR (immediate)` | Reversed subtract from immediate (unpredicated) | SVE 反向减立即数（无谓词） | `SUBR <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `SUBR (vectors)` | Reversed subtract (predicated) | SVE 反向向量减法（有谓词） | `SUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `SUDOT` | Signed by unsigned 8-bit integer dot product by indexed element to 32-bit integer | SVE 有符号×无符号 8 位整数点积（索引元素）到 32 位整数 | `SUDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_I8MM, FEAT_SME, FEAT_SVE |
| `SUNPKHI, SUNPKLO` | Signed unpack and extend half of vector | SVE 有符号解包并符号扩展向量高/低半部分 | `SUNPKHI <Zd>.<T>, <Zn>.<Tb>`<br>`SUNPKLO <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE |
| `SUQADD` | Signed saturating unsigned add | SVE 有符号饱和加无符号整数 | `SUQADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `SXTB, SXTH, SXTW` | Signed byte / halfword / word extend (predicated) | SVE 有符号字节/半字/字符号扩展（有谓词） | `SXTB <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`SXTB <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`SXTH <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`SXTH <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`SXTW <Zd>.D, <Pg>/M, <Zn>.D`<br>`SXTW <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `TBL` | Programmable table lookup in one or two vector table (zeroing) | SVE 可编程表查找（一或两张向量表，补零） | `TBL <Zd>.<T>, { <Zn>.<T> }, <Zm>.<T>`<br>`TBL <Zd>.<T>, { <Zn1>.<T>, <Zn2>.<T> }, <Zm>.<T>` | FEAT_SME, FEAT_SVE, FEAT_SVE2 |
| `TBLQ` | Programmable table lookup within each quadword vector segment (zeroing) | SVE 每个四字段内可编程表查找（补零） | `TBLQ <Zd>.<T>, { <Zn>.<T> }, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `TBX` | Programmable table lookup in single vector table (merging) | SVE 可编程表查找（单张向量表，保留原值） | `TBX <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `TBXQ` | Programmable table lookup within each quadword vector segment (merging) | SVE 每个四字段内可编程表查找（保留原值） | `TBXQ <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `TRN1, TRN2 (predicates)` | Interleave even or odd elements from two predicates | SVE 交织两谓词的偶数或奇数元素 | `TRN1 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>`<br>`TRN2 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `TRN1, TRN2 (vectors)` | Interleave even or odd elements from two vectors | SVE 交织两向量的偶数或奇数元素 | `TRN1 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`TRN1 <Zd>.Q, <Zn>.Q, <Zm>.Q`<br>`TRN2 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`TRN2 <Zd>.Q, <Zn>.Q, <Zm>.Q` | FEAT_F64MM, FEAT_SME, FEAT_SVE |
| `UABA` | Unsigned absolute difference and accumulate | SVE 无符号绝对差并累加 | `UABA <Zda>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UABALB` | Unsigned absolute difference and accumulate long (bottom) | SVE 无符号绝对差并累加长（取下半元素） | `UABALB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UABALT` | Unsigned absolute difference and accumulate long (top) | SVE 无符号绝对差并累加长（取上半元素） | `UABALT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UABD` | Unsigned absolute difference (predicated) | SVE 无符号绝对差（有谓词） | `UABD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UABDLB` | Unsigned absolute difference long (bottom) | SVE 无符号绝对差长（取下半元素） | `UABDLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UABDLT` | Unsigned absolute difference long (top) | SVE 无符号绝对差长（取上半元素） | `UABDLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UADALP` | Unsigned add and accumulate long pairwise | SVE 无符号相邻对加长并累加 | `UADALP <Zda>.<T>, <Pg>/M, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UADDLB` | Unsigned add long (bottom) | SVE 无符号加长（取下半元素） | `UADDLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UADDLT` | Unsigned add long (top) | SVE 无符号加长（取上半元素） | `UADDLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UADDV` | Unsigned add reduction to scalar | SVE 无符号加法归约到标量 | `UADDV <Dd>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `UADDWB` | Unsigned add wide (bottom) | SVE 无符号宽加（取下半元素） | `UADDWB <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UADDWT` | Unsigned add wide (top) | SVE 无符号宽加（取上半元素） | `UADDWT <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UCLAMP` | Unsigned clamp to minimum/maximum | SVE 无符号最小/最大值钳位 | `UCLAMP <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2p1 |
| `UCVTF (predicated)` | Unsigned integer convert to floating-point (predicated) | SVE 无符号整数转浮点数（有谓词） | `UCVTF <Zd>.H, <Pg>/M, <Zn>.H`<br>`UCVTF <Zd>.H, <Pg>/Z, <Zn>.H`<br>`UCVTF <Zd>.H, <Pg>/M, <Zn>.S`<br>`UCVTF <Zd>.H, <Pg>/Z, <Zn>.S`<br>`UCVTF <Zd>.S, <Pg>/M, <Zn>.S`<br>`UCVTF <Zd>.S, <Pg>/Z, <Zn>.S`<br>`UCVTF <Zd>.D, <Pg>/M, <Zn>.S`<br>`UCVTF <Zd>.D, <Pg>/Z, <Zn>.S`<br>`UCVTF <Zd>.H, <Pg>/M, <Zn>.D`<br>`UCVTF <Zd>.H, <Pg>/Z, <Zn>.D`<br>`UCVTF <Zd>.S, <Pg>/M, <Zn>.D`<br>`UCVTF <Zd>.S, <Pg>/Z, <Zn>.D`<br>`UCVTF <Zd>.D, <Pg>/M, <Zn>.D`<br>`UCVTF <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `UDIV` | Unsigned divide (predicated) | SVE 无符号除法（有谓词） | `UDIV <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UDIVR` | Unsigned reversed divide (predicated) | SVE 无符号反向除法（有谓词） | `UDIVR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UDOT (2-way, indexed)` | Unsigned integer dot product by indexed element (two-way) | SVE 无符号整数点积（双路，索引元素）到 32 位 | `UDOT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME2, FEAT_SVE2p1 |
| `UDOT (2-way, vectors)` | Unsigned integer dot product (two-way) | SVE 无符号整数点积（双路，向量） | `UDOT <Zda>.S, <Zn>.H, <Zm>.H` | FEAT_SME2, FEAT_SVE2p1 |
| `UDOT (4-way, indexed)` | Unsigned integer dot product by indexed element (four-way) | SVE 无符号整数点积（四路，索引元素） | `UDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]`<br>`UDOT <Zda>.D, <Zn>.H, <Zm>.H[<imm>]` | FEAT_SME, FEAT_SVE |
| `UDOT (4-way, vectors)` | Unsigned integer dot product (four-way) | SVE 无符号整数点积（四路，向量） | `UDOT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE |
| `UHADD` | Unsigned halving add | SVE 无符号折半加法 | `UHADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UHSUB` | Unsigned halving subtract | SVE 无符号折半减法 | `UHSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UHSUBR` | Unsigned halving subtract reversed | SVE 无符号折半反向减法 | `UHSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UMAX (immediate)` | Unsigned maximum with immediate (unpredicated) | SVE 无符号与立即数取最大值（无谓词） | `UMAX <Zdn>.<T>, <Zdn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `UMAX (vectors)` | Unsigned maximum (predicated) | SVE 无符号向量取最大值（有谓词） | `UMAX <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UMAXP` | Unsigned maximum pairwise | SVE 无符号相邻对取最大值 | `UMAXP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UMAXQV` | Unsigned maximum reduction of quadword vector segments | SVE 无符号最大值归约（四字段） | `UMAXQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `UMAXV` | Unsigned maximum reduction to scalar | SVE 无符号最大值归约到标量 | `UMAXV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `UMIN (immediate)` | Unsigned minimum with immediate (unpredicated) | SVE 无符号与立即数取最小值（无谓词） | `UMIN <Zdn>.<T>, <Zdn>.<T>, #<imm>` | FEAT_SME, FEAT_SVE |
| `UMIN (vectors)` | Unsigned minimum (predicated) | SVE 无符号向量取最小值（有谓词） | `UMIN <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UMINP` | Unsigned minimum pairwise | SVE 无符号相邻对取最小值 | `UMINP <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UMINQV` | Unsigned minimum reduction of quadword vector segments | SVE 无符号最小值归约（四字段） | `UMINQV <Vd>.<T>, <Pg>, <Zn>.<Tb>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `UMINV` | Unsigned minimum reduction to scalar | SVE 无符号最小值归约到标量 | `UMINV <V><d>, <Pg>, <Zn>.<T>` | FEAT_SME, FEAT_SVE |
| `UMLALB (indexed)` | Unsigned multiply-add long by indexed element (bottom) | SVE 无符号乘加长（索引元素，取下半元素） | `UMLALB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMLALB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMLALB (vectors)` | Unsigned multiply-add long (bottom) | 无符号长乘加（取低半部分元素） | `UMLALB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UMLALT (indexed)` | Unsigned multiply-add long by indexed element (top) | 无符号长乘加索引元素（取高半部分元素） | `UMLALT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMLALT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMLALT (vectors)` | Unsigned multiply-add long (top) | 无符号长乘加（取高半部分元素） | `UMLALT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UMLSLB (indexed)` | Unsigned multiply-subtract long by indexed element (bottom) | 无符号长乘减索引元素（取低半部分元素） | `UMLSLB <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMLSLB <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMLSLB (vectors)` | Unsigned multiply-subtract long (bottom) | 无符号长乘减（取低半部分元素） | `UMLSLB <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UMLSLT (indexed)` | Unsigned multiply-subtract long by indexed element (top) | 无符号长乘减索引元素（取高半部分元素） | `UMLSLT <Zda>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMLSLT <Zda>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMLSLT (vectors)` | Unsigned multiply-subtract long (top) | 无符号长乘减（取高半部分元素） | `UMLSLT <Zda>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UMMLA` | Unsigned 8-bit integer matrix multiply-accumulate to 32-bit integer | 无符号8位整数矩阵乘累加至32位整数 | `UMMLA <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_I8MM, FEAT_SVE |
| `UMULH (predicated)` | Unsigned multiply returning high half (predicated) | 无符号乘法取高半结果（有谓词） | `UMULH <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UMULH (unpredicated)` | Unsigned multiply returning high half (unpredicated) | 无符号乘法取高半结果（无谓词） | `UMULH <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UMULLB (indexed)` | Unsigned multiply long by indexed element (bottom) | 无符号长乘索引元素（取低半部分元素） | `UMULLB <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMULLB <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMULLB (vectors)` | Unsigned multiply long (bottom) | 无符号长乘（取低半部分元素） | `UMULLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UMULLT (indexed)` | Unsigned multiply long by indexed element (top) | 无符号长乘索引元素（取高半部分元素） | `UMULLT <Zd>.S, <Zn>.H, <Zm>.H[<imm>]`<br>`UMULLT <Zd>.D, <Zn>.S, <Zm>.S[<imm>]` | FEAT_SME, FEAT_SVE2 |
| `UMULLT (vectors)` | Unsigned multiply long (top) | 无符号长乘（取高半部分元素） | `UMULLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UQADD (immediate)` | Unsigned saturating add immediate (unpredicated) | 无符号饱和加立即数（无谓词） | `UQADD <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `UQADD (vectors, predicated)` | Unsigned saturating add (predicated) | 无符号饱和加法（有谓词） | `UQADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQADD (vectors, unpredicated)` | Unsigned saturating add (unpredicated) | 无符号饱和加法（无谓词） | `UQADD <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQCVTN` | Unsigned 32-bit integer saturating extract narrow to interleaved 16-bit integer | 无符号32位整数饱和窄化提取至交织16位整数 | `UQCVTN <Zd>.H, { <Zn1>.S-<Zn2>.S }` | FEAT_SME2, FEAT_SVE2p1 |
| `UQDECB` | Unsigned saturating decrement scalar by multiple of 8-bit predicate constraint element count | 标量无符号饱和递减，减量为8位谓词约束元素个数的倍数 | `UQDECB <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQDECB <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECD (scalar)` | Unsigned saturating decrement scalar by multiple of 64-bit predicate constraint element count | 标量无符号饱和递减，减量为64位谓词约束元素个数的倍数 | `UQDECD <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQDECD <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECD (vector)` | Unsigned saturating decrement vector by multiple of 64-bit predicate constraint element count | 向量无符号饱和递减，减量为64位谓词约束元素个数的倍数 | `UQDECD <Zdn>.D{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECH (scalar)` | Unsigned saturating decrement scalar by multiple of 16-bit predicate constraint element count | 标量无符号饱和递减，减量为16位谓词约束元素个数的倍数 | `UQDECH <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQDECH <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECH (vector)` | Unsigned saturating decrement vector by multiple of 16-bit predicate constraint element count | 向量无符号饱和递减，减量为16位谓词约束元素个数的倍数 | `UQDECH <Zdn>.H{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECP (scalar)` | Unsigned saturating decrement scalar by count of true predicate elements | 标量无符号饱和递减，减量为谓词真元素个数 | `UQDECP <Wdn>, <Pm>.<T>`<br>`UQDECP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQDECP (vector)` | Unsigned saturating decrement vector by count of true predicate elements | 向量无符号饱和递减，减量为谓词真元素个数 | `UQDECP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQDECW (scalar)` | Unsigned saturating decrement scalar by multiple of 32-bit predicate constraint element count | 标量无符号饱和递减，减量为32位谓词约束元素个数的倍数 | `UQDECW <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQDECW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQDECW (vector)` | Unsigned saturating decrement vector by multiple of 32-bit predicate constraint element count | 向量无符号饱和递减，减量为32位谓词约束元素个数的倍数 | `UQDECW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCB` | Unsigned saturating increment scalar by multiple of 8-bit predicate constraint element count | 标量无符号饱和递增，增量为8位谓词约束元素个数的倍数 | `UQINCB <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQINCB <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCD (scalar)` | Unsigned saturating increment scalar by multiple of 64-bit predicate constraint element count | 标量无符号饱和递增，增量为64位谓词约束元素个数的倍数 | `UQINCD <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQINCD <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCD (vector)` | Unsigned saturating increment vector by multiple of 64-bit predicate constraint element count | 向量无符号饱和递增，增量为64位谓词约束元素个数的倍数 | `UQINCD <Zdn>.D{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCH (scalar)` | Unsigned saturating increment scalar by multiple of 16-bit predicate constraint element count | 标量无符号饱和递增，增量为16位谓词约束元素个数的倍数 | `UQINCH <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQINCH <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCH (vector)` | Unsigned saturating increment vector by multiple of 16-bit predicate constraint element count | 向量无符号饱和递增，增量为16位谓词约束元素个数的倍数 | `UQINCH <Zdn>.H{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCP (scalar)` | Unsigned saturating increment scalar by count of true predicate elements | 标量无符号饱和递增，增量为谓词真元素个数 | `UQINCP <Wdn>, <Pm>.<T>`<br>`UQINCP <Xdn>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQINCP (vector)` | Unsigned saturating increment vector by count of true predicate elements | 向量无符号饱和递增，增量为谓词真元素个数 | `UQINCP <Zdn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQINCW (scalar)` | Unsigned saturating increment scalar by multiple of 32-bit predicate constraint element count | 标量无符号饱和递增，增量为32位谓词约束元素个数的倍数 | `UQINCW <Wdn>{, <pattern>{, MUL #<imm>}}`<br>`UQINCW <Xdn>{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQINCW (vector)` | Unsigned saturating increment vector by multiple of 32-bit predicate constraint element count | 向量无符号饱和递增，增量为32位谓词约束元素个数的倍数 | `UQINCW <Zdn>.S{, <pattern>{, MUL #<imm>}}` | FEAT_SME, FEAT_SVE |
| `UQRSHL` | Unsigned saturating rounding shift left (predicated) | 无符号饱和舍入左移（有谓词） | `UQRSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQRSHLR` | Unsigned saturating rounding shift left reversed (predicated) | 无符号饱和舍入左移（反向，有谓词） | `UQRSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQRSHRN` | Unsigned saturating rounding shift right narrow by immediate to interleaved integer | 无符号饱和舍入右移窄化立即数至交织整数 | `UQRSHRN <Zd>.H, { <Zn1>.S-<Zn2>.S }, #<const>` | FEAT_SME2, FEAT_SVE2p1 |
| `UQRSHRNB` | Unsigned saturating rounding shift right narrow by immediate (bottom) | 无符号饱和舍入右移窄化立即数（取低半部分） | `UQRSHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `UQRSHRNT` | Unsigned saturating rounding shift right narrow by immediate (top) | 无符号饱和舍入右移窄化立即数（取高半部分） | `UQRSHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `UQSHL (immediate)` | Unsigned saturating shift left by immediate | 无符号饱和左移立即数 | `UQSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `UQSHL (vectors)` | Unsigned saturating shift left (predicated) | 无符号饱和左移（有谓词） | `UQSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQSHLR` | Unsigned saturating shift left reversed (predicated) | 无符号饱和左移（反向，有谓词） | `UQSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQSHRNB` | Unsigned saturating shift right narrow by immediate (bottom) | 无符号饱和右移窄化立即数（取低半部分） | `UQSHRNB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `UQSHRNT` | Unsigned saturating shift right narrow by immediate (top) | 无符号饱和右移窄化立即数（取高半部分） | `UQSHRNT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `UQSUB (immediate)` | Unsigned saturating subtract immediate (unpredicated) | 无符号饱和减立即数（无谓词） | `UQSUB <Zdn>.<T>, <Zdn>.<T>, #<imm>{, <shift>}` | FEAT_SME, FEAT_SVE |
| `UQSUB (vectors, predicated)` | Unsigned saturating subtract (predicated) | 无符号饱和减法（有谓词） | `UQSUB <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQSUB (vectors, unpredicated)` | Unsigned saturating subtract (unpredicated) | 无符号饱和减法（无谓词） | `UQSUB <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE |
| `UQSUBR` | Unsigned saturating subtract reversed (predicated) | 无符号饱和减法（反向，有谓词） | `UQSUBR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `UQXTNB` | Unsigned saturating extract narrow (bottom) | 无符号饱和提取窄化（取低半部分） | `UQXTNB <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UQXTNT` | Unsigned saturating extract narrow (top) | 无符号饱和提取窄化（取高半部分） | `UQXTNT <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `URECPE` | Unsigned reciprocal estimate (predicated) | 无符号倒数估算（有谓词） | `URECPE <Zd>.S, <Pg>/M, <Zn>.S`<br>`URECPE <Zd>.S, <Pg>/Z, <Zn>.S` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `URHADD` | Unsigned rounding halving add | 无符号舍入折半加法 | `URHADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `URSHL` | Unsigned rounding shift left (predicated) | 无符号舍入左移（有谓词） | `URSHL <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `URSHLR` | Unsigned rounding shift left reversed (predicated) | 无符号舍入左移（反向，有谓词） | `URSHLR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `URSHR` | Unsigned rounding shift right by immediate | 无符号舍入右移立即数 | `URSHR <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `URSQRTE` | Unsigned reciprocal square root estimate (predicated) | 无符号倒数平方根估算（有谓词） | `URSQRTE <Zd>.S, <Pg>/M, <Zn>.S`<br>`URSQRTE <Zd>.S, <Pg>/Z, <Zn>.S` | FEAT_SME, FEAT_SME2p2, FEAT_SVE2, FEAT_SVE2p2 |
| `URSRA` | Unsigned rounding shift right and accumulate (immediate) | 无符号舍入右移并累加立即数 | `URSRA <Zda>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `USDOT (indexed)` | Unsigned by signed 8-bit integer dot product by indexed element to 32-bit integer | 无符号×有符号8位整数点积索引元素至32位整数 | `USDOT <Zda>.S, <Zn>.B, <Zm>.B[<imm>]` | FEAT_I8MM, FEAT_SME, FEAT_SVE |
| `USDOT (vectors)` | Unsigned by signed 8-bit integer dot product to 32-bit integer | 无符号×有符号8位整数向量点积至32位整数 | `USDOT <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_I8MM, FEAT_SME, FEAT_SVE |
| `USHLLB` | Unsigned shift left long by immediate (bottom) | 无符号长左移立即数（取低半部分元素） | `USHLLB <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `USHLLT` | Unsigned shift left long by immediate (top) | 无符号长左移立即数（取高半部分元素） | `USHLLT <Zd>.<T>, <Zn>.<Tb>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `USMMLA` | Unsigned by signed 8-bit integer matrix multiply-accumulate to 32-bit integer | 无符号×有符号8位整数矩阵乘累加至32位整数 | `USMMLA <Zda>.S, <Zn>.B, <Zm>.B` | FEAT_I8MM, FEAT_SVE |
| `USQADD` | Unsigned saturating signed add | 无符号饱和有符号加法 | `USQADD <Zdn>.<T>, <Pg>/M, <Zdn>.<T>, <Zm>.<T>` | FEAT_SME, FEAT_SVE2 |
| `USRA` | Unsigned shift right and accumulate (immediate) | 无符号右移并累加立即数 | `USRA <Zda>.<T>, <Zn>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `USUBLB` | Unsigned subtract long (bottom) | 无符号长减法（取低半部分元素） | `USUBLB <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `USUBLT` | Unsigned subtract long (top) | 无符号长减法（取高半部分元素） | `USUBLT <Zd>.<T>, <Zn>.<Tb>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `USUBWB` | Unsigned subtract wide (bottom) | 无符号宽减法（取低半部分元素） | `USUBWB <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `USUBWT` | Unsigned subtract wide (top) | 无符号宽减法（取高半部分元素） | `USUBWT <Zd>.<T>, <Zn>.<T>, <Zm>.<Tb>` | FEAT_SME, FEAT_SVE2 |
| `UUNPKHI, UUNPKLO` | Unsigned unpack and extend half of vector | 无符号解包并扩展向量高半部分元素 | `UUNPKHI <Zd>.<T>, <Zn>.<Tb>`<br>`UUNPKLO <Zd>.<T>, <Zn>.<Tb>` | FEAT_SME, FEAT_SVE |
| `UXTB, UXTH, UXTW` | Unsigned byte / halfword / word extend (predicated) | 无符号字节/半字/字扩展（有谓词） | `UXTB <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`UXTB <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`UXTH <Zd>.<T>, <Pg>/M, <Zn>.<T>`<br>`UXTH <Zd>.<T>, <Pg>/Z, <Zn>.<T>`<br>`UXTW <Zd>.D, <Pg>/M, <Zn>.D`<br>`UXTW <Zd>.D, <Pg>/Z, <Zn>.D` | FEAT_SME, FEAT_SME2p2, FEAT_SVE, FEAT_SVE2p2 |
| `UZP1, UZP2 (predicates)` | Concatenate even or odd elements from two predicates | 从两个谓词中拼接偶数或奇数位元素 | `UZP1 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>`<br>`UZP2 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `UZP1, UZP2 (vectors)` | Concatenate even or odd elements from two vectors | 从两个向量中拼接偶数或奇数位元素 | `UZP1 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`UZP1 <Zd>.Q, <Zn>.Q, <Zm>.Q`<br>`UZP2 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`UZP2 <Zd>.Q, <Zn>.Q, <Zm>.Q` | FEAT_F64MM, FEAT_SME, FEAT_SVE |
| `UZPQ1` | Concatenate even elements within each pair of quadword vector segments | 拼接每对128位向量段中的偶数元素 | `UZPQ1 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `UZPQ2` | Concatenate odd elements within each pair of quadword vector segments | 拼接每对128位向量段中的奇数元素 | `UZPQ2 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `WHILEGE (predicate as counter)` | While decrementing signed scalar greater than or equal to scalar (predicate-as-counter) | 递减有符号标量大于等于标量时循环（谓词计数器形式） | `WHILEGE <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEGE (predicate pair)` | While decrementing signed scalar greater than or equal to scalar (pair of predicates) | 递减有符号标量大于等于标量时循环（谓词对形式） | `WHILEGE { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEGE (predicate)` | While decrementing signed scalar greater than or equal to scalar | 递减有符号标量大于等于标量时循环 | `WHILEGE <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE2 |
| `WHILEGT (predicate as counter)` | While decrementing signed scalar greater than scalar (predicate-as-counter) | 递减有符号标量大于标量时循环（谓词计数器形式） | `WHILEGT <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEGT (predicate pair)` | While decrementing signed scalar greater than scalar (pair of predicates) | 递减有符号标量大于标量时循环（谓词对形式） | `WHILEGT { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEGT (predicate)` | While decrementing signed scalar greater than scalar | 递减有符号标量大于标量时循环 | `WHILEGT <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE2 |
| `WHILEHI (predicate as counter)` | While decrementing unsigned scalar higher than scalar (predicate-as-counter) | 递减无符号标量高于标量时循环（谓词计数器形式） | `WHILEHI <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEHI (predicate pair)` | While decrementing unsigned scalar higher than scalar (pair of predicates) | 递减无符号标量高于标量时循环（谓词对形式） | `WHILEHI { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEHI (predicate)` | While decrementing unsigned scalar higher than scalar | 递减无符号标量高于标量时循环 | `WHILEHI <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE2 |
| `WHILEHS (predicate as counter)` | While decrementing unsigned scalar higher than or same as scalar (predicate-as-counter) | 递减无符号标量高于或等于标量时循环（谓词计数器形式） | `WHILEHS <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEHS (predicate pair)` | While decrementing unsigned scalar higher than or same as scalar (pair of predicates) | 递减无符号标量高于或等于标量时循环（谓词对形式） | `WHILEHS { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILEHS (predicate)` | While decrementing unsigned scalar higher than or same as scalar | 递减无符号标量高于或等于标量时循环 | `WHILEHS <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE2 |
| `WHILELE (predicate as counter)` | While incrementing signed scalar less than or equal to scalar (predicate-as-counter) | 递增有符号标量小于等于标量时循环（谓词计数器形式） | `WHILELE <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELE (predicate pair)` | While incrementing signed scalar less than or equal to scalar (pair of predicates) | 递增有符号标量小于等于标量时循环（谓词对形式） | `WHILELE { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELE (predicate)` | While incrementing signed scalar less than or equal to scalar | 递增有符号标量小于等于标量时循环 | `WHILELE <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `WHILELO (predicate as counter)` | While incrementing unsigned scalar lower than scalar (predicate-as-counter) | 递增无符号标量低于标量时循环（谓词计数器形式） | `WHILELO <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELO (predicate pair)` | While incrementing unsigned scalar lower than scalar (pair of predicates) | 递增无符号标量低于标量时循环（谓词对形式） | `WHILELO { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELO (predicate)` | While incrementing unsigned scalar lower than scalar | 递增无符号标量低于标量时循环 | `WHILELO <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `WHILELS (predicate as counter)` | While incrementing unsigned scalar lower than or same as scalar (predicate-as-counter) | 递增无符号标量低于或等于标量时循环（谓词计数器形式） | `WHILELS <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELS (predicate pair)` | While incrementing unsigned scalar lower than or same as scalar (pair of predicates) | 递增无符号标量低于或等于标量时循环（谓词对形式） | `WHILELS { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELS (predicate)` | While incrementing unsigned scalar lower than or same as scalar | 递增无符号标量低于或等于标量时循环 | `WHILELS <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `WHILELT (predicate as counter)` | While incrementing signed scalar less than scalar (predicate-as-counter) | 递增有符号标量小于标量时循环（谓词计数器形式） | `WHILELT <PNd>.<T>, <Xn>, <Xm>, <vl>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELT (predicate pair)` | While incrementing signed scalar less than scalar (pair of predicates) | 递增有符号标量小于标量时循环（谓词对形式） | `WHILELT { <Pd1>.<T>, <Pd2>.<T> }, <Xn>, <Xm>` | FEAT_SME2, FEAT_SVE2p1 |
| `WHILELT (predicate)` | While incrementing signed scalar less than scalar | 递增有符号标量小于标量时循环 | `WHILELT <Pd>.<T>, <R><n>, <R><m>` | FEAT_SME, FEAT_SVE |
| `WHILERW` | While free of read-after-write conflicts | 无读后写冲突时循环 | `WHILERW <Pd>.<T>, <Xn>, <Xm>` | FEAT_SME, FEAT_SVE2 |
| `WHILEWR` | While free of write-after-read/write conflicts | 无写后读/写冲突时循环 | `WHILEWR <Pd>.<T>, <Xn>, <Xm>` | FEAT_SME, FEAT_SVE2 |
| `WRFFR` | Write the first-fault register | 写首错误寄存器（FFR） | `WRFFR <Pn>.B` | FEAT_SVE |
| `XAR` | Bitwise exclusive-OR and rotate right by immediate | 按立即数对向量执行异或并循环右移 | `XAR <Zdn>.<T>, <Zdn>.<T>, <Zm>.<T>, #<const>` | FEAT_SME, FEAT_SVE2 |
| `ZIP1, ZIP2 (predicates)` | Interleave elements from two half predicates | 从两个半谓词交织合并元素 | `ZIP2 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>`<br>`ZIP1 <Pd>.<T>, <Pn>.<T>, <Pm>.<T>` | FEAT_SME, FEAT_SVE |
| `ZIP1, ZIP2 (vectors)` | Interleave elements from two half vectors | 从两个半向量交织合并元素 | `ZIP2 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`ZIP2 <Zd>.Q, <Zn>.Q, <Zm>.Q`<br>`ZIP1 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>`<br>`ZIP1 <Zd>.Q, <Zn>.Q, <Zm>.Q` | FEAT_F64MM, FEAT_SME, FEAT_SVE |
| `ZIPQ1` | Interleave elements from low halves of each pair of quadword vector segments | 从每对128位向量段低半部分交织合并元素 | `ZIPQ1 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |
| `ZIPQ2` | Interleave elements from high halves of each pair of quadword vector segments | 从每对128位向量段高半部分交织合并元素 | `ZIPQ2 <Zd>.<T>, <Zn>.<T>, <Zm>.<T>` | FEAT_SME2p1, FEAT_SVE2p1 |

