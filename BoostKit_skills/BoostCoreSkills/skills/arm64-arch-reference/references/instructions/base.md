# A64 指令 — 基础指令（Base）

> 数据源：ARM 官方 A64 ISA 机器可读规范（2026-03_rel），共 507 条。汇编模板列即官方 `asmtemplate`（Encoding）。
> 源数据下载：https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-03_96.tar.gz

| 指令名 | 英文简述 | 中文简介 | 汇编模板（Encoding） | 关联特性 |
| --- | --- | --- | --- | --- |
| `ABS` | Absolute value | 求绝对值 | `ABS <Wd>, <Wn>`<br>`ABS <Xd>, <Xn>` | FEAT_CSSC |
| `ADC` | Add with carry | 带进位加法 | `ADC <Wd>, <Wn>, <Wm>`<br>`ADC <Xd>, <Xn>, <Xm>` | — |
| `ADCS` | Add with carry, setting flags | 带进位加法并设置标志位 | `ADCS <Wd>, <Wn>, <Wm>`<br>`ADCS <Xd>, <Xn>, <Xm>` | — |
| `ADD (extended register)` | Add extended and scaled register | 扩展并缩放寄存器后相加 | `ADD <Wd\|WSP>, <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`ADD <Xd\|SP>, <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `ADD (immediate)` | Add immediate value | 加立即数 | `ADD <Wd\|WSP>, <Wn\|WSP>, #<imm>{, <shift>}`<br>`ADD <Xd\|SP>, <Xn\|SP>, #<imm>{, <shift>}` | — |
| `ADD (shifted register)` | Add optionally-shifted register | 加可选移位寄存器 | `ADD <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`ADD <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `ADDG` | Add with tag | 带内存标签的加法 | `ADDG <Xd\|SP>, <Xn\|SP>, #<uimm6>, #<uimm4>` | FEAT_MTE |
| `ADDPT` | Add checked pointer | 带检查的指针加法 | `ADDPT <Xd\|SP>, <Xn\|SP>, <Xm>{, LSL #<amount>}` | FEAT_CPA |
| `ADDS (extended register)` | Add extended and scaled register, setting flags | 扩展并缩放寄存器后相加并设置标志位 | `ADDS <Wd>, <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`ADDS <Xd>, <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `ADDS (immediate)` | Add immediate value, setting flags | 加立即数并设置标志位 | `ADDS <Wd>, <Wn\|WSP>, #<imm>{, <shift>}`<br>`ADDS <Xd>, <Xn\|SP>, #<imm>{, <shift>}` | — |
| `ADDS (shifted register)` | Add optionally-shifted register, setting flags | 加可选移位寄存器并设置标志位 | `ADDS <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`ADDS <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `ADR` | Form PC-relative address | 计算PC相对地址 | `ADR <Xd>, <label>` | — |
| `ADRP` | Form PC-relative address to 4KB page | 计算PC相对4KB页地址 | `ADRP <Xd>, <label>` | — |
| `AND (immediate)` | Bitwise AND (immediate) | 按位与（立即数） | `AND <Wd\|WSP>, <Wn>, #<imm>`<br>`AND <Xd\|SP>, <Xn>, #<imm>` | — |
| `AND (shifted register)` | Bitwise AND (shifted register) | 按位与（移位寄存器） | `AND <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`AND <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `ANDS (immediate)` | Bitwise AND (immediate), setting flags | 按位与（立即数）并设置标志位 | `ANDS <Wd>, <Wn>, #<imm>`<br>`ANDS <Xd>, <Xn>, #<imm>` | — |
| `ANDS (shifted register)` | Bitwise AND (shifted register), setting flags | 按位与（移位寄存器）并设置标志位 | `ANDS <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`ANDS <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `APAS` | Associate physical address space: an alias of SYS | 关联物理地址空间（SYS 的别名） | `APAS <Xt>` | FEAT_RME_GPC3 |
| `ASR (immediate)` | Arithmetic shift right (immediate): an alias of SBFM | 算术右移（立即数）（SBFM 的别名） | `ASR <Wd>, <Wn>, #<shift>`<br>`ASR <Xd>, <Xn>, #<shift>` | — |
| `ASR (register)` | Arithmetic shift right (register): an alias of ASRV | 算术右移（寄存器）（ASRV 的别名） | `ASR <Wd>, <Wn>, <Wm>`<br>`ASR <Xd>, <Xn>, <Xm>` | — |
| `ASRV` | Arithmetic shift right variable | 算术右移可变位数 | `ASRV <Wd>, <Wn>, <Wm>`<br>`ASRV <Xd>, <Xn>, <Xm>` | — |
| `AT` | Address translate: an alias of SYS | 地址转换（SYS 的别名） | `AT <at_op>, <Xt>` | FEAT_ATS1A, FEAT_PAN2 |
| `AUTDA, AUTDZA` | Authenticate data address, using key A | 使用密钥A验证数据地址 | `AUTDA <Xd>, <Xn\|SP>`<br>`AUTDZA <Xd>` | FEAT_PAuth |
| `AUTDB, AUTDZB` | Authenticate data address, using key B | 使用密钥B验证数据地址 | `AUTDB <Xd>, <Xn\|SP>`<br>`AUTDZB <Xd>` | FEAT_PAuth |
| `AUTIA, AUTIA1716, AUTIASP, AUTIAZ, AUTIZA` | Authenticate instruction address, using key A | 使用密钥A验证指令地址 | `AUTIA <Xd>, <Xn\|SP>`<br>`AUTIZA <Xd>`<br>`AUTIA1716`<br>`AUTIASP`<br>`AUTIAZ` | FEAT_PAuth |
| `AUTIA171615` | Authenticate instruction address, using key A | 使用密钥A验证指令地址 | `AUTIA171615` | FEAT_PAuth_LR |
| `AUTIASPPC` | Authenticate return address using key A, using an immediate offset | 使用密钥A通过立即数偏移验证返回地址 | `AUTIASPPC <label>` | FEAT_PAuth_LR |
| `AUTIASPPCR` | Authenticate return address using key A, using a register | 使用密钥A通过寄存器验证返回地址 | `AUTIASPPCR <Xn>` | FEAT_PAuth_LR |
| `AUTIB, AUTIB1716, AUTIBSP, AUTIBZ, AUTIZB` | Authenticate instruction address, using key B | 使用密钥B验证指令地址 | `AUTIB <Xd>, <Xn\|SP>`<br>`AUTIZB <Xd>`<br>`AUTIB1716`<br>`AUTIBSP`<br>`AUTIBZ` | FEAT_PAuth |
| `AUTIB171615` | Authenticate instruction address, using key B | 使用密钥B验证指令地址 | `AUTIB171615` | FEAT_PAuth_LR |
| `AUTIBSPPC` | Authenticate return address using key B, using an immediate offset | 使用密钥B通过立即数偏移验证返回地址 | `AUTIBSPPC <label>` | FEAT_PAuth_LR |
| `AUTIBSPPCR` | Authenticate return address using key B, using a register | 使用密钥B通过寄存器验证返回地址 | `AUTIBSPPCR <Xn>` | FEAT_PAuth_LR |
| `AXFLAG` | Convert floating-point condition flags from Arm to external format | 将浮点条件标志从ARM格式转换为外部格式 | `AXFLAG` | FEAT_FlagM2 |
| `B` | Branch | 无条件跳转 | `B <label>` | — |
| `B.cond` | Branch conditionally | 条件跳转 | `B.<cond> <label>` | — |
| `BC.cond` | Branch consistent conditionally | 一致性条件跳转 | `BC.<cond> <label>` | FEAT_HBC |
| `BFC` | Bitfield clear: an alias of BFM | 位域清零（BFM 的别名） | `BFC <Wd>, #<lsb>, #<width>`<br>`BFC <Xd>, #<lsb>, #<width>` | FEAT_ASMv8p2 |
| `BFI` | Bitfield insert: an alias of BFM | 位域插入（BFM 的别名） | `BFI <Wd>, <Wn>, #<lsb>, #<width>`<br>`BFI <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `BFM` | Bitfield move | 位域移动 | `BFM <Wd>, <Wn>, #<immr>, #<imms>`<br>`BFM <Xd>, <Xn>, #<immr>, #<imms>` | — |
| `BFXIL` | Bitfield extract and insert at low end: an alias of BFM | 位域提取并插入低端（BFM 的别名） | `BFXIL <Wd>, <Wn>, #<lsb>, #<width>`<br>`BFXIL <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `BIC (shifted register)` | Bitwise bit clear (shifted register) | 按位清零（移位寄存器） | `BIC <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`BIC <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `BICS (shifted register)` | Bitwise bit clear (shifted register), setting flags | 按位清零（移位寄存器）并设置标志位 | `BICS <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`BICS <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `BL` | Branch with link | 带链接跳转 | `BL <label>` | — |
| `BLR` | Branch with link to register | 跳转到寄存器地址并保存返回地址 | `BLR <Xn>` | — |
| `BLRAA, BLRAAZ, BLRAB, BLRABZ` | Branch with link to register, with pointer authentication | 带指针认证跳转到寄存器并保存返回地址 | `BLRAA <Xn>, <Xm\|SP>`<br>`BLRAAZ <Xn>`<br>`BLRAB <Xn>, <Xm\|SP>`<br>`BLRABZ <Xn>` | FEAT_PAuth |
| `BR` | Branch to register | 跳转到寄存器地址 | `BR <Xn>` | — |
| `BRAA, BRAAZ, BRAB, BRABZ` | Branch to register, with pointer authentication | 带指针认证跳转到寄存器 | `BRAA <Xn>, <Xm\|SP>`<br>`BRAAZ <Xn>`<br>`BRAB <Xn>, <Xm\|SP>`<br>`BRABZ <Xn>` | FEAT_PAuth |
| `BRB` | Branch record buffer: an alias of SYS | 分支记录缓冲区操作（SYS 的别名） | `BRB <brb_op>` | FEAT_BRBE |
| `BRK` | Breakpoint instruction | 断点指令 | `BRK #<imm>` | — |
| `BTI` | Branch target identification | 分支目标标识 | `BTI {<targets>}` | FEAT_BTI |
| `CAS, CASA, CASAL, CASL` | Compare and swap word or doubleword in memory | 内存中字或双字的比较并交换 | `CAS <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASA <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASAL <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASL <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CAS <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASA <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASAL <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASL <Xs>, <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSE |
| `CASB, CASAB, CASALB, CASLB` | Compare and swap byte in memory | 内存中字节的比较并交换 | `CASB <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASAB <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASALB <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASLB <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LSE |
| `CASH, CASAH, CASALH, CASLH` | Compare and swap halfword in memory | 内存中半字的比较并交换 | `CASH <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASAH <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASALH <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`CASLH <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LSE |
| `CASP, CASPA, CASPAL, CASPL` | Compare and swap pair of words or doublewords in memory | 内存中字或双字对的比较并交换 | `CASP <Ws>, <W(s+1)>, <Wt>, <W(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPA <Ws>, <W(s+1)>, <Wt>, <W(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPAL <Ws>, <W(s+1)>, <Wt>, <W(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPL <Ws>, <W(s+1)>, <Wt>, <W(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASP <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPA <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPAL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]` | FEAT_LSE |
| `CASPT, CASPAT, CASPALT, CASPLT` | Compare and swap pair unprivileged | 非特权字或双字对的比较并交换 | `CASPT <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPAT <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPALT <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]`<br>`CASPLT <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `CAST, CASAT, CASALT, CASLT` | Compare and swap unprivileged | 非特权字或双字的比较并交换 | `CAST <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASAT <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASALT <Xs>, <Xt>, [<Xn\|SP>{, #0}]`<br>`CASLT <Xs>, <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `CB<cc> (immediate)` | Compare register with immediate and branch | 寄存器与立即数比较并按条件跳转 | `CBGT <Wt>, #<imm>, <label>`<br>`CBLT <Wt>, #<imm>, <label>`<br>`CBHI <Wt>, #<imm>, <label>`<br>`CBLO <Wt>, #<imm>, <label>`<br>`CBEQ <Wt>, #<imm>, <label>`<br>`CBNE <Wt>, #<imm>, <label>`<br>`CBGT <Xt>, #<imm>, <label>`<br>`CBLT <Xt>, #<imm>, <label>`<br>`CBHI <Xt>, #<imm>, <label>`<br>`CBLO <Xt>, #<imm>, <label>`<br>`CBEQ <Xt>, #<imm>, <label>`<br>`CBNE <Xt>, #<imm>, <label>` | FEAT_CMPBR |
| `CB<cc> (register)` | Compare registers and branch | 寄存器间比较并按条件跳转 | `CBGT <Wt>, <Wm>, <label>`<br>`CBGE <Wt>, <Wm>, <label>`<br>`CBHI <Wt>, <Wm>, <label>`<br>`CBHS <Wt>, <Wm>, <label>`<br>`CBEQ <Wt>, <Wm>, <label>`<br>`CBNE <Wt>, <Wm>, <label>`<br>`CBGT <Xt>, <Xm>, <label>`<br>`CBGE <Xt>, <Xm>, <label>`<br>`CBHI <Xt>, <Xm>, <label>`<br>`CBHS <Xt>, <Xm>, <label>`<br>`CBEQ <Xt>, <Xm>, <label>`<br>`CBNE <Xt>, <Xm>, <label>` | FEAT_CMPBR |
| `CBB<cc>` | Compare bytes and branch | 字节比较并按条件跳转 | `CBBGT <Wt>, <Wm>, <label>`<br>`CBBGE <Wt>, <Wm>, <label>`<br>`CBBHI <Wt>, <Wm>, <label>`<br>`CBBHS <Wt>, <Wm>, <label>`<br>`CBBEQ <Wt>, <Wm>, <label>`<br>`CBBNE <Wt>, <Wm>, <label>` | FEAT_CMPBR |
| `CBBLE` | Compare signed less than or equal to bytes and branch: an alias of CBB<cc> | 字节有符号小于等于比较并跳转（CBB<cc> 的别名） | `CBBLE <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBBLO` | Compare unsigned lower than bytes and branch: an alias of CBB<cc> | 字节无符号低于比较并跳转（CBB<cc> 的别名） | `CBBLO <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBBLS` | Compare unsigned lower than or same as bytes and branch: an alias of CBB<cc> | 字节无符号低于等于比较并跳转（CBB<cc> 的别名） | `CBBLS <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBBLT` | Compare signed less than bytes and branch: an alias of CBB<cc> | 字节有符号小于比较并跳转（CBB<cc> 的别名） | `CBBLT <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBGE (immediate)` | Compare signed greater than or equal to immediate and branch: an alias of CB<cc> (immediate) | 有符号大于等于立即数比较并跳转（CB<cc> 立即数的别名） | `CBGE <Wt>, #<immp1>, <label>`<br>`CBGE <Xt>, #<immp1>, <label>` | FEAT_CMPBR |
| `CBH<cc>` | Compare halfwords and branch | 半字比较并按条件跳转 | `CBHGT <Wt>, <Wm>, <label>`<br>`CBHGE <Wt>, <Wm>, <label>`<br>`CBHHI <Wt>, <Wm>, <label>`<br>`CBHHS <Wt>, <Wm>, <label>`<br>`CBHEQ <Wt>, <Wm>, <label>`<br>`CBHNE <Wt>, <Wm>, <label>` | FEAT_CMPBR |
| `CBHLE` | Compare signed less than or equal to halfwords and branch: an alias of CBH<cc> | 半字有符号小于等于比较并跳转（CBH<cc> 的别名） | `CBHLE <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBHLO` | Compare unsigned lower than halfwords and branch: an alias of CBH<cc> | 半字无符号低于比较并跳转（CBH<cc> 的别名） | `CBHLO <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBHLS` | Compare unsigned lower than or same as halfwords and branch: an alias of CBH<cc> | 半字无符号低于等于比较并跳转（CBH<cc> 的别名） | `CBHLS <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBHLT` | Compare signed less than halfwords and branch: an alias of CBH<cc> | 半字有符号小于比较并跳转（CBH<cc> 的别名） | `CBHLT <Wm>, <Wt>, <label>` | FEAT_CMPBR |
| `CBHS (immediate)` | Compare unsigned higher than or same as immediate and branch: an alias of CB<cc> (immediate) | 无符号高于等于立即数比较并跳转（CB<cc> 立即数的别名） | `CBHS <Wt>, #<immp1>, <label>`<br>`CBHS <Xt>, #<immp1>, <label>` | FEAT_CMPBR |
| `CBLE (immediate)` | Compare signed less than or equal to immediate and branch: an alias of CB<cc> (immediate) | 有符号小于等于立即数比较并跳转（CB<cc> 立即数的别名） | `CBLE <Wt>, #<imms1>, <label>`<br>`CBLE <Xt>, #<imms1>, <label>` | FEAT_CMPBR |
| `CBLE (register)` | Compare signed less than or equal to register and branch: an alias of CB<cc> (register) | 有符号小于等于寄存器比较并跳转（CB<cc> 寄存器的别名） | `CBLE <Wm>, <Wt>, <label>`<br>`CBLE <Xm>, <Xt>, <label>` | FEAT_CMPBR |
| `CBLO (register)` | Compare unsigned lower than register and branch: an alias of CB<cc> (register) | 无符号低于寄存器比较并跳转（CB<cc> 寄存器的别名） | `CBLO <Wm>, <Wt>, <label>`<br>`CBLO <Xm>, <Xt>, <label>` | FEAT_CMPBR |
| `CBLS (immediate)` | Compare unsigned lower than or same as immediate and branch: an alias of CB<cc> (immediate) | 无符号低于等于立即数比较并跳转（CB<cc> 立即数的别名） | `CBLS <Wt>, #<imms1>, <label>`<br>`CBLS <Xt>, #<imms1>, <label>` | FEAT_CMPBR |
| `CBLS (register)` | Compare unsigned lower than or same as register and branch: an alias of CB<cc> (register) | 无符号低于等于寄存器比较并跳转（CB<cc> 寄存器的别名） | `CBLS <Wm>, <Wt>, <label>`<br>`CBLS <Xm>, <Xt>, <label>` | FEAT_CMPBR |
| `CBLT (register)` | Compare signed less than register and branch: an alias of CB<cc> (register) | 有符号小于寄存器比较并跳转（CB<cc> 寄存器的别名） | `CBLT <Wm>, <Wt>, <label>`<br>`CBLT <Xm>, <Xt>, <label>` | FEAT_CMPBR |
| `CBNZ` | Compare and branch on nonzero | 非零比较并跳转 | `CBNZ <Wt>, <label>`<br>`CBNZ <Xt>, <label>` | — |
| `CBZ` | Compare and branch on zero | 零比较并跳转 | `CBZ <Wt>, <label>`<br>`CBZ <Xt>, <label>` | — |
| `CCMN (immediate)` | Conditional compare negative (immediate) | 条件比较负值（立即数） | `CCMN <Wn>, #<imm>, #<nzcv>, <cond>`<br>`CCMN <Xn>, #<imm>, #<nzcv>, <cond>` | — |
| `CCMN (register)` | Conditional compare negative (register) | 条件比较负值（寄存器） | `CCMN <Wn>, <Wm>, #<nzcv>, <cond>`<br>`CCMN <Xn>, <Xm>, #<nzcv>, <cond>` | — |
| `CCMP (immediate)` | Conditional compare (immediate) | 条件比较（立即数） | `CCMP <Wn>, #<imm>, #<nzcv>, <cond>`<br>`CCMP <Xn>, #<imm>, #<nzcv>, <cond>` | — |
| `CCMP (register)` | Conditional compare (register) | 条件比较（寄存器） | `CCMP <Wn>, <Wm>, #<nzcv>, <cond>`<br>`CCMP <Xn>, <Xm>, #<nzcv>, <cond>` | — |
| `CFINV` | Invert carry flag | 反转进位标志 | `CFINV` | FEAT_FlagM |
| `CFP` | Control flow prediction restriction by context: an alias of SYS | 按上下文限制控制流预测（SYS 的别名） | `CFP RCTX, <Xt>` | FEAT_SPECRES |
| `CHKFEAT` | Check feature status | 检查特性状态 | `CHKFEAT X16` | FEAT_CHK |
| `CINC` | Conditional increment: an alias of CSINC | 条件递增（CSINC 的别名） | `CINC <Wd>, <Wn>, <invcond>`<br>`CINC <Xd>, <Xn>, <invcond>` | — |
| `CINV` | Conditional invert: an alias of CSINV | 条件取反（CSINV 的别名） | `CINV <Wd>, <Wn>, <invcond>`<br>`CINV <Xd>, <Xn>, <invcond>` | — |
| `CLRBHB` | Clear branch history | 清除分支历史 | `CLRBHB` | FEAT_CLRBHB |
| `CLREX` | Clear exclusive | 清除独占访问标记 | `CLREX {#<imm>}` | — |
| `CLS` | Count leading sign bits | 计算前导符号位数 | `CLS <Wd>, <Wn>`<br>`CLS <Xd>, <Xn>` | — |
| `CLZ` | Count leading zeros | 计算前导零位数 | `CLZ <Wd>, <Wn>`<br>`CLZ <Xd>, <Xn>` | — |
| `CMN (extended register)` | Compare negative (extended register): an alias of ADDS (extended register) | 比较负值（扩展寄存器）（ADDS 扩展寄存器的别名） | `CMN <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`CMN <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `CMN (immediate)` | Compare negative (immediate): an alias of ADDS (immediate) | 比较负值（立即数）（ADDS 立即数的别名） | `CMN <Wn\|WSP>, #<imm>{, <shift>}`<br>`CMN <Xn\|SP>, #<imm>{, <shift>}` | — |
| `CMN (shifted register)` | Compare negative (shifted register): an alias of ADDS (shifted register) | 比较负值（移位寄存器）（ADDS 移位寄存器的别名） | `CMN <Wn>, <Wm>{, <shift> #<amount>}`<br>`CMN <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `CMP (extended register)` | Compare (extended register): an alias of SUBS (extended register) | 比较（扩展寄存器）（SUBS 扩展寄存器的别名） | `CMP <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`CMP <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `CMP (immediate)` | Compare (immediate): an alias of SUBS (immediate) | 比较（立即数）（SUBS 立即数的别名） | `CMP <Wn\|WSP>, #<imm>{, <shift>}`<br>`CMP <Xn\|SP>, #<imm>{, <shift>}` | — |
| `CMP (shifted register)` | Compare (shifted register): an alias of SUBS (shifted register) | 比较（移位寄存器）（SUBS 移位寄存器的别名） | `CMP <Wn>, <Wm>{, <shift> #<amount>}`<br>`CMP <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `CMPP` | Compare with tag: an alias of SUBPS | 带标签比较（SUBPS 的别名） | `CMPP <Xn\|SP>, <Xm\|SP>` | FEAT_MTE |
| `CNEG` | Conditional negate: an alias of CSNEG | 条件取负（CSNEG 的别名） | `CNEG <Wd>, <Wn>, <invcond>`<br>`CNEG <Xd>, <Xn>, <invcond>` | — |
| `CNT` | Count bits | 统计置位位数 | `CNT <Wd>, <Wn>`<br>`CNT <Xd>, <Xn>` | FEAT_CSSC |
| `COSP` | Clear other speculative prediction restriction by context: an alias of SYS | 按上下文清除其他推测预测限制（SYS 的别名） | `COSP RCTX, <Xt>` | FEAT_SPECRES2 |
| `CPP` | Cache prefetch prediction restriction by context: an alias of SYS | 按上下文限制缓存预取预测（SYS 的别名） | `CPP RCTX, <Xt>` | FEAT_SPECRES |
| `CPYFP, CPYFM, CPYFE` | Memory copy forward-only | 仅向前内存拷贝 | `CPYFP [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFM [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFE [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPN, CPYFMN, CPYFEN` | Memory copy forward-only, reads and writes non-temporal | 仅向前内存拷贝，读写均非时序 | `CPYFPN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPRN, CPYFMRN, CPYFERN` | Memory copy forward-only, reads non-temporal | 仅向前内存拷贝，读非时序 | `CPYFPRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFERN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPRT, CPYFMRT, CPYFERT` | Memory copy forward-only, reads unprivileged | 仅向前内存拷贝，非特权读 | `CPYFPRT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMRT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFERT [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPRTN, CPYFMRTN, CPYFERTN` | Memory copy forward-only, reads unprivileged, reads and writes non-temporal | 仅向前内存拷贝，非特权读且读写非时序 | `CPYFPRTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMRTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFERTN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPRTRN, CPYFMRTRN, CPYFERTRN` | Memory copy forward-only, reads unprivileged and non-temporal | 仅向前内存拷贝，非特权且非时序读 | `CPYFPRTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMRTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFERTRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPRTWN, CPYFMRTWN, CPYFERTWN` | Memory copy forward-only, reads unprivileged, writes non-temporal | 仅向前内存拷贝，非特权读、写非时序 | `CPYFPRTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMRTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFERTWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPT, CPYFMT, CPYFET` | Memory copy forward-only, reads and writes unprivileged | 仅向前内存拷贝，读写均非特权 | `CPYFPT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFET [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPTN, CPYFMTN, CPYFETN` | Memory copy forward-only, reads and writes unprivileged and non-temporal | 仅向前内存拷贝，读写均非特权且非时序 | `CPYFPTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFETN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPTRN, CPYFMTRN, CPYFETRN` | Memory copy forward-only, reads and writes unprivileged, reads non-temporal | 仅向前内存拷贝，读写非特权、读非时序 | `CPYFPTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFETRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPTWN, CPYFMTWN, CPYFETWN` | Memory copy forward-only, reads and writes unprivileged, writes non-temporal | 仅向前内存拷贝，读写非特权、写非时序 | `CPYFPTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFETWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPWN, CPYFMWN, CPYFEWN` | Memory copy forward-only, writes non-temporal | 仅向前内存拷贝，写非时序 | `CPYFPWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPWT, CPYFMWT, CPYFEWT` | Memory copy forward-only, writes unprivileged | 仅向前内存拷贝，非特权写 | `CPYFPWT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMWT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEWT [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPWTN, CPYFMWTN, CPYFEWTN` | Memory copy forward-only, writes unprivileged, reads and writes non-temporal | 仅向前内存拷贝，非特权写且读写非时序 | `CPYFPWTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMWTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEWTN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPWTRN, CPYFMWTRN, CPYFEWTRN` | Memory copy forward-only, writes unprivileged, reads non-temporal | 仅向前内存拷贝，非特权写、读非时序 | `CPYFPWTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMWTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEWTRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYFPWTWN, CPYFMWTWN, CPYFEWTWN` | Memory copy forward-only, writes unprivileged and non-temporal | 仅向前内存拷贝，非特权且非时序写 | `CPYFPWTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFMWTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYFEWTWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYP, CPYM, CPYE` | Memory copy | 内存拷贝 | `CPYP [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYM [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYE [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPN, CPYMN, CPYEN` | Memory copy, reads and writes non-temporal | 内存拷贝，读写均非时序 | `CPYPN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPRN, CPYMRN, CPYERN` | Memory copy, reads non-temporal | 内存复制，读取使用非临时访问语义 | `CPYPRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYERN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPRT, CPYMRT, CPYERT` | Memory copy, reads unprivileged | 内存复制，读取使用非特权访问语义 | `CPYPRT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMRT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYERT [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPRTN, CPYMRTN, CPYERTN` | Memory copy, reads unprivileged, reads and writes non-temporal | 内存复制，读取非特权，读写均非临时访问 | `CPYPRTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMRTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYERTN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPRTRN, CPYMRTRN, CPYERTRN` | Memory copy, reads unprivileged and non-temporal | 内存复制，读取非特权且非临时访问 | `CPYPRTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMRTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYERTRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPRTWN, CPYMRTWN, CPYERTWN` | Memory copy, reads unprivileged, writes non-temporal | 内存复制，读取非特权，写入非临时访问 | `CPYPRTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMRTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYERTWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPT, CPYMT, CPYET` | Memory copy, reads and writes unprivileged | 内存复制，读写均使用非特权访问语义 | `CPYPT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYET [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPTN, CPYMTN, CPYETN` | Memory copy, reads and writes unprivileged and non-temporal | 内存复制，读写均非特权且非临时访问 | `CPYPTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYETN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPTRN, CPYMTRN, CPYETRN` | Memory copy, reads and writes unprivileged, reads non-temporal | 内存复制，读写非特权，读取非临时访问 | `CPYPTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYETRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPTWN, CPYMTWN, CPYETWN` | Memory copy, reads and writes unprivileged, writes non-temporal | 内存复制，读写非特权，写入非临时访问 | `CPYPTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYETWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPWN, CPYMWN, CPYEWN` | Memory copy, writes non-temporal | 内存复制，写入使用非临时访问语义 | `CPYPWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPWT, CPYMWT, CPYEWT` | Memory copy, writes unprivileged | 内存复制，写入使用非特权访问语义 | `CPYPWT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMWT [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEWT [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPWTN, CPYMWTN, CPYEWTN` | Memory copy, writes unprivileged, reads and writes non-temporal | 内存复制，写入非特权，读写均非临时访问 | `CPYPWTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMWTN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEWTN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPWTRN, CPYMWTRN, CPYEWTRN` | Memory copy, writes unprivileged, reads non-temporal | 内存复制，写入非特权，读取非临时访问 | `CPYPWTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMWTRN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEWTRN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CPYPWTWN, CPYMWTWN, CPYEWTWN` | Memory copy, writes unprivileged and non-temporal | 内存复制，写入非特权且非临时访问 | `CPYPWTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYMWTWN [<Xd>]!, [<Xs>]!, <Xn>!`<br>`CPYEWTWN [<Xd>]!, [<Xs>]!, <Xn>!` | FEAT_MOPS |
| `CRC32B, CRC32H, CRC32W, CRC32X` | CRC32 checksum | 计算 CRC32 校验和 | `CRC32B <Wd>, <Wn>, <Wm>`<br>`CRC32H <Wd>, <Wn>, <Wm>`<br>`CRC32W <Wd>, <Wn>, <Wm>`<br>`CRC32X <Wd>, <Wn>, <Xm>` | FEAT_CRC32 |
| `CRC32CB, CRC32CH, CRC32CW, CRC32CX` | CRC32C checksum | 计算 CRC32C 校验和 | `CRC32CB <Wd>, <Wn>, <Wm>`<br>`CRC32CH <Wd>, <Wn>, <Wm>`<br>`CRC32CW <Wd>, <Wn>, <Wm>`<br>`CRC32CX <Wd>, <Wn>, <Xm>` | FEAT_CRC32 |
| `CSDB` | Consumption of speculative data barrier | 消费推测数据屏障 | `CSDB` | — |
| `CSEL` | Conditional select | 条件选择寄存器值 | `CSEL <Wd>, <Wn>, <Wm>, <cond>`<br>`CSEL <Xd>, <Xn>, <Xm>, <cond>` | — |
| `CSET` | Conditional set: an alias of CSINC | 条件置位（CSINC 的别名） | `CSET <Wd>, <invcond>`<br>`CSET <Xd>, <invcond>` | — |
| `CSETM` | Conditional set mask: an alias of CSINV | 条件置位掩码（CSINV 的别名） | `CSETM <Wd>, <invcond>`<br>`CSETM <Xd>, <invcond>` | — |
| `CSINC` | Conditional select increment | 条件选择并加一 | `CSINC <Wd>, <Wn>, <Wm>, <cond>`<br>`CSINC <Xd>, <Xn>, <Xm>, <cond>` | — |
| `CSINV` | Conditional select invert | 条件选择并按位取反 | `CSINV <Wd>, <Wn>, <Wm>, <cond>`<br>`CSINV <Xd>, <Xn>, <Xm>, <cond>` | — |
| `CSNEG` | Conditional select negation | 条件选择并取负 | `CSNEG <Wd>, <Wn>, <Wm>, <cond>`<br>`CSNEG <Xd>, <Xn>, <Xm>, <cond>` | — |
| `CTZ` | Count trailing zeros | 统计尾部零位个数 | `CTZ <Wd>, <Wn>`<br>`CTZ <Xd>, <Xn>` | FEAT_CSSC |
| `DC` | Data cache operation: an alias of SYS | 数据缓存操作（SYS 的别名） | `DC <dc_op>, <Xt>` | FEAT_DPB, FEAT_DPB2, FEAT_MEC, FEAT_MTE, FEAT_MTE2, FEAT_OCCMO, FEAT_PoPS, FEAT_RME |
| `DCPS1` | Debug change PE state to EL1 | 调试模式：将 PE 状态切换到 EL1 | `DCPS1 {#<imm>}` | — |
| `DCPS2` | Debug change PE state to EL2 | 调试模式：将 PE 状态切换到 EL2 | `DCPS2 {#<imm>}` | — |
| `DCPS3` | Debug change PE state to EL3 | 调试模式：将 PE 状态切换到 EL3 | `DCPS3 {#<imm>}` | — |
| `DGH` | Data gathering hint | 数据聚集提示 | `DGH` | FEAT_DGH |
| `DMB` | Data memory barrier | 数据内存屏障 | `DMB (<option>\|#<imm>)` | — |
| `DRPS` | Debug restore PE state | 调试模式：恢复 PE 状态 | `DRPS` | — |
| `DSB` | Data synchronization barrier | 数据同步屏障 | `DSB (<option>\|#<imm>)`<br>`DSB <option>nXS` | FEAT_XS |
| `DVP` | Data value prediction restriction by context: an alias of SYS | 按上下文限制数据值预测（SYS 的别名） | `DVP RCTX, <Xt>` | FEAT_SPECRES |
| `EON (shifted register)` | Bitwise exclusive-OR NOT (shifted register) | 按位异或非（移位寄存器） | `EON <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`EON <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `EOR (immediate)` | Bitwise exclusive-OR (immediate) | 按位异或（立即数） | `EOR <Wd\|WSP>, <Wn>, #<imm>`<br>`EOR <Xd\|SP>, <Xn>, #<imm>` | — |
| `EOR (shifted register)` | Bitwise exclusive-OR (shifted register) | 按位异或（移位寄存器） | `EOR <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`EOR <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `ERET` | Exception return | 从异常返回 | `ERET` | — |
| `ERETAA, ERETAB` | Exception return, with pointer authentication | 带指针认证的异常返回 | `ERETAA`<br>`ERETAB` | FEAT_PAuth |
| `ESB` | Error synchronization barrier | 错误同步屏障 | `ESB` | FEAT_RAS |
| `EXTR` | Extract register | 从寄存器对中提取位域 | `EXTR <Wd>, <Wn>, <Wm>, #<lsb>`<br>`EXTR <Xd>, <Xn>, <Xm>, #<lsb>` | — |
| `GCSB` | Guarded Control Stack barrier | 受保护控制栈屏障 | `GCSB DSYNC` | FEAT_GCS |
| `GCSPOPCX` | Guarded Control Stack pop and compare exception return record: an alias of SYS | 受保护控制栈弹出并比较异常返回记录（SYS 的别名） | `GCSPOPCX` | FEAT_GCS |
| `GCSPOPM` | Guarded Control Stack pop: an alias of SYSL | 受保护控制栈弹出（SYSL 的别名） | `GCSPOPM {<Xt>}` | FEAT_GCS |
| `GCSPOPX` | Guarded Control Stack pop exception return record: an alias of SYS | 受保护控制栈弹出异常返回记录（SYS 的别名） | `GCSPOPX` | FEAT_GCS |
| `GCSPUSHM` | Guarded Control Stack push: an alias of SYS | 受保护控制栈压栈（SYS 的别名） | `GCSPUSHM <Xt>` | FEAT_GCS |
| `GCSPUSHX` | Guarded Control Stack push exception return record: an alias of SYS | 受保护控制栈压入异常返回记录（SYS 的别名） | `GCSPUSHX` | FEAT_GCS |
| `GCSSS1` | Guarded Control Stack switch stack 1: an alias of SYS | 受保护控制栈切换栈第一步（SYS 的别名） | `GCSSS1 <Xt>` | FEAT_GCS |
| `GCSSS2` | Guarded Control Stack switch stack 2: an alias of SYSL | 受保护控制栈切换栈第二步（SYSL 的别名） | `GCSSS2 <Xt>` | FEAT_GCS |
| `GCSSTR` | Guarded Control Stack store register | 向受保护控制栈存储寄存器 | `GCSSTR <Xt>, [<Xn\|SP>]` | FEAT_GCS |
| `GCSSTTR` | Guarded Control Stack store register (unprivileged) | 向受保护控制栈存储寄存器（非特权） | `GCSSTTR <Xt>, [<Xn\|SP>]` | FEAT_GCS |
| `GMI` | Tag mask insert | 插入标签掩码 | `GMI <Xd>, <Xn\|SP>, <Xm>` | FEAT_MTE |
| `HINT` | Hint instruction | 提示指令 | `HINT #<imm>` | — |
| `HLT` | Halt instruction | 暂停指令 | `HLT #<imm>` | — |
| `HVC` | Hypervisor call | 调用虚拟机监控程序 | `HVC #<imm>` | — |
| `IC` | Instruction cache operation: an alias of SYS | 指令缓存操作（SYS 的别名） | `IC <ic_op>{, <Xt>}` | — |
| `IRG` | Insert random tag | 插入随机内存标签 | `IRG <Xd\|SP>, <Xn\|SP>{, <Xm>}` | FEAT_MTE |
| `ISB` | Instruction synchronization barrier | 指令同步屏障 | `ISB {<option>\|#<imm>}` | — |
| `LD64B` | Single-copy atomic 64-byte Load | 单拷贝原子 64 字节加载 | `LD64B <Xt>, [<Xn\|SP> {, #0}]` | FEAT_LS64 |
| `LDADD, LDADDA, LDADDAL, LDADDL` | Atomic add on word or doubleword | 原子加法（字或双字） | `LDADD <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADD <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDADDA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDADDAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDADDL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDADDB, LDADDAB, LDADDALB, LDADDLB` | Atomic add on byte | 原子加法（字节） | `LDADDB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDADDH, LDADDAH, LDADDALH, LDADDLH` | Atomic add on halfword | 原子加法（半字） | `LDADDH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDADDLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDAPR` | Load-acquire RCpc register | 加载-获取 RCpc 寄存器 | `LDAPR <Wt>, [<Xn\|SP>], #4`<br>`LDAPR <Xt>, [<Xn\|SP>], #8`<br>`LDAPR <Wt>, [<Xn\|SP> {, #0}]`<br>`LDAPR <Xt>, [<Xn\|SP> {, #0}]` | FEAT_LRCPC, FEAT_LRCPC3 |
| `LDAPRB` | Load-acquire RCpc register byte | 加载-获取 RCpc 寄存器字节 | `LDAPRB <Wt>, [<Xn\|SP> {, #0}]` | FEAT_LRCPC |
| `LDAPRH` | Load-acquire RCpc register halfword | 加载-获取 RCpc 寄存器半字 | `LDAPRH <Wt>, [<Xn\|SP> {, #0}]` | FEAT_LRCPC |
| `LDAPUR` | Load-acquire RCpc register (unscaled) | 加载-获取 RCpc 寄存器（非比例偏移） | `LDAPUR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPUR <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAPURB` | Load-acquire RCpc register byte (unscaled) | 加载-获取 RCpc 寄存器字节（非比例偏移） | `LDAPURB <Wt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAPURH` | Load-acquire RCpc register halfword (unscaled) | 加载-获取 RCpc 寄存器半字（非比例偏移） | `LDAPURH <Wt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAPURSB` | Load-acquire RCpc register signed byte (unscaled) | 加载-获取 RCpc 寄存器有符号字节（非比例偏移） | `LDAPURSB <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPURSB <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAPURSH` | Load-acquire RCpc register signed halfword (unscaled) | 加载-获取 RCpc 寄存器有符号半字（非比例偏移） | `LDAPURSH <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDAPURSH <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAPURSW` | Load-acquire RCpc register signed word (unscaled) | 加载-获取 RCpc 寄存器有符号字（非比例偏移） | `LDAPURSW <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `LDAR` | Load-acquire register | 加载-获取寄存器 | `LDAR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDAR <Xt>, [<Xn\|SP>{, #0}]` | — |
| `LDARB` | Load-acquire register byte | 加载-获取寄存器字节 | `LDARB <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LDARH` | Load-acquire register halfword | 加载-获取寄存器半字 | `LDARH <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LDATXR` | Load-acquire unprivileged exclusive register | 加载-获取非特权独占寄存器 | `LDATXR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDATXR <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `LDAXP` | Load-acquire exclusive pair of registers | 加载-获取独占寄存器对 | `LDAXP <Wt1>, <Wt2>, [<Xn\|SP>{, #0}]`<br>`LDAXP <Xt1>, <Xt2>, [<Xn\|SP>{, #0}]` | — |
| `LDAXR` | Load-acquire exclusive register | 加载-获取独占寄存器 | `LDAXR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDAXR <Xt>, [<Xn\|SP>{, #0}]` | — |
| `LDAXRB` | Load-acquire exclusive register byte | 加载-获取独占寄存器字节 | `LDAXRB <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LDAXRH` | Load-acquire exclusive register halfword | 加载-获取独占寄存器半字 | `LDAXRH <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LDCLR, LDCLRA, LDCLRAL, LDCLRL` | Atomic bit clear on word or doubleword | 原子位清零（字或双字） | `LDCLR <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLR <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDCLRA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDCLRAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDCLRL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB` | Atomic bit clear on byte | 原子位清零（字节） | `LDCLRB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH` | Atomic bit clear on halfword | 原子位清零（半字） | `LDCLRH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDCLRLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDCLRP, LDCLRPA, LDCLRPAL, LDCLRPL` | Atomic bit clear on quadword | 原子位清零（四字） | `LDCLRP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDCLRPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDCLRPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDCLRPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_LSE128 |
| `LDEOR, LDEORA, LDEORAL, LDEORL` | Atomic exclusive-OR on word or doubleword | 原子按位异或（字或双字） | `LDEOR <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEOR <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDEORA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDEORAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDEORL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDEORB, LDEORAB, LDEORALB, LDEORLB` | Atomic exclusive-OR on byte | 原子按位异或（字节） | `LDEORB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDEORH, LDEORAH, LDEORALH, LDEORLH` | Atomic exclusive-OR on halfword | 原子按位异或（半字） | `LDEORH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDEORLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDG` | Load Allocation Tag | 加载内存分配标签 | `LDG <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_MTE |
| `LDGM` | Load tag multiple | 批量加载内存标签 | `LDGM <Xt>, [<Xn\|SP>]` | FEAT_MTE2 |
| `LDIAPP` | Load-Acquire RCpc ordered pair of registers | 加载-获取 RCpc 有序寄存器对 | `LDIAPP <Wt1>, <Wt2>, [<Xn\|SP>], #8`<br>`LDIAPP <Wt1>, <Wt2>, [<Xn\|SP>]`<br>`LDIAPP <Xt1>, <Xt2>, [<Xn\|SP>], #16`<br>`LDIAPP <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_LRCPC3 |
| `LDLAR` | Load LOAcquire register | LOAcquire 加载寄存器 | `LDLAR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDLAR <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `LDLARB` | Load LOAcquire register byte | LOAcquire 加载寄存器字节 | `LDLARB <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `LDLARH` | Load LOAcquire register halfword | LOAcquire 加载寄存器半字 | `LDLARH <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `LDNP` | Load pair of registers, with non-temporal hint | 加载寄存器对（非临时提示） | `LDNP <Wt1>, <Wt2>, [<Xn\|SP>{, #<imm>}]`<br>`LDNP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | — |
| `LDP` | Load pair of registers | 加载寄存器对 | `LDP <Wt1>, <Wt2>, [<Xn\|SP>], #<imm>`<br>`LDP <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`LDP <Wt1>, <Wt2>, [<Xn\|SP>, #<imm>]!`<br>`LDP <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`LDP <Wt1>, <Wt2>, [<Xn\|SP>{, #<imm>}]`<br>`LDP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | — |
| `LDPSW` | Load pair of registers signed word | 加载有符号字寄存器对 | `LDPSW <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`LDPSW <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`LDPSW <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | — |
| `LDR (immediate)` | Load register (immediate) | 加载寄存器（立即数偏移） | `LDR <Wt>, [<Xn\|SP>], #<simm>`<br>`LDR <Xt>, [<Xn\|SP>], #<simm>`<br>`LDR <Wt>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Xt>, [<Xn\|SP>, #<simm>]!`<br>`LDR <Wt>, [<Xn\|SP>{, #<pimm>}]`<br>`LDR <Xt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDR (literal)` | Load register (literal) | 加载寄存器（PC 相对字面量） | `LDR <Wt>, <label>`<br>`LDR <Xt>, <label>` | — |
| `LDR (register)` | Load register (register) | 加载寄存器（寄存器偏移） | `LDR <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`LDR <Xt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `LDRAA, LDRAB` | Load register, with pointer authentication | 带指针认证的加载寄存器 | `LDRAA <Xt>, [<Xn\|SP>{, #<simm>}]`<br>`LDRAA <Xt>, [<Xn\|SP>{, #<simm>}]!`<br>`LDRAB <Xt>, [<Xn\|SP>{, #<simm>}]`<br>`LDRAB <Xt>, [<Xn\|SP>{, #<simm>}]!` | FEAT_PAuth |
| `LDRB (immediate)` | Load register byte (immediate) | 加载字节寄存器（立即数偏移） | `LDRB <Wt>, [<Xn\|SP>], #<simm>`<br>`LDRB <Wt>, [<Xn\|SP>, #<simm>]!`<br>`LDRB <Wt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDRB (register)` | Load register byte (register) | 加载字节寄存器（寄存器偏移） | `LDRB <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`LDRB <Wt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]` | — |
| `LDRH (immediate)` | Load register halfword (immediate) | 加载半字寄存器（立即数偏移） | `LDRH <Wt>, [<Xn\|SP>], #<simm>`<br>`LDRH <Wt>, [<Xn\|SP>, #<simm>]!`<br>`LDRH <Wt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDRH (register)` | Load register halfword (register) | 加载半字寄存器（寄存器偏移） | `LDRH <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `LDRSB (immediate)` | Load register signed byte (immediate) | 加载有符号字节寄存器（立即数偏移） | `LDRSB <Wt>, [<Xn\|SP>], #<simm>`<br>`LDRSB <Xt>, [<Xn\|SP>], #<simm>`<br>`LDRSB <Wt>, [<Xn\|SP>, #<simm>]!`<br>`LDRSB <Xt>, [<Xn\|SP>, #<simm>]!`<br>`LDRSB <Wt>, [<Xn\|SP>{, #<pimm>}]`<br>`LDRSB <Xt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDRSB (register)` | Load register signed byte (register) | 加载有符号字节寄存器（寄存器偏移） | `LDRSB <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`LDRSB <Wt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]`<br>`LDRSB <Xt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`LDRSB <Xt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]` | — |
| `LDRSH (immediate)` | Load register signed halfword (immediate) | 加载有符号半字寄存器（立即数偏移） | `LDRSH <Wt>, [<Xn\|SP>], #<simm>`<br>`LDRSH <Xt>, [<Xn\|SP>], #<simm>`<br>`LDRSH <Wt>, [<Xn\|SP>, #<simm>]!`<br>`LDRSH <Xt>, [<Xn\|SP>, #<simm>]!`<br>`LDRSH <Wt>, [<Xn\|SP>{, #<pimm>}]`<br>`LDRSH <Xt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDRSH (register)` | Load register signed halfword (register) | 加载有符号半字寄存器（寄存器偏移） | `LDRSH <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`LDRSH <Xt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `LDRSW (immediate)` | Load register signed word (immediate) | 加载有符号字寄存器（立即数偏移） | `LDRSW <Xt>, [<Xn\|SP>], #<simm>`<br>`LDRSW <Xt>, [<Xn\|SP>, #<simm>]!`<br>`LDRSW <Xt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `LDRSW (literal)` | Load register signed word (literal) | 加载有符号字寄存器（PC 相对字面量） | `LDRSW <Xt>, <label>` | — |
| `LDRSW (register)` | Load register signed word (register) | 加载有符号字寄存器（寄存器偏移） | `LDRSW <Xt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `LDSET, LDSETA, LDSETAL, LDSETL` | Atomic bit set on word or doubleword | 原子位置位（字或双字） | `LDSET <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSET <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSETA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSETAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSETL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSETB, LDSETAB, LDSETALB, LDSETLB` | Atomic bit set on byte | 原子位置位（字节） | `LDSETB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSETH, LDSETAH, LDSETALH, LDSETLH` | Atomic bit set on halfword | 原子位置位（半字） | `LDSETH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSETLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSETP, LDSETPA, LDSETPAL, LDSETPL` | Atomic bit set on quadword | 原子位置位（四字） | `LDSETP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDSETPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDSETPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`LDSETPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_LSE128 |
| `LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL` | Atomic signed maximum on word or doubleword | 原子有符号最大值（字或双字） | `LDSMAX <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAX <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMAXA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMAXAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMAXL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB` | Atomic signed maximum on byte | 原子有符号最大值（字节） | `LDSMAXB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH` | Atomic signed maximum on halfword | 原子有符号最大值（半字） | `LDSMAXH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMAXLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSMIN, LDSMINA, LDSMINAL, LDSMINL` | Atomic signed minimum on word or doubleword | 原子有符号最小值（字或双字） | `LDSMIN <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMIN <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMINA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMINAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDSMINL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB` | Atomic signed minimum on byte | 原子有符号最小值（字节） | `LDSMINB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH` | Atomic signed minimum on halfword | 原子有符号最小值（半字） | `LDSMINH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDSMINLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDTADD, LDTADDA, LDTADDAL, LDTADDL` | Atomic add unprivileged | 原子非特权加法 | `LDTADD <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTADDA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTADDAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTADDL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTADD <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTADDA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTADDAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTADDL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSUI |
| `LDTCLR, LDTCLRA, LDTCLRAL, LDTCLRL` | Atomic bit clear unprivileged | 原子位清零（非特权模式） | `LDTCLR <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTCLRA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTCLRAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTCLRL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTCLR <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTCLRA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTCLRAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTCLRL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSUI |
| `LDTNP` | Load unprivileged pair of registers, with non-temporal hint | 加载非特权寄存器对（非临时提示） | `LDTNP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_LSUI |
| `LDTP` | Load unprivileged pair of registers | 加载非特权寄存器对 | `LDTP <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`LDTP <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`LDTP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_LSUI |
| `LDTR` | Load register (unprivileged) | 加载寄存器（非特权模式） | `LDTR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDTR <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTRB` | Load register byte (unprivileged) | 加载字节寄存器（非特权模式） | `LDTRB <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTRH` | Load register halfword (unprivileged) | 加载半字寄存器（非特权模式） | `LDTRH <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTRSB` | Load register signed byte (unprivileged) | 加载有符号字节寄存器（非特权模式） | `LDTRSB <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDTRSB <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTRSH` | Load register signed halfword (unprivileged) | 加载有符号半字寄存器（非特权模式） | `LDTRSH <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDTRSH <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTRSW` | Load register signed word (unprivileged) | 加载有符号字寄存器（非特权模式） | `LDTRSW <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDTSET, LDTSETA, LDTSETAL, LDTSETL` | Atomic bit set unprivileged | 原子位置位（非特权模式） | `LDTSET <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTSETA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTSETAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTSETL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDTSET <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTSETA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTSETAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDTSETL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSUI |
| `LDTXR` | Load unprivileged exclusive register | 加载非特权独占寄存器 | `LDTXR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDTXR <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL` | Atomic unsigned maximum on word or doubleword | 原子无符号最大值操作（字或双字） | `LDUMAX <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAX <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMAXA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMAXAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMAXL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB` | Atomic unsigned maximum on byte | 原子无符号最大值操作（字节） | `LDUMAXB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH` | Atomic unsigned maximum on halfword | 原子无符号最大值操作（半字） | `LDUMAXH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMAXLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUMIN, LDUMINA, LDUMINAL, LDUMINL` | Atomic unsigned minimum on word or doubleword | 原子无符号最小值操作（字或双字） | `LDUMIN <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINA <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINL <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMIN <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMINA <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMINAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`LDUMINL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB` | Atomic unsigned minimum on byte | 原子无符号最小值操作（字节） | `LDUMINB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH` | Atomic unsigned minimum on halfword | 原子无符号最小值操作（半字） | `LDUMINH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`LDUMINLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `LDUR` | Load register (unscaled) | 加载寄存器（非对齐偏移） | `LDUR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDUR <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDURB` | Load register byte (unscaled) | 加载字节寄存器（非对齐偏移） | `LDURB <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDURH` | Load register halfword (unscaled) | 加载半字寄存器（非对齐偏移） | `LDURH <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDURSB` | Load register signed byte (unscaled) | 加载有符号字节寄存器（非对齐偏移） | `LDURSB <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDURSB <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDURSH` | Load register signed halfword (unscaled) | 加载有符号半字寄存器（非对齐偏移） | `LDURSH <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`LDURSH <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDURSW` | Load register signed word (unscaled) | 加载有符号字寄存器（非对齐偏移） | `LDURSW <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `LDXP` | Load exclusive pair of registers | 加载独占寄存器对 | `LDXP <Wt1>, <Wt2>, [<Xn\|SP>{, #0}]`<br>`LDXP <Xt1>, <Xt2>, [<Xn\|SP>{, #0}]` | — |
| `LDXR` | Load exclusive register | 加载独占寄存器 | `LDXR <Wt>, [<Xn\|SP>{, #0}]`<br>`LDXR <Xt>, [<Xn\|SP>{, #0}]` | — |
| `LDXRB` | Load exclusive register byte | 加载独占字节寄存器 | `LDXRB <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LDXRH` | Load exclusive register halfword | 加载独占半字寄存器 | `LDXRH <Wt>, [<Xn\|SP>{, #0}]` | — |
| `LSL (immediate)` | Logical shift left (immediate): an alias of UBFM | 立即数逻辑左移（UBFM 的别名） | `LSL <Wd>, <Wn>, #<shift>`<br>`LSL <Xd>, <Xn>, #<shift>` | — |
| `LSL (register)` | Logical shift left (register): an alias of LSLV | 寄存器逻辑左移（LSLV 的别名） | `LSL <Wd>, <Wn>, <Wm>`<br>`LSL <Xd>, <Xn>, <Xm>` | — |
| `LSLV` | Logical shift left variable | 可变逻辑左移 | `LSLV <Wd>, <Wn>, <Wm>`<br>`LSLV <Xd>, <Xn>, <Xm>` | — |
| `LSR (immediate)` | Logical shift right (immediate): an alias of UBFM | 立即数逻辑右移（UBFM 的别名） | `LSR <Wd>, <Wn>, #<shift>`<br>`LSR <Xd>, <Xn>, #<shift>` | — |
| `LSR (register)` | Logical shift right (register): an alias of LSRV | 寄存器逻辑右移（LSRV 的别名） | `LSR <Wd>, <Wn>, <Wm>`<br>`LSR <Xd>, <Xn>, <Xm>` | — |
| `LSRV` | Logical shift right variable | 可变逻辑右移 | `LSRV <Wd>, <Wn>, <Wm>`<br>`LSRV <Xd>, <Xn>, <Xm>` | — |
| `MADD` | Multiply-add | 乘加运算 | `MADD <Wd>, <Wn>, <Wm>, <Wa>`<br>`MADD <Xd>, <Xn>, <Xm>, <Xa>` | — |
| `MADDPT` | Multiply-add checked pointer | 带检查指针的乘加运算 | `MADDPT <Xd>, <Xn>, <Xm>, <Xa>` | FEAT_CPA |
| `MNEG` | Multiply-negate: an alias of MSUB | 乘法取反（MSUB 的别名） | `MNEG <Wd>, <Wn>, <Wm>`<br>`MNEG <Xd>, <Xn>, <Xm>` | — |
| `MOV (bitmask immediate)` | Move bitmask immediate value: an alias of ORR (immediate) | 移动位掩码立即数（ORR 立即数的别名） | `MOV <Wd\|WSP>, #<imm>`<br>`MOV <Xd\|SP>, #<imm>` | — |
| `MOV (inverted wide immediate)` | Move inverted wide immediate value: an alias of MOVN | 移动反转宽立即数（MOVN 的别名） | `MOV <Wd>, #<imm>`<br>`MOV <Xd>, #<imm>` | — |
| `MOV (register)` | Move register value: an alias of ORR (shifted register) | 移动寄存器值（ORR 移位寄存器的别名） | `MOV <Wd>, <Wm>`<br>`MOV <Xd>, <Xm>` | — |
| `MOV (to/from SP)` | Move register value to or from SP: an alias of ADD (immediate) | 寄存器与 SP 之间移动值（ADD 立即数的别名） | `MOV <Wd\|WSP>, <Wn\|WSP>`<br>`MOV <Xd\|SP>, <Xn\|SP>` | — |
| `MOV (wide immediate)` | Move wide immediate value: an alias of MOVZ | 移动宽立即数（MOVZ 的别名） | `MOV <Wd>, #<imm>`<br>`MOV <Xd>, #<imm>` | — |
| `MOVK` | Move wide with keep | 带保留的宽立即数移动 | `MOVK <Wd>, #<imm>{, LSL #<shift>}`<br>`MOVK <Xd>, #<imm>{, LSL #<shift>}` | — |
| `MOVN` | Move wide with NOT | 带取反的宽立即数移动 | `MOVN <Wd>, #<imm>{, LSL #<shift>}`<br>`MOVN <Xd>, #<imm>{, LSL #<shift>}` | — |
| `MOVZ` | Move wide with zero | 带零扩展的宽立即数移动 | `MOVZ <Wd>, #<imm>{, LSL #<shift>}`<br>`MOVZ <Xd>, #<imm>{, LSL #<shift>}` | — |
| `MRRS` | Move System register to two adjacent general-purpose registers | 将系统寄存器移动到两个相邻通用寄存器 | `MRRS <Xt>, <Xt+1>, (<systemreg>\|S<op0>_<op1>_<Cn>_<Cm>_<op2>)` | FEAT_SYSREG128 |
| `MRS` | Move System register to general-purpose register | 将系统寄存器移动到通用寄存器 | `MRS <Xt>, (<systemreg>\|S<op0>_<op1>_<Cn>_<Cm>_<op2>)` | — |
| `MSR (immediate)` | Move immediate value to special register | 将立即数移动到特殊寄存器 | `MSR <pstatefield>, #<imm>` | FEAT_DIT, FEAT_EBEP, FEAT_MTE, FEAT_NMI, FEAT_PAN, FEAT_SME, FEAT_SSBS, FEAT_UAO |
| `MSR (register)` | Move general-purpose register to System register | 将通用寄存器移动到系统寄存器 | `MSR (<systemreg>\|S<op0>_<op1>_<Cn>_<Cm>_<op2>), <Xt>` | — |
| `MSRR` | Move two adjacent general-purpose registers to System register | 将两个相邻通用寄存器移动到系统寄存器 | `MSRR (<systemreg>\|S<op0>_<op1>_<Cn>_<Cm>_<op2>), <Xt>, <Xt+1>` | FEAT_SYSREG128 |
| `MSUB` | Multiply-subtract | 乘减运算 | `MSUB <Wd>, <Wn>, <Wm>, <Wa>`<br>`MSUB <Xd>, <Xn>, <Xm>, <Xa>` | — |
| `MSUBPT` | Multiply-subtract checked pointer | 带检查指针的乘减运算 | `MSUBPT <Xd>, <Xn>, <Xm>, <Xa>` | FEAT_CPA |
| `MUL` | Multiply: an alias of MADD | 乘法（MADD 的别名） | `MUL <Wd>, <Wn>, <Wm>`<br>`MUL <Xd>, <Xn>, <Xm>` | — |
| `MVN` | Bitwise NOT: an alias of ORN (shifted register) | 按位取反（ORN 移位寄存器的别名） | `MVN <Wd>, <Wm>{, <shift> #<amount>}`<br>`MVN <Xd>, <Xm>{, <shift> #<amount>}` | — |
| `NEG (shifted register)` | Negate (shifted register): an alias of SUB (shifted register) | 取反（移位寄存器）（SUB 移位寄存器的别名） | `NEG <Wd>, <Wm>{, <shift> #<amount>}`<br>`NEG <Xd>, <Xm>{, <shift> #<amount>}` | — |
| `NEGS` | Negate, setting flags: an alias of SUBS (shifted register) | 取反并设置标志位（SUBS 移位寄存器的别名） | `NEGS <Wd>, <Wm>{, <shift> #<amount>}`<br>`NEGS <Xd>, <Xm>{, <shift> #<amount>}` | — |
| `NGC` | Negate with carry: an alias of SBC | 带进位取反（SBC 的别名） | `NGC <Wd>, <Wm>`<br>`NGC <Xd>, <Xm>` | — |
| `NGCS` | Negate with carry, setting flags: an alias of SBCS | 带进位取反并设置标志位（SBCS 的别名） | `NGCS <Wd>, <Wm>`<br>`NGCS <Xd>, <Xm>` | — |
| `NOP` | No operation | 空操作 | `NOP` | — |
| `ORN (shifted register)` | Bitwise OR NOT (shifted register) | 按位 OR NOT（移位寄存器） | `ORN <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`ORN <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `ORR (immediate)` | Bitwise OR (immediate) | 按位 OR（立即数） | `ORR <Wd\|WSP>, <Wn>, #<imm>`<br>`ORR <Xd\|SP>, <Xn>, #<imm>` | — |
| `ORR (shifted register)` | Bitwise OR (shifted register) | 按位 OR（移位寄存器） | `ORR <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`ORR <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `PACDA, PACDZA` | Pointer Authentication Code for data address, using key A | 为数据地址生成指针认证码（密钥 A） | `PACDA <Xd>, <Xn\|SP>`<br>`PACDZA <Xd>` | FEAT_PAuth |
| `PACDB, PACDZB` | Pointer Authentication Code for data address, using key B | 为数据地址生成指针认证码（密钥 B） | `PACDB <Xd>, <Xn\|SP>`<br>`PACDZB <Xd>` | FEAT_PAuth |
| `PACGA` | Pointer Authentication Code, using generic key | 使用通用密钥生成指针认证码 | `PACGA <Xd>, <Xn>, <Xm\|SP>` | FEAT_PAuth |
| `PACIA, PACIA1716, PACIASP, PACIAZ, PACIZA` | Pointer Authentication Code for instruction address, using key A | 为指令地址生成指针认证码（密钥 A） | `PACIA <Xd>, <Xn\|SP>`<br>`PACIZA <Xd>`<br>`PACIA1716`<br>`PACIASP`<br>`PACIAZ` | FEAT_PAuth |
| `PACIA171615` | Pointer Authentication Code for instruction address, using key A | 为指令地址生成指针认证码（密钥 A） | `PACIA171615` | FEAT_PAuth_LR |
| `PACIASPPC` | Pointer Authentication Code for return address, using key A | 为返回地址生成指针认证码（密钥 A） | `PACIASPPC` | FEAT_PAuth_LR |
| `PACIB, PACIB1716, PACIBSP, PACIBZ, PACIZB` | Pointer Authentication Code for instruction address, using key B | 为指令地址生成指针认证码（密钥 B） | `PACIB <Xd>, <Xn\|SP>`<br>`PACIZB <Xd>`<br>`PACIB1716`<br>`PACIBSP`<br>`PACIBZ` | FEAT_PAuth |
| `PACIB171615` | Pointer Authentication Code for instruction address, using key B | 为指令地址生成指针认证码（密钥 B） | `PACIB171615` | FEAT_PAuth_LR |
| `PACIBSPPC` | Pointer Authentication Code for return address, using key B | 为返回地址生成指针认证码（密钥 B） | `PACIBSPPC` | FEAT_PAuth_LR |
| `PACM` | Pointer authentication modifier | 指针认证修饰符 | `PACM` | FEAT_PAuth_LR |
| `PACNBIASPPC` | Pointer Authentication Code for return address, using key A, not a branch target | 为返回地址生成指针认证码（密钥 A，非分支目标） | `PACNBIASPPC` | FEAT_PAuth_LR |
| `PACNBIBSPPC` | Pointer Authentication Code for return address, using key B, not a branch target | 为返回地址生成指针认证码（密钥 B，非分支目标） | `PACNBIBSPPC` | FEAT_PAuth_LR |
| `PRFM (immediate)` | Prefetch memory (immediate) | 预取内存（立即数偏移） | `PRFM (<prfop>\|#<imm5>), [<Xn\|SP>{, #<pimm>}]` | FEAT_PCDPHINT, FEAT_PRFMSLC |
| `PRFM (literal)` | Prefetch memory (literal) | 预取内存（字面量） | `PRFM (<prfop>\|#<imm5>), <label>` | FEAT_PRFMSLC |
| `PRFM (register)` | Prefetch memory (register) | 预取内存（寄存器偏移） | `PRFM (<prfop>\|#<imm5>), [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | FEAT_PRFMSLC |
| `PRFUM` | Prefetch memory (unscaled offset) | 预取内存（非对齐偏移） | `PRFUM (<prfop>\|#<imm5>), [<Xn\|SP>{, #<simm>}]` | FEAT_PRFMSLC |
| `PSB` | Profiling synchronization barrier | 性能分析同步屏障 | `PSB CSYNC` | FEAT_SPE |
| `PSSBB` | Physical speculative store bypass barrier: an alias of DSB | 物理推测性存储绕过屏障（DSB 的别名） | `PSSBB` | — |
| `RBIT` | Reverse bits | 按位翻转 | `RBIT <Wd>, <Wn>`<br>`RBIT <Xd>, <Xn>` | — |
| `RCWCAS, RCWCASA, RCWCASAL, RCWCASL` | Read check write compare and swap doubleword in memory | 读检写比较并交换双字（内存） | `RCWCAS <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCASA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCASAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCASL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWCASP, RCWCASPA, RCWCASPAL, RCWCASPL` | Read check write compare and swap quadword in memory | 读检写比较并交换四字（内存） | `RCWCASP <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWCASPA <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWCASPAL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWCASPL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWCLR, RCWCLRA, RCWCLRAL, RCWCLRL` | Read check write atomic bit clear on doubleword in memory | 读检写原子位清零（双字，内存） | `RCWCLR <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCLRA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCLRAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWCLRL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWCLRP, RCWCLRPA, RCWCLRPAL, RCWCLRPL` | Read check write atomic bit clear on quadword in memory | 读检写原子位清零（四字，内存） | `RCWCLRP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWCLRPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWCLRPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWCLRPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSCAS, RCWSCASA, RCWSCASAL, RCWSCASL` | Read check write software compare and swap doubleword in memory | 读检写软件比较并交换双字（内存） | `RCWSCAS <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCASA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCASAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCASL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSCASP, RCWSCASPA, RCWSCASPAL, RCWSCASPL` | Read check write software compare and swap quadword in memory | 读检写软件比较并交换四字（内存） | `RCWSCASP <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWSCASPA <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWSCASPAL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]`<br>`RCWSCASPL <Xs>, <X(s+1)>, <Xt>, <X(t+1)>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSCLR, RCWSCLRA, RCWSCLRAL, RCWSCLRL` | Read check write software atomic bit clear on doubleword in memory | 读检写软件原子位清零（双字，内存） | `RCWSCLR <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCLRA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCLRAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSCLRL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSCLRP, RCWSCLRPA, RCWSCLRPAL, RCWSCLRPL` | Read check write software atomic bit clear on quadword in memory | 读检写软件原子位清零（四字，内存） | `RCWSCLRP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSCLRPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSCLRPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSCLRPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSET, RCWSETA, RCWSETAL, RCWSETL` | Read check write atomic bit set on doubleword in memory | 读检写原子位置位（双字，内存） | `RCWSET <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSETA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSETAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSETL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSETP, RCWSETPA, RCWSETPAL, RCWSETPL` | Read check write atomic bit set on quadword in memory | 读检写原子位置位（四字，内存） | `RCWSETP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSETPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSETPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSETPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSSET, RCWSSETA, RCWSSETAL, RCWSSETL` | Read check write software atomic bit set on doubleword in memory | 读检写软件原子位置位（双字，内存） | `RCWSSET <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSETA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSETAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSETL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSSETP, RCWSSETPA, RCWSSETPAL, RCWSSETPL` | Read check write software atomic bit set on quadword in memory | 读检写软件原子位置位（四字，内存） | `RCWSSETP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSETPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSETPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSETPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSSWP, RCWSSWPA, RCWSSWPAL, RCWSSWPL` | Read check write software swap doubleword in memory | 读检写软件交换双字（内存） | `RCWSSWP <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSWPA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSWPAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSSWPL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSSWPP, RCWSSWPPA, RCWSSWPPAL, RCWSSWPPL` | Read check write software swap quadword in memory | 读检写软件交换四字（内存） | `RCWSSWPP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSWPPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSWPPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSSWPPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RCWSWP, RCWSWPA, RCWSWPAL, RCWSWPL` | Read check write swap doubleword in memory | 读检写交换双字（内存） | `RCWSWP <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSWPA <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSWPAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`RCWSWPL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_THE |
| `RCWSWPP, RCWSWPPA, RCWSWPPAL, RCWSWPPL` | Read check write swap quadword in memory | 读检写交换四字（内存） | `RCWSWPP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSWPPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSWPPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`RCWSWPPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_D128, FEAT_THE |
| `RET` | Return from subroutine | 从子程序返回 | `RET {<Xn>}` | — |
| `RETAA, RETAB` | Return from subroutine, with pointer authentication | 从子程序返回（带指针认证） | `RETAA`<br>`RETAB` | FEAT_PAuth |
| `RETAASPPC, RETABSPPC` | Return from subroutine, with enhanced pointer authentication using an immediate offset | 从子程序返回（增强指针认证，立即数偏移） | `RETAASPPC <label>`<br>`RETABSPPC <label>` | FEAT_PAuth_LR |
| `RETAASPPCR, RETABSPPCR` | Return from subroutine, with enhanced pointer authentication using a register | 从子程序返回（增强指针认证，寄存器偏移） | `RETAASPPCR <Xm>`<br>`RETABSPPCR <Xm>` | FEAT_PAuth_LR |
| `REV` | Reverse bytes | 字节序翻转 | `REV <Wd>, <Wn>`<br>`REV <Xd>, <Xn>` | — |
| `REV16` | Reverse bytes in 16-bit halfwords | 在 16 位半字内翻转字节序 | `REV16 <Wd>, <Wn>`<br>`REV16 <Xd>, <Xn>` | — |
| `REV32` | Reverse bytes in 32-bit words | 在 32 位字内翻转字节序 | `REV32 <Xd>, <Xn>` | — |
| `REV64` | Reverse bytes: an alias of REV | 64 位字节序翻转（REV 的别名） | `REV64 <Xd>, <Xn>` | — |
| `RMIF` | Rotate, mask insert flags | 循环移位并掩码插入标志位 | `RMIF <Xn>, #<shift>, #<mask>` | FEAT_FlagM |
| `ROR (immediate)` | Rotate right (immediate): an alias of EXTR | 立即数循环右移（EXTR 的别名） | `ROR <Wd>, <Ws>, #<shift>`<br>`ROR <Xd>, <Xs>, #<shift>` | — |
| `ROR (register)` | Rotate right (register): an alias of RORV | 寄存器循环右移（RORV 的别名） | `ROR <Wd>, <Wn>, <Wm>`<br>`ROR <Xd>, <Xn>, <Xm>` | — |
| `RORV` | Rotate right variable | 可变循环右移 | `RORV <Wd>, <Wn>, <Wm>`<br>`RORV <Xd>, <Xn>, <Xm>` | — |
| `RPRFM` | Range prefetch memory | 范围预取内存 | `RPRFM (<rprfop>\|#<imm6>), <Xm>, [<Xn\|SP>]` | FEAT_RPRFM |
| `SB` | Speculation barrier | 推测屏障 | `SB` | FEAT_SB |
| `SBC` | Subtract with carry | 带进位减法 | `SBC <Wd>, <Wn>, <Wm>`<br>`SBC <Xd>, <Xn>, <Xm>` | — |
| `SBCS` | Subtract with carry, setting flags | 带进位减法并设置标志位 | `SBCS <Wd>, <Wn>, <Wm>`<br>`SBCS <Xd>, <Xn>, <Xm>` | — |
| `SBFIZ` | Signed bitfield insert in zeros: an alias of SBFM | 有符号位域插零（SBFM 的别名） | `SBFIZ <Wd>, <Wn>, #<lsb>, #<width>`<br>`SBFIZ <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `SBFM` | Signed bitfield move | 有符号位域移动 | `SBFM <Wd>, <Wn>, #<immr>, #<imms>`<br>`SBFM <Xd>, <Xn>, #<immr>, #<imms>` | — |
| `SBFX` | Signed bitfield extract: an alias of SBFM | 有符号位域提取（SBFM 的别名） | `SBFX <Wd>, <Wn>, #<lsb>, #<width>`<br>`SBFX <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `SDIV (quotient)` | Signed divide | 有符号除法（取商） | `SDIV <Wd>, <Wn>, <Wm>`<br>`SDIV <Xd>, <Xn>, <Xm>` | — |
| `SETF8, SETF16` | Evaluation of 8-bit or 16-bit flag values | 评估 8 位或 16 位标志值 | `SETF8 <Wn>`<br>`SETF16 <Wn>` | FEAT_FlagM |
| `SETGP, SETGM, SETGE` | Memory set with tag setting | 带标签设置的内存清零 | `SETGP [<Xd>]!, <Xn>!, <Xs>`<br>`SETGM [<Xd>]!, <Xn>!, <Xs>`<br>`SETGE [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS, FEAT_MTE |
| `SETGPN, SETGMN, SETGEN` | Memory set with tag setting, non-temporal | 带标签设置的内存清零（非临时） | `SETGPN [<Xd>]!, <Xn>!, <Xs>`<br>`SETGMN [<Xd>]!, <Xn>!, <Xs>`<br>`SETGEN [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS, FEAT_MTE |
| `SETGPT, SETGMT, SETGET` | Memory set with tag setting, unprivileged | 带标签设置的内存清零（非特权模式） | `SETGPT [<Xd>]!, <Xn>!, <Xs>`<br>`SETGMT [<Xd>]!, <Xn>!, <Xs>`<br>`SETGET [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS, FEAT_MTE |
| `SETGPTN, SETGMTN, SETGETN` | Memory set with tag setting, unprivileged and non-temporal | 带标签设置的内存填充（非特权、非临时） | `SETGPTN [<Xd>]!, <Xn>!, <Xs>`<br>`SETGMTN [<Xd>]!, <Xn>!, <Xs>`<br>`SETGETN [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS, FEAT_MTE |
| `SETP, SETM, SETE` | Memory set | 内存填充 | `SETP [<Xd>]!, <Xn>!, <Xs>`<br>`SETM [<Xd>]!, <Xn>!, <Xs>`<br>`SETE [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS |
| `SETPN, SETMN, SETEN` | Memory set, non-temporal | 内存填充（非临时） | `SETPN [<Xd>]!, <Xn>!, <Xs>`<br>`SETMN [<Xd>]!, <Xn>!, <Xs>`<br>`SETEN [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS |
| `SETPT, SETMT, SETET` | Memory set, unprivileged | 内存填充（非特权） | `SETPT [<Xd>]!, <Xn>!, <Xs>`<br>`SETMT [<Xd>]!, <Xn>!, <Xs>`<br>`SETET [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS |
| `SETPTN, SETMTN, SETETN` | Memory set, unprivileged and non-temporal | 内存填充（非特权、非临时） | `SETPTN [<Xd>]!, <Xn>!, <Xs>`<br>`SETMTN [<Xd>]!, <Xn>!, <Xs>`<br>`SETETN [<Xd>]!, <Xn>!, <Xs>` | FEAT_MOPS |
| `SEV` | Send event | 发送事件至所有 PE | `SEV` | — |
| `SEVL` | Send event local | 发送本地事件 | `SEVL` | — |
| `SMADDL` | Signed multiply-add long | 有符号乘加长（32×32+64→64） | `SMADDL <Xd>, <Wn>, <Wm>, <Xa>` | — |
| `SMAX (immediate)` | Signed maximum (immediate) | 有符号最大值（立即数） | `SMAX <Wd>, <Wn>, #<simm>`<br>`SMAX <Xd>, <Xn>, #<simm>` | FEAT_CSSC |
| `SMAX (register)` | Signed maximum (register) | 有符号最大值（寄存器） | `SMAX <Wd>, <Wn>, <Wm>`<br>`SMAX <Xd>, <Xn>, <Xm>` | FEAT_CSSC |
| `SMC` | Secure monitor call | 安全监控调用 | `SMC #<imm>` | — |
| `SMIN (immediate)` | Signed minimum (immediate) | 有符号最小值（立即数） | `SMIN <Wd>, <Wn>, #<simm>`<br>`SMIN <Xd>, <Xn>, #<simm>` | FEAT_CSSC |
| `SMIN (register)` | Signed minimum (register) | 有符号最小值（寄存器） | `SMIN <Wd>, <Wn>, <Wm>`<br>`SMIN <Xd>, <Xn>, <Xm>` | FEAT_CSSC |
| `SMNEGL` | Signed multiply-negate long: an alias of SMSUBL | 有符号乘负长（SMSUBL 的别名） | `SMNEGL <Xd>, <Wn>, <Wm>` | — |
| `SMSTART` | Enable access to Streaming SVE mode and SME architectural state: an alias of MSR (immediate) | 启用 Streaming SVE 模式及 SME 架构状态（MSR immediate 的别名） | `SMSTART {<option>}` | FEAT_SME |
| `SMSTOP` | Disable access to Streaming SVE mode and SME architectural state: an alias of MSR (immediate) | 禁用 Streaming SVE 模式及 SME 架构状态（MSR immediate 的别名） | `SMSTOP {<option>}` | FEAT_SME |
| `SMSUBL` | Signed multiply-subtract long | 有符号乘减长（32×32 后减 64→64） | `SMSUBL <Xd>, <Wn>, <Wm>, <Xa>` | — |
| `SMULH` | Signed multiply high | 有符号乘高位（64×64→高 64 位） | `SMULH <Xd>, <Xn>, <Xm>` | — |
| `SMULL (32-bit)` | Signed multiply long: an alias of SMADDL | 有符号乘长（SMADDL 的别名） | `SMULL <Xd>, <Wn>, <Wm>` | — |
| `SSBB` | Speculative store bypass barrier: an alias of DSB | 推测存储绕过屏障（DSB 的别名） | `SSBB` | — |
| `ST2G` | Store Allocation Tags | 存储两个分配标签 | `ST2G <Xt\|SP>, [<Xn\|SP>], #<simm>`<br>`ST2G <Xt\|SP>, [<Xn\|SP>, #<simm>]!`<br>`ST2G <Xt\|SP>, [<Xn\|SP>{, #<simm>}]` | FEAT_MTE |
| `ST64B` | Single-copy atomic 64-byte store without status result | 单拷贝原子 64 字节存储（无状态结果） | `ST64B <Xt>, [<Xn\|SP> {, #0}]` | FEAT_LS64 |
| `ST64BV` | Single-copy atomic 64-byte store with status result | 单拷贝原子 64 字节存储（有状态结果） | `ST64BV <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LS64_V |
| `ST64BV0` | Single-copy atomic 64-byte EL0 store with status result | 单拷贝原子 64 字节 EL0 存储（有状态结果） | `ST64BV0 <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LS64_ACCDATA |
| `STADD, STADDL` | Atomic add on word or doubleword, without return: an alias of LDADD, LDADDA, LDADDAL, LDADDL | 原子加字或双字（无返回，LDADD 系列的别名） | `STADD <Ws>, [<Xn\|SP>]`<br>`STADDL <Ws>, [<Xn\|SP>]`<br>`STADD <Xs>, [<Xn\|SP>]`<br>`STADDL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STADDB, STADDLB` | Atomic add on byte, without return: an alias of LDADDB, LDADDAB, LDADDALB, LDADDLB | 原子加字节（无返回，LDADDB 系列的别名） | `STADDB <Ws>, [<Xn\|SP>]`<br>`STADDLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STADDH, STADDLH` | Atomic add on halfword, without return: an alias of LDADDH, LDADDAH, LDADDALH, LDADDLH | 原子加半字（无返回，LDADDH 系列的别名） | `STADDH <Ws>, [<Xn\|SP>]`<br>`STADDLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STCLR, STCLRL` | Atomic bit clear on word or doubleword, without return: an alias of LDCLR, LDCLRA, LDCLRAL, LDCLRL | 原子位清除字或双字（无返回，LDCLR 系列的别名） | `STCLR <Ws>, [<Xn\|SP>]`<br>`STCLRL <Ws>, [<Xn\|SP>]`<br>`STCLR <Xs>, [<Xn\|SP>]`<br>`STCLRL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STCLRB, STCLRLB` | Atomic bit clear on byte, without return: an alias of LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB | 原子位清除字节（无返回，LDCLRB 系列的别名） | `STCLRB <Ws>, [<Xn\|SP>]`<br>`STCLRLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STCLRH, STCLRLH` | Atomic bit clear on halfword, without return: an alias of LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH | 原子位清除半字（无返回，LDCLRH 系列的别名） | `STCLRH <Ws>, [<Xn\|SP>]`<br>`STCLRLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STEOR, STEORL` | Atomic exclusive-OR on word or doubleword, without return: an alias of LDEOR, LDEORA, LDEORAL, LDEORL | 原子异或字或双字（无返回，LDEOR 系列的别名） | `STEOR <Ws>, [<Xn\|SP>]`<br>`STEORL <Ws>, [<Xn\|SP>]`<br>`STEOR <Xs>, [<Xn\|SP>]`<br>`STEORL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STEORB, STEORLB` | Atomic exclusive-OR on byte, without return: an alias of LDEORB, LDEORAB, LDEORALB, LDEORLB | 原子异或字节（无返回，LDEORB 系列的别名） | `STEORB <Ws>, [<Xn\|SP>]`<br>`STEORLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STEORH, STEORLH` | Atomic exclusive-OR on halfword, without return: an alias of LDEORH, LDEORAH, LDEORALH, LDEORLH | 原子异或半字（无返回，LDEORH 系列的别名） | `STEORH <Ws>, [<Xn\|SP>]`<br>`STEORLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STG` | Store Allocation Tag | 存储单个分配标签 | `STG <Xt\|SP>, [<Xn\|SP>], #<simm>`<br>`STG <Xt\|SP>, [<Xn\|SP>, #<simm>]!`<br>`STG <Xt\|SP>, [<Xn\|SP>{, #<simm>}]` | FEAT_MTE |
| `STGM` | Store Allocation Tag multiple | 存储多个分配标签 | `STGM <Xt>, [<Xn\|SP>]` | FEAT_MTE2 |
| `STGP` | Store Allocation Tag and pair of registers | 存储分配标签及一对寄存器 | `STGP <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`STGP <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`STGP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_MTE |
| `STILP` | Store-release ordered pair of registers | 有序存储释放一对寄存器 | `STILP <Wt1>, <Wt2>, [<Xn\|SP>, #-8]!`<br>`STILP <Wt1>, <Wt2>, [<Xn\|SP>]`<br>`STILP <Xt1>, <Xt2>, [<Xn\|SP>, #-16]!`<br>`STILP <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_LRCPC3 |
| `STLLR` | Store LORelease register | LORelease 存储寄存器 | `STLLR <Wt>, [<Xn\|SP>{, #0}]`<br>`STLLR <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `STLLRB` | Store LORelease register byte | LORelease 存储寄存器字节 | `STLLRB <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `STLLRH` | Store LORelease register halfword | LORelease 存储寄存器半字 | `STLLRH <Wt>, [<Xn\|SP>{, #0}]` | FEAT_LOR |
| `STLR` | Store-release register | 存储释放寄存器 | `STLR <Wt>, [<Xn\|SP>{, #0}]`<br>`STLR <Xt>, [<Xn\|SP>{, #0}]`<br>`STLR <Wt>, [<Xn\|SP>, #-4]!`<br>`STLR <Xt>, [<Xn\|SP>, #-8]!` | FEAT_LRCPC3 |
| `STLRB` | Store-release register byte | 存储释放寄存器字节 | `STLRB <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STLRH` | Store-release register halfword | 存储释放寄存器半字 | `STLRH <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STLTXR` | Store-release unprivileged exclusive register | 存储释放非特权独占寄存器 | `STLTXR <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`STLTXR <Ws>, <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `STLUR` | Store-release register (unscaled) | 存储释放寄存器（非对齐偏移） | `STLUR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`STLUR <Xt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `STLURB` | Store-release register byte (unscaled) | 存储释放寄存器字节（非对齐偏移） | `STLURB <Wt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `STLURH` | Store-release register halfword (unscaled) | 存储释放寄存器半字（非对齐偏移） | `STLURH <Wt>, [<Xn\|SP>{, #<simm>}]` | FEAT_LRCPC2 |
| `STLXP` | Store-release exclusive pair of registers | 存储释放独占一对寄存器 | `STLXP <Ws>, <Wt1>, <Wt2>, [<Xn\|SP>{, #0}]`<br>`STLXP <Ws>, <Xt1>, <Xt2>, [<Xn\|SP>{, #0}]` | — |
| `STLXR` | Store-release exclusive register | 存储释放独占寄存器 | `STLXR <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`STLXR <Ws>, <Xt>, [<Xn\|SP>{, #0}]` | — |
| `STLXRB` | Store-release exclusive register byte | 存储释放独占寄存器字节 | `STLXRB <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STLXRH` | Store-release exclusive register halfword | 存储释放独占寄存器半字 | `STLXRH <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STNP` | Store pair of registers, with non-temporal hint | 存储一对寄存器（非临时提示） | `STNP <Wt1>, <Wt2>, [<Xn\|SP>{, #<imm>}]`<br>`STNP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | — |
| `STP` | Store pair of registers | 存储一对寄存器 | `STP <Wt1>, <Wt2>, [<Xn\|SP>], #<imm>`<br>`STP <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`STP <Wt1>, <Wt2>, [<Xn\|SP>, #<imm>]!`<br>`STP <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`STP <Wt1>, <Wt2>, [<Xn\|SP>{, #<imm>}]`<br>`STP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | — |
| `STR (immediate)` | Store register (immediate) | 存储寄存器（立即数偏移） | `STR <Wt>, [<Xn\|SP>], #<simm>`<br>`STR <Xt>, [<Xn\|SP>], #<simm>`<br>`STR <Wt>, [<Xn\|SP>, #<simm>]!`<br>`STR <Xt>, [<Xn\|SP>, #<simm>]!`<br>`STR <Wt>, [<Xn\|SP>{, #<pimm>}]`<br>`STR <Xt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `STR (register)` | Store register (register) | 存储寄存器（寄存器偏移） | `STR <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]`<br>`STR <Xt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `STRB (immediate)` | Store register byte (immediate) | 存储寄存器字节（立即数偏移） | `STRB <Wt>, [<Xn\|SP>], #<simm>`<br>`STRB <Wt>, [<Xn\|SP>, #<simm>]!`<br>`STRB <Wt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `STRB (register)` | Store register byte (register) | 存储寄存器字节（寄存器偏移） | `STRB <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>), <extend> {<amount>}]`<br>`STRB <Wt>, [<Xn\|SP>, <Xm>{, LSL <amount>}]` | — |
| `STRH (immediate)` | Store register halfword (immediate) | 存储寄存器半字（立即数偏移） | `STRH <Wt>, [<Xn\|SP>], #<simm>`<br>`STRH <Wt>, [<Xn\|SP>, #<simm>]!`<br>`STRH <Wt>, [<Xn\|SP>{, #<pimm>}]` | — |
| `STRH (register)` | Store register halfword (register) | 存储寄存器半字（寄存器偏移） | `STRH <Wt>, [<Xn\|SP>, (<Wm>\|<Xm>){, <extend> {<amount>}}]` | — |
| `STSET, STSETL` | Atomic bit set on word or doubleword, without return: an alias of LDSET, LDSETA, LDSETAL, LDSETL | 原子位置位字或双字（无返回，LDSET 系列的别名） | `STSET <Ws>, [<Xn\|SP>]`<br>`STSETL <Ws>, [<Xn\|SP>]`<br>`STSET <Xs>, [<Xn\|SP>]`<br>`STSETL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STSETB, STSETLB` | Atomic bit set on byte, without return: an alias of LDSETB, LDSETAB, LDSETALB, LDSETLB | 原子位置位字节（无返回，LDSETB 系列的别名） | `STSETB <Ws>, [<Xn\|SP>]`<br>`STSETLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STSETH, STSETLH` | Atomic bit set on halfword, without return: an alias of LDSETH, LDSETAH, LDSETALH, LDSETLH | 原子位置位半字（无返回，LDSETH 系列的别名） | `STSETH <Ws>, [<Xn\|SP>]`<br>`STSETLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STSHH` | Store shared hint | 存储共享提示 | `STSHH <policy>` | FEAT_PCDPHINT |
| `STSMAX, STSMAXL` | Atomic signed maximum on word or doubleword, without return: an alias of LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL | 原子有符号最大值字或双字（无返回，LDSMAX 系列的别名） | `STSMAX <Ws>, [<Xn\|SP>]`<br>`STSMAXL <Ws>, [<Xn\|SP>]`<br>`STSMAX <Xs>, [<Xn\|SP>]`<br>`STSMAXL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STSMAXB, STSMAXLB` | Atomic signed maximum on byte, without return: an alias of LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB | 原子有符号最大值字节（无返回，LDSMAXB 系列的别名） | `STSMAXB <Ws>, [<Xn\|SP>]`<br>`STSMAXLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STSMAXH, STSMAXLH` | Atomic signed maximum on halfword, without return: an alias of LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH | 原子有符号最大值半字（无返回，LDSMAXH 系列的别名） | `STSMAXH <Ws>, [<Xn\|SP>]`<br>`STSMAXLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STSMIN, STSMINL` | Atomic signed minimum on word or doubleword, without return: an alias of LDSMIN, LDSMINA, LDSMINAL, LDSMINL | 原子有符号最小值字或双字（无返回，LDSMIN 系列的别名） | `STSMIN <Ws>, [<Xn\|SP>]`<br>`STSMINL <Ws>, [<Xn\|SP>]`<br>`STSMIN <Xs>, [<Xn\|SP>]`<br>`STSMINL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STSMINB, STSMINLB` | Atomic signed minimum on byte, without return: an alias of LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB | 原子有符号最小值字节（无返回，LDSMINB 系列的别名） | `STSMINB <Ws>, [<Xn\|SP>]`<br>`STSMINLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STSMINH, STSMINLH` | Atomic signed minimum on halfword, without return: an alias of LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH | 原子有符号最小值半字（无返回，LDSMINH 系列的别名） | `STSMINH <Ws>, [<Xn\|SP>]`<br>`STSMINLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STTADD, STTADDL` | Atomic add unprivileged, without return: an alias of LDTADD, LDTADDA, LDTADDAL, LDTADDL | 非特权原子加（无返回，LDTADD 系列的别名） | `STTADD <Ws>, [<Xn\|SP>]`<br>`STTADDL <Ws>, [<Xn\|SP>]`<br>`STTADD <Xs>, [<Xn\|SP>]`<br>`STTADDL <Xs>, [<Xn\|SP>]` | FEAT_LSUI |
| `STTCLR, STTCLRL` | Atomic bit clear unprivileged, without return: an alias of LDTCLR, LDTCLRA, LDTCLRAL, LDTCLRL | 非特权原子位清除（无返回，LDTCLR 系列的别名） | `STTCLR <Ws>, [<Xn\|SP>]`<br>`STTCLRL <Ws>, [<Xn\|SP>]`<br>`STTCLR <Xs>, [<Xn\|SP>]`<br>`STTCLRL <Xs>, [<Xn\|SP>]` | FEAT_LSUI |
| `STTNP` | Store unprivileged pair of registers, with non-temporal hint | 存储非特权一对寄存器（非临时提示） | `STTNP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_LSUI |
| `STTP` | Store unprivileged pair of registers | 存储非特权一对寄存器 | `STTP <Xt1>, <Xt2>, [<Xn\|SP>], #<imm>`<br>`STTP <Xt1>, <Xt2>, [<Xn\|SP>, #<imm>]!`<br>`STTP <Xt1>, <Xt2>, [<Xn\|SP>{, #<imm>}]` | FEAT_LSUI |
| `STTR` | Store register (unprivileged) | 存储寄存器（非特权） | `STTR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`STTR <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STTRB` | Store register byte (unprivileged) | 存储寄存器字节（非特权） | `STTRB <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STTRH` | Store register halfword (unprivileged) | 存储寄存器半字（非特权） | `STTRH <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STTSET, STTSETL` | Atomic bit set unprivileged, without return: an alias of LDTSET, LDTSETA, LDTSETAL, LDTSETL | 非特权原子位置位（无返回，LDTSET 系列的别名） | `STTSET <Ws>, [<Xn\|SP>]`<br>`STTSETL <Ws>, [<Xn\|SP>]`<br>`STTSET <Xs>, [<Xn\|SP>]`<br>`STTSETL <Xs>, [<Xn\|SP>]` | FEAT_LSUI |
| `STTXR` | Store unprivileged exclusive register | 存储非特权独占寄存器 | `STTXR <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`STTXR <Ws>, <Xt>, [<Xn\|SP>{, #0}]` | FEAT_LSUI |
| `STUMAX, STUMAXL` | Atomic unsigned maximum on word or doubleword, without return: an alias of LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL | 原子无符号最大值字或双字（无返回，LDUMAX 系列的别名） | `STUMAX <Ws>, [<Xn\|SP>]`<br>`STUMAXL <Ws>, [<Xn\|SP>]`<br>`STUMAX <Xs>, [<Xn\|SP>]`<br>`STUMAXL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STUMAXB, STUMAXLB` | Atomic unsigned maximum on byte, without return: an alias of LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB | 原子无符号最大值字节（无返回，LDUMAXB 系列的别名） | `STUMAXB <Ws>, [<Xn\|SP>]`<br>`STUMAXLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STUMAXH, STUMAXLH` | Atomic unsigned maximum on halfword, without return: an alias of LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH | 原子无符号最大值半字（无返回，LDUMAXH 系列的别名） | `STUMAXH <Ws>, [<Xn\|SP>]`<br>`STUMAXLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STUMIN, STUMINL` | Atomic unsigned minimum on word or doubleword, without return: an alias of LDUMIN, LDUMINA, LDUMINAL, LDUMINL | 原子无符号最小值字或双字（无返回，LDUMIN 系列的别名） | `STUMIN <Ws>, [<Xn\|SP>]`<br>`STUMINL <Ws>, [<Xn\|SP>]`<br>`STUMIN <Xs>, [<Xn\|SP>]`<br>`STUMINL <Xs>, [<Xn\|SP>]` | FEAT_LSE |
| `STUMINB, STUMINLB` | Atomic unsigned minimum on byte, without return: an alias of LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB | 原子无符号最小值字节（无返回，LDUMINB 系列的别名） | `STUMINB <Ws>, [<Xn\|SP>]`<br>`STUMINLB <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STUMINH, STUMINLH` | Atomic unsigned minimum on halfword, without return: an alias of LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH | 原子无符号最小值半字（无返回，LDUMINH 系列的别名） | `STUMINH <Ws>, [<Xn\|SP>]`<br>`STUMINLH <Ws>, [<Xn\|SP>]` | FEAT_LSE |
| `STUR` | Store register (unscaled) | 存储寄存器（非对齐偏移） | `STUR <Wt>, [<Xn\|SP>{, #<simm>}]`<br>`STUR <Xt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STURB` | Store register byte (unscaled) | 存储寄存器字节（非对齐偏移） | `STURB <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STURH` | Store register halfword (unscaled) | 存储寄存器半字（非对齐偏移） | `STURH <Wt>, [<Xn\|SP>{, #<simm>}]` | — |
| `STXP` | Store exclusive pair of registers | 存储独占一对寄存器 | `STXP <Ws>, <Wt1>, <Wt2>, [<Xn\|SP>{, #0}]`<br>`STXP <Ws>, <Xt1>, <Xt2>, [<Xn\|SP>{, #0}]` | — |
| `STXR` | Store exclusive register | 存储独占寄存器 | `STXR <Ws>, <Wt>, [<Xn\|SP>{, #0}]`<br>`STXR <Ws>, <Xt>, [<Xn\|SP>{, #0}]` | — |
| `STXRB` | Store exclusive register byte | 存储独占寄存器字节 | `STXRB <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STXRH` | Store exclusive register halfword | 存储独占寄存器半字 | `STXRH <Ws>, <Wt>, [<Xn\|SP>{, #0}]` | — |
| `STZ2G` | Store Allocation Tags, zeroing | 存储两个分配标签并清零内存 | `STZ2G <Xt\|SP>, [<Xn\|SP>], #<simm>`<br>`STZ2G <Xt\|SP>, [<Xn\|SP>, #<simm>]!`<br>`STZ2G <Xt\|SP>, [<Xn\|SP>{, #<simm>}]` | FEAT_MTE |
| `STZG` | Store Allocation Tag, zeroing | 存储单个分配标签并清零内存 | `STZG <Xt\|SP>, [<Xn\|SP>], #<simm>`<br>`STZG <Xt\|SP>, [<Xn\|SP>, #<simm>]!`<br>`STZG <Xt\|SP>, [<Xn\|SP>{, #<simm>}]` | FEAT_MTE |
| `STZGM` | Store Allocation Tag and zero multiple | 存储多个分配标签并清零内存 | `STZGM <Xt>, [<Xn\|SP>]` | FEAT_MTE2 |
| `SUB (extended register)` | Subtract extended and scaled register | 减法（扩展并缩放寄存器） | `SUB <Wd\|WSP>, <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`SUB <Xd\|SP>, <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `SUB (immediate)` | Subtract immediate value | 减法（立即数） | `SUB <Wd\|WSP>, <Wn\|WSP>, #<imm>{, <shift>}`<br>`SUB <Xd\|SP>, <Xn\|SP>, #<imm>{, <shift>}` | — |
| `SUB (shifted register)` | Subtract optionally-shifted register | 减法（可选移位寄存器） | `SUB <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`SUB <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `SUBG` | Subtract with tag | 带标签的减法 | `SUBG <Xd\|SP>, <Xn\|SP>, #<uimm6>, #<uimm4>` | FEAT_MTE |
| `SUBP` | Subtract pointer | 指针相减 | `SUBP <Xd>, <Xn\|SP>, <Xm\|SP>` | FEAT_MTE |
| `SUBPS` | Subtract pointer, setting flags | 指针相减并设置标志位 | `SUBPS <Xd>, <Xn\|SP>, <Xm\|SP>` | FEAT_MTE |
| `SUBPT` | Subtract checked pointer | 带检查的指针相减 | `SUBPT <Xd\|SP>, <Xn\|SP>, <Xm>{, LSL #<amount>}` | FEAT_CPA |
| `SUBS (extended register)` | Subtract extended and scaled register, setting flags | 减法并设置标志位（扩展并缩放寄存器） | `SUBS <Wd>, <Wn\|WSP>, <Wm>{, <extend> {#<amount>}}`<br>`SUBS <Xd>, <Xn\|SP>, <R><m>{, <extend> {#<amount>}}` | — |
| `SUBS (immediate)` | Subtract immediate value, setting flags | 减法并设置标志位（立即数） | `SUBS <Wd>, <Wn\|WSP>, #<imm>{, <shift>}`<br>`SUBS <Xd>, <Xn\|SP>, #<imm>{, <shift>}` | — |
| `SUBS (shifted register)` | Subtract optionally-shifted register, setting flags | 减法并设置标志位（可选移位寄存器） | `SUBS <Wd>, <Wn>, <Wm>{, <shift> #<amount>}`<br>`SUBS <Xd>, <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `SVC` | Supervisor call | 管理员调用（系统调用） | `SVC #<imm>` | — |
| `SWP, SWPA, SWPAL, SWPL` | Swap word or doubleword in memory | 原子交换字或双字 | `SWP <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPA <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPL <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWP <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPA <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSE |
| `SWPB, SWPAB, SWPALB, SWPLB` | Swap byte in memory | 原子交换字节 | `SWPB <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPAB <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPALB <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPLB <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `SWPH, SWPAH, SWPALH, SWPLH` | Swap halfword in memory | 原子交换半字 | `SWPH <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPAH <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPALH <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPLH <Ws>, <Wt>, [<Xn\|SP>]` | FEAT_LSE |
| `SWPP, SWPPA, SWPPAL, SWPPL` | Swap quadword in memory | 原子交换四字（128 位） | `SWPP <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`SWPPA <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`SWPPAL <Xt1>, <Xt2>, [<Xn\|SP>]`<br>`SWPPL <Xt1>, <Xt2>, [<Xn\|SP>]` | FEAT_LSE128 |
| `SWPT, SWPTA, SWPTAL, SWPTL` | Swap unprivileged | 非特权原子交换 | `SWPT <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPTA <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPTAL <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPTL <Ws>, <Wt>, [<Xn\|SP>]`<br>`SWPT <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPTA <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPTAL <Xs>, <Xt>, [<Xn\|SP>]`<br>`SWPTL <Xs>, <Xt>, [<Xn\|SP>]` | FEAT_LSUI |
| `SXTB` | Signed extend byte: an alias of SBFM | 有符号字节扩展（SBFM 的别名） | `SXTB <Wd>, <Wn>`<br>`SXTB <Xd>, <Wn>` | — |
| `SXTH` | Sign extend halfword: an alias of SBFM | 有符号半字扩展（SBFM 的别名） | `SXTH <Wd>, <Wn>`<br>`SXTH <Xd>, <Wn>` | — |
| `SXTW` | Sign extend word: an alias of SBFM | 有符号字扩展（SBFM 的别名） | `SXTW <Xd>, <Wn>` | — |
| `SYS` | System instruction | 系统指令 | `SYS #<op1>, <Cn>, <Cm>, #<op2>{, <Xt>}` | — |
| `SYSL` | System instruction with result | 带返回值的系统指令 | `SYSL <Xt>, #<op1>, <Cn>, <Cm>, #<op2>` | — |
| `SYSP` | 128-bit system instruction | 128 位系统指令 | `SYSP #<op1>, <Cn>, <Cm>, #<op2>{, <Xt1>, <Xt2>}` | FEAT_SYSINSTR128 |
| `TBNZ` | Test bit and branch if nonzero | 测试位非零则跳转 | `TBNZ <R><t>, #<imm>, <label>` | — |
| `TBZ` | Test bit and branch if zero | 测试位为零则跳转 | `TBZ <R><t>, #<imm>, <label>` | — |
| `TLBI` | TLB invalidate operation: an alias of SYS | TLB 无效化操作（SYS 的别名） | `TLBI <tlbi_op>{, <Xt>}` | FEAT_RME, FEAT_TLBIOS, FEAT_TLBIRANGE, FEAT_TLBIW, FEAT_XS |
| `TLBIP` | TLB invalidate pair operation: an alias of SYSP | TLB 无效化配对操作（SYSP 的别名） | `TLBIP <tlbip_op>{, <Xt1>, <Xt2>}` | FEAT_D128, FEAT_SYSINSTR128 |
| `TRCIT` | Trace instrumentation: an alias of SYS | 跟踪插桩（SYS 的别名） | `TRCIT <Xt>` | FEAT_ITE |
| `TSB` | Trace synchronization barrier | 跟踪同步屏障 | `TSB CSYNC` | FEAT_TRF |
| `TST (immediate)` | Test bits (immediate): an alias of ANDS (immediate) | 按位测试（立即数）（ANDS 立即数的别名） | `TST <Wn>, #<imm>`<br>`TST <Xn>, #<imm>` | — |
| `TST (shifted register)` | Test (shifted register): an alias of ANDS (shifted register) | 按位测试（移位寄存器）（ANDS 移位寄存器的别名） | `TST <Wn>, <Wm>{, <shift> #<amount>}`<br>`TST <Xn>, <Xm>{, <shift> #<amount>}` | — |
| `UBFIZ` | Unsigned bitfield insert in zeros: an alias of UBFM | 无符号位域插入零（UBFM 的别名） | `UBFIZ <Wd>, <Wn>, #<lsb>, #<width>`<br>`UBFIZ <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `UBFM` | Unsigned bitfield move | 无符号位域移动 | `UBFM <Wd>, <Wn>, #<immr>, #<imms>`<br>`UBFM <Xd>, <Xn>, #<immr>, #<imms>` | — |
| `UBFX` | Unsigned bitfield extract: an alias of UBFM | 无符号位域提取（UBFM 的别名） | `UBFX <Wd>, <Wn>, #<lsb>, #<width>`<br>`UBFX <Xd>, <Xn>, #<lsb>, #<width>` | — |
| `UDF` | Permanently undefined | 永久未定义指令 | `UDF #<imm>` | — |
| `UDIV (quotient)` | Unsigned divide | 无符号除法（取商） | `UDIV <Wd>, <Wn>, <Wm>`<br>`UDIV <Xd>, <Xn>, <Xm>` | — |
| `UMADDL` | Unsigned multiply-add long | 无符号乘加长（32位×32位+64位→64位） | `UMADDL <Xd>, <Wn>, <Wm>, <Xa>` | — |
| `UMAX (immediate)` | Unsigned maximum (immediate) | 无符号最大值（立即数） | `UMAX <Wd>, <Wn>, #<uimm>`<br>`UMAX <Xd>, <Xn>, #<uimm>` | FEAT_CSSC |
| `UMAX (register)` | Unsigned maximum (register) | 无符号最大值（寄存器） | `UMAX <Wd>, <Wn>, <Wm>`<br>`UMAX <Xd>, <Xn>, <Xm>` | FEAT_CSSC |
| `UMIN (immediate)` | Unsigned minimum (immediate) | 无符号最小值（立即数） | `UMIN <Wd>, <Wn>, #<uimm>`<br>`UMIN <Xd>, <Xn>, #<uimm>` | FEAT_CSSC |
| `UMIN (register)` | Unsigned minimum (register) | 无符号最小值（寄存器） | `UMIN <Wd>, <Wn>, <Wm>`<br>`UMIN <Xd>, <Xn>, <Xm>` | FEAT_CSSC |
| `UMNEGL` | Unsigned multiply-negate long: an alias of UMSUBL | 无符号乘法取负长（UMSUBL 的别名） | `UMNEGL <Xd>, <Wn>, <Wm>` | — |
| `UMSUBL` | Unsigned multiply-subtract long | 无符号乘减长（32位×32位，64位减） | `UMSUBL <Xd>, <Wn>, <Wm>, <Xa>` | — |
| `UMULH` | Unsigned multiply high | 无符号乘法高位结果 | `UMULH <Xd>, <Xn>, <Xm>` | — |
| `UMULL (32-bit)` | Unsigned multiply long: an alias of UMADDL | 无符号乘法长（UMADDL 的别名） | `UMULL <Xd>, <Wn>, <Wm>` | — |
| `UXTB` | Unsigned extend byte: an alias of UBFM | 无符号字节零扩展（UBFM 的别名） | `UXTB <Wd>, <Wn>` | — |
| `UXTH` | Unsigned extend halfword: an alias of UBFM | 无符号半字零扩展（UBFM 的别名） | `UXTH <Wd>, <Wn>` | — |
| `WFE` | Wait for event | 等待事件 | `WFE` | — |
| `WFET` | Wait for event with timeout | 带超时的等待事件 | `WFET <Xt>` | FEAT_WFxT |
| `WFI` | Wait for interrupt | 等待中断 | `WFI` | — |
| `WFIT` | Wait for interrupt with timeout | 带超时的等待中断 | `WFIT <Xt>` | FEAT_WFxT |
| `XAFLAG` | Convert floating-point condition flags from external format to Arm format | 将浮点条件标志从外部格式转换为 Arm 格式 | `XAFLAG` | FEAT_FlagM2 |
| `XPACD, XPACI, XPACLRI` | Strip Pointer Authentication Code | 去除指针认证码（PAC） | `XPACD <Xd>`<br>`XPACI <Xd>`<br>`XPACLRI` | FEAT_PAuth |
| `YIELD` | Yield | 让出处理器提示 | `YIELD` | — |

