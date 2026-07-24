# 类别级转换模板（按需 Read）

SKILL.md 速查表 30 条覆盖最高频；本文档按类别给出**模板和易错点**，覆盖更广。
任何 intrinsic 不确定时，先查 SKILL.md → 再 `lookup.py` → 再读本文件对应类别段。

---

## 1. Load / Store

### 关键认知

- SVE 所有 load/store 都要传 `svbool_t pg` 谓词控制激活元素
- 全活跃 `svptrue_b32()`（按元素宽度 _b8/_b16/_b32/_b64）= 等价 AVX2 full load
- 内存对齐：x86 区分 `_load_` / `_loadu_`；SVE 只有一种 `svld1_*`，硬件不要求对齐（VL=256 时 32B 对齐仍推荐）

### 模板

```c
// AVX2
__m256i v = _mm256_loadu_si256((const __m256i*)ptr);
__m256i w = _mm256_load_si256((const __m256i*)ptr_aligned);
_mm256_storeu_si256((__m256i*)out, v);

// SVE (VL=256, 8 x int32)
svbool_t pg = svptrue_b32();
svint32_t v = svld1_s32(pg, (const int32_t*)ptr);
svint32_t w = svld1_s32(pg, (const int32_t*)ptr_aligned);
svst1_s32(pg, (int32_t*)out, v);
```

### 元素类型映射

| AVX2 后缀 | SVE 函数后缀 | 谓词 |
|---|---|---|
| `_epi8`  / `_si256→i8` | `_s8` 或 `_u8` | `svptrue_b8()` |
| `_epi16` / `_si256→i16` | `_s16` / `_u16` | `svptrue_b16()` |
| `_epi32` / `_si256→i32` | `_s32` / `_u32` | `svptrue_b32()` |
| `_epi64` / `_si256→i64` | `_s64` / `_u64` | `svptrue_b64()` |
| `_ps` | `_f32` | `svptrue_b32()` |
| `_pd` | `_f64` | `svptrue_b64()` |

### 半向量 (`__m128i`)

```c
// AVX2
__m128i v = _mm_loadu_si128((const __m128i*)ptr);   // 4 x int32

// SVE — 用 svptrue_pat_b32(SV_VL4) 谓词限制只激活前 4 个 lane
svbool_t pg4 = svptrue_pat_b32(SV_VL4);
svint32_t v = svld1_s32(pg4, (const int32_t*)ptr);
```

### maskload / maskstore（HIGH-RISK）

x86 `_mm256_maskload_epi32(p, mask)`：mask 是 i32 向量，最高位为 1 时加载该 lane。
SVE 需要把"向量 mask"转成 `svbool_t`：

```c
// AVX2
__m256i mask = ...;
__m256i v = _mm256_maskload_epi32((const int*)p, mask);

// SVE
svint32_t mask_v = ...;
svbool_t  pg_mask = svcmplt_s32(svptrue_b32(), mask_v, svdup_s32(0));  // 最高位=1 等价于 < 0
svint32_t v = svld1_s32(pg_mask, (const int32_t*)p);
// 未激活 lane SVE 默认为 0，与 maskload 行为一致
```

---

## 2. Arithmetic

### 关键认知

