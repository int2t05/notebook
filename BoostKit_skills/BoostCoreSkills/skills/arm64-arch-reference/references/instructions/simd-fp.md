# A64 指令 — SIMD 与浮点指令（SIMD & Floating-point）

> 数据源：ARM 官方 A64 ISA 机器可读规范（2026-03_rel），共 463 条。汇编模板列即官方 `asmtemplate`（Encoding）。
> 源数据下载：https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz

| 指令名 | 英文简述 | 中文简介 | 汇编模板（Encoding） | 关联特性 |
| --- | --- | --- | --- | --- |
| `ABS` | Absolute value (vector) | 向量绝对值 | `ABS D<d>, D<n>`<br>`ABS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `ADD (vector)` | Add (vector) | 向量加法 | `ADD D<d>, D<n>, D<m>`<br>`ADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `ADDHN, ADDHN2` | Add returning high narrow | 加法并取高位窄结果（ADDHN/ADDHN2） | `ADDHN{2} <Vd>.<Tb>, <Vn>.<Ta>, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `ADDP (scalar)` | Add pair of elements (scalar) | 成对元素相加（标量） | `ADDP D<d>, <Vn>.2D` | FEAT_AdvSIMD |
| `ADDP (vector)` | Add pairwise (vector) | 成对相加（向量） | `ADDP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `ADDV` | Add across vector | 向量跨通道累加 | `ADDV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `AESD` | AES single round decryption | AES 单轮解密 | `AESD <Vd>.16B, <Vn>.16B` | FEAT_AES |
| `AESE` | AES single round encryption | AES 单轮加密 | `AESE <Vd>.16B, <Vn>.16B` | FEAT_AES |
| `AESIMC` | AES inverse mix columns | AES 逆混列变换 | `AESIMC <Vd>.16B, <Vn>.16B` | FEAT_AES |
| `AESMC` | AES mix columns | AES 混列变换 | `AESMC <Vd>.16B, <Vn>.16B` | FEAT_AES |
| `AND (vector)` | Bitwise AND (vector) | 向量按位与 | `AND <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `BCAX` | Bit clear and exclusive-OR | 位清除后异或 | `BCAX <Vd>.16B, <Vn>.16B, <Vm>.16B, <Va>.16B` | FEAT_SHA3 |
| `BF1CVTL, BF1CVTL2, BF2CVTL, BF2CVTL2` | 8-bit floating-point convert to BFloat16 (vector) | 8位浮点转换为 BFloat16（向量） | `BF1CVTL{2} <Vd>.8H, <Vn>.<Ta>`<br>`BF2CVTL{2} <Vd>.8H, <Vn>.<Ta>` | FEAT_FP8 |
| `BFCVT` | Single-precision convert to BFloat16 (scalar) | 单精度转换为 BFloat16（标量） | `BFCVT <Hd>, <Sn>` | FEAT_BF16 |
| `BFCVTN, BFCVTN2` | Single-precision convert to BFloat16 (vector) | 单精度转换为 BFloat16（向量，BFCVTN/BFCVTN2） | `BFCVTN{2} <Vd>.<Ta>, <Vn>.4S` | FEAT_BF16 |
| `BFDOT (by element)` | BFloat16 dot product to single-precision (vector, by element) | BFloat16 点积到单精度（向量，按元素） | `BFDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.2H[<index>]` | FEAT_BF16 |
| `BFDOT (vector)` | BFloat16 dot product to single-precision (vector) | BFloat16 点积到单精度（向量） | `BFDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_BF16 |
| `BFMLALB, BFMLALT (by element)` | BFloat16 multiply-add to single-precision (by element) | BFloat16 乘加到单精度（按元素） | `BFMLAL<bt> <Vd>.4S, <Vn>.8H, <Vm>.H[<index>]` | FEAT_BF16 |
| `BFMLALB, BFMLALT (vector)` | BFloat16 multiply-add to single-precision (vector) | BFloat16 乘加到单精度（向量） | `BFMLAL<bt> <Vd>.4S, <Vn>.8H, <Vm>.8H` | FEAT_BF16 |
| `BFMMLA (widening)` | BFloat16 matrix multiply-accumulate to single-precision | BFloat16 矩阵乘累加到单精度 | `BFMMLA <Vd>.4S, <Vn>.8H, <Vm>.8H` | FEAT_BF16 |
| `BIC (vector, immediate)` | Bitwise bit clear (vector, immediate) | 向量按位清除（立即数） | `BIC <Vd>.<T>, #<imm8>{, LSL #<amount>}` | FEAT_AdvSIMD |
| `BIC (vector, register)` | Bitwise bit clear (vector, register) | 向量按位清除（寄存器） | `BIC <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `BIF` | Bitwise insert if false | 条件为假时按位插入 | `BIF <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `BIT` | Bitwise insert if true | 条件为真时按位插入 | `BIT <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `BSL` | Bitwise select | 按位选择 | `BSL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CLS (vector)` | Count leading sign bits (vector) | 统计前导符号位数（向量） | `CLS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `CLZ (vector)` | Count leading zero bits (vector) | 统计前导零位数（向量） | `CLZ <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `CMEQ (register)` | Compare bitwise equal (vector) | 按位比较相等（向量，寄存器） | `CMEQ D<d>, D<n>, D<m>`<br>`CMEQ <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CMEQ (zero)` | Compare bitwise equal to zero (vector) | 按位比较是否等于零（向量） | `CMEQ D<d>, D<n>, #0`<br>`CMEQ <Vd>.<T>, <Vn>.<T>, #0` | FEAT_AdvSIMD |
| `CMGE (register)` | Compare signed greater than or equal (vector) | 有符号比较大于等于（向量，寄存器） | `CMGE D<d>, D<n>, D<m>`<br>`CMGE <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CMGE (zero)` | Compare signed greater than or equal to zero (vector) | 有符号比较大于等于零（向量） | `CMGE D<d>, D<n>, #0`<br>`CMGE <Vd>.<T>, <Vn>.<T>, #0` | FEAT_AdvSIMD |
| `CMGT (register)` | Compare signed greater than (vector) | 有符号比较大于（向量，寄存器） | `CMGT D<d>, D<n>, D<m>`<br>`CMGT <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CMGT (zero)` | Compare signed greater than zero (vector) | 有符号比较大于零（向量） | `CMGT D<d>, D<n>, #0`<br>`CMGT <Vd>.<T>, <Vn>.<T>, #0` | FEAT_AdvSIMD |
| `CMHI (register)` | Compare unsigned higher (vector) | 无符号比较更高（向量，寄存器） | `CMHI D<d>, D<n>, D<m>`<br>`CMHI <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CMHS (register)` | Compare unsigned higher or same (vector) | 无符号比较大于等于（向量，寄存器） | `CMHS D<d>, D<n>, D<m>`<br>`CMHS <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CMLE (zero)` | Compare signed less than or equal to zero (vector) | 有符号比较小于等于零（向量） | `CMLE D<d>, D<n>, #0`<br>`CMLE <Vd>.<T>, <Vn>.<T>, #0` | FEAT_AdvSIMD |
| `CMLT (zero)` | Compare signed less than zero (vector) | 有符号比较小于零（向量） | `CMLT D<d>, D<n>, #0`<br>`CMLT <Vd>.<T>, <Vn>.<T>, #0` | FEAT_AdvSIMD |
| `CMTST` | Compare bitwise test bits nonzero (vector) | 按位测试非零比较（向量） | `CMTST D<d>, D<n>, D<m>`<br>`CMTST <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `CNT` | Population count per byte | 按字节统计置位位数 | `CNT <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `DUP (element)` | Duplicate vector element to vector or scalar | 将向量元素复制到向量或标量 | `DUP <V><d>, <Vn>.<T>[<index>]`<br>`DUP <Vd>.<T>, <Vn>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `DUP (general)` | Duplicate general-purpose register to vector | 将通用寄存器值复制到向量 | `DUP <Vd>.<T>, <R><n>` | FEAT_AdvSIMD |
| `EOR (vector)` | Bitwise exclusive-OR (vector) | 向量按位异或 | `EOR <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `EOR3` | Three-way exclusive-OR | 三路按位异或 | `EOR3 <Vd>.16B, <Vn>.16B, <Vm>.16B, <Va>.16B` | FEAT_SHA3 |
| `EXT` | Extract vector from pair of vectors | 从两个向量中提取拼接向量 | `EXT <Vd>.<T>, <Vn>.<T>, <Vm>.<T>, #<index>` | FEAT_AdvSIMD |
| `F1CVTL, F1CVTL2, F2CVTL, F2CVTL2` | 8-bit floating-point convert to half-precision (vector) | 8位浮点转换为半精度（向量） | `F1CVTL{2} <Vd>.8H, <Vn>.<Ta>`<br>`F2CVTL{2} <Vd>.8H, <Vn>.<Ta>` | FEAT_FP8 |
| `FABD` | Floating-point absolute difference (vector) | 浮点绝对差（向量） | `FABD <Hd>, <Hn>, <Hm>`<br>`FABD <V><d>, <V><n>, <V><m>`<br>`FABD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FABS (scalar)` | Floating-point absolute value (scalar) | 浮点绝对值（标量） | `FABS <Hd>, <Hn>`<br>`FABS <Sd>, <Sn>`<br>`FABS <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FABS (vector)` | Floating-point absolute value (vector) | 浮点绝对值（向量） | `FABS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FACGE` | Floating-point absolute compare greater than or equal (vector) | 浮点绝对值比较大于等于（向量） | `FACGE <Hd>, <Hn>, <Hm>`<br>`FACGE <V><d>, <V><n>, <V><m>`<br>`FACGE <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FACGT` | Floating-point absolute compare greater than (vector) | 浮点绝对值比较大于（向量） | `FACGT <Hd>, <Hn>, <Hm>`<br>`FACGT <V><d>, <V><n>, <V><m>`<br>`FACGT <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FADD (scalar)` | Floating-point add (scalar) | 浮点加法（标量） | `FADD <Hd>, <Hn>, <Hm>`<br>`FADD <Sd>, <Sn>, <Sm>`<br>`FADD <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FADD (vector)` | Floating-point add (vector) | 浮点加法（向量） | `FADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FADDP (scalar)` | Floating-point add pair of elements (scalar) | 浮点成对元素相加（标量） | `FADDP H<d>, <Vn>.2H`<br>`FADDP <V><d>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FADDP (vector)` | Floating-point add pairwise (vector) | 浮点成对相加（向量） | `FADDP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FAMAX` | Floating-point absolute maximum | 浮点绝对最大值 | `FAMAX <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FAMINMAX |
| `FAMIN` | Floating-point absolute minimum | 浮点绝对最小值 | `FAMIN <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FAMINMAX |
| `FCADD` | Floating-point complex add | 浮点复数加法 | `FCADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>, #<rotate>` | FEAT_FCMA |
| `FCCMP` | Floating-point conditional quiet compare (scalar) | 浮点条件静默比较（标量） | `FCCMP <Hn>, <Hm>, #<nzcv>, <cond>`<br>`FCCMP <Sn>, <Sm>, #<nzcv>, <cond>`<br>`FCCMP <Dn>, <Dm>, #<nzcv>, <cond>` | FEAT_FP, FEAT_FP16 |
| `FCCMPE` | Floating-point conditional signaling compare (scalar) | 浮点条件信号比较（标量） | `FCCMPE <Hn>, <Hm>, #<nzcv>, <cond>`<br>`FCCMPE <Sn>, <Sm>, #<nzcv>, <cond>`<br>`FCCMPE <Dn>, <Dm>, #<nzcv>, <cond>` | FEAT_FP, FEAT_FP16 |
| `FCMEQ (register)` | Floating-point compare equal (vector) | 浮点比较相等（向量，寄存器） | `FCMEQ <Hd>, <Hn>, <Hm>`<br>`FCMEQ <V><d>, <V><n>, <V><m>`<br>`FCMEQ <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMEQ (zero)` | Floating-point compare equal to zero (vector) | 浮点比较等于零（向量） | `FCMEQ <Hd>, <Hn>, #0.0`<br>`FCMEQ <V><d>, <V><n>, #0.0`<br>`FCMEQ <Vd>.<T>, <Vn>.<T>, #0.0` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMGE (register)` | Floating-point compare greater than or equal (vector) | 浮点比较大于等于（向量，寄存器） | `FCMGE <Hd>, <Hn>, <Hm>`<br>`FCMGE <V><d>, <V><n>, <V><m>`<br>`FCMGE <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMGE (zero)` | Floating-point compare greater than or equal to zero (vector) | 浮点比较大于等于零（向量） | `FCMGE <Hd>, <Hn>, #0.0`<br>`FCMGE <V><d>, <V><n>, #0.0`<br>`FCMGE <Vd>.<T>, <Vn>.<T>, #0.0` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMGT (register)` | Floating-point compare greater than (vector) | 浮点比较大于（向量，寄存器） | `FCMGT <Hd>, <Hn>, <Hm>`<br>`FCMGT <V><d>, <V><n>, <V><m>`<br>`FCMGT <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMGT (zero)` | Floating-point compare greater than zero (vector) | 浮点比较大于零（向量） | `FCMGT <Hd>, <Hn>, #0.0`<br>`FCMGT <V><d>, <V><n>, #0.0`<br>`FCMGT <Vd>.<T>, <Vn>.<T>, #0.0` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMLA` | Floating-point complex multiply accumulate | 浮点复数乘累加（向量） | `FCMLA <Vd>.<T>, <Vn>.<T>, <Vm>.<T>, #<rotate>` | FEAT_FCMA |
| `FCMLA (by element)` | Floating-point complex multiply accumulate (by element) | 浮点复数乘累加（按元素） | `FCMLA <Vd>.<T>, <Vn>.<T>, <Vm>.<Ts>[<index>], #<rotate>` | FEAT_FCMA |
| `FCMLE (zero)` | Floating-point compare less than or equal to zero (vector) | 浮点比较小于等于零（向量） | `FCMLE <Hd>, <Hn>, #0.0`<br>`FCMLE <V><d>, <V><n>, #0.0`<br>`FCMLE <Vd>.<T>, <Vn>.<T>, #0.0` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMLT (zero)` | Floating-point compare less than zero (vector) | 浮点比较小于零（向量） | `FCMLT <Hd>, <Hn>, #0.0`<br>`FCMLT <V><d>, <V><n>, #0.0`<br>`FCMLT <Vd>.<T>, <Vn>.<T>, #0.0` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCMP` | Floating-point quiet compare (scalar) | 浮点静默比较（标量） | `FCMP <Hn>, <Hm>`<br>`FCMP <Hn>, #0.0`<br>`FCMP <Sn>, <Sm>`<br>`FCMP <Sn>, #0.0`<br>`FCMP <Dn>, <Dm>`<br>`FCMP <Dn>, #0.0` | FEAT_FP, FEAT_FP16 |
| `FCMPE` | Floating-point signaling compare (scalar) | 浮点信号比较（标量） | `FCMPE <Hn>, <Hm>`<br>`FCMPE <Hn>, #0.0`<br>`FCMPE <Sn>, <Sm>`<br>`FCMPE <Sn>, #0.0`<br>`FCMPE <Dn>, <Dm>`<br>`FCMPE <Dn>, #0.0` | FEAT_FP, FEAT_FP16 |
| `FCSEL` | Floating-point conditional select (scalar) | 浮点条件选择（标量） | `FCSEL <Hd>, <Hn>, <Hm>, <cond>`<br>`FCSEL <Sd>, <Sn>, <Sm>, <cond>`<br>`FCSEL <Dd>, <Dn>, <Dm>, <cond>` | FEAT_FP, FEAT_FP16 |
| `FCVT` | Floating-point convert precision (scalar) | 浮点精度转换（标量） | `FCVT <Sd>, <Hn>`<br>`FCVT <Dd>, <Hn>`<br>`FCVT <Hd>, <Sn>`<br>`FCVT <Dd>, <Sn>`<br>`FCVT <Hd>, <Dn>`<br>`FCVT <Sd>, <Dn>` | FEAT_FP |
| `FCVTAS (scalar SIMD&FP)` | Floating-point convert to signed integer, rounding to nearest with ties to away (scalar SIMD&FP) | 浮点转有符号整数，向最近舍入（标量 SIMD&FP） | `FCVTAS <Sd>, <Hn>`<br>`FCVTAS <Dd>, <Hn>`<br>`FCVTAS <Dd>, <Sn>`<br>`FCVTAS <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTAS (scalar)` | Floating-point convert to signed integer, rounding to nearest with ties to away (scalar) | 浮点转有符号整数，向最近舍入（标量） | `FCVTAS <Wd>, <Hn>`<br>`FCVTAS <Xd>, <Hn>`<br>`FCVTAS <Wd>, <Sn>`<br>`FCVTAS <Xd>, <Sn>`<br>`FCVTAS <Wd>, <Dn>`<br>`FCVTAS <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTAS (vector)` | Floating-point convert to signed integer, rounding to nearest with ties to away (vector) | 浮点转有符号整数，向最近舍入（向量） | `FCVTAS <Hd>, <Hn>`<br>`FCVTAS <V><d>, <V><n>`<br>`FCVTAS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTAU (scalar SIMD&FP)` | Floating-point convert to unsigned integer, rounding to nearest with ties to away (scalar SIMD&FP) | 浮点转无符号整数，向最近舍入（标量 SIMD&FP） | `FCVTAU <Sd>, <Hn>`<br>`FCVTAU <Dd>, <Hn>`<br>`FCVTAU <Dd>, <Sn>`<br>`FCVTAU <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTAU (scalar)` | Floating-point convert to unsigned integer, rounding to nearest with ties to away (scalar) | 浮点转无符号整数，向最近舍入（标量） | `FCVTAU <Wd>, <Hn>`<br>`FCVTAU <Xd>, <Hn>`<br>`FCVTAU <Wd>, <Sn>`<br>`FCVTAU <Xd>, <Sn>`<br>`FCVTAU <Wd>, <Dn>`<br>`FCVTAU <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTAU (vector)` | Floating-point convert to unsigned integer, rounding to nearest with ties to away (vector) | 浮点转无符号整数，向最近舍入（向量） | `FCVTAU <Hd>, <Hn>`<br>`FCVTAU <V><d>, <V><n>`<br>`FCVTAU <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTL, FCVTL2` | Floating-point convert to higher precision long (vector) | 浮点转高精度长格式（向量，FCVTL/FCVTL2） | `FCVTL{2} <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `FCVTMS (scalar SIMD&FP)` | Floating-point convert to signed integer, rounding toward minus infinity (scalar SIMD&FP) | 浮点转有符号整数，向负无穷舍入（标量 SIMD&FP） | `FCVTMS <Sd>, <Hn>`<br>`FCVTMS <Dd>, <Hn>`<br>`FCVTMS <Dd>, <Sn>`<br>`FCVTMS <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTMS (scalar)` | Floating-point convert to signed integer, rounding toward minus infinity (scalar) | 浮点转有符号整数，向负无穷舍入（标量） | `FCVTMS <Wd>, <Hn>`<br>`FCVTMS <Xd>, <Hn>`<br>`FCVTMS <Wd>, <Sn>`<br>`FCVTMS <Xd>, <Sn>`<br>`FCVTMS <Wd>, <Dn>`<br>`FCVTMS <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTMS (vector)` | Floating-point convert to signed integer, rounding toward minus infinity (vector) | 浮点转有符号整数，向负无穷舍入（向量） | `FCVTMS <Hd>, <Hn>`<br>`FCVTMS <V><d>, <V><n>`<br>`FCVTMS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTMU (scalar SIMD&FP)` | Floating-point convert to unsigned integer, rounding toward minus infinity (scalar SIMD&FP) | 浮点转无符号整数，向负无穷舍入（标量 SIMD&FP） | `FCVTMU <Sd>, <Hn>`<br>`FCVTMU <Dd>, <Hn>`<br>`FCVTMU <Dd>, <Sn>`<br>`FCVTMU <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTMU (scalar)` | Floating-point convert to unsigned integer, rounding toward minus infinity (scalar) | 浮点转无符号整数，向负无穷舍入（标量） | `FCVTMU <Wd>, <Hn>`<br>`FCVTMU <Xd>, <Hn>`<br>`FCVTMU <Wd>, <Sn>`<br>`FCVTMU <Xd>, <Sn>`<br>`FCVTMU <Wd>, <Dn>`<br>`FCVTMU <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTMU (vector)` | Floating-point convert to unsigned integer, rounding toward minus infinity (vector) | 浮点转无符号整数，向负无穷舍入（向量） | `FCVTMU <Hd>, <Hn>`<br>`FCVTMU <V><d>, <V><n>`<br>`FCVTMU <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTN (half-precision to 8-bit floating-point)` | Half-precision convert to 8-bit floating-point (vector) | 半精度转换为8位浮点（向量） | `FCVTN <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_FP8 |
| `FCVTN, FCVTN2 (double to single-precision, single to half-precision)` | Floating-point convert to lower precision narrow (vector) | 浮点转低精度窄格式（向量，FCVTN/FCVTN2） | `FCVTN{2} <Vd>.<Tb>, <Vn>.<Ta>` | FEAT_AdvSIMD |
| `FCVTN, FCVTN2 (single-precision to 8-bit floating-point)` | Single-precision convert to 8-bit floating-point (vector) | 单精度转换为8位浮点（向量，FCVTN/FCVTN2） | `FCVTN{2} <Vd>.<Ta>, <Vn>.4S, <Vm>.4S` | FEAT_FP8 |
| `FCVTNS (scalar SIMD&FP)` | Floating-point convert to signed integer, rounding to nearest with ties to even (scalar SIMD&FP) | 浮点转有符号整数，就近舍入偶数（标量 SIMD&FP） | `FCVTNS <Sd>, <Hn>`<br>`FCVTNS <Dd>, <Hn>`<br>`FCVTNS <Dd>, <Sn>`<br>`FCVTNS <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTNS (scalar)` | Floating-point convert to signed integer, rounding to nearest with ties to even (scalar) | 浮点转有符号整数，就近舍入偶数（标量） | `FCVTNS <Wd>, <Hn>`<br>`FCVTNS <Xd>, <Hn>`<br>`FCVTNS <Wd>, <Sn>`<br>`FCVTNS <Xd>, <Sn>`<br>`FCVTNS <Wd>, <Dn>`<br>`FCVTNS <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTNS (vector)` | Floating-point convert to signed integer, rounding to nearest with ties to even (vector) | 浮点转有符号整数，就近舍入偶数（向量） | `FCVTNS <Hd>, <Hn>`<br>`FCVTNS <V><d>, <V><n>`<br>`FCVTNS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTNU (scalar SIMD&FP)` | Floating-point convert to unsigned integer, rounding to nearest with ties to even (scalar SIMD&FP) | 浮点转无符号整数，就近舍入偶数（标量 SIMD&FP） | `FCVTNU <Sd>, <Hn>`<br>`FCVTNU <Dd>, <Hn>`<br>`FCVTNU <Dd>, <Sn>`<br>`FCVTNU <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTNU (scalar)` | Floating-point convert to unsigned integer, rounding to nearest with ties to even (scalar) | 浮点转无符号整数，就近舍入（偶数优先）（标量） | `FCVTNU <Wd>, <Hn>`<br>`FCVTNU <Xd>, <Hn>`<br>`FCVTNU <Wd>, <Sn>`<br>`FCVTNU <Xd>, <Sn>`<br>`FCVTNU <Wd>, <Dn>`<br>`FCVTNU <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTNU (vector)` | Floating-point convert to unsigned integer, rounding to nearest with ties to even (vector) | 浮点转无符号整数，就近舍入（偶数优先）（向量） | `FCVTNU <Hd>, <Hn>`<br>`FCVTNU <V><d>, <V><n>`<br>`FCVTNU <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTPS (scalar SIMD&FP)` | Floating-point convert to signed integer, rounding toward plus infinity (scalar SIMD&FP) | 浮点转有符号整数，向正无穷舍入（标量 SIMD&FP） | `FCVTPS <Sd>, <Hn>`<br>`FCVTPS <Dd>, <Hn>`<br>`FCVTPS <Dd>, <Sn>`<br>`FCVTPS <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTPS (scalar)` | Floating-point convert to signed integer, rounding toward plus infinity (scalar) | 浮点转有符号整数，向正无穷舍入（标量） | `FCVTPS <Wd>, <Hn>`<br>`FCVTPS <Xd>, <Hn>`<br>`FCVTPS <Wd>, <Sn>`<br>`FCVTPS <Xd>, <Sn>`<br>`FCVTPS <Wd>, <Dn>`<br>`FCVTPS <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTPS (vector)` | Floating-point convert to signed integer, rounding toward plus infinity (vector) | 浮点转有符号整数，向正无穷舍入（向量） | `FCVTPS <Hd>, <Hn>`<br>`FCVTPS <V><d>, <V><n>`<br>`FCVTPS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTPU (scalar SIMD&FP)` | Floating-point convert to unsigned integer, rounding toward plus infinity (scalar SIMD&FP) | 浮点转无符号整数，向正无穷舍入（标量 SIMD&FP） | `FCVTPU <Sd>, <Hn>`<br>`FCVTPU <Dd>, <Hn>`<br>`FCVTPU <Dd>, <Sn>`<br>`FCVTPU <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTPU (scalar)` | Floating-point convert to unsigned integer, rounding toward plus infinity (scalar) | 浮点转无符号整数，向正无穷舍入（标量） | `FCVTPU <Wd>, <Hn>`<br>`FCVTPU <Xd>, <Hn>`<br>`FCVTPU <Wd>, <Sn>`<br>`FCVTPU <Xd>, <Sn>`<br>`FCVTPU <Wd>, <Dn>`<br>`FCVTPU <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTPU (vector)` | Floating-point convert to unsigned integer, rounding toward plus infinity (vector) | 浮点转无符号整数，向正无穷舍入（向量） | `FCVTPU <Hd>, <Hn>`<br>`FCVTPU <V><d>, <V><n>`<br>`FCVTPU <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTXN, FCVTXN2` | Floating-point convert to lower precision narrow, rounding to odd (vector) | 浮点降精度窄化转换，奇数舍入（向量） | `FCVTXN S<d>, D<n>`<br>`FCVTXN{2} <Vd>.<Tb>, <Vn>.2D` | FEAT_AdvSIMD |
| `FCVTZS (scalar SIMD&FP)` | Floating-point convert to signed integer, rounding toward zero (scalar SIMD&FP) | 浮点转有符号整数，向零舍入（标量 SIMD&FP） | `FCVTZS <Sd>, <Hn>`<br>`FCVTZS <Dd>, <Hn>`<br>`FCVTZS <Dd>, <Sn>`<br>`FCVTZS <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTZS (scalar, fixed-point)` | Floating-point convert to signed fixed-point, rounding toward zero (scalar) | 浮点转有符号定点数，向零舍入（标量） | `FCVTZS <Wd>, <Hn>, #<fbits>`<br>`FCVTZS <Xd>, <Hn>, #<fbits>`<br>`FCVTZS <Wd>, <Sn>, #<fbits>`<br>`FCVTZS <Xd>, <Sn>, #<fbits>`<br>`FCVTZS <Wd>, <Dn>, #<fbits>`<br>`FCVTZS <Xd>, <Dn>, #<fbits>` | FEAT_FP, FEAT_FP16 |
| `FCVTZS (scalar, integer)` | Floating-point convert to signed integer, rounding toward zero (scalar) | 浮点转有符号整数，向零舍入（标量） | `FCVTZS <Wd>, <Hn>`<br>`FCVTZS <Xd>, <Hn>`<br>`FCVTZS <Wd>, <Sn>`<br>`FCVTZS <Xd>, <Sn>`<br>`FCVTZS <Wd>, <Dn>`<br>`FCVTZS <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTZS (vector, fixed-point)` | Floating-point convert to signed fixed-point, rounding toward zero (vector) | 浮点转有符号定点数，向零舍入（向量） | `FCVTZS <V><d>, <V><n>, #<fbits>`<br>`FCVTZS <Vd>.<T>, <Vn>.<T>, #<fbits>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTZS (vector, integer)` | Floating-point convert to signed integer, rounding toward zero (vector) | 浮点转有符号整数，向零舍入（向量） | `FCVTZS <Hd>, <Hn>`<br>`FCVTZS <V><d>, <V><n>`<br>`FCVTZS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTZU (scalar SIMD&FP)` | Floating-point convert to unsigned integer, rounding toward zero (scalar SIMD&FP) | 浮点转无符号整数，向零舍入（标量 SIMD&FP） | `FCVTZU <Sd>, <Hn>`<br>`FCVTZU <Dd>, <Hn>`<br>`FCVTZU <Dd>, <Sn>`<br>`FCVTZU <Sd>, <Dn>` | FEAT_FPRCVT |
| `FCVTZU (scalar, fixed-point)` | Floating-point convert to unsigned fixed-point, rounding toward zero (scalar) | 浮点转无符号定点数，向零舍入（标量） | `FCVTZU <Wd>, <Hn>, #<fbits>`<br>`FCVTZU <Xd>, <Hn>, #<fbits>`<br>`FCVTZU <Wd>, <Sn>, #<fbits>`<br>`FCVTZU <Xd>, <Sn>, #<fbits>`<br>`FCVTZU <Wd>, <Dn>, #<fbits>`<br>`FCVTZU <Xd>, <Dn>, #<fbits>` | FEAT_FP, FEAT_FP16 |
| `FCVTZU (scalar, integer)` | Floating-point convert to unsigned integer, rounding toward zero (scalar) | 浮点转无符号整数，向零舍入（标量） | `FCVTZU <Wd>, <Hn>`<br>`FCVTZU <Xd>, <Hn>`<br>`FCVTZU <Wd>, <Sn>`<br>`FCVTZU <Xd>, <Sn>`<br>`FCVTZU <Wd>, <Dn>`<br>`FCVTZU <Xd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FCVTZU (vector, fixed-point)` | Floating-point convert to unsigned fixed-point, rounding toward zero (vector) | 浮点转无符号定点数，向零舍入（向量） | `FCVTZU <V><d>, <V><n>, #<fbits>`<br>`FCVTZU <Vd>.<T>, <Vn>.<T>, #<fbits>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FCVTZU (vector, integer)` | Floating-point convert to unsigned integer, rounding toward zero (vector) | 浮点转无符号整数，向零舍入（向量） | `FCVTZU <Hd>, <Hn>`<br>`FCVTZU <V><d>, <V><n>`<br>`FCVTZU <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FDIV (scalar)` | Floating-point divide (scalar) | 浮点除法（标量） | `FDIV <Hd>, <Hn>, <Hm>`<br>`FDIV <Sd>, <Sn>, <Sm>`<br>`FDIV <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FDIV (vector)` | Floating-point divide (vector) | 浮点除法（向量） | `FDIV <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FDOT (8-bit floating-point to half-precision, by element)` | 8-bit floating-point dot product to half-precision (vector, by element) | 8 位浮点点积累加至半精度（向量，按元素） | `FDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.2B[<index>]` | FEAT_FP8DOT2 |
| `FDOT (8-bit floating-point to half-precision, vector)` | 8-bit floating-point dot product to half-precision (vector) | 8 位浮点点积累加至半精度（向量） | `FDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_FP8DOT2 |
| `FDOT (8-bit floating-point to single-precision, by element)` | 8-bit floating-point dot product to single-precision (vector, by element) | 8 位浮点点积累加至单精度（向量，按元素） | `FDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.4B[<index>]` | FEAT_FP8DOT4 |
| `FDOT (8-bit floating-point to single-precision, vector)` | 8-bit floating-point dot product to single-precision (vector) | 8 位浮点点积累加至单精度（向量） | `FDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_FP8DOT4 |
| `FJCVTZS` | Floating-point JavaScript convert to signed fixed-point, rounding toward zero | 浮点 JavaScript 风格转有符号定点数，向零舍入 | `FJCVTZS <Wd>, <Dn>` | FEAT_JSCVT |
| `FMADD` | Floating-point fused multiply-add (scalar) | 浮点融合乘加（标量） | `FMADD <Hd>, <Hn>, <Hm>, <Ha>`<br>`FMADD <Sd>, <Sn>, <Sm>, <Sa>`<br>`FMADD <Dd>, <Dn>, <Dm>, <Da>` | FEAT_FP, FEAT_FP16 |
| `FMAX (scalar)` | Floating-point maximum (scalar) | 浮点最大值（标量） | `FMAX <Hd>, <Hn>, <Hm>`<br>`FMAX <Sd>, <Sn>, <Sm>`<br>`FMAX <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FMAX (vector)` | Floating-point maximum (vector) | 浮点最大值（向量） | `FMAX <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXNM (scalar)` | Floating-point maximum number (scalar) | 浮点数值最大值（标量） | `FMAXNM <Hd>, <Hn>, <Hm>`<br>`FMAXNM <Sd>, <Sn>, <Sm>`<br>`FMAXNM <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FMAXNM (vector)` | Floating-point maximum number (vector) | 浮点数值最大值（向量） | `FMAXNM <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXNMP (scalar)` | Floating-point maximum number of pair of elements (scalar) | 相邻元素对浮点数值最大值（标量） | `FMAXNMP H<d>, <Vn>.2H`<br>`FMAXNMP <V><d>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXNMP (vector)` | Floating-point maximum number pairwise (vector) | 浮点数值最大值逐对归约（向量） | `FMAXNMP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXNMV` | Floating-point maximum number across vector | 浮点数值最大值跨向量归约 | `FMAXNMV <V><d>, <Vn>.<T>`<br>`FMAXNMV S<d>, <Vn>.4S` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXP (scalar)` | Floating-point maximum of pair of elements (scalar) | 相邻元素对浮点最大值（标量） | `FMAXP H<d>, <Vn>.2H`<br>`FMAXP <V><d>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXP (vector)` | Floating-point maximum pairwise (vector) | 浮点最大值逐对归约（向量） | `FMAXP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMAXV` | Floating-point maximum across vector | 浮点最大值跨向量归约 | `FMAXV <V><d>, <Vn>.<T>`<br>`FMAXV S<d>, <Vn>.4S` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMIN (scalar)` | Floating-point minimum (scalar) | 浮点最小值（标量） | `FMIN <Hd>, <Hn>, <Hm>`<br>`FMIN <Sd>, <Sn>, <Sm>`<br>`FMIN <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FMIN (vector)` | Floating-point minimum (vector) | 浮点最小值（向量） | `FMIN <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINNM (scalar)` | Floating-point minimum number (scalar) | 浮点数值最小值（标量） | `FMINNM <Hd>, <Hn>, <Hm>`<br>`FMINNM <Sd>, <Sn>, <Sm>`<br>`FMINNM <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FMINNM (vector)` | Floating-point minimum number (vector) | 浮点数值最小值（向量） | `FMINNM <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINNMP (scalar)` | Floating-point minimum number of pair of elements (scalar) | 相邻元素对浮点数值最小值（标量） | `FMINNMP H<d>, <Vn>.2H`<br>`FMINNMP <V><d>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINNMP (vector)` | Floating-point minimum number pairwise (vector) | 浮点数值最小值逐对归约（向量） | `FMINNMP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINNMV` | Floating-point minimum number across vector | 浮点数值最小值跨向量归约 | `FMINNMV <V><d>, <Vn>.<T>`<br>`FMINNMV S<d>, <Vn>.4S` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINP (scalar)` | Floating-point minimum of pair of elements (scalar) | 相邻元素对浮点最小值（标量） | `FMINP H<d>, <Vn>.2H`<br>`FMINP <V><d>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINP (vector)` | Floating-point minimum pairwise (vector) | 浮点最小值逐对归约（向量） | `FMINP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMINV` | Floating-point minimum across vector | 浮点最小值跨向量归约 | `FMINV <V><d>, <Vn>.<T>`<br>`FMINV S<d>, <Vn>.4S` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMLA (by element)` | Floating-point fused multiply-add to accumulator (by element) | 浮点融合乘加至累加器（按元素） | `FMLA <Hd>, <Hn>, <Vm>.H[<index>]`<br>`FMLA <V><d>, <V><n>, <Vm>.<Ts>[<index>]`<br>`FMLA <Vd>.<T>, <Vn>.<T>, <Vm>.H[<index>]`<br>`FMLA <Vd>.<T>, <Vn>.<T>, <Vm>.<Ts>[<index>]` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMLA (vector)` | Floating-point fused multiply-add to accumulator (vector) | 浮点融合乘加至累加器（向量） | `FMLA <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMLAL, FMLAL2 (by element)` | Floating-point fused multiply-add long to accumulator (by element) | 浮点融合长乘加至累加器（按元素） | `FMLAL <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.H[<index>]`<br>`FMLAL2 <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.H[<index>]` | FEAT_FHM |
| `FMLAL, FMLAL2 (vector)` | Floating-point fused multiply-add long to accumulator (vector) | 浮点融合长乘加至累加器（向量） | `FMLAL <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>`<br>`FMLAL2 <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_FHM |
| `FMLALB, FMLALT (by element)` | 8-bit floating-point multiply-add to half-precision (vector, by element) | 8 位浮点乘加至半精度（向量，按元素） | `FMLALB <Vd>.8H, <Vn>.16B, <Vm>.B[<index>]`<br>`FMLALT <Vd>.8H, <Vn>.16B, <Vm>.B[<index>]` | FEAT_FP8FMA |
| `FMLALB, FMLALT (vector)` | 8-bit floating-point multiply-add to half-precision (vector) | 8 位浮点乘加至半精度（向量） | `FMLALB <Vd>.8H, <Vn>.16B, <Vm>.16B`<br>`FMLALT <Vd>.8H, <Vn>.16B, <Vm>.16B` | FEAT_FP8FMA |
| `FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT (by element)` | 8-bit floating-point multiply-add to single-precision (vector, by element) | 8 位浮点乘加至单精度（向量，按元素） | `FMLALLBB <Vd>.4S, <Vn>.16B, <Vm>.B[<index>]`<br>`FMLALLBT <Vd>.4S, <Vn>.16B, <Vm>.B[<index>]`<br>`FMLALLTB <Vd>.4S, <Vn>.16B, <Vm>.B[<index>]`<br>`FMLALLTT <Vd>.4S, <Vn>.16B, <Vm>.B[<index>]` | FEAT_FP8FMA |
| `FMLALLBB, FMLALLBT, FMLALLTB, FMLALLTT (vector)` | 8-bit floating-point multiply-add to single-precision (vector) | 8 位浮点乘加至单精度（向量） | `FMLALLBB <Vd>.4S, <Vn>.16B, <Vm>.16B`<br>`FMLALLBT <Vd>.4S, <Vn>.16B, <Vm>.16B`<br>`FMLALLTB <Vd>.4S, <Vn>.16B, <Vm>.16B`<br>`FMLALLTT <Vd>.4S, <Vn>.16B, <Vm>.16B` | FEAT_FP8FMA |
| `FMLS (by element)` | Floating-point fused multiply-subtract from accumulator (by element) | 浮点融合乘减至累加器（按元素） | `FMLS <Hd>, <Hn>, <Vm>.H[<index>]`<br>`FMLS <V><d>, <V><n>, <Vm>.<Ts>[<index>]`<br>`FMLS <Vd>.<T>, <Vn>.<T>, <Vm>.H[<index>]`<br>`FMLS <Vd>.<T>, <Vn>.<T>, <Vm>.<Ts>[<index>]` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMLS (vector)` | Floating-point fused multiply-subtract from accumulator (vector) | 浮点融合乘减至累加器（向量） | `FMLS <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMLSL, FMLSL2 (by element)` | Floating-point fused multiply-subtract long from accumulator (by element) | 浮点融合长乘减至累加器（按元素） | `FMLSL <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.H[<index>]`<br>`FMLSL2 <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.H[<index>]` | FEAT_FHM |
| `FMLSL, FMLSL2 (vector)` | Floating-point fused multiply-subtract long from accumulator (vector) | 浮点融合长乘减至累加器（向量） | `FMLSL <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>`<br>`FMLSL2 <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_FHM |
| `FMMLA (widening, 8-bit floating-point to half-precision)` | 8-bit floating-point matrix multiply-accumulate to half-precision | 8 位浮点矩阵乘累加至半精度 | `FMMLA <Vd>.8H, <Vn>.16B, <Vm>.16B` | FEAT_F8F16MM |
| `FMMLA (widening, 8-bit floating-point to single-precision)` | 8-bit floating-point matrix multiply-accumulate to single-precision | 8 位浮点矩阵乘累加至单精度 | `FMMLA <Vd>.4S, <Vn>.16B, <Vm>.16B` | FEAT_F8F32MM |
| `FMOV (general)` | Floating-point move to or from general-purpose register without conversion | 浮点与通用寄存器间无转换移动 | `FMOV <Wd>, <Hn>`<br>`FMOV <Xd>, <Hn>`<br>`FMOV <Hd>, <Wn>`<br>`FMOV <Sd>, <Wn>`<br>`FMOV <Wd>, <Sn>`<br>`FMOV <Hd>, <Xn>`<br>`FMOV <Dd>, <Xn>`<br>`FMOV <Vd>.D[1], <Xn>`<br>`FMOV <Xd>, <Dn>`<br>`FMOV <Xd>, <Vn>.D[1]` | FEAT_FP, FEAT_FP16 |
| `FMOV (register)` | Floating-point move register without conversion | 浮点寄存器间无转换移动 | `FMOV <Hd>, <Hn>`<br>`FMOV <Sd>, <Sn>`<br>`FMOV <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FMOV (scalar, immediate)` | Floating-point move immediate (scalar) | 浮点立即数移动（标量） | `FMOV <Hd>, #<imm>`<br>`FMOV <Sd>, #<imm>`<br>`FMOV <Dd>, #<imm>` | FEAT_FP, FEAT_FP16 |
| `FMOV (vector, immediate)` | Floating-point move immediate (vector) | 浮点立即数移动（向量） | `FMOV <Vd>.<T>, #<imm>`<br>`FMOV <Vd>.2D, #<imm>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMSUB` | Floating-point fused multiply-subtract (scalar) | 浮点融合乘减（标量） | `FMSUB <Hd>, <Hn>, <Hm>, <Ha>`<br>`FMSUB <Sd>, <Sn>, <Sm>, <Sa>`<br>`FMSUB <Dd>, <Dn>, <Dm>, <Da>` | FEAT_FP, FEAT_FP16 |
| `FMUL (by element)` | Floating-point multiply (by element) | 浮点乘法（按元素） | `FMUL <Hd>, <Hn>, <Vm>.H[<index>]`<br>`FMUL <V><d>, <V><n>, <Vm>.<Ts>[<index>]`<br>`FMUL <Vd>.<T>, <Vn>.<T>, <Vm>.H[<index>]`<br>`FMUL <Vd>.<T>, <Vn>.<T>, <Vm>.<Ts>[<index>]` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMUL (scalar)` | Floating-point multiply (scalar) | 浮点乘法（标量） | `FMUL <Hd>, <Hn>, <Hm>`<br>`FMUL <Sd>, <Sn>, <Sm>`<br>`FMUL <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FMUL (vector)` | Floating-point multiply (vector) | 浮点乘法（向量） | `FMUL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMULX` | Floating-point multiply extended | 浮点扩展乘法 | `FMULX <Hd>, <Hn>, <Hm>`<br>`FMULX <V><d>, <V><n>, <V><m>`<br>`FMULX <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FMULX (by element)` | Floating-point multiply extended (by element) | 浮点扩展乘法（按元素） | `FMULX <Hd>, <Hn>, <Vm>.H[<index>]`<br>`FMULX <V><d>, <V><n>, <Vm>.<Ts>[<index>]`<br>`FMULX <Vd>.<T>, <Vn>.<T>, <Vm>.H[<index>]`<br>`FMULX <Vd>.<T>, <Vn>.<T>, <Vm>.<Ts>[<index>]` | FEAT_AdvSIMD, FEAT_FP16 |
| `FNEG (scalar)` | Floating-point negate (scalar) | 浮点取反（标量） | `FNEG <Hd>, <Hn>`<br>`FNEG <Sd>, <Sn>`<br>`FNEG <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FNEG (vector)` | Floating-point negate (vector) | 浮点取反（向量） | `FNEG <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FNMADD` | Floating-point negated fused multiply-add (scalar) | 浮点否定融合乘加（标量） | `FNMADD <Hd>, <Hn>, <Hm>, <Ha>`<br>`FNMADD <Sd>, <Sn>, <Sm>, <Sa>`<br>`FNMADD <Dd>, <Dn>, <Dm>, <Da>` | FEAT_FP, FEAT_FP16 |
| `FNMSUB` | Floating-point negated fused multiply-subtract (scalar) | 浮点否定融合乘减（标量） | `FNMSUB <Hd>, <Hn>, <Hm>, <Ha>`<br>`FNMSUB <Sd>, <Sn>, <Sm>, <Sa>`<br>`FNMSUB <Dd>, <Dn>, <Dm>, <Da>` | FEAT_FP, FEAT_FP16 |
| `FNMUL (scalar)` | Floating-point multiply-negate (scalar) | 浮点乘法取反（标量） | `FNMUL <Hd>, <Hn>, <Hm>`<br>`FNMUL <Sd>, <Sn>, <Sm>`<br>`FNMUL <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FRECPE` | Floating-point reciprocal estimate | 浮点倒数估算 | `FRECPE <Hd>, <Hn>`<br>`FRECPE <V><d>, <V><n>`<br>`FRECPE <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRECPS` | Floating-point reciprocal step | 浮点倒数迭代步进 | `FRECPS <Hd>, <Hn>, <Hm>`<br>`FRECPS <V><d>, <V><n>, <V><m>`<br>`FRECPS <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRECPX` | Floating-point reciprocal exponent (scalar) | 浮点倒数指数（标量） | `FRECPX <Hd>, <Hn>`<br>`FRECPX <V><d>, <V><n>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINT32X (scalar)` | Floating-point round to 32-bit integer, using current rounding mode (scalar) | 浮点舍入至 32 位整数，使用当前舍入模式（标量） | `FRINT32X <Sd>, <Sn>`<br>`FRINT32X <Dd>, <Dn>` | FEAT_FRINTTS |
| `FRINT32X (vector)` | Floating-point round to 32-bit integer, using current rounding mode (vector) | 浮点舍入至 32 位整数，使用当前舍入模式（向量） | `FRINT32X <Vd>.<T>, <Vn>.<T>` | FEAT_FRINTTS |
| `FRINT32Z (scalar)` | Floating-point round to 32-bit integer toward zero (scalar) | 浮点舍入至 32 位整数，向零舍入（标量） | `FRINT32Z <Sd>, <Sn>`<br>`FRINT32Z <Dd>, <Dn>` | FEAT_FRINTTS |
| `FRINT32Z (vector)` | Floating-point round to 32-bit integer toward zero (vector) | 浮点舍入至 32 位整数，向零舍入（向量） | `FRINT32Z <Vd>.<T>, <Vn>.<T>` | FEAT_FRINTTS |
| `FRINT64X (scalar)` | Floating-point round to 64-bit integer, using current rounding mode (scalar) | 浮点舍入至 64 位整数，使用当前舍入模式（标量） | `FRINT64X <Sd>, <Sn>`<br>`FRINT64X <Dd>, <Dn>` | FEAT_FRINTTS |
| `FRINT64X (vector)` | Floating-point round to 64-bit integer, using current rounding mode (vector) | 浮点舍入至 64 位整数，使用当前舍入模式（向量） | `FRINT64X <Vd>.<T>, <Vn>.<T>` | FEAT_FRINTTS |
| `FRINT64Z (scalar)` | Floating-point round to 64-bit integer toward zero (scalar) | 浮点舍入至 64 位整数，向零舍入（标量） | `FRINT64Z <Sd>, <Sn>`<br>`FRINT64Z <Dd>, <Dn>` | FEAT_FRINTTS |
| `FRINT64Z (vector)` | Floating-point round to 64-bit integer toward zero (vector) | 浮点舍入至 64 位整数，向零舍入（向量） | `FRINT64Z <Vd>.<T>, <Vn>.<T>` | FEAT_FRINTTS |
| `FRINTA (scalar)` | Floating-point round to integral, to nearest with ties to away (scalar) | 浮点舍入至整数，就近远离零舍入（标量） | `FRINTA <Hd>, <Hn>`<br>`FRINTA <Sd>, <Sn>`<br>`FRINTA <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTA (vector)` | Floating-point round to integral, to nearest with ties to away (vector) | 浮点舍入至整数，就近远离零舍入（向量） | `FRINTA <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTI (scalar)` | Floating-point round to integral, using current rounding mode (scalar) | 浮点舍入至整数，使用当前舍入模式（标量） | `FRINTI <Hd>, <Hn>`<br>`FRINTI <Sd>, <Sn>`<br>`FRINTI <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTI (vector)` | Floating-point round to integral, using current rounding mode (vector) | 浮点舍入至整数，使用当前舍入模式（向量） | `FRINTI <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTM (scalar)` | Floating-point round to integral, toward minus infinity (scalar) | 浮点舍入至整数，向负无穷舍入（标量） | `FRINTM <Hd>, <Hn>`<br>`FRINTM <Sd>, <Sn>`<br>`FRINTM <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTM (vector)` | Floating-point round to integral, toward minus infinity (vector) | 浮点舍入至整数，向负无穷舍入（向量） | `FRINTM <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTN (scalar)` | Floating-point round to integral, to nearest with ties to even (scalar) | 浮点舍入至整数，就近偶数舍入（标量） | `FRINTN <Hd>, <Hn>`<br>`FRINTN <Sd>, <Sn>`<br>`FRINTN <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTN (vector)` | Floating-point round to integral, to nearest with ties to even (vector) | 浮点舍入至整数，就近偶数舍入（向量） | `FRINTN <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTP (scalar)` | Floating-point round to integral, toward plus infinity (scalar) | 浮点舍入至整数，向正无穷舍入（标量） | `FRINTP <Hd>, <Hn>`<br>`FRINTP <Sd>, <Sn>`<br>`FRINTP <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTP (vector)` | Floating-point round to integral, toward plus infinity (vector) | 浮点舍入至整数，向正无穷舍入（向量） | `FRINTP <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTX (scalar)` | Floating-point round to integral exact, using current rounding mode (scalar) | 浮点精确舍入至整数，使用当前舍入模式（标量） | `FRINTX <Hd>, <Hn>`<br>`FRINTX <Sd>, <Sn>`<br>`FRINTX <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTX (vector)` | Floating-point round to integral exact, using current rounding mode (vector) | 浮点精确舍入至整数，使用当前舍入模式（向量） | `FRINTX <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRINTZ (scalar)` | Floating-point round to integral, toward zero (scalar) | 浮点舍入至整数，向零舍入（标量） | `FRINTZ <Hd>, <Hn>`<br>`FRINTZ <Sd>, <Sn>`<br>`FRINTZ <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FRINTZ (vector)` | Floating-point round to integral, toward zero (vector) | 浮点舍入至整数，向零舍入（向量） | `FRINTZ <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRSQRTE` | Floating-point reciprocal square root estimate | 浮点倒数平方根估算 | `FRSQRTE <Hd>, <Hn>`<br>`FRSQRTE <V><d>, <V><n>`<br>`FRSQRTE <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FRSQRTS` | Floating-point reciprocal square root step | 浮点倒数平方根迭代步进 | `FRSQRTS <Hd>, <Hn>, <Hm>`<br>`FRSQRTS <V><d>, <V><n>, <V><m>`<br>`FRSQRTS <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FSCALE` | Floating-point adjust exponent by vector | 按向量调整浮点指数 | `FSCALE <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_FP8 |
| `FSQRT (scalar)` | Floating-point square root (scalar) | 浮点平方根（标量） | `FSQRT <Hd>, <Hn>`<br>`FSQRT <Sd>, <Sn>`<br>`FSQRT <Dd>, <Dn>` | FEAT_FP, FEAT_FP16 |
| `FSQRT (vector)` | Floating-point square root (vector) | 浮点平方根（向量） | `FSQRT <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `FSUB (scalar)` | Floating-point subtract (scalar) | 浮点减法（标量） | `FSUB <Hd>, <Hn>, <Hm>`<br>`FSUB <Sd>, <Sn>, <Sm>`<br>`FSUB <Dd>, <Dn>, <Dm>` | FEAT_FP, FEAT_FP16 |
| `FSUB (vector)` | Floating-point subtract (vector) | 浮点减法（向量） | `FSUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `INS (element)` | Insert vector element from another vector element | 从另一向量元素插入向量元素 | `INS <Vd>.<Ts>[<index1>], <Vn>.<Ts>[<index2>]` | FEAT_AdvSIMD |
| `INS (general)` | Insert vector element from general-purpose register | 从通用寄存器插入向量元素 | `INS <Vd>.<Ts>[<index>], <R><n>` | FEAT_AdvSIMD |
| `LD1 (multiple structures)` | Load multiple single-element structures to one, two, three, or four registers | 加载多个单元素结构到一至四个寄存器 | `LD1 { <Vt>.<T> }, [<Xn\|SP>]`<br>`LD1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>]`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>]`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>]`<br>`LD1 { <Vt>.<T> }, [<Xn\|SP>], <imm>`<br>`LD1 { <Vt>.<T> }, [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <imm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <imm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <imm>`<br>`LD1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD1 (single structure)` | Load one single-element structure to one lane of one register | 加载一个单元素结构到寄存器指定通道 | `LD1 { <Vt>.B }[<index>], [<Xn\|SP>]`<br>`LD1 { <Vt>.H }[<index>], [<Xn\|SP>]`<br>`LD1 { <Vt>.S }[<index>], [<Xn\|SP>]`<br>`LD1 { <Vt>.D }[<index>], [<Xn\|SP>]`<br>`LD1 { <Vt>.B }[<index>], [<Xn\|SP>], #1`<br>`LD1 { <Vt>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.D }[<index>], [<Xn\|SP>], #8`<br>`LD1 { <Vt>.D }[<index>], [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.H }[<index>], [<Xn\|SP>], #2`<br>`LD1 { <Vt>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`LD1 { <Vt>.S }[<index>], [<Xn\|SP>], #4`<br>`LD1 { <Vt>.S }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD1R` | Load one single-element structure and replicate to all lanes (of one register) | 加载单元素结构并复制到寄存器所有通道 | `LD1R { <Vt>.<T> }, [<Xn\|SP>]`<br>`LD1R { <Vt>.<T> }, [<Xn\|SP>], <imm>`<br>`LD1R { <Vt>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD2 (multiple structures)` | Load multiple 2-element structures to two registers | 加载多个 2 元素结构到两个寄存器 | `LD2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>]`<br>`LD2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <imm>`<br>`LD2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD2 (single structure)` | Load single 2-element structure to one lane of two registers | 加载单个 2 元素结构到两寄存器指定通道 | `LD2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>]`<br>`LD2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>]`<br>`LD2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>]`<br>`LD2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>]`<br>`LD2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>], #2`<br>`LD2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`LD2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>], #4`<br>`LD2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`LD2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>], #8`<br>`LD2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`LD2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>], #16`<br>`LD2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD2R` | Load single 2-element structure and replicate to all lanes of two registers | 加载单个 2 元素结构并复制到两寄存器所有通道 | `LD2R { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>]`<br>`LD2R { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <imm>`<br>`LD2R { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD3 (multiple structures)` | Load multiple 3-element structures to three registers | 加载多个 3 元素结构到三个寄存器 | `LD3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>]`<br>`LD3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <imm>`<br>`LD3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD3 (single structure)` | Load single 3-element structure to one lane of three registers | 加载单个 3 元素结构到三寄存器指定通道 | `LD3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>]`<br>`LD3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>]`<br>`LD3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>]`<br>`LD3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>]`<br>`LD3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>], #3`<br>`LD3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`LD3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>], #6`<br>`LD3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`LD3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>], #12`<br>`LD3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`LD3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>], #24`<br>`LD3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD3R` | Load single 3-element structure and replicate to all lanes of three registers | 加载单个 3 元素结构并复制到三寄存器所有通道 | `LD3R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>]`<br>`LD3R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <imm>`<br>`LD3R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD4 (multiple structures)` | Load multiple 4-element structures to four registers | 加载多个 4 元素结构到四个寄存器 | `LD4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>]`<br>`LD4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <imm>`<br>`LD4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD4 (single structure)` | Load single 4-element structure to one lane of four registers | 加载单个4元素结构体到四个寄存器的指定通道 | `LD4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>]`<br>`LD4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>]`<br>`LD4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>]`<br>`LD4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>]`<br>`LD4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>], #4`<br>`LD4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`LD4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>], #8`<br>`LD4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`LD4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>], #16`<br>`LD4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`LD4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>], #32`<br>`LD4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LD4R` | Load single 4-element structure and replicate to all lanes of four registers | 加载单个4元素结构体并复制到四个寄存器的所有通道 | `LD4R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>]`<br>`LD4R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <imm>`<br>`LD4R { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `LDAP1 (SIMD&FP)` | Load-acquire RCpc one single-element structure to one lane of one register | Load-acquire RCpc 单元素结构体到一个SIMD&FP寄存器的指定通道 | `LDAP1 { <Vt>.D }[<index>], [<Xn\|SP>]` | FEAT_AdvSIMD, FEAT_LRCPC3 |
| `LDAPUR (SIMD&FP)` | Load-acquire RCpc SIMD&FP register (unscaled offset) | Load-acquire RCpc SIMD&FP寄存器（无缩放偏移） | `LDAPUR <Bt>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPUR <Ht>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPUR <St>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPUR <Dt>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPUR <Qt>, [<Xn\|SP>{, #<simm>}]` | FEAT_FP, FEAT_LRCPC3 |
| `LDBFADD, LDBFADDA, LDBFADDAL, LDBFADDL` | Atomic BFloat16 add | 原子BFloat16加法 | `LDBFADD <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFADDA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFADDAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFADDL <Hs>, <Ht>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDBFMAX, LDBFMAXA, LDBFMAXAL, LDBFMAXL` | Atomic BFloat16 maximum | 原子BFloat16最大值 | `LDBFMAX <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXL <Hs>, <Ht>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDBFMAXNM, LDBFMAXNMA, LDBFMAXNMAL, LDBFMAXNML` | Atomic BFloat16 maximum number | 原子BFloat16最大数值（number） | `LDBFMAXNM <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXNMA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXNMAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMAXNML <Hs>, <Ht>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDBFMIN, LDBFMINA, LDBFMINAL, LDBFMINL` | Atomic BFloat16 minimum | 原子BFloat16最小值 | `LDBFMIN <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINL <Hs>, <Ht>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDBFMINNM, LDBFMINNMA, LDBFMINNMAL, LDBFMINNML` | Atomic BFloat16 minimum number | 原子BFloat16最小数值（number） | `LDBFMINNM <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINNMA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINNMAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDBFMINNML <Hs>, <Ht>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDFADD, LDFADDA, LDFADDAL, LDFADDL` | Atomic floating-point add | 原子浮点加法 | `LDFADD <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFADDA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFADDAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFADDL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFADD <Ss>, <St>, [<Xn\|SP>]`<br>`LDFADDA <Ss>, <St>, [<Xn\|SP>]`<br>`LDFADDAL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFADDL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFADD <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFADDA <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFADDAL <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFADDL <Ds>, <Dt>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDFMAX, LDFMAXA, LDFMAXAL, LDFMAXL` | Atomic floating-point maximum | 原子浮点最大值 | `LDFMAX <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAX <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXA <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXAL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAX <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXA <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXAL <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXL <Ds>, <Dt>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDFMAXNM, LDFMAXNMA, LDFMAXNMAL, LDFMAXNML` | Atomic floating-point maximum number | 原子浮点最大数值（number） | `LDFMAXNM <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXNMA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXNMAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXNML <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMAXNM <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXNMA <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXNMAL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXNML <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMAXNM <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXNMA <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXNMAL <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMAXNML <Ds>, <Dt>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDFMIN, LDFMINA, LDFMINAL, LDFMINL` | Atomic floating-point minimum | 原子浮点最小值 | `LDFMIN <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMIN <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINA <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINAL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMIN <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINA <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINAL <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINL <Ds>, <Dt>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDFMINNM, LDFMINNMA, LDFMINNMAL, LDFMINNML` | Atomic floating-point minimum number | 原子浮点最小数值（number） | `LDFMINNM <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINNMA <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINNMAL <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINNML <Hs>, <Ht>, [<Xn\|SP>]`<br>`LDFMINNM <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINNMA <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINNMAL <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINNML <Ss>, <St>, [<Xn\|SP>]`<br>`LDFMINNM <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINNMA <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINNMAL <Ds>, <Dt>, [<Xn\|SP>]`<br>`LDFMINNML <Ds>, <Dt>, [<Xn\|SP>]` | FEAT_LSFE |
| `LDNP (SIMD&FP)` | Load pair of SIMD&FP registers, with non-temporal hint | 加载一对SIMD&FP寄存器（非临时访问提示） | `LDNP <St1>, <St2>, [<Xn\|SP>{, #<imm>}]`<br>`LDNP <Dt1>, <Dt2>, [<Xn\|SP>{, #<imm>}]`<br>`LDNP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP |
| `LDP (SIMD&FP)` | Load pair of SIMD&FP registers | 加载一对SIMD&FP寄存器 | `LDP <St1>, <St2>, [<Xn\|SP>], #<imm>`<br>`LDP <Dt1>, <Dt2>, [<Xn\|SP>], #<imm>`<br>`LDP <Qt1>, <Qt2>, [<Xn\|SP>], #<imm>`<br>`LDP <St1>, <St2>, [<Xn\|SP>, #<imm>]!`<br>`LDP <Dt1>, <Dt2>, [<Xn\|SP>, #<imm>]!`<br>`LDP <Qt1>, <Qt2>, [<Xn\|SP>, #<imm>]!`<br>`LDP <St1>, <St2>, [<Xn\|SP>{, #<imm>}]`<br>`LDP <Dt1>, <Dt2>, [<Xn\|SP>{, #<imm>}]`<br>`LDP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP |
| `LDR (immediate, SIMD&FP)` | Load SIMD&FP register (immediate offset) | 加载SIMD&FP寄存器（立即数偏移） | `LDR <Bt>, [<Xn\|SP>], #<simm>`<br>`LDR <Ht>, [<Xn\|SP>], #<simm>`<br>`LDR <St>, [<Xn\|SP>], #<simm>`<br>`LDR <Dt>, [<Xn\|SP>], #<simm>`<br>`LDR <Qt>, [<Xn\|SP>], #<simm>`<br>`LDR <Bt>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Ht>, [<Xn\|SP>, #<simm>]!`<br>`LDR <St>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Dt>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Qt>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Bt>, [<Xn\|SP>{, #<pimm>}]`<br>`LDR <Ht>, [<Xn\|SP>{, #<pimm>}]`<br>`LDR <St>, [<Xn\|SP>{, #<pimm>}]`<br>`LDR <Dt>, [<Xn\|SP>{, #<pimm>}]`<br>`LDR <Qt>, [<Xn\|SP>{, #<pimm>}]` | FEAT_FP |
| `LDR (literal, SIMD&FP)` | Load SIMD&FP register (PC-relative literal) | 加载SIMD&FP寄存器（PC相对字面量） | `LDR <St>, <label>`<br>`LDR <Dt>, <label>`<br>`LDR <Qt>, <label>` | FEAT_FP |
| `LDR (register, SIMD&FP)` | Load SIMD&FP register (register offset) | 加载SIMD&FP寄存器（寄存器偏移） | `LDR <Bt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`LDR <Bt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]`<br>`LDR <Ht>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`LDR <St>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`LDR <Dt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`LDR <Qt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | FEAT_FP |
| `LDTNP (SIMD&FP)` | Load unprivileged pair of SIMD&FP registers, with non-temporal hint | 非特权加载一对SIMD&FP寄存器（非临时访问提示） | `LDTNP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP, FEAT_LSUI |
| `LDTP (SIMD&FP)` | Load unprivileged pair of SIMD&FP registers | 非特权加载一对SIMD&FP寄存器 | `LDTP <Qt1>, <Qt2>, [<Xn\|SP>], #<imm>`<br>`LDTP <Qt1>, <Qt2>, [<Xn\|SP>, #<imm>]!`<br>`LDTP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP, FEAT_LSUI |
| `LDUR (SIMD&FP)` | Load SIMD&FP register (unscaled offset) | 加载SIMD&FP寄存器（无缩放偏移） | `LDUR <Bt>, [<Xn\|SP>{, #<simm>}]`<br>`LDUR <Ht>, [<Xn\|SP>{, #<simm>}]`<br>`LDUR <St>, [<Xn\|SP>{, #<simm>}]`<br>`LDUR <Dt>, [<Xn\|SP>{, #<simm>}]`<br>`LDUR <Qt>, [<Xn\|SP>{, #<simm>}]` | FEAT_FP |
| `LUTI2` | Lookup table read with 2-bit indices | 使用2位索引读查找表 | `LUTI2 <Vd>.16B, { <Vn>.16B }, <Vm>[<index>]`<br>`LUTI2 <Vd>.8H, { <Vn>.8H }, <Vm>[<index>]` | FEAT_AdvSIMD, FEAT_LUT |
| `LUTI4` | Lookup table read with 4-bit indices | 使用4位索引读查找表 | `LUTI4 <Vd>.16B, { <Vn>.16B }, <Vm>[<index>]`<br>`LUTI4 <Vd>.8H, { <Vn1>.8H, <Vn2>.8H }, <Vm>[<index>]` | FEAT_AdvSIMD, FEAT_LUT |
| `MLA (by element)` | Multiply-add to accumulator (vector, by element) | 乘加累积（向量，按元素） | `MLA <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `MLA (vector)` | Multiply-add to accumulator (vector) | 乘加累积（向量） | `MLA <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `MLS (by element)` | Multiply-subtract from accumulator (vector, by element) | 乘减累积（向量，按元素） | `MLS <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `MLS (vector)` | Multiply-subtract from accumulator (vector) | 乘减累积（向量） | `MLS <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `MOV (element)` | Move vector element to another vector element: an alias of INS (element) | 将向量元素移动到另一向量元素（INS element 的别名） | `MOV <Vd>.<Ts>[<index1>], <Vn>.<Ts>[<index2>]` | FEAT_AdvSIMD |
| `MOV (from general)` | Move general-purpose register to a vector element: an alias of INS (general) | 将通用寄存器移动到向量元素（INS general 的别名） | `MOV <Vd>.<Ts>[<index>], <R><n>` | FEAT_AdvSIMD |
| `MOV (scalar)` | Move vector element to scalar: an alias of DUP (element) | 将向量元素移动到标量（DUP element 的别名） | `MOV <V><d>, <Vn>.<T>[<index>]` | FEAT_AdvSIMD |
| `MOV (to general)` | Move vector element to general-purpose register: an alias of UMOV | 将向量元素移动到通用寄存器（UMOV 的别名） | `MOV <Wd>, <Vn>.S[<index>]`<br>`MOV <Xd>, <Vn>.D[<index>]` | FEAT_AdvSIMD |
| `MOV (vector)` | Move vector: an alias of ORR (vector, register) | 移动向量（ORR vector register 的别名） | `MOV <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `MOVI` | Move immediate (vector) | 向量立即数传送 | `MOVI <Vd>.<T>, #<imm8>{, LSL #0}`<br>`MOVI <Vd>.<T>, #<imm8>{, LSL #<amount>}`<br>`MOVI <Vd>.<T>, #<imm8>, MSL #<amount>`<br>`MOVI <Dd>, #<imm>`<br>`MOVI <Vd>.2D, #<imm>` | FEAT_AdvSIMD |
| `MUL (by element)` | Multiply (vector, by element) | 向量按元素乘法 | `MUL <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `MUL (vector)` | Multiply (vector) | 向量乘法 | `MUL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `MVN` | Bitwise NOT (vector): an alias of NOT | 向量按位取反（NOT 的别名） | `MVN <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `MVNI` | Move inverted immediate (vector) | 向量取反立即数传送 | `MVNI <Vd>.<T>, #<imm8>{, LSL #<amount>}`<br>`MVNI <Vd>.<T>, #<imm8>, MSL #<amount>` | FEAT_AdvSIMD |
| `NEG (vector)` | Negate (vector) | 向量取反 | `NEG D<d>, D<n>`<br>`NEG <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `NOT` | Bitwise NOT (vector) | 向量按位取反 | `NOT <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `ORN (vector)` | Bitwise inclusive OR NOT (vector) | 向量按位OR NOT | `ORN <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `ORR (vector, immediate)` | Bitwise inclusive OR (vector, immediate) | 向量按位OR（立即数） | `ORR <Vd>.<T>, #<imm8>{, LSL #<amount>}` | FEAT_AdvSIMD |
| `ORR (vector, register)` | Bitwise inclusive OR (vector, register) | 向量按位OR（寄存器） | `ORR <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `PMUL` | Polynomial multiply | 多项式乘法 | `PMUL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `PMULL, PMULL2` | Polynomial multiply long | 多项式长乘法 | `PMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `RADDHN, RADDHN2` | Rounding add returning high narrow | 舍入加法取高位窄结果 | `RADDHN{2} <Vd>.<Tb>, <Vn>.<Ta>, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `RAX1` | Rotate and exclusive-OR | 循环移位并异或 | `RAX1 <Vd>.2D, <Vn>.2D, <Vm>.2D` | FEAT_SHA3 |
| `RBIT (vector)` | Reverse bit order (vector) | 向量按位反转 | `RBIT <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `REV16 (vector)` | Reverse elements in 16-bit halfwords (vector) | 向量内16位半字字节逆序 | `REV16 <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `REV32 (vector)` | Reverse elements in 32-bit words (vector) | 向量内32位字字节逆序 | `REV32 <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `REV64` | Reverse elements in 64-bit doublewords (vector) | 向量内64位双字字节逆序 | `REV64 <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `RSHRN, RSHRN2` | Rounding shift right narrow (immediate) | 舍入右移窄化（立即数） | `RSHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `RSUBHN, RSUBHN2` | Rounding subtract returning high narrow | 舍入减法取高位窄结果 | `RSUBHN{2} <Vd>.<Tb>, <Vn>.<Ta>, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `SABA` | Signed absolute difference and accumulate | 有符号绝对差并累加 | `SABA <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SABAL, SABAL2` | Signed absolute difference and accumulate long | 有符号绝对差并累加长整型 | `SABAL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SABD` | Signed absolute difference | 有符号绝对差 | `SABD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SABDL, SABDL2` | Signed absolute difference long | 有符号绝对差长整型 | `SABDL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SADALP` | Signed add and accumulate long pairwise | 有符号成对加法并累加长整型 | `SADALP <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `SADDL, SADDL2` | Signed add long (vector) | 有符号长整型加法（向量） | `SADDL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SADDLP` | Signed add long pairwise | 有符号成对长整型加法 | `SADDLP <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `SADDLV` | Signed add long across vector | 有符号长整型跨向量加法 | `SADDLV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SADDW, SADDW2` | Signed add wide | 有符号宽加法 | `SADDW{2} <Vd>.<Ta>, <Vn>.<Ta>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SCVTF (scalar SIMD&FP)` | Signed integer convert to floating-point (scalar SIMD&FP) | 有符号整数转浮点（标量SIMD&FP） | `SCVTF <Hd>, <Sn>`<br>`SCVTF <Dd>, <Sn>`<br>`SCVTF <Hd>, <Dn>`<br>`SCVTF <Sd>, <Dn>` | FEAT_FPRCVT |
| `SCVTF (scalar, fixed-point)` | Signed fixed-point convert to floating-point (scalar) | 有符号定点数转浮点（标量） | `SCVTF <Hd>, <Wn>, #<fbits>`<br>`SCVTF <Hd>, <Xn>, #<fbits>`<br>`SCVTF <Sd>, <Wn>, #<fbits>`<br>`SCVTF <Sd>, <Xn>, #<fbits>`<br>`SCVTF <Dd>, <Wn>, #<fbits>`<br>`SCVTF <Dd>, <Xn>, #<fbits>` | FEAT_FP, FEAT_FP16 |
| `SCVTF (scalar, integer)` | Signed integer convert to floating-point (scalar) | 有符号整数转浮点（标量） | `SCVTF <Hd>, <Wn>`<br>`SCVTF <Sd>, <Wn>`<br>`SCVTF <Dd>, <Wn>`<br>`SCVTF <Hd>, <Xn>`<br>`SCVTF <Sd>, <Xn>`<br>`SCVTF <Dd>, <Xn>` | FEAT_FP, FEAT_FP16 |
| `SCVTF (vector, fixed-point)` | Signed fixed-point convert to floating-point (vector) | 有符号定点数转浮点（向量） | `SCVTF <V><d>, <V><n>, #<fbits>`<br>`SCVTF <Vd>.<T>, <Vn>.<T>, #<fbits>` | FEAT_AdvSIMD, FEAT_FP16 |
| `SCVTF (vector, integer)` | Signed integer convert to floating-point (vector) | 有符号整数转浮点（向量） | `SCVTF <Hd>, <Hn>`<br>`SCVTF <V><d>, <V><n>`<br>`SCVTF <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `SDOT (by element)` | Dot product signed arithmetic (vector, by element) | 有符号点积运算（向量，按元素） | `SDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.4B[<index>]` | FEAT_DotProd |
| `SDOT (vector)` | Dot product signed arithmetic (vector) | 有符号点积运算（向量） | `SDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_DotProd |
| `SHA1C` | SHA1 hash update (choose) | SHA1哈希更新（choose） | `SHA1C <Qd>, <Sn>, <Vm>.4S` | FEAT_SHA1 |
| `SHA1H` | SHA1 fixed rotate | SHA1固定旋转 | `SHA1H <Sd>, <Sn>` | FEAT_SHA1 |
| `SHA1M` | SHA1 hash update (majority) | SHA1哈希更新（majority） | `SHA1M <Qd>, <Sn>, <Vm>.4S` | FEAT_SHA1 |
| `SHA1P` | SHA1 hash update (parity) | SHA1哈希更新（parity） | `SHA1P <Qd>, <Sn>, <Vm>.4S` | FEAT_SHA1 |
| `SHA1SU0` | SHA1 schedule update 0 | SHA1调度更新0 | `SHA1SU0 <Vd>.4S, <Vn>.4S, <Vm>.4S` | FEAT_SHA1 |
| `SHA1SU1` | SHA1 schedule update 1 | SHA1调度更新1 | `SHA1SU1 <Vd>.4S, <Vn>.4S` | FEAT_SHA1 |
| `SHA256H` | SHA-256 hash update (part 1) | SHA-256哈希更新第1部分 | `SHA256H <Qd>, <Qn>, <Vm>.4S` | FEAT_SHA256 |
| `SHA256H2` | SHA-256 hash update (part 2) | SHA-256哈希更新第2部分 | `SHA256H2 <Qd>, <Qn>, <Vm>.4S` | FEAT_SHA256 |
| `SHA256SU0` | SHA-256 schedule update 0 | SHA-256调度更新0 | `SHA256SU0 <Vd>.4S, <Vn>.4S` | FEAT_SHA256 |
| `SHA256SU1` | SHA-256 schedule update 1 | SHA-256调度更新1 | `SHA256SU1 <Vd>.4S, <Vn>.4S, <Vm>.4S` | FEAT_SHA256 |
| `SHA512H` | SHA-512 hash update part 1 | SHA-512哈希更新第1部分 | `SHA512H <Qd>, <Qn>, <Vm>.2D` | FEAT_SHA512 |
| `SHA512H2` | SHA-512 hash update part 2 | SHA-512哈希更新第2部分 | `SHA512H2 <Qd>, <Qn>, <Vm>.2D` | FEAT_SHA512 |
| `SHA512SU0` | SHA-512 schedule update 0 | SHA-512调度更新0 | `SHA512SU0 <Vd>.2D, <Vn>.2D` | FEAT_SHA512 |
| `SHA512SU1` | SHA-512 schedule update 1 | SHA-512调度更新1 | `SHA512SU1 <Vd>.2D, <Vn>.2D, <Vm>.2D` | FEAT_SHA512 |
| `SHADD` | Signed halving add | 有符号折半加法 | `SHADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SHL` | Shift left (immediate) | 左移（立即数） | `SHL D<d>, D<n>, #<shift>`<br>`SHL <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SHLL, SHLL2` | Shift left long (by element size) | 按元素大小左移长整型 | `SHLL{2} <Vd>.<Ta>, <Vn>.<Tb>, #<shift>` | FEAT_AdvSIMD |
| `SHRN, SHRN2` | Shift right narrow (immediate) | 右移窄化（立即数） | `SHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `SHSUB` | Signed halving subtract | 有符号折半减法 | `SHSUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SLI` | Shift left and insert (immediate) | 左移并插入（立即数） | `SLI D<d>, D<n>, #<shift>`<br>`SLI <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SM3PARTW1` | SM3PARTW1 | SM3消息扩展第一步 | `SM3PARTW1 <Vd>.4S, <Vn>.4S, <Vm>.4S` | FEAT_SM3 |
| `SM3PARTW2` | SM3PARTW2 | SM3消息扩展第二步 | `SM3PARTW2 <Vd>.4S, <Vn>.4S, <Vm>.4S` | FEAT_SM3 |
| `SM3SS1` | SM3SS1 | SM3压缩函数SS1计算 | `SM3SS1 <Vd>.4S, <Vn>.4S, <Vm>.4S, <Va>.4S` | FEAT_SM3 |
| `SM3TT1A` | SM3TT1A | SM3压缩函数TT1A轮函数 | `SM3TT1A <Vd>.4S, <Vn>.4S, <Vm>.S[<imm2>]` | FEAT_SM3 |
| `SM3TT1B` | SM3TT1B | SM3压缩函数TT1B轮函数 | `SM3TT1B <Vd>.4S, <Vn>.4S, <Vm>.S[<imm2>]` | FEAT_SM3 |
| `SM3TT2A` | SM3TT2A | SM3压缩函数TT2A轮函数 | `SM3TT2A <Vd>.4S, <Vn>.4S, <Vm>.S[<imm2>]` | FEAT_SM3 |
| `SM3TT2B` | SM3TT2B | SM3压缩函数TT2B轮函数 | `SM3TT2B <Vd>.4S, <Vn>.4S, <Vm>.S[<imm2>]` | FEAT_SM3 |
| `SM4E` | SM4 encode | SM4加密轮函数 | `SM4E <Vd>.4S, <Vn>.4S` | FEAT_SM4 |
| `SM4EKEY` | SM4 key | SM4密钥扩展 | `SM4EKEY <Vd>.4S, <Vn>.4S, <Vm>.4S` | FEAT_SM4 |
| `SMAX` | Signed maximum (vector) | 有符号最大值（向量） | `SMAX <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SMAXP` | Signed maximum pairwise | 有符号成对最大值 | `SMAXP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SMAXV` | Signed maximum across vector | 有符号跨向量最大值 | `SMAXV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SMIN` | Signed minimum (vector) | 有符号最小值（向量） | `SMIN <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SMINP` | Signed minimum pairwise | 有符号成对最小值 | `SMINP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SMINV` | Signed minimum across vector | 有符号跨向量最小值 | `SMINV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SMLAL, SMLAL2 (by element)` | Signed multiply-add long (vector, by element) | 有符号乘加长整型（向量，按元素） | `SMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SMLAL, SMLAL2 (vector)` | Signed multiply-add long (vector) | 有符号乘加长整型（向量） | `SMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SMLSL, SMLSL2 (by element)` | Signed multiply-subtract long (vector, by element) | 有符号乘减长整型（向量，按元素） | `SMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SMLSL, SMLSL2 (vector)` | Signed multiply-subtract long (vector) | 有符号乘减长整型（向量） | `SMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SMMLA (vector)` | Signed 8-bit integer matrix multiply-accumulate to 32-bit integer (vector) | 有符号8位整数矩阵乘累加到32位整数（向量） | `SMMLA <Vd>.4S, <Vn>.16B, <Vm>.16B` | FEAT_I8MM |
| `SMOV` | Signed move vector element to general-purpose register | 有符号向量元素移动到通用寄存器 | `SMOV <Wd>, <Vn>.<Ts>[<index>]`<br>`SMOV <Xd>, <Vn>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SMULL, SMULL2 (by element)` | Signed multiply long (vector, by element) | 有符号长整型乘法（向量，按元素） | `SMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SMULL, SMULL2 (vector)` | Signed multiply long (vector) | 有符号长整型乘法（向量） | `SMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SQABS` | Signed saturating absolute value | 有符号饱和绝对值 | `SQABS <V><d>, <V><n>`<br>`SQABS <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SQADD` | Signed saturating add | 有符号饱和加法 | `SQADD <V><d>, <V><n>, <V><m>`<br>`SQADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQDMLAL, SQDMLAL2 (by element)` | Signed saturating doubling multiply-add long (by element) | 有符号饱和倍精度乘加长整型（按元素） | `SQDMLAL <Va><d>, <Vb><n>, V<m>.<Ts>[<index>]`<br>`SQDMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SQDMLAL, SQDMLAL2 (vector)` | Signed saturating doubling multiply-add long | 有符号饱和倍精度乘加长整型 | `SQDMLAL <Va><d>, <Vb><n>, <Vb><m>`<br>`SQDMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SQDMLSL, SQDMLSL2 (by element)` | Signed saturating doubling multiply-subtract long (by element) | 有符号饱和倍精度乘减长整型（按元素） | `SQDMLSL <Va><d>, <Vb><n>, V<m>.<Ts>[<index>]`<br>`SQDMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SQDMLSL, SQDMLSL2 (vector)` | Signed saturating doubling multiply-subtract long | 有符号饱和倍精度乘减长整型 | `SQDMLSL <Va><d>, <Vb><n>, <Vb><m>`<br>`SQDMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SQDMULH (by element)` | Signed saturating doubling multiply returning high half (by element) | 有符号饱和倍精度乘法取高半（按元素） | `SQDMULH <V><d>, <V><n>, V<m>.<Ts>[<index>]`<br>`SQDMULH <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SQDMULH (vector)` | Signed saturating doubling multiply returning high half | 有符号饱和倍精度乘法取高半 | `SQDMULH <V><d>, <V><n>, <V><m>`<br>`SQDMULH <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQDMULL, SQDMULL2 (by element)` | Signed saturating doubling multiply long (by element) | 有符号饱和倍增长乘法（按元素） | `SQDMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]`<br>`SQDMULL <Va><d>, <Vb><n>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SQDMULL, SQDMULL2 (vector)` | Signed saturating doubling multiply long | 有符号饱和倍增长乘法（向量） | `SQDMULL <Va><d>, <Vb><n>, <Vb><m>`<br>`SQDMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SQNEG` | Signed saturating negate | 有符号饱和取反 | `SQNEG <V><d>, <V><n>`<br>`SQNEG <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SQRDMLAH (by element)` | Signed saturating rounding doubling multiply accumulate returning high half (by element) | 有符号饱和舍入倍增乘累加取高半部分（按元素） | `SQRDMLAH <V><d>, <V><n>, V<m>.<Ts>[<index>]`<br>`SQRDMLAH <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_RDM |
| `SQRDMLAH (vector)` | Signed saturating rounding doubling multiply accumulate returning high half (vector) | 有符号饱和舍入倍增乘累加取高半部分（向量） | `SQRDMLAH <V><d>, <V><n>, <V><m>`<br>`SQRDMLAH <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_RDM |
| `SQRDMLSH (by element)` | Signed saturating rounding doubling multiply subtract returning high half (by element) | 有符号饱和舍入倍增乘减取高半部分（按元素） | `SQRDMLSH <V><d>, <V><n>, V<m>.<Ts>[<index>]`<br>`SQRDMLSH <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_RDM |
| `SQRDMLSH (vector)` | Signed saturating rounding doubling multiply subtract returning high half (vector) | 有符号饱和舍入倍增乘减取高半部分（向量） | `SQRDMLSH <V><d>, <V><n>, <V><m>`<br>`SQRDMLSH <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_RDM |
| `SQRDMULH (by element)` | Signed saturating rounding doubling multiply returning high half (by element) | 有符号饱和舍入倍增乘法取高半部分（按元素） | `SQRDMULH <V><d>, <V><n>, V<m>.<Ts>[<index>]`<br>`SQRDMULH <Vd>.<T>, <Vn>.<T>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `SQRDMULH (vector)` | Signed saturating rounding doubling multiply returning high half | 有符号饱和舍入倍增乘法取高半部分（向量） | `SQRDMULH <V><d>, <V><n>, <V><m>`<br>`SQRDMULH <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQRSHL` | Signed saturating rounding shift left (register) | 有符号饱和舍入左移（寄存器） | `SQRSHL <V><d>, <V><n>, <V><m>`<br>`SQRSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQRSHRN, SQRSHRN2` | Signed saturating rounded shift right narrow (immediate) | 有符号饱和舍入右移窄化（立即数） | `SQRSHRN <Vb><d>, <Va><n>, #<shift>`<br>`SQRSHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `SQRSHRUN, SQRSHRUN2` | Signed saturating rounded shift right unsigned narrow (immediate) | 有符号饱和舍入右移无符号窄化（立即数） | `SQRSHRUN <Vb><d>, <Va><n>, #<shift>`<br>`SQRSHRUN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `SQSHL (immediate)` | Signed saturating shift left (immediate) | 有符号饱和左移（立即数） | `SQSHL <V><d>, <V><n>, #<shift>`<br>`SQSHL <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SQSHL (register)` | Signed saturating shift left (register) | 有符号饱和左移（寄存器） | `SQSHL <V><d>, <V><n>, <V><m>`<br>`SQSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQSHLU` | Signed saturating shift left unsigned (immediate) | 有符号饱和左移转无符号（立即数） | `SQSHLU <V><d>, <V><n>, #<shift>`<br>`SQSHLU <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SQSHRN, SQSHRN2` | Signed saturating shift right narrow (immediate) | 有符号饱和右移窄化（立即数） | `SQSHRN <Vb><d>, <Va><n>, #<shift>`<br>`SQSHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `SQSHRUN, SQSHRUN2` | Signed saturating shift right unsigned narrow (immediate) | 有符号饱和右移无符号窄化（立即数） | `SQSHRUN <Vb><d>, <Va><n>, #<shift>`<br>`SQSHRUN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `SQSUB` | Signed saturating subtract | 有符号饱和减法 | `SQSUB <V><d>, <V><n>, <V><m>`<br>`SQSUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SQXTN, SQXTN2` | Signed saturating extract narrow | 有符号饱和提取窄化 | `SQXTN <Vb><d>, <Va><n>`<br>`SQXTN{2} <Vd>.<Tb>, <Vn>.<Ta>` | FEAT_AdvSIMD |
| `SQXTUN, SQXTUN2` | Signed saturating extract unsigned narrow | 有符号饱和提取无符号窄化 | `SQXTUN <Vb><d>, <Va><n>`<br>`SQXTUN{2} <Vd>.<Tb>, <Vn>.<Ta>` | FEAT_AdvSIMD |
| `SRHADD` | Signed rounding halving add | 有符号舍入折半加法 | `SRHADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SRI` | Shift right and insert (immediate) | 右移并插入（立即数） | `SRI D<d>, D<n>, #<shift>`<br>`SRI <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SRSHL` | Signed rounding shift left (register) | 有符号舍入左移（寄存器） | `SRSHL D<d>, D<n>, D<m>`<br>`SRSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SRSHR` | Signed rounding shift right (immediate) | 有符号舍入右移（立即数） | `SRSHR D<d>, D<n>, #<shift>`<br>`SRSHR <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SRSRA` | Signed rounding shift right and accumulate (immediate) | 有符号舍入右移并累加（立即数） | `SRSRA D<d>, D<n>, #<shift>`<br>`SRSRA <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SSHL` | Signed shift left (register) | 有符号左移（寄存器） | `SSHL D<d>, D<n>, D<m>`<br>`SSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SSHLL, SSHLL2` | Signed shift left long (immediate) | 有符号长左移（立即数） | `SSHLL{2} <Vd>.<Ta>, <Vn>.<Tb>, #<shift>` | FEAT_AdvSIMD |
| `SSHR` | Signed shift right (immediate) | 有符号右移（立即数） | `SSHR D<d>, D<n>, #<shift>`<br>`SSHR <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SSRA` | Signed shift right and accumulate (immediate) | 有符号右移并累加（立即数） | `SSRA D<d>, D<n>, #<shift>`<br>`SSRA <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `SSUBL, SSUBL2` | Signed subtract long | 有符号长减法 | `SSUBL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `SSUBW, SSUBW2` | Signed subtract wide | 有符号宽减法 | `SSUBW{2} <Vd>.<Ta>, <Vn>.<Ta>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `ST1 (multiple structures)` | Store multiple single-element structures from one, two, three, or four registers | 将1/2/3/4个寄存器中的多个单元素结构存储到内存 | `ST1 { <Vt>.<T> }, [<Xn\|SP>]`<br>`ST1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>]`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>]`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>]`<br>`ST1 { <Vt>.<T> }, [<Xn\|SP>], <imm>`<br>`ST1 { <Vt>.<T> }, [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <imm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <imm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <imm>`<br>`ST1 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST1 (single structure)` | Store a single-element structure from one lane of one register | 将单个寄存器某通道的单元素结构存储到内存 | `ST1 { <Vt>.B }[<index>], [<Xn\|SP>]`<br>`ST1 { <Vt>.H }[<index>], [<Xn\|SP>]`<br>`ST1 { <Vt>.S }[<index>], [<Xn\|SP>]`<br>`ST1 { <Vt>.D }[<index>], [<Xn\|SP>]`<br>`ST1 { <Vt>.B }[<index>], [<Xn\|SP>], #1`<br>`ST1 { <Vt>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.H }[<index>], [<Xn\|SP>], #2`<br>`ST1 { <Vt>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.S }[<index>], [<Xn\|SP>], #4`<br>`ST1 { <Vt>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`ST1 { <Vt>.D }[<index>], [<Xn\|SP>], #8`<br>`ST1 { <Vt>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST2 (multiple structures)` | Store multiple 2-element structures from two registers | 将两个寄存器中的多个2元素结构存储到内存 | `ST2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>]`<br>`ST2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <imm>`<br>`ST2 { <Vt>.<T>, <Vt2>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST2 (single structure)` | Store single 2-element structure from one lane of two registers | 将两个寄存器某通道的单个2元素结构存储到内存 | `ST2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>]`<br>`ST2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>]`<br>`ST2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>]`<br>`ST2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>]`<br>`ST2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>], #2`<br>`ST2 { <Vt>.B, <Vt2>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`ST2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>], #4`<br>`ST2 { <Vt>.H, <Vt2>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`ST2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>], #8`<br>`ST2 { <Vt>.S, <Vt2>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`ST2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>], #16`<br>`ST2 { <Vt>.D, <Vt2>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST3 (multiple structures)` | Store multiple 3-element structures from three registers | 将三个寄存器中的多个3元素结构存储到内存 | `ST3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>]`<br>`ST3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <imm>`<br>`ST3 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST3 (single structure)` | Store single 3-element structure from one lane of three registers | 将三个寄存器某通道的单个3元素结构存储到内存 | `ST3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>]`<br>`ST3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>]`<br>`ST3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>]`<br>`ST3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>]`<br>`ST3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>], #3`<br>`ST3 { <Vt>.B, <Vt2>.B, <Vt3>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`ST3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>], #6`<br>`ST3 { <Vt>.H, <Vt2>.H, <Vt3>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`ST3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>], #12`<br>`ST3 { <Vt>.S, <Vt2>.S, <Vt3>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`ST3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>], #24`<br>`ST3 { <Vt>.D, <Vt2>.D, <Vt3>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST4 (multiple structures)` | Store multiple 4-element structures from four registers | 将四个寄存器中的多个4元素结构存储到内存 | `ST4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>]`<br>`ST4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <imm>`<br>`ST4 { <Vt>.<T>, <Vt2>.<T>, <Vt3>.<T>, <Vt4>.<T> }, [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `ST4 (single structure)` | Store single 4-element structure from one lane of four registers | 将四个寄存器某通道的单个4元素结构存储到内存 | `ST4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>]`<br>`ST4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>]`<br>`ST4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>]`<br>`ST4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>]`<br>`ST4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>], #4`<br>`ST4 { <Vt>.B, <Vt2>.B, <Vt3>.B, <Vt4>.B }[<index>], [<Xn\|SP>], <Xm>`<br>`ST4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>], #8`<br>`ST4 { <Vt>.H, <Vt2>.H, <Vt3>.H, <Vt4>.H }[<index>], [<Xn\|SP>], <Xm>`<br>`ST4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>], #16`<br>`ST4 { <Vt>.S, <Vt2>.S, <Vt3>.S, <Vt4>.S }[<index>], [<Xn\|SP>], <Xm>`<br>`ST4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>], #32`<br>`ST4 { <Vt>.D, <Vt2>.D, <Vt3>.D, <Vt4>.D }[<index>], [<Xn\|SP>], <Xm>` | FEAT_AdvSIMD |
| `STBFADD, STBFADDL` | Atomic BFloat16 floating-point add, without return | 原子 BFloat16 浮点加法（无返回） | `STBFADD <Hs>, [<Xn\|SP>]`<br>`STBFADDL <Hs>, [<Xn\|SP>]` | FEAT_LSFE |
| `STBFMAX, STBFMAXL` | Atomic BFloat16 floating-point maximum, without return | 原子 BFloat16 浮点最大值（无返回） | `STBFMAX <Hs>, [<Xn\|SP>]`<br>`STBFMAXL <Hs>, [<Xn\|SP>]` | FEAT_LSFE |
| `STBFMAXNM, STBFMAXNML` | Atomic BFloat16 floating-point maximum number, without return | 原子 BFloat16 浮点最大数（无返回） | `STBFMAXNM <Hs>, [<Xn\|SP>]`<br>`STBFMAXNML <Hs>, [<Xn\|SP>]` | FEAT_LSFE |
| `STBFMIN, STBFMINL` | Atomic BFloat16 floating-point minimum, without return | 原子 BFloat16 浮点最小值（无返回） | `STBFMIN <Hs>, [<Xn\|SP>]`<br>`STBFMINL <Hs>, [<Xn\|SP>]` | FEAT_LSFE |
| `STBFMINNM, STBFMINNML` | Atomic BFloat16 floating-point minimum number, without return | 原子 BFloat16 浮点最小数（无返回） | `STBFMINNM <Hs>, [<Xn\|SP>]`<br>`STBFMINNML <Hs>, [<Xn\|SP>]` | FEAT_LSFE |
| `STFADD, STFADDL` | Atomic floating-point add, without return | 原子浮点加法（无返回） | `STFADD <Hs>, [<Xn\|SP>]`<br>`STFADDL <Hs>, [<Xn\|SP>]`<br>`STFADD <Ss>, [<Xn\|SP>]`<br>`STFADDL <Ss>, [<Xn\|SP>]`<br>`STFADD <Ds>, [<Xn\|SP>]`<br>`STFADDL <Ds>, [<Xn\|SP>]` | FEAT_LSFE |
| `STFMAX, STFMAXL` | Atomic floating-point maximum, without return | 原子浮点最大值（无返回） | `STFMAX <Hs>, [<Xn\|SP>]`<br>`STFMAXL <Hs>, [<Xn\|SP>]`<br>`STFMAX <Ss>, [<Xn\|SP>]`<br>`STFMAXL <Ss>, [<Xn\|SP>]`<br>`STFMAX <Ds>, [<Xn\|SP>]`<br>`STFMAXL <Ds>, [<Xn\|SP>]` | FEAT_LSFE |
| `STFMAXNM, STFMAXNML` | Atomic floating-point maximum number, without return | 原子浮点最大数（无返回） | `STFMAXNM <Hs>, [<Xn\|SP>]`<br>`STFMAXNML <Hs>, [<Xn\|SP>]`<br>`STFMAXNM <Ss>, [<Xn\|SP>]`<br>`STFMAXNML <Ss>, [<Xn\|SP>]`<br>`STFMAXNM <Ds>, [<Xn\|SP>]`<br>`STFMAXNML <Ds>, [<Xn\|SP>]` | FEAT_LSFE |
| `STFMIN, STFMINL` | Atomic floating-point minimum, without return | 原子浮点最小值（无返回） | `STFMIN <Hs>, [<Xn\|SP>]`<br>`STFMINL <Hs>, [<Xn\|SP>]`<br>`STFMIN <Ss>, [<Xn\|SP>]`<br>`STFMINL <Ss>, [<Xn\|SP>]`<br>`STFMIN <Ds>, [<Xn\|SP>]`<br>`STFMINL <Ds>, [<Xn\|SP>]` | FEAT_LSFE |
| `STFMINNM, STFMINNML` | Atomic floating-point minimum number, without return | 原子浮点最小数（无返回） | `STFMINNM <Hs>, [<Xn\|SP>]`<br>`STFMINNML <Hs>, [<Xn\|SP>]`<br>`STFMINNM <Ss>, [<Xn\|SP>]`<br>`STFMINNML <Ss>, [<Xn\|SP>]`<br>`STFMINNM <Ds>, [<Xn\|SP>]`<br>`STFMINNML <Ds>, [<Xn\|SP>]` | FEAT_LSFE |
| `STL1 (SIMD&FP)` | Store-release a single-element structure from one lane of one register | 释放存储 SIMD&FP 寄存器某通道的单元素结构 | `STL1 { <Vt>.D }[<index>], [<Xn\|SP>]` | FEAT_AdvSIMD, FEAT_LRCPC3 |
| `STLUR (SIMD&FP)` | Store-release SIMD&FP register (unscaled offset) | 释放存储 SIMD&FP 寄存器（无缩放偏移） | `STLUR <Bt>, [<Xn\|SP>{, #<simm>}]`<br>`STLUR <Ht>, [<Xn\|SP>{, #<simm>}]`<br>`STLUR <St>, [<Xn\|SP>{, #<simm>}]`<br>`STLUR <Dt>, [<Xn\|SP>{, #<simm>}]`<br>`STLUR <Qt>, [<Xn\|SP>{, #<simm>}]` | FEAT_FP, FEAT_LRCPC3 |
| `STNP (SIMD&FP)` | Store pair of SIMD&FP registers, with non-temporal hint | 存储一对 SIMD&FP 寄存器（非临时提示） | `STNP <St1>, <St2>, [<Xn\|SP>{, #<imm>}]`<br>`STNP <Dt1>, <Dt2>, [<Xn\|SP>{, #<imm>}]`<br>`STNP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP |
| `STP (SIMD&FP)` | Store pair of SIMD&FP registers | 存储一对 SIMD&FP 寄存器 | `STP <St1>, <St2>, [<Xn\|SP>], #<imm>`<br>`STP <Dt1>, <Dt2>, [<Xn\|SP>], #<imm>`<br>`STP <Qt1>, <Qt2>, [<Xn\|SP>], #<imm>`<br>`STP <St1>, <St2>, [<Xn\|SP>, #<imm>]!`<br>`STP <Dt1>, <Dt2>, [<Xn\|SP>, #<imm>]!`<br>`STP <Qt1>, <Qt2>, [<Xn\|SP>, #<imm>]!`<br>`STP <St1>, <St2>, [<Xn\|SP>{, #<imm>}]`<br>`STP <Dt1>, <Dt2>, [<Xn\|SP>{, #<imm>}]`<br>`STP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP |
| `STR (immediate, SIMD&FP)` | Store SIMD&FP register (immediate offset) | 存储 SIMD&FP 寄存器（立即数偏移） | `STR <Bt>, [<Xn\|SP>], #<simm>`<br>`STR <Ht>, [<Xn\|SP>], #<simm>`<br>`STR <St>, [<Xn\|SP>], #<simm>`<br>`STR <Dt>, [<Xn\|SP>], #<simm>`<br>`STR <Qt>, [<Xn\|SP>], #<simm>`<br>`STR <Bt>, [<Xn\|SP>, #<simm>]!`<br>`STR <Ht>, [<Xn\|SP>, #<simm>]!`<br>`STR <St>, [<Xn\|SP>, #<simm>]!`<br>`STR <Dt>, [<Xn\|SP>, #<simm>]!`<br>`STR <Qt>, [<Xn\|SP>, #<simm>]!`<br>`STR <Bt>, [<Xn\|SP>{, #<pimm>}]`<br>`STR <Ht>, [<Xn\|SP>{, #<pimm>}]`<br>`STR <St>, [<Xn\|SP>{, #<pimm>}]`<br>`STR <Dt>, [<Xn\|SP>{, #<pimm>}]`<br>`STR <Qt>, [<Xn\|SP>{, #<pimm>}]` | FEAT_FP |
| `STR (register, SIMD&FP)` | Store SIMD&FP register (register offset) | 存储 SIMD&FP 寄存器（寄存器偏移） | `STR <Bt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`STR <Bt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]`<br>`STR <Ht>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`STR <St>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`STR <Dt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`STR <Qt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | FEAT_FP |
| `STTNP (SIMD&FP)` | Store unprivileged pair of SIMD&FP registers, with non-temporal hint | 非特权存储一对 SIMD&FP 寄存器（非临时提示） | `STTNP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP, FEAT_LSUI |
| `STTP (SIMD&FP)` | Store unprivileged pair of SIMD&FP registers | 非特权存储一对 SIMD&FP 寄存器 | `STTP <Qt1>, <Qt2>, [<Xn\|SP>], #<imm>`<br>`STTP <Qt1>, <Qt2>, [<Xn\|SP>, #<imm>]!`<br>`STTP <Qt1>, <Qt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_FP, FEAT_LSUI |
| `STUR (SIMD&FP)` | Store SIMD&FP register (unscaled offset) | 存储 SIMD&FP 寄存器（无缩放偏移） | `STUR <Bt>, [<Xn\|SP>{, #<simm>}]`<br>`STUR <Ht>, [<Xn\|SP>{, #<simm>}]`<br>`STUR <St>, [<Xn\|SP>{, #<simm>}]`<br>`STUR <Dt>, [<Xn\|SP>{, #<simm>}]`<br>`STUR <Qt>, [<Xn\|SP>{, #<simm>}]` | FEAT_FP |
| `SUB (vector)` | Subtract (vector) | 向量减法 | `SUB D<d>, D<n>, D<m>`<br>`SUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `SUBHN, SUBHN2` | Subtract returning high narrow | 减法取高位窄化结果 | `SUBHN{2} <Vd>.<Tb>, <Vn>.<Ta>, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `SUDOT (by element)` | Dot product with signed and unsigned integers (vector, by element) | 有符号与无符号整数点积（向量，按元素） | `SUDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.4B[<index>]` | FEAT_I8MM |
| `SUQADD` | Signed saturating accumulate of unsigned value | 有符号饱和累加无符号值 | `SUQADD <V><d>, <V><n>`<br>`SUQADD <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `SXTL, SXTL2` | Signed extend long: an alias of SSHLL, SSHLL2 | 有符号长扩展（SSHLL/SSHLL2 的别名） | `SXTL{2} <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `TBL` | Table vector lookup | 向量表查找 | `TBL <Vd>.<Ta>, { <Vn>.16B }, <Vm>.<Ta>`<br>`TBL <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B }, <Vm>.<Ta>`<br>`TBL <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B, <Vn+2>.16B }, <Vm>.<Ta>`<br>`TBL <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B, <Vn+2>.16B, <Vn+3>.16B }, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `TBX` | Table vector lookup extension | 向量表查找扩展 | `TBX <Vd>.<Ta>, { <Vn>.16B }, <Vm>.<Ta>`<br>`TBX <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B }, <Vm>.<Ta>`<br>`TBX <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B, <Vn+2>.16B }, <Vm>.<Ta>`<br>`TBX <Vd>.<Ta>, { <Vn>.16B, <Vn+1>.16B, <Vn+2>.16B, <Vn+3>.16B }, <Vm>.<Ta>` | FEAT_AdvSIMD |
| `TRN1` | Transpose vectors (primary) | 向量转置（主） | `TRN1 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `TRN2` | Transpose vectors (secondary) | 向量转置（次） | `TRN2 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UABA` | Unsigned absolute difference and accumulate | 无符号绝对差并累加 | `UABA <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UABAL, UABAL2` | Unsigned absolute difference and accumulate long | 无符号绝对差并长累加 | `UABAL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UABD` | Unsigned absolute difference (vector) | 无符号绝对差（向量） | `UABD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UABDL, UABDL2` | Unsigned absolute difference long | 无符号绝对差长结果 | `UABDL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UADALP` | Unsigned add and accumulate long pairwise | 无符号成对加法并长累加 | `UADALP <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `UADDL, UADDL2` | Unsigned add long (vector) | 无符号长加法（向量） | `UADDL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UADDLP` | Unsigned add long pairwise | 无符号成对长加法 | `UADDLP <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `UADDLV` | Unsigned sum long across vector | 无符号跨向量长求和 | `UADDLV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `UADDW, UADDW2` | Unsigned add wide | 无符号宽加法 | `UADDW{2} <Vd>.<Ta>, <Vn>.<Ta>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UCVTF (scalar SIMD&FP)` | Unsigned integer convert to floating-point (scalar SIMD&FP) | 无符号整数转浮点（标量 SIMD&FP） | `UCVTF <Hd>, <Sn>`<br>`UCVTF <Dd>, <Sn>`<br>`UCVTF <Hd>, <Dn>`<br>`UCVTF <Sd>, <Dn>` | FEAT_FPRCVT |
| `UCVTF (scalar, fixed-point)` | Unsigned fixed-point convert to floating-point (scalar) | 无符号定点数转浮点（标量） | `UCVTF <Hd>, <Wn>, #<fbits>`<br>`UCVTF <Hd>, <Xn>, #<fbits>`<br>`UCVTF <Sd>, <Wn>, #<fbits>`<br>`UCVTF <Sd>, <Xn>, #<fbits>`<br>`UCVTF <Dd>, <Wn>, #<fbits>`<br>`UCVTF <Dd>, <Xn>, #<fbits>` | FEAT_FP, FEAT_FP16 |
| `UCVTF (scalar, integer)` | Unsigned integer convert to floating-point (scalar) | 无符号整数转浮点（标量） | `UCVTF <Hd>, <Wn>`<br>`UCVTF <Sd>, <Wn>`<br>`UCVTF <Dd>, <Wn>`<br>`UCVTF <Hd>, <Xn>`<br>`UCVTF <Sd>, <Xn>`<br>`UCVTF <Dd>, <Xn>` | FEAT_FP, FEAT_FP16 |
| `UCVTF (vector, fixed-point)` | Unsigned fixed-point convert to floating-point (vector) | 无符号定点数转浮点（向量） | `UCVTF <V><d>, <V><n>, #<fbits>`<br>`UCVTF <Vd>.<T>, <Vn>.<T>, #<fbits>` | FEAT_AdvSIMD, FEAT_FP16 |
| `UCVTF (vector, integer)` | Unsigned integer convert to floating-point (vector) | 无符号整数转浮点（向量） | `UCVTF <Hd>, <Hn>`<br>`UCVTF <V><d>, <V><n>`<br>`UCVTF <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD, FEAT_FP16 |
| `UDOT (by element)` | Dot product unsigned arithmetic (vector, by element) | 无符号整数点积（向量，按元素） | `UDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.4B[<index>]` | FEAT_DotProd |
| `UDOT (vector)` | Dot product unsigned arithmetic (vector) | 无符号整数点积（向量） | `UDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_DotProd |
| `UHADD` | Unsigned halving add | 无符号折半加法 | `UHADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UHSUB` | Unsigned halving subtract | 无符号折半减法 | `UHSUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UMAX` | Unsigned maximum (vector) | 无符号最大值（向量） | `UMAX <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UMAXP` | Unsigned maximum pairwise | 无符号成对最大值 | `UMAXP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UMAXV` | Unsigned maximum across vector | 无符号跨向量最大值 | `UMAXV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `UMIN` | Unsigned minimum (vector) | 无符号最小值（向量） | `UMIN <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UMINP` | Unsigned minimum pairwise | 无符号成对最小值 | `UMINP <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UMINV` | Unsigned minimum across vector | 无符号跨向量最小值 | `UMINV <V><d>, <Vn>.<T>` | FEAT_AdvSIMD |
| `UMLAL, UMLAL2 (by element)` | Unsigned multiply-add long (vector, by element) | 无符号长乘累加（向量，按元素） | `UMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `UMLAL, UMLAL2 (vector)` | Unsigned multiply-add long (vector) | 无符号长乘累加（向量） | `UMLAL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UMLSL, UMLSL2 (by element)` | Unsigned multiply-subtract long (vector, by element) | 无符号长乘减（向量，按元素） | `UMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `UMLSL, UMLSL2 (vector)` | Unsigned multiply-subtract long (vector) | 无符号长乘减（向量） | `UMLSL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UMMLA (vector)` | Unsigned 8-bit integer matrix multiply-accumulate to 32-bit integer (vector) | 无符号8位整数矩阵乘累加至32位整数（向量） | `UMMLA <Vd>.4S, <Vn>.16B, <Vm>.16B` | FEAT_I8MM |
| `UMOV` | Unsigned move vector element to general-purpose register | 将向量元素无符号移动到通用寄存器 | `UMOV <Wd>, <Vn>.<Ts>[<index>]`<br>`UMOV <Xd>, <Vn>.D[<index>]` | FEAT_AdvSIMD |
| `UMULL, UMULL2 (by element)` | Unsigned multiply long (vector, by element) | 无符号长乘法（向量，按元素） | `UMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, V<m>.<Ts>[<index>]` | FEAT_AdvSIMD |
| `UMULL, UMULL2 (vector)` | Unsigned multiply long (vector) | 无符号长乘法（向量） | `UMULL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UQADD` | Unsigned saturating add | 无符号饱和加法 | `UQADD <V><d>, <V><n>, <V><m>`<br>`UQADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UQRSHL` | Unsigned saturating rounding shift left (register) | 无符号饱和舍入左移（寄存器） | `UQRSHL <V><d>, <V><n>, <V><m>`<br>`UQRSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UQRSHRN, UQRSHRN2` | Unsigned saturating rounded shift right narrow (immediate) | 无符号饱和舍入右移窄化（立即数） | `UQRSHRN <Vb><d>, <Va><n>, #<shift>`<br>`UQRSHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `UQSHL (immediate)` | Unsigned saturating shift left (immediate) | 无符号饱和左移（立即数） | `UQSHL <V><d>, <V><n>, #<shift>`<br>`UQSHL <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `UQSHL (register)` | Unsigned saturating shift left (register) | 无符号饱和左移（寄存器） | `UQSHL <V><d>, <V><n>, <V><m>`<br>`UQSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UQSHRN, UQSHRN2` | Unsigned saturating shift right narrow (immediate) | 无符号饱和右移窄化（立即数） | `UQSHRN <Vb><d>, <Va><n>, #<shift>`<br>`UQSHRN{2} <Vd>.<Tb>, <Vn>.<Ta>, #<shift>` | FEAT_AdvSIMD |
| `UQSUB` | Unsigned saturating subtract | 无符号饱和减法 | `UQSUB <V><d>, <V><n>, <V><m>`<br>`UQSUB <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UQXTN, UQXTN2` | Unsigned saturating extract narrow | 无符号饱和提取窄化 | `UQXTN <Vb><d>, <Va><n>`<br>`UQXTN{2} <Vd>.<Tb>, <Vn>.<Ta>` | FEAT_AdvSIMD |
| `URECPE` | Unsigned reciprocal estimate | 无符号倒数估算 | `URECPE <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `URHADD` | Unsigned rounding halving add | 无符号舍入折半加法 | `URHADD <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `URSHL` | Unsigned rounding shift left (register) | 无符号舍入左移（寄存器） | `URSHL D<d>, D<n>, D<m>`<br>`URSHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `URSHR` | Unsigned rounding shift right (immediate) | 无符号舍入右移（立即数） | `URSHR D<d>, D<n>, #<shift>`<br>`URSHR <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `URSQRTE` | Unsigned reciprocal square root estimate | 无符号倒数平方根估算 | `URSQRTE <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `URSRA` | Unsigned rounding shift right and accumulate (immediate) | 无符号舍入右移并累加（立即数） | `URSRA D<d>, D<n>, #<shift>`<br>`URSRA <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `USDOT (by element)` | Dot product with unsigned and signed integers (vector, by element) | 无符号与有符号整数点积（向量，按元素） | `USDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.4B[<index>]` | FEAT_I8MM |
| `USDOT (vector)` | Dot product with unsigned and signed integers (vector) | 无符号与有符号整数点积（向量） | `USDOT <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_I8MM |
| `USHL` | Unsigned shift left (register) | 无符号左移（寄存器） | `USHL D<d>, D<n>, D<m>`<br>`USHL <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `USHLL, USHLL2` | Unsigned shift left long (immediate) | 无符号长左移（立即数） | `USHLL{2} <Vd>.<Ta>, <Vn>.<Tb>, #<shift>` | FEAT_AdvSIMD |
| `USHR` | Unsigned shift right (immediate) | 无符号右移（立即数） | `USHR D<d>, D<n>, #<shift>`<br>`USHR <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `USMMLA (vector)` | Unsigned and signed 8-bit integer matrix multiply-accumulate to 32-bit integer (vector) | 无符号与有符号8位整数矩阵乘累加至32位整数（向量） | `USMMLA <Vd>.4S, <Vn>.16B, <Vm>.16B` | FEAT_I8MM |
| `USQADD` | Unsigned saturating accumulate of signed value | 无符号饱和累加有符号值 | `USQADD <V><d>, <V><n>`<br>`USQADD <Vd>.<T>, <Vn>.<T>` | FEAT_AdvSIMD |
| `USRA` | Unsigned shift right and accumulate (immediate) | 无符号右移并累加（立即数） | `USRA D<d>, D<n>, #<shift>`<br>`USRA <Vd>.<T>, <Vn>.<T>, #<shift>` | FEAT_AdvSIMD |
| `USUBL, USUBL2` | Unsigned subtract long | 无符号长减法 | `USUBL{2} <Vd>.<Ta>, <Vn>.<Tb>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `USUBW, USUBW2` | Unsigned subtract wide | 无符号宽减法 | `USUBW{2} <Vd>.<Ta>, <Vn>.<Ta>, <Vm>.<Tb>` | FEAT_AdvSIMD |
| `UXTL, UXTL2` | Unsigned extend long: an alias of USHLL, USHLL2 | 无符号长扩展（USHLL/USHLL2 的别名） | `UXTL{2} <Vd>.<Ta>, <Vn>.<Tb>` | FEAT_AdvSIMD |
| `UZP1` | Unzip vectors (primary) | 向量解交织（低半部分） | `UZP1 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `UZP2` | Unzip vectors (secondary) | 向量解交织（高半部分） | `UZP2 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `XAR` | Exclusive-OR and rotate | 异或并旋转 | `XAR <Vd>.2D, <Vn>.2D, <Vm>.2D, #<imm6>` | FEAT_SHA3 |
| `XTN, XTN2` | Extract narrow | 窄化提取 | `XTN{2} <Vd>.<Tb>, <Vn>.<Ta>` | FEAT_AdvSIMD |
| `ZIP1` | Zip vectors (primary) | 向量交织（低半部分） | `ZIP1 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |
| `ZIP2` | Zip vectors (secondary) | 向量交织（高半部分） | `ZIP2 <Vd>.<T>, <Vn>.<T>, <Vm>.<T>` | FEAT_AdvSIMD |