- SVE 算术运算大多有 `_m`/`_x`/`_z` 三种谓词版本：
  - `_m` (merge): 未激活 lane 保留 op1 原值
  - `_x` (don't care): 未激活 lane 值未定义，**最快，默认用这个**
  - `_z` (zero): 未激活 lane 清零
- 全活跃情况下 `_x` 与 `_m`/`_z` 结果相同，但 `_x` 编译器优化空间最大

### 模板

```c
// AVX2
__m256i s = _mm256_add_epi32(a, b);
__m256i d = _mm256_sub_epi32(a, b);
__m256i m = _mm256_mullo_epi32(a, b);
__m256i mn = _mm256_min_epi32(a, b);
__m256i mx = _mm256_max_epi32(a, b);

// SVE
svbool_t pg = svptrue_b32();
svint32_t s  = svadd_s32_x(pg, a, b);
svint32_t d  = svsub_s32_x(pg, a, b);
svint32_t m  = svmul_s32_x(pg, a, b);
svint32_t mn = svmin_s32_x(pg, a, b);
svint32_t mx = svmax_s32_x(pg, a, b);
```

### 64-bit 乘法

x86 `_mm256_mullo_epi64` 仅 AVX-512 有；SVE 直接支持：
```c
svint64_t r = svmul_s64_x(svptrue_b64(), a, b);
```

### 浮点 FMA

```c
// AVX2
__m256 r = _mm256_fmadd_ps(a, b, c);   // a*b + c

// SVE
svfloat32_t r = svmla_f32_x(svptrue_b32(), c, a, b);
// 注意参数顺序：svmla(pg, acc, op1, op2) 计算 acc + op1*op2
```

---

## 3. Logical

```c
// AVX2
__m256i x = _mm256_and_si256(a, b);
__m256i o = _mm256_or_si256(a, b);
__m256i e = _mm256_xor_si256(a, b);
__m256i n = _mm256_andnot_si256(a, b);   // ~a & b

// SVE
svbool_t pg = svptrue_b32();
svint32_t x = svand_s32_x(pg, a, b);
svint32_t o = svorr_s32_x(pg, a, b);
svint32_t e = sveor_s32_x(pg, a, b);
svint32_t n = svbic_s32_x(pg, b, a);     // ⚠️ 操作数反了：svbic = op1 & ~op2
```

`svbic` 是 BIT CLEAR：`b & ~a`，刚好对应 AVX2 `andnot(a,b) = ~a & b`。**注意参数顺序**。

---

## 4. Compare（HIGH-RISK，返回类型变了）

### 关键认知

- **AVX2 cmp 返回 `__m256i` 向量**（-1 / 0 mask）
- **SVE cmp 返回 `svbool_t` 谓词**（不是向量）
- 这意味着所有"用 cmp 结果作为下游 and/or 输入"的代码必须改写

### 直接对应

```c
// AVX2
__m256i eq = _mm256_cmpeq_epi32(a, b);
__m256i gt = _mm256_cmpgt_epi32(a, b);

// SVE — 返回 svbool_t
svbool_t pg = svptrue_b32();
svbool_t eq = svcmpeq_s32(pg, a, b);
svbool_t gt = svcmpgt_s32(pg, a, b);
```

### 把谓词当 mask 用（最常见的下游模式）

```c
// AVX2 模式：用 cmp 结果选值
__m256i cmp = _mm256_cmpeq_epi32(a, b);
__m256i sel = _mm256_and_si256(cmp, x);   // x where eq, 0 elsewhere

// SVE 改写
svbool_t cmp = svcmpeq_s32(svptrue_b32(), a, b);
svint32_t sel = svsel_s32(cmp, x, svdup_s32(0));  // x where cmp true, 0 elsewhere
```

### 谓词转回 mask 向量（少用，避免）

```c
// 偶尔需要的：把 svbool_t 转回 -1/0 向量
svint32_t mask_vec = svsel_s32(cmp, svdup_s32(-1), svdup_s32(0));
```

---

## 5. Broadcast / Set

```c
// AVX2
__m256i s = _mm256_set1_epi32(42);
__m256i z = _mm256_setzero_si256();

// SVE
svint32_t s = svdup_s32(42);
svint32_t z = svdup_s32(0);
```

### `_mm256_set_epi32(e7,e6,...,e0)` — 没有单指令对应

```c
// AVX2
__m256i v = _mm256_set_epi32(7,6,5,4,3,2,1,0);

// SVE — 用栈数组 + ld1
int32_t tmp[8] = {0,1,2,3,4,5,6,7};
svint32_t v = svld1_s32(svptrue_b32(), tmp);
```

或用 `svindex` 生成等差序列：
```c
svint32_t v = svindex_s32(0, 1);   // {0,1,2,3,4,5,6,7}
```

---

## 6. Shift

```c
// AVX2
__m256i a = _mm256_slli_epi32(x, 5);
__m256i b = _mm256_srli_epi32(x, 5);    // logical right
__m256i c = _mm256_srai_epi32(x, 5);    // arithmetic right

// SVE
svbool_t pg = svptrue_b32();
svint32_t a = svlsl_n_s32_x(pg, x, 5);
svint32_t b = svreinterpret_s32_u32(
    svlsr_n_u32_x(pg, svreinterpret_u32_s32(x), 5));  // logical 需先转 unsigned
svint32_t c = svasr_n_s32_x(pg, x, 5);
```

### Variable shift

```c
// AVX2 (var per lane)
__m256i r = _mm256_sllv_epi32(x, count);

// SVE
svint32_t r = svlsl_s32_x(pg, x, svreinterpret_u32_s32(count));
```

---

## 7. Shuffle / Permute（HIGH-RISK，必须 lookup.py）

### 核心区别

- AVX2 shuffle 几乎都是"按 128-bit lane 内"的（VPSHUFB、VPSHUFD），跨 lane 操作要用 `permute2x128` / `permute4x64`
- SVE 没有"lane"概念，整个向量平坦；shuffle 主要用 `svtbl` (table lookup)

### `_mm256_shuffle_epi8` → svtbl

```c
// AVX2
__m256i idx = _mm256_setr_epi8(0,2,4,6, 8,10,12,14, ...);
__m256i r = _mm256_shuffle_epi8(data, idx);
// 注意：AVX2 这条是 lane-内 shuffle，每 16 字节独立

// SVE — svtbl 跨整个向量
svuint8_t r = svtbl_u8(svreinterpret_u8_s8(data), svreinterpret_u8_s8(idx));
// ⚠️ 行为差异：svtbl 是全向量索引，不分 lane！
// 如果原代码依赖 lane-内语义，需特殊处理：把 idx 加上 lane 偏移
```

### `_mm256_permute4x64_epi64`

```c
// AVX2 — 按 64-bit 块重排
__m256i r = _mm256_permute4x64_epi64(a, _MM_SHUFFLE(3,1,2,0));

// SVE
svuint64_t idx = svdupq_n_u64(0, 2, 1, 3);  // 注意 SVE dupq 也只覆盖前 128 bit
// VL=256 时需要 8 个元素的索引：
uint64_t tmp[4] = {0, 2, 1, 3};
svuint64_t idx = svld1_u64(svptrue_b64(), tmp);
svuint64_t r = svtbl_u64(svreinterpret_u64_s64(a), idx);
```

### `_mm256_alignr_epi8` (concat shift)

```c
// AVX2
__m256i r = _mm256_alignr_epi8(a, b, 4);  // ((a:b) >> 4 bytes) 低 32B

// SVE — svext
svint8_t r = svext_s8(svreinterpret_s8(b), svreinterpret_s8(a), 4);
// svext(a, b, n) = (b 在右、a 在左 的拼接) 取从位置 n 起的 VL bytes
```

---

## 8. Movemask（HIGH-RISK，常需重构控制流）

`_mm256_movemask_epi8` 把 32 字节的最高位打包成 32-bit int。SVE 没有直接对应。

### 用途模式 1：`if (mask != 0)` — 任一字节非零

```c
// AVX2
int mask = _mm256_movemask_epi8(v);
if (mask != 0) { ... }

// SVE — 用 svptest_any
svbool_t hi = svcmplt_s8(svptrue_b8(), v, svdup_s8(0));  // 最高位 = 1 等价 < 0
if (svptest_any(svptrue_b8(), hi)) { ... }
```

### 用途模式 2：`__builtin_popcount(mask)` — 计算 1 的个数

```c
// AVX2
int cnt = __builtin_popcount(_mm256_movemask_epi8(v));

// SVE
svbool_t hi = svcmplt_s8(svptrue_b8(), v, svdup_s8(0));
uint64_t cnt = svcntp_b8(svptrue_b8(), hi);
```

### 用途模式 3：`mask == 0xffffffff` — 全部命中

```c
// SVE
if (svptest_first(svptrue_b8(), svnot_b_z(svptrue_b8(), hi))) {
    // 有未激活，不是 all
} else {
    // all true
}
```

### 用途模式 4：把 mask 当索引/位图存到内存

这是最棘手的场景。建议**重构**：把"先提取 bitmask 再处理"的两步合并成一个 SVE 谓词驱动的循环，不再显式 32-bit bitmask。如果实在需要 bitmask，临时用栈数组 + svst1_u8 + 自己 popcnt。

**遇到 movemask 必须停下来评估上下文，先把改造方案给用户确认再改。**

---

## 9. Reduce / Horizontal

```c
// AVX2 (无直接的 horizontal sum，要拼)
// 常见手写：
__m256i s = _mm256_add_epi32(v, _mm256_permute2x128_si256(v, v, 1));
s = _mm256_hadd_epi32(s, s);
s = _mm256_hadd_epi32(s, s);
int sum = _mm256_extract_epi32(s, 0);

// SVE — 一条指令
int sum = (int)svaddv_s32(svptrue_b32(), v);
```

| AVX2 模式 | SVE |
|---|---|
| horizontal sum | `svaddv_s32(pg, v)` → 标量 |
| horizontal min | `svminv_s32(pg, v)` |
| horizontal max | `svmaxv_s32(pg, v)` |
| any 非零 | `svptest_any(pg, svcmpne_n_s32(pg, v, 0))` |

---

## 10. Convert（HIGH-RISK，类型/宽度都变）

```c
// AVX2: int32 → float32
__m256 f = _mm256_cvtepi32_ps(v);

// SVE
svfloat32_t f = svcvt_f32_s32_x(svptrue_b32(), v);
```

```c
// AVX2: float32 → int32 (truncate)
__m256i v = _mm256_cvttps_epi32(f);

// SVE
svint32_t v = svcvt_s32_f32_x(svptrue_b32(), f);
```

```c
// AVX2: int8 → int16 (符号扩展)
__m128i a = ...;  // 16 x int8
__m256i b = _mm256_cvtepi8_epi16(a);  // 16 x int16

// SVE — 扩窄/扩宽：svunpklo / svunpkhi
svint8_t a = ...;  // 32 x int8 (VL=256)
svint16_t lo = svunpklo_s16(a);   // 低 16 个扩成 int16
svint16_t hi = svunpkhi_s16(a);   // 高 16 个扩成 int16
// ⚠️ AVX2 cvtepi8_epi16 是从 __m128i 扩成 __m256i（16→16 个元素）
// SVE 等价：先从内存只 load 半向量，svld1sb_s16(svptrue_b16(), p) 直接边 load 边扩
```

---

## 11. Bitwise reinterpret

x86 `_mm256_castsi256_ps` 之类是零成本类型转换。SVE 对应 `svreinterpret_*`：

```c
svfloat32_t f = svreinterpret_f32_s32(v);
svint32_t   i = svreinterpret_s32_f32(f);
svuint8_t   u = svreinterpret_u8_s8(s);
```

零成本，编译器不会插指令。

---

## 通用易错点（每次替换都查）

1. **谓词宽度匹配元素**：处理 `int32` 用 `svptrue_b32()`，不是 `svptrue_b8()`
2. **mul 是 mullo 还是 mulhi**：AVX2 `_mm256_mullo_epi32` = SVE `svmul_s32_x`（低 32 位）；mulhi 要用 `svmulh`
3. **`andnot` 参数顺序反了**：详见 [Logical](#3-logical)
4. **logical shift 要先转 unsigned**：详见 [Shift](#6-shift)
5. **cmp 返回类型变了**：详见 [Compare](#4-compare高风险返回类型变了)
6. **shuffle 跨 lane 行为不同**：详见 [Shuffle](#7-shuffle--permutehigh-risk必须-lookuppy)
7. **movemask 没有直接对应**：详见 [Movemask](#8-movemaskhigh-risk常需重构控制流)
8. **半向量类型用 `svptrue_pat_b32(SV_VL4)` 谓词限制激活 lane 数**
