# AVX2 → SVE Migration Reference
> **生成日期**: 2026-05-15  
> **用途**: x86 AVX2（256-bit）到 ARM SVE/SVE2 迁移对照表

---

## 概述

本文档提供 x86 AVX2 intrinsics 到 ARM SVE/SVE2 的迁移映射。AVX2 是 256-bit 固定长度 SIMD，而 SVE 是可伸缩向量扩展（128-2048 bit）。在迁移时，SVE 的向量长度（VL）可配置为 256-bit 以匹配 AVX2 的处理宽度。

**关键差异**:
- AVX2 使用固定 256-bit 寄存器（`__m256i`, `__m256`, `__m256d`）
- SVE 使用可变长度寄存器（`svint32_t`, `svfloat32_t` 等），需要谓词寄存器（`svbool_t`）控制活跃元素
- SVE 指令通常需要额外的谓词参数（`pg`）来指定活跃元素
- SVE 使用 `svptrue_b32()` 等函数创建全活跃谓词

---

## 目录

- [Arithmetic](#arithmetic)
- [Compare](#compare)
- [Convert](#convert)
- [Load](#load)
- [Logical](#logical)
- [Miscellaneous](#miscellaneous)
- [Probability/Statistics](#probabilitystatistics)
- [Shift](#shift)
- [Special Math Functions](#special-math-functions)
- [Store](#store)
- [Swizzle](#swizzle)

---

## Arithmetic

### `_mm256_add_epi16`

**AVX2 签名**: `__m256i _mm256_add_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPADDW`

**描述**: Add packed 16-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_add_epi16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_add_epi32`

**AVX2 签名**: `__m256i _mm256_add_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPADDD`

**描述**: Add packed 32-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_add_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_add_epi64`

**AVX2 签名**: `__m256i _mm256_add_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPADDQ`

**描述**: Add packed 64-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_add_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_add_epi8`

**AVX2 签名**: `__m256i _mm256_add_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPADDB`

**描述**: Add packed 8-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svadd[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svadd[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svadd[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svadd[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svadd[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_add_epi8
// SVE: svadd[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_adds_epi16`

**AVX2 签名**: `__m256i _mm256_adds_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPADDSW`

**描述**: Add packed 16-bit integers in "a" and "b" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_adds_epi16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_adds_epi8`

**AVX2 签名**: `__m256i _mm256_adds_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPADDSB`

**描述**: Add packed 8-bit integers in "a" and "b" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svadd[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svadd[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svadd[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svadd[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svadd[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_adds_epi8
// SVE: svadd[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_adds_epu16`

**AVX2 签名**: `__m256i _mm256_adds_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPADDUSW`

**描述**: Add packed unsigned 16-bit integers in "a" and "b" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_adds_epu16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_adds_epu8`

**AVX2 签名**: `__m256i _mm256_adds_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPADDUSB`

**描述**: Add packed unsigned 8-bit integers in "a" and "b" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svadd[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svadd[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svadd[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svadd[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svadd[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_adds_epu8
// SVE: svadd[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hadd_epi16`

**AVX2 签名**: `__m256i _mm256_hadd_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPHADDW`

**描述**: Horizontally add adjacent pairs of 16-bit integers in "a" and "b", and pack the signed 16-bit results in "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hadd_epi16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hadd_epi32`

**AVX2 签名**: `__m256i _mm256_hadd_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPHADDD`

**描述**: Horizontally add adjacent pairs of 32-bit integers in "a" and "b", and pack the signed 32-bit results in "dst".

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hadd_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hadds_epi16`

**AVX2 签名**: `__m256i _mm256_hadds_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPHADDSW`

**描述**: Horizontally add adjacent pairs of signed 16-bit integers in "a" and "b" using saturation, and pack the signed 16-bit results in "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hadds_epi16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hsub_epi16`

**AVX2 签名**: `__m256i _mm256_hsub_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPHSUBW`

**描述**: Horizontally subtract adjacent pairs of 16-bit integers in "a" and "b", and pack the signed 16-bit results in "dst".

**SVE 对应指令**:

1. `svuint16_t svhsub[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
2. `svuint16_t svhsub[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
3. `svuint16_t svhsub[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
4. `svuint16_t svhsub[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2
5. `svuint16_t svhsub[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hsub_epi16
// SVE: svhsub[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hsub_epi32`

**AVX2 签名**: `__m256i _mm256_hsub_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPHSUBD`

**描述**: Horizontally subtract adjacent pairs of 32-bit integers in "a" and "b", and pack the signed 32-bit results in "dst".

**SVE 对应指令**:

1. `svuint32_t svhsub[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
2. `svuint32_t svhsub[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
3. `svuint32_t svhsub[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
4. `svuint32_t svhsub[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE2
5. `svuint32_t svhsub[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hsub_epi32
// SVE: svhsub[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_hsubs_epi16`

**AVX2 签名**: `__m256i _mm256_hsubs_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPHSUBSW`

**描述**: Horizontally subtract adjacent pairs of signed 16-bit integers in "a" and "b" using saturation, and pack the signed 16-bit results in "dst".

**SVE 对应指令**:

1. `svuint16_t svhsub[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
2. `svuint16_t svhsub[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
3. `svuint16_t svhsub[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
4. `svuint16_t svhsub[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2
5. `svuint16_t svhsub[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_hsubs_epi16
// SVE: svhsub[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_madd_epi16`

**AVX2 签名**: `__m256i _mm256_madd_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMADDWD`

**描述**: Multiply packed signed 16-bit integers in "a" and "b", producing intermediate signed 32-bit integers. Horizontally add adjacent pairs of intermediate 32-bit integers, and pack the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_maddubs_epi16`

**AVX2 签名**: `__m256i _mm256_maddubs_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMADDUBSW`

**描述**: Vertically multiply each unsigned 8-bit integer from "a" with the corresponding signed 8-bit integer from "b", producing intermediate signed 16-bit integers. Horizontally add adjacent pairs of intermediate signed 16-bit integers, and pack the saturated results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_mul_epi32`

**AVX2 签名**: `__m256i _mm256_mul_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPMULDQ`

**描述**: Multiply the low signed 32-bit integers from each packed 64-bit element in "a" and "b", and store the signed 64-bit results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_mul_epu32`

**AVX2 签名**: `__m256i _mm256_mul_epu32(__m256i a, __m256i b)`

**x86 指令**: `VPMULUDQ`

**描述**: Multiply the low unsigned 32-bit integers from each packed 64-bit element in "a" and "b", and store the unsigned 64-bit results in "dst".

**SVE 对应指令**:

1. `svuint64_t svmul[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svmul[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svmul[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svmul[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svmul[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mul_epu32
// SVE: svmul[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_mulhi_epi16`

**AVX2 签名**: `__m256i _mm256_mulhi_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMULHW`

**描述**: Multiply the packed signed 16-bit integers in "a" and "b", producing intermediate 32-bit integers, and store the high 16 bits of the intermediate integers in "dst".

**SVE 对应指令**:

1. `svuint16_t svmul[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svmul[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svmul[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svmul[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svmul[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mulhi_epi16
// SVE: svmul[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_mulhi_epu16`

**AVX2 签名**: `__m256i _mm256_mulhi_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPMULHUW`

**描述**: Multiply the packed unsigned 16-bit integers in "a" and "b", producing intermediate 32-bit integers, and store the high 16 bits of the intermediate integers in "dst".

**SVE 对应指令**:

1. `svuint16_t svmul[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svmul[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svmul[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svmul[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svmul[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mulhi_epu16
// SVE: svmul[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_mulhrs_epi16`

**AVX2 签名**: `__m256i _mm256_mulhrs_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMULHRSW`

**描述**: Multiply packed signed 16-bit integers in "a" and "b", producing intermediate signed 32-bit integers. Truncate each intermediate integer to the 18 most significant bits, round by adding 1, and store bits [16:1] to "dst".

**SVE 对应指令**:

1. `svuint16_t svadd[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svadd[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svadd[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svadd[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svadd[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mulhrs_epi16
// SVE: svadd[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_mullo_epi16`

**AVX2 签名**: `__m256i _mm256_mullo_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMULLW`

**描述**: Multiply the packed signed 16-bit integers in "a" and "b", producing intermediate 32-bit integers, and store the low 16 bits of the intermediate integers in "dst".

**SVE 对应指令**:

1. `svuint16_t svmul[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svmul[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svmul[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svmul[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svmul[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mullo_epi16
// SVE: svmul[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_mullo_epi32`

**AVX2 签名**: `__m256i _mm256_mullo_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPMULLD`

**描述**: Multiply the packed signed 32-bit integers in "a" and "b", producing intermediate 64-bit integers, and store the low 32 bits of the intermediate integers in "dst".

**SVE 对应指令**:

1. `svuint32_t svmul[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svmul[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svmul[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svmul[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svmul[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mullo_epi32
// SVE: svmul[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sad_epu8`

**AVX2 签名**: `__m256i _mm256_sad_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPSADBW`

**描述**: Compute the absolute differences of packed unsigned 8-bit integers in "a" and "b", then horizontally sum each consecutive 8 differences to produce four unsigned 16-bit integers, and pack these unsigned 16-bit integers in the low 16 bits of 64-bit elements in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sad_epu8
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sign_epi16`

**AVX2 签名**: `__m256i _mm256_sign_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPSIGNW`

**描述**: Negate packed signed 16-bit integers in "a" when the corresponding signed 16-bit integer in "b" is negative, and store the results in "dst". Element in "dst" are zeroed out when the corresponding element in "b" is zero.

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sign_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sign_epi32`

**AVX2 签名**: `__m256i _mm256_sign_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPSIGND`

**描述**: Negate packed signed 32-bit integers in "a" when the corresponding signed 32-bit integer in "b" is negative, and store the results in "dst". Element in "dst" are zeroed out when the corresponding element in "b" is zero.

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sign_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sign_epi8`

**AVX2 签名**: `__m256i _mm256_sign_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPSIGNB`

**描述**: Negate packed signed 8-bit integers in "a" when the corresponding signed 8-bit integer in "b" is negative, and store the results in "dst". Element in "dst" are zeroed out when the corresponding element in "b" is zero.

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sign_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sub_epi16`

**AVX2 签名**: `__m256i _mm256_sub_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPSUBW`

**描述**: Subtract packed 16-bit integers in "b" from packed 16-bit integers in "a", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svhsub[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
2. `svuint16_t svhsub[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
3. `svuint16_t svhsub[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
4. `svuint16_t svhsub[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2
5. `svuint16_t svhsub[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sub_epi16
// SVE: svhsub[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sub_epi32`

**AVX2 签名**: `__m256i _mm256_sub_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPSUBD`

**描述**: Subtract packed 32-bit integers in "b" from packed 32-bit integers in "a", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svhsub[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
2. `svuint32_t svhsub[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
3. `svuint32_t svhsub[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE2
4. `svuint32_t svhsub[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE2
5. `svuint32_t svhsub[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sub_epi32
// SVE: svhsub[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sub_epi64`

**AVX2 签名**: `__m256i _mm256_sub_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPSUBQ`

**描述**: Subtract packed 64-bit integers in "b" from packed 64-bit integers in "a", and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svhsub[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE2
2. `svuint64_t svhsub[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE2
3. `svuint64_t svhsub[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE2
4. `svuint64_t svhsub[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE2
5. `svuint64_t svhsub[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sub_epi64
// SVE: svhsub[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_sub_epi8`

**AVX2 签名**: `__m256i _mm256_sub_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPSUBB`

**描述**: Subtract packed 8-bit integers in "b" from packed 8-bit integers in "a", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svhsub[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
2. `svuint8_t svhsub[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
3. `svuint8_t svhsub[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
4. `svuint8_t svhsub[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2
5. `svuint8_t svhsub[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sub_epi8
// SVE: svhsub[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_subs_epi16`

**AVX2 签名**: `__m256i _mm256_subs_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPSUBSW`

**描述**: Subtract packed signed 16-bit integers in "b" from packed 16-bit integers in "a" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svhsub[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
2. `svuint16_t svhsub[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
3. `svuint16_t svhsub[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
4. `svuint16_t svhsub[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2
5. `svuint16_t svhsub[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_subs_epi16
// SVE: svhsub[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_subs_epi8`

**AVX2 签名**: `__m256i _mm256_subs_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPSUBSB`

**描述**: Subtract packed signed 8-bit integers in "b" from packed 8-bit integers in "a" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svhsub[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
2. `svuint8_t svhsub[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
3. `svuint8_t svhsub[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
4. `svuint8_t svhsub[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2
5. `svuint8_t svhsub[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_subs_epi8
// SVE: svhsub[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_subs_epu16`

**AVX2 签名**: `__m256i _mm256_subs_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPSUBUSW`

**描述**: Subtract packed unsigned 16-bit integers in "b" from packed unsigned 16-bit integers in "a" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svhsub[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
2. `svuint16_t svhsub[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
3. `svuint16_t svhsub[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE2
4. `svuint16_t svhsub[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2
5. `svuint16_t svhsub[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_subs_epu16
// SVE: svhsub[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_subs_epu8`

**AVX2 签名**: `__m256i _mm256_subs_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPSUBUSB`

**描述**: Subtract packed unsigned 8-bit integers in "b" from packed unsigned 8-bit integers in "a" using saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svhsub[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
2. `svuint8_t svhsub[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
3. `svuint8_t svhsub[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE2
4. `svuint8_t svhsub[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2
5. `svuint8_t svhsub[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE2

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_subs_epu8
// SVE: svhsub[_u8]_m(svptrue_b8(), a, b)
```

---

## Compare

### `_mm256_cmpeq_epi16`

**AVX2 签名**: `__m256i _mm256_cmpeq_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPCMPEQW`

**描述**: Compare packed 16-bit integers in "a" and "b" for equality, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpeq_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpeq_epi32`

**AVX2 签名**: `__m256i _mm256_cmpeq_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPCMPEQD`

**描述**: Compare packed 32-bit integers in "a" and "b" for equality, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpeq_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpeq_epi64`

**AVX2 签名**: `__m256i _mm256_cmpeq_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPCMPEQQ`

**描述**: Compare packed 64-bit integers in "a" and "b" for equality, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpeq_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpeq_epi8`

**AVX2 签名**: `__m256i _mm256_cmpeq_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPCMPEQB`

**描述**: Compare packed 8-bit integers in "a" and "b" for equality, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpeq_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpgt_epi16`

**AVX2 签名**: `__m256i _mm256_cmpgt_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPCMPGTW`

**描述**: Compare packed signed 16-bit integers in "a" and "b" for greater-than, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpgt_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpgt_epi32`

**AVX2 签名**: `__m256i _mm256_cmpgt_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPCMPGTD`

**描述**: Compare packed signed 32-bit integers in "a" and "b" for greater-than, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpgt_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpgt_epi64`

**AVX2 签名**: `__m256i _mm256_cmpgt_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPCMPGTQ`

**描述**: Compare packed signed 64-bit integers in "a" and "b" for greater-than, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpgt_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_cmpgt_epi8`

**AVX2 签名**: `__m256i _mm256_cmpgt_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPCMPGTB`

**描述**: Compare packed signed 8-bit integers in "a" and "b" for greater-than, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cmpgt_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

## Convert

### `_mm256_cvtepi16_epi32`

**AVX2 签名**: `__m256i _mm256_cvtepi16_epi32(__m128i a)`

**x86 指令**: `VPMOVSXWD`

**描述**: Sign extend packed 16-bit integers in "a" to packed 32-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepi16_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepi16_epi64(__m128i a)`

**x86 指令**: `VPMOVSXWQ`

**描述**: Sign extend packed 16-bit integers in "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepi32_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepi32_epi64(__m128i a)`

**x86 指令**: `VPMOVSXDQ`

**描述**: Sign extend packed 32-bit integers in "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepi8_epi16`

**AVX2 签名**: `__m256i _mm256_cvtepi8_epi16(__m128i a)`

**x86 指令**: `VPMOVSXBW`

**描述**: Sign extend packed 8-bit integers in "a" to packed 16-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepi8_epi32`

**AVX2 签名**: `__m256i _mm256_cvtepi8_epi32(__m128i a)`

**x86 指令**: `VPMOVSXBD`

**描述**: Sign extend packed 8-bit integers in "a" to packed 32-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepi8_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepi8_epi64(__m128i a)`

**x86 指令**: `VPMOVSXBQ`

**描述**: Sign extend packed 8-bit integers in the low 8 bytes of "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_cvtepu16_epi32`

**AVX2 签名**: `__m256i _mm256_cvtepu16_epi32(__m128i a)`

**x86 指令**: `VPMOVZXWD`

**描述**: Zero extend packed unsigned 16-bit integers in "a" to packed 32-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu16_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a)
```

---

### `_mm256_cvtepu16_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepu16_epi64(__m128i a)`

**x86 指令**: `VPMOVZXWQ`

**描述**: Zero extend packed unsigned 16-bit integers in "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu16_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a)
```

---

### `_mm256_cvtepu32_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepu32_epi64(__m128i a)`

**x86 指令**: `VPMOVZXDQ`

**描述**: Zero extend packed unsigned 32-bit integers in "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu32_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a)
```

---

### `_mm256_cvtepu8_epi16`

**AVX2 签名**: `__m256i _mm256_cvtepu8_epi16(__m128i a)`

**x86 指令**: `VPMOVZXBW`

**描述**: Zero extend packed unsigned 8-bit integers in "a" to packed 16-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu8_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a)
```

---

### `_mm256_cvtepu8_epi32`

**AVX2 签名**: `__m256i _mm256_cvtepu8_epi32(__m128i a)`

**x86 指令**: `VPMOVZXBD`

**描述**: Zero extend packed unsigned 8-bit integers in "a" to packed 32-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu8_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a)
```

---

### `_mm256_cvtepu8_epi64`

**AVX2 签名**: `__m256i _mm256_cvtepu8_epi64(__m128i a)`

**x86 指令**: `VPMOVZXBQ`

**描述**: Zero extend packed unsigned 8-bit integers in the low 8 byte sof "a" to packed 64-bit integers, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_cvtepu8_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a)
```

---

## Load

### `_mm256_i32gather_epi32`

**AVX2 签名**: `__m256i _mm256_i32gather_epi32(int const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VPGATHERDD`

**描述**: Gather 32-bit integers from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i32gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm256_i32gather_epi64`

**AVX2 签名**: `__m256i _mm256_i32gather_epi64(__int64 const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VPGATHERDQ`

**描述**: Gather 64-bit integers from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i32gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm256_i32gather_pd`

**AVX2 签名**: `__m256d _mm256_i32gather_pd(double const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VGATHERDPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i32gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm256_i32gather_ps`

**AVX2 签名**: `__m256 _mm256_i32gather_ps(float const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VGATHERDPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i32gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm256_i64gather_epi32`

**AVX2 签名**: `__m128i _mm256_i64gather_epi32(int const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VPGATHERQD`

**描述**: Gather 32-bit integers from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i64gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm256_i64gather_epi64`

**AVX2 签名**: `__m256i _mm256_i64gather_epi64(__int64 const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VPGATHERQQ`

**描述**: Gather 64-bit integers from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i64gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm256_i64gather_pd`

**AVX2 签名**: `__m256d _mm256_i64gather_pd(double const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VGATHERQPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i64gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm256_i64gather_ps`

**AVX2 签名**: `__m128 _mm256_i64gather_ps(float const* base_addr, __m256i vindex, const int scale)`

**x86 指令**: `VGATHERQPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_i64gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm256_mask_i32gather_epi32`

**AVX2 签名**: `__m256i _mm256_mask_i32gather_epi32(__m256i src, int const* base_addr, __m256i vindex, __m256i mask, const int scale)`

**x86 指令**: `VPGATHERDD`

**描述**: Gather 32-bit integers from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i32gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm256_mask_i32gather_epi64`

**AVX2 签名**: `__m256i _mm256_mask_i32gather_epi64(__m256i src, __int64 const* base_addr, __m128i vindex, __m256i mask, const int scale)`

**x86 指令**: `VPGATHERDQ`

**描述**: Gather 64-bit integers from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i32gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm256_mask_i32gather_pd`

**AVX2 签名**: `__m256d _mm256_mask_i32gather_pd(__m256d src, double const* base_addr, __m128i vindex, __m256d mask, const int scale)`

**x86 指令**: `VGATHERDPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i32gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm256_mask_i32gather_ps`

**AVX2 签名**: `__m256 _mm256_mask_i32gather_ps(__m256 src, float const* base_addr, __m256i vindex, __m256 mask, const int scale)`

**x86 指令**: `VGATHERDPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i32gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm256_mask_i64gather_epi32`

**AVX2 签名**: `__m128i _mm256_mask_i64gather_epi32(__m128i src, int const* base_addr, __m256i vindex, __m128i mask, const int scale)`

**x86 指令**: `VPGATHERQD`

**描述**: Gather 32-bit integers from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i64gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm256_mask_i64gather_epi64`

**AVX2 签名**: `__m256i _mm256_mask_i64gather_epi64(__m256i src, __int64 const* base_addr, __m256i vindex, __m256i mask, const int scale)`

**x86 指令**: `VPGATHERQQ`

**描述**: Gather 64-bit integers from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i64gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm256_mask_i64gather_pd`

**AVX2 签名**: `__m256d _mm256_mask_i64gather_pd(__m256d src, double const* base_addr, __m256i vindex, __m256d mask, const int scale)`

**x86 指令**: `VGATHERQPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i64gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm256_mask_i64gather_ps`

**AVX2 签名**: `__m128 _mm256_mask_i64gather_ps(__m128 src, float const* base_addr, __m256i vindex, __m128 mask, const int scale)`

**x86 指令**: `VGATHERQPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mask_i64gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm256_maskload_epi32`

**AVX2 签名**: `__m256i _mm256_maskload_epi32(int const* mem_addr, __m256i mask)`

**x86 指令**: `VPMASKMOVD`

**描述**: Load packed 32-bit integers from memory into "dst" using "mask" (elements are zeroed out when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_maskload_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm256_maskload_epi64`

**AVX2 签名**: `__m256i _mm256_maskload_epi64(__int64 const* mem_addr, __m256i mask)`

**x86 指令**: `VPMASKMOVQ`

**描述**: Load packed 64-bit integers from memory into "dst" using "mask" (elements are zeroed out when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_maskload_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm256_stream_load_si256`

**AVX2 签名**: `__m256i _mm256_stream_load_si256(void const* mem_addr)`

**x86 指令**: `VMOVNTDQA`

**描述**: Load 256-bits of integer data from memory into "dst" using a non-temporal memory hint.
	"mem_addr" must be aligned on a 32-byte boundary or a general-protection exception may be generated.

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm_i32gather_epi32`

**AVX2 签名**: `__m128i _mm_i32gather_epi32(int const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VPGATHERDD`

**描述**: Gather 32-bit integers from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i32gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm_i32gather_epi64`

**AVX2 签名**: `__m128i _mm_i32gather_epi64(__int64 const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VPGATHERDQ`

**描述**: Gather 64-bit integers from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i32gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm_i32gather_pd`

**AVX2 签名**: `__m128d _mm_i32gather_pd(double const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VGATHERDPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i32gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm_i32gather_ps`

**AVX2 签名**: `__m128 _mm_i32gather_ps(float const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VGATHERDPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i32gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm_i64gather_epi32`

**AVX2 签名**: `__m128i _mm_i64gather_epi32(int const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VPGATHERQD`

**描述**: Gather 32-bit integers from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i64gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm_i64gather_epi64`

**AVX2 签名**: `__m128i _mm_i64gather_epi64(__int64 const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VPGATHERQQ`

**描述**: Gather 64-bit integers from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i64gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), base_addr, vindex)
```

---

### `_mm_i64gather_pd`

**AVX2 签名**: `__m128d _mm_i64gather_pd(double const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VGATHERQPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i64gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm_i64gather_ps`

**AVX2 签名**: `__m128 _mm_i64gather_ps(float const* base_addr, __m128i vindex, const int scale)`

**x86 指令**: `VGATHERQPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst". "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_i64gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), base_addr, vindex)
```

---

### `_mm_mask_i32gather_epi32`

**AVX2 签名**: `__m128i _mm_mask_i32gather_epi32(__m128i src, int const* base_addr, __m128i vindex, __m128i mask, const int scale)`

**x86 指令**: `VPGATHERDD`

**描述**: Gather 32-bit integers from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i32gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm_mask_i32gather_epi64`

**AVX2 签名**: `__m128i _mm_mask_i32gather_epi64(__m128i src, __int64 const* base_addr, __m128i vindex, __m128i mask, const int scale)`

**x86 指令**: `VPGATHERDQ`

**描述**: Gather 64-bit integers from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i32gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm_mask_i32gather_pd`

**AVX2 签名**: `__m128d _mm_mask_i32gather_pd(__m128d src, double const* base_addr, __m128i vindex, __m128d mask, const int scale)`

**x86 指令**: `VGATHERDPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 32-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i32gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm_mask_i32gather_ps`

**AVX2 签名**: `__m128 _mm_mask_i32gather_ps(__m128 src, float const* base_addr, __m128i vindex, __m128 mask, const int scale)`

**x86 指令**: `VGATHERDPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 32-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 32-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i32gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm_mask_i64gather_epi32`

**AVX2 签名**: `__m128i _mm_mask_i64gather_epi32(__m128i src, int const* base_addr, __m128i vindex, __m128i mask, const int scale)`

**x86 指令**: `VPGATHERQD`

**描述**: Gather 32-bit integers from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i64gather_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm_mask_i64gather_epi64`

**AVX2 签名**: `__m128i _mm_mask_i64gather_epi64(__m128i src, __int64 const* base_addr, __m128i vindex, __m128i mask, const int scale)`

**x86 指令**: `VPGATHERQQ`

**描述**: Gather 64-bit integers from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i64gather_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), src, base_addr)
```

---

### `_mm_mask_i64gather_pd`

**AVX2 签名**: `__m128d _mm_mask_i64gather_pd(__m128d src, double const* base_addr, __m128i vindex, __m128d mask, const int scale)`

**x86 指令**: `VGATHERQPD`

**描述**: Gather double-precision (64-bit) floating-point elements from memory using 64-bit indices. 64-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
2. `svfloat64_t svadd[_f64]_x(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_z(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat64_t svadd[_n_f64]_m(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE
5. `svfloat64_t svadd[_n_f64]_x(svbool_t pg, svfloat64_t op1, float64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i64gather_pd
// SVE: svadd[_f64]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm_mask_i64gather_ps`

**AVX2 签名**: `__m128 _mm_mask_i64gather_ps(__m128 src, float const* base_addr, __m128i vindex, __m128 mask, const int scale)`

**x86 指令**: `VGATHERQPS`

**描述**: Gather single-precision (32-bit) floating-point elements from memory using 64-bit indices. 32-bit elements are loaded from addresses starting at "base_addr" and offset by each 64-bit element in "vindex" (each index is scaled by the factor in "scale"). Gathered elements are merged into "dst" using "mask" (elements are copied from "src" when the highest bit is not set in the corresponding element). "scale" should be 1, 2, 4 or 8.

**SVE 对应指令**:

1. `svfloat16_t svadd[_f16]_m(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
2. `svfloat32_t svadd[_f32]_m(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE
3. `svfloat64_t svadd[_f64]_m(svbool_t pg, svfloat64_t op1, svfloat64_t op2)` — SME and SME2, SVE
4. `svfloat16_t svadd[_f16]_x(svbool_t pg, svfloat16_t op1, svfloat16_t op2)` — SME and SME2, SVE
5. `svfloat32_t svadd[_f32]_x(svbool_t pg, svfloat32_t op1, svfloat32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_mask_i64gather_ps
// SVE: svadd[_f16]_m(svptrue_b32(), src, base_addr)
```

---

### `_mm_maskload_epi32`

**AVX2 签名**: `__m128i _mm_maskload_epi32(int const* mem_addr, __m128i mask)`

**x86 指令**: `VPMASKMOVD`

**描述**: Load packed 32-bit integers from memory into "dst" using "mask" (elements are zeroed out when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_maskload_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm_maskload_epi64`

**AVX2 签名**: `__m128i _mm_maskload_epi64(__int64 const* mem_addr, __m128i mask)`

**x86 指令**: `VPMASKMOVQ`

**描述**: Load packed 64-bit integers from memory into "dst" using "mask" (elements are zeroed out when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_maskload_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), mem_addr, mask)
```

---

## Logical

### `_mm256_and_si256`

**AVX2 签名**: `__m256i _mm256_and_si256(__m256i a, __m256i b)`

**x86 指令**: `VPAND`

**描述**: Compute the bitwise AND of 256 bits (representing integer data) in "a" and "b", and store the result in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_andnot_si256`

**AVX2 签名**: `__m256i _mm256_andnot_si256(__m256i a, __m256i b)`

**x86 指令**: `VPANDN`

**描述**: Compute the bitwise NOT of 256 bits (representing integer data) in "a" and then AND with "b", and store the result in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_or_si256`

**AVX2 签名**: `__m256i _mm256_or_si256(__m256i a, __m256i b)`

**x86 指令**: `VPOR`

**描述**: Compute the bitwise OR of 256 bits (representing integer data) in "a" and "b", and store the result in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_xor_si256`

**AVX2 签名**: `__m256i _mm256_xor_si256(__m256i a, __m256i b)`

**x86 指令**: `VPXOR`

**描述**: Compute the bitwise XOR of 256 bits (representing integer data) in "a" and "b", and store the result in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

## Miscellaneous

### `_mm256_alignr_epi8`

**AVX2 签名**: `__m256i _mm256_alignr_epi8(__m256i a, __m256i b, const int imm8)`

**x86 指令**: `VPALIGNR`

**描述**: Concatenate pairs of 16-byte blocks in "a" and "b" into a 32-byte temporary result, shift the result right by "imm8" bytes, and store the low 16 bytes in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_alignr_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_movemask_epi8`

**AVX2 签名**: `int _mm256_movemask_epi8(__m256i a)`

**x86 指令**: `VPMOVMSKB`

**描述**: Create mask from the most significant bit of each 8-bit element in "a", and store the result in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_movemask_epi8
// SVE: svand[_u32]_m(svptrue_b8(), a)
```

---

### `_mm256_mpsadbw_epu8`

**AVX2 签名**: `__m256i _mm256_mpsadbw_epu8(__m256i a, __m256i b, const int imm8)`

**x86 指令**: `VMPSADBW`

**描述**: Compute the sum of absolute differences (SADs) of quadruplets of unsigned 8-bit integers in "a" compared to those in "b", and store the 16-bit results in "dst".
	Eight SADs are performed for each 128-bit lane using one quadruplet from "b" and eight quadruplets from "a". One quadruplet is selected from "b" starting at on the offset specified in "imm8". Eight quadruplets are formed from sequential 8-bit integers selected from "a" starting at the offset specified in "imm8".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_mpsadbw_epu8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_packs_epi16`

**AVX2 签名**: `__m256i _mm256_packs_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPACKSSWB`

**描述**: Convert packed signed 16-bit integers from "a" and "b" to packed 8-bit integers using signed saturation, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_packs_epi32`

**AVX2 签名**: `__m256i _mm256_packs_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPACKSSDW`

**描述**: Convert packed signed 32-bit integers from "a" and "b" to packed 16-bit integers using signed saturation, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_packus_epi16`

**AVX2 签名**: `__m256i _mm256_packus_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPACKUSWB`

**描述**: Convert packed signed 16-bit integers from "a" and "b" to packed 8-bit integers using unsigned saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_packus_epi16
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_packus_epi32`

**AVX2 签名**: `__m256i _mm256_packus_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPACKUSDW`

**描述**: Convert packed signed 32-bit integers from "a" and "b" to packed 16-bit integers using unsigned saturation, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_packus_epi32
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

## Probability/Statistics

### `_mm256_avg_epu16`

**AVX2 签名**: `__m256i _mm256_avg_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPAVGW`

**描述**: Average packed unsigned 16-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_avg_epu16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_avg_epu8`

**AVX2 签名**: `__m256i _mm256_avg_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPAVGB`

**描述**: Average packed unsigned 8-bit integers in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_avg_epu8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

## Shift

### `_mm256_bslli_epi128`

**AVX2 签名**: `__m256i _mm256_bslli_epi128(__m256i a, const int imm8)`

**x86 指令**: `VPSLLDQ`

**描述**: Shift 128-bit lanes in "a" left by "imm8" bytes while shifting in zeros, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_bsrli_epi128`

**AVX2 签名**: `__m256i _mm256_bsrli_epi128(__m256i a, const int imm8)`

**x86 指令**: `VPSRLDQ`

**描述**: Shift 128-bit lanes in "a" right by "imm8" bytes while shifting in zeros, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_sll_epi16`

**AVX2 签名**: `__m256i _mm256_sll_epi16(__m256i a, __m128i count)`

**x86 指令**: `VPSLLW`

**描述**: Shift packed 16-bit integers in "a" left by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sll_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, count)
```

---

### `_mm256_sll_epi32`

**AVX2 签名**: `__m256i _mm256_sll_epi32(__m256i a, __m128i count)`

**x86 指令**: `VPSLLD`

**描述**: Shift packed 32-bit integers in "a" left by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sll_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_sll_epi64`

**AVX2 签名**: `__m256i _mm256_sll_epi64(__m256i a, __m128i count)`

**x86 指令**: `VPSLLQ`

**描述**: Shift packed 64-bit integers in "a" left by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sll_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

### `_mm256_slli_epi16`

**AVX2 签名**: `__m256i _mm256_slli_epi16(__m256i a, int imm8)`

**x86 指令**: `VPSLLW`

**描述**: Shift packed 16-bit integers in "a" left by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_slli_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_slli_epi32`

**AVX2 签名**: `__m256i _mm256_slli_epi32(__m256i a, int imm8)`

**x86 指令**: `VPSLLD`

**描述**: Shift packed 32-bit integers in "a" left by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_slli_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_slli_epi64`

**AVX2 签名**: `__m256i _mm256_slli_epi64(__m256i a, int imm8)`

**x86 指令**: `VPSLLQ`

**描述**: Shift packed 64-bit integers in "a" left by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_slli_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_slli_si256`

**AVX2 签名**: `__m256i _mm256_slli_si256(__m256i a, const int imm8)`

**x86 指令**: `VPSLLDQ`

**描述**: Shift 128-bit lanes in "a" left by "imm8" bytes while shifting in zeros, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_sllv_epi32`

**AVX2 签名**: `__m256i _mm256_sllv_epi32(__m256i a, __m256i count)`

**x86 指令**: `VPSLLVD`

**描述**: Shift packed 32-bit integers in "a" left by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sllv_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_sllv_epi64`

**AVX2 签名**: `__m256i _mm256_sllv_epi64(__m256i a, __m256i count)`

**x86 指令**: `VPSLLVQ`

**描述**: Shift packed 64-bit integers in "a" left by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sllv_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

### `_mm256_sra_epi16`

**AVX2 签名**: `__m256i _mm256_sra_epi16(__m256i a, __m128i count)`

**x86 指令**: `VPSRAW`

**描述**: Shift packed 16-bit integers in "a" right by "count" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sra_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, count)
```

---

### `_mm256_sra_epi32`

**AVX2 签名**: `__m256i _mm256_sra_epi32(__m256i a, __m128i count)`

**x86 指令**: `VPSRAD`

**描述**: Shift packed 32-bit integers in "a" right by "count" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_sra_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srai_epi16`

**AVX2 签名**: `__m256i _mm256_srai_epi16(__m256i a, int imm8)`

**x86 指令**: `VPSRAW`

**描述**: Shift packed 16-bit integers in "a" right by "imm8" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srai_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_srai_epi32`

**AVX2 签名**: `__m256i _mm256_srai_epi32(__m256i a, int imm8)`

**x86 指令**: `VPSRAD`

**描述**: Shift packed 32-bit integers in "a" right by "imm8" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srai_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_srav_epi32`

**AVX2 签名**: `__m256i _mm256_srav_epi32(__m256i a, __m256i count)`

**x86 指令**: `VPSRAVD`

**描述**: Shift packed 32-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srav_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srl_epi16`

**AVX2 签名**: `__m256i _mm256_srl_epi16(__m256i a, __m128i count)`

**x86 指令**: `VPSRLW`

**描述**: Shift packed 16-bit integers in "a" right by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srl_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srl_epi32`

**AVX2 签名**: `__m256i _mm256_srl_epi32(__m256i a, __m128i count)`

**x86 指令**: `VPSRLD`

**描述**: Shift packed 32-bit integers in "a" right by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srl_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srl_epi64`

**AVX2 签名**: `__m256i _mm256_srl_epi64(__m256i a, __m128i count)`

**x86 指令**: `VPSRLQ`

**描述**: Shift packed 64-bit integers in "a" right by "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srl_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srli_epi16`

**AVX2 签名**: `__m256i _mm256_srli_epi16(__m256i a, int imm8)`

**x86 指令**: `VPSRLW`

**描述**: Shift packed 16-bit integers in "a" right by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srli_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_srli_epi32`

**AVX2 签名**: `__m256i _mm256_srli_epi32(__m256i a, int imm8)`

**x86 指令**: `VPSRLD`

**描述**: Shift packed 32-bit integers in "a" right by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srli_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_srli_epi64`

**AVX2 签名**: `__m256i _mm256_srli_epi64(__m256i a, int imm8)`

**x86 指令**: `VPSRLQ`

**描述**: Shift packed 64-bit integers in "a" right by "imm8" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srli_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_srli_si256`

**AVX2 签名**: `__m256i _mm256_srli_si256(__m256i a, const int imm8)`

**x86 指令**: `VPSRLDQ`

**描述**: Shift 128-bit lanes in "a" right by "imm8" bytes while shifting in zeros, and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_srlv_epi32`

**AVX2 签名**: `__m256i _mm256_srlv_epi32(__m256i a, __m256i count)`

**x86 指令**: `VPSRLVD`

**描述**: Shift packed 32-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srlv_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm256_srlv_epi64`

**AVX2 签名**: `__m256i _mm256_srlv_epi64(__m256i a, __m256i count)`

**x86 指令**: `VPSRLVQ`

**描述**: Shift packed 64-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_srlv_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

### `_mm_sllv_epi32`

**AVX2 签名**: `__m128i _mm_sllv_epi32(__m128i a, __m128i count)`

**x86 指令**: `VPSLLVD`

**描述**: Shift packed 32-bit integers in "a" left by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_sllv_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm_sllv_epi64`

**AVX2 签名**: `__m128i _mm_sllv_epi64(__m128i a, __m128i count)`

**x86 指令**: `VPSLLVQ`

**描述**: Shift packed 64-bit integers in "a" left by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_sllv_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

### `_mm_srav_epi32`

**AVX2 签名**: `__m128i _mm_srav_epi32(__m128i a, __m128i count)`

**x86 指令**: `VPSRAVD`

**描述**: Shift packed 32-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in sign bits, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_srav_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm_srlv_epi32`

**AVX2 签名**: `__m128i _mm_srlv_epi32(__m128i a, __m128i count)`

**x86 指令**: `VPSRLVD`

**描述**: Shift packed 32-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_srlv_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, count)
```

---

### `_mm_srlv_epi64`

**AVX2 签名**: `__m128i _mm_srlv_epi64(__m128i a, __m128i count)`

**x86 指令**: `VPSRLVQ`

**描述**: Shift packed 64-bit integers in "a" right by the amount specified by the corresponding element in "count" while shifting in zeros, and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_srlv_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, count)
```

---

## Special Math Functions

### `_mm256_abs_epi16`

**AVX2 签名**: `__m256i _mm256_abs_epi16(__m256i a)`

**x86 指令**: `VPABSW`

**描述**: Compute the absolute value of packed signed 16-bit integers in "a", and store the unsigned results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_abs_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a)
```

---

### `_mm256_abs_epi32`

**AVX2 签名**: `__m256i _mm256_abs_epi32(__m256i a)`

**x86 指令**: `VPABSD`

**描述**: Compute the absolute value of packed signed 32-bit integers in "a", and store the unsigned results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_abs_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a)
```

---

### `_mm256_abs_epi8`

**AVX2 签名**: `__m256i _mm256_abs_epi8(__m256i a)`

**x86 指令**: `VPABSB`

**描述**: Compute the absolute value of packed signed 8-bit integers in "a", and store the unsigned results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_abs_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a)
```

---

### `_mm256_max_epi16`

**AVX2 签名**: `__m256i _mm256_max_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMAXSW`

**描述**: Compare packed signed 16-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_max_epi32`

**AVX2 签名**: `__m256i _mm256_max_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPMAXSD`

**描述**: Compare packed signed 32-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_max_epi8`

**AVX2 签名**: `__m256i _mm256_max_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPMAXSB`

**描述**: Compare packed signed 8-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_max_epu16`

**AVX2 签名**: `__m256i _mm256_max_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPMAXUW`

**描述**: Compare packed unsigned 16-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epu16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_max_epu32`

**AVX2 签名**: `__m256i _mm256_max_epu32(__m256i a, __m256i b)`

**x86 指令**: `VPMAXUD`

**描述**: Compare packed unsigned 32-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epu32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_max_epu8`

**AVX2 签名**: `__m256i _mm256_max_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPMAXUB`

**描述**: Compare packed unsigned 8-bit integers in "a" and "b", and store packed maximum values in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_max_epu8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epi16`

**AVX2 签名**: `__m256i _mm256_min_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPMINSW`

**描述**: Compare packed signed 16-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epi32`

**AVX2 签名**: `__m256i _mm256_min_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPMINSD`

**描述**: Compare packed signed 32-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epi8`

**AVX2 签名**: `__m256i _mm256_min_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPMINSB`

**描述**: Compare packed signed 8-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epu16`

**AVX2 签名**: `__m256i _mm256_min_epu16(__m256i a, __m256i b)`

**x86 指令**: `VPMINUW`

**描述**: Compare packed unsigned 16-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epu16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epu32`

**AVX2 签名**: `__m256i _mm256_min_epu32(__m256i a, __m256i b)`

**x86 指令**: `VPMINUD`

**描述**: Compare packed unsigned 32-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epu32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_min_epu8`

**AVX2 签名**: `__m256i _mm256_min_epu8(__m256i a, __m256i b)`

**x86 指令**: `VPMINUB`

**描述**: Compare packed unsigned 8-bit integers in "a" and "b", and store packed minimum values in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_min_epu8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

## Store

### `_mm256_maskstore_epi32`

**AVX2 签名**: `void _mm256_maskstore_epi32(int* mem_addr, __m256i mask, __m256i a)`

**x86 指令**: `VPMASKMOVD`

**描述**: Store packed 32-bit integers from "a" into memory using "mask" (elements are not stored when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_maskstore_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm256_maskstore_epi64`

**AVX2 签名**: `void _mm256_maskstore_epi64(__int64* mem_addr, __m256i mask, __m256i a)`

**x86 指令**: `VPMASKMOVQ`

**描述**: Store packed 64-bit integers from "a" into memory using "mask" (elements are not stored when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_maskstore_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm_maskstore_epi32`

**AVX2 签名**: `void _mm_maskstore_epi32(int* mem_addr, __m128i mask, __m128i a)`

**x86 指令**: `VPMASKMOVD`

**描述**: Store packed 32-bit integers from "a" into memory using "mask" (elements are not stored when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint32_t svadd[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svadd[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svadd[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svadd[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svadd[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_maskstore_epi32
// SVE: svadd[_u32]_m(svptrue_b8(), mem_addr, mask)
```

---

### `_mm_maskstore_epi64`

**AVX2 签名**: `void _mm_maskstore_epi64(__int64* mem_addr, __m128i mask, __m128i a)`

**x86 指令**: `VPMASKMOVQ`

**描述**: Store packed 64-bit integers from "a" into memory using "mask" (elements are not stored when the highest bit is not set in the corresponding element).

**SVE 对应指令**:

1. `svuint64_t svadd[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svadd[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svadd[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svadd[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svadd[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_maskstore_epi64
// SVE: svadd[_u64]_m(svptrue_b8(), mem_addr, mask)
```

---

## Swizzle

### `_mm256_blend_epi16`

**AVX2 签名**: `__m256i _mm256_blend_epi16(__m256i a, __m256i b, const int imm8)`

**x86 指令**: `VPBLENDW`

**描述**: Blend packed 16-bit integers from "a" and "b" within 128-bit lanes using control mask "imm8", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_blend_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_blend_epi32`

**AVX2 签名**: `__m256i _mm256_blend_epi32(__m256i a, __m256i b, const int imm8)`

**x86 指令**: `VPBLENDD`

**描述**: Blend packed 32-bit integers from "a" and "b" using control mask "imm8", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_blend_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_blendv_epi8`

**AVX2 签名**: `__m256i _mm256_blendv_epi8(__m256i a, __m256i b, __m256i mask)`

**x86 指令**: `VPBLENDVB`

**描述**: Blend packed 8-bit integers from "a" and "b" using "mask", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_blendv_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_broadcastb_epi8`

**AVX2 签名**: `__m256i _mm256_broadcastb_epi8(__m128i a)`

**x86 指令**: `VPBROADCASTB`

**描述**: Broadcast the low packed 8-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint8_t sveor[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t sveor[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t sveor[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t sveor[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t sveor[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_broadcastb_epi8
// SVE: sveor[_u8]_m(svptrue_b8(), a)
```

---

### `_mm256_broadcastd_epi32`

**AVX2 签名**: `__m256i _mm256_broadcastd_epi32(__m128i a)`

**x86 指令**: `VPBROADCASTD`

**描述**: Broadcast the low packed 32-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint32_t sveor[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t sveor[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t sveor[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t sveor[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t sveor[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_broadcastd_epi32
// SVE: sveor[_u32]_m(svptrue_b8(), a)
```

---

### `_mm256_broadcastq_epi64`

**AVX2 签名**: `__m256i _mm256_broadcastq_epi64(__m128i a)`

**x86 指令**: `VPBROADCASTQ`

**描述**: Broadcast the low packed 64-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint64_t sveor[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t sveor[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t sveor[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t sveor[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t sveor[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_broadcastq_epi64
// SVE: sveor[_u64]_m(svptrue_b8(), a)
```

---

### `_mm256_broadcastsd_pd`

**AVX2 签名**: `__m256d _mm256_broadcastsd_pd(__m128d a)`

**x86 指令**: `VBROADCASTSD`

**描述**: Broadcast the low double-precision (64-bit) floating-point element from "a" to all elements of "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_broadcastsi128_si256`

**AVX2 签名**: `__m256i _mm256_broadcastsi128_si256(__m128i a)`

**x86 指令**: `VBROADCASTI128`

**描述**: Broadcast 128 bits of integer data from "a" to all 128-bit lanes in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_broadcastss_ps`

**AVX2 签名**: `__m256 _mm256_broadcastss_ps(__m128 a)`

**x86 指令**: `VBROADCASTSS`

**描述**: Broadcast the low single-precision (32-bit) floating-point element from "a" to all elements of "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_broadcastw_epi16`

**AVX2 签名**: `__m256i _mm256_broadcastw_epi16(__m128i a)`

**x86 指令**: `VPBROADCASTW`

**描述**: Broadcast the low packed 16-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint16_t sveor[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t sveor[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t sveor[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t sveor[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t sveor[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_broadcastw_epi16
// SVE: sveor[_u16]_m(svptrue_b8(), a)
```

---

### `_mm256_extract_epi16`

**AVX2 签名**: `int _mm256_extract_epi16(__m256i a, const int index)`

**描述**: Extract a 16-bit integer from "a", selected with "index", and store the result in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_extract_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, index)
```

---

### `_mm256_extract_epi8`

**AVX2 签名**: `int _mm256_extract_epi8(__m256i a, const int index)`

**描述**: Extract an 8-bit integer from "a", selected with "index", and store the result in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_extract_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, index)
```

---

### `_mm256_extracti128_si256`

**AVX2 签名**: `__m128i _mm256_extracti128_si256(__m256i a, const int imm8)`

**x86 指令**: `VEXTRACTI128`

**描述**: Extract 128 bits (composed of integer data) from "a", selected with "imm8", and store the result in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_inserti128_si256`

**AVX2 签名**: `__m256i _mm256_inserti128_si256(__m256i a, __m128i b, const int imm8)`

**x86 指令**: `VINSERTI128`

**描述**: Copy "a" to "dst", then insert 128 bits (composed of integer data) from "b" into "dst" at the location specified by "imm8".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_permute2x128_si256`

**AVX2 签名**: `__m256i _mm256_permute2x128_si256(__m256i a, __m256i b, const int imm8)`

**x86 指令**: `VPERM2I128`

**描述**: Shuffle 128-bits (composed of integer data) selected by "imm8" from "a" and "b", and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_permute4x64_epi64`

**AVX2 签名**: `__m256i _mm256_permute4x64_epi64(__m256i a, const int imm8)`

**x86 指令**: `VPERMQ`

**描述**: Shuffle 64-bit integers in "a" across lanes using the control in "imm8", and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_permute4x64_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_permute4x64_pd`

**AVX2 签名**: `__m256d _mm256_permute4x64_pd(__m256d a, const int imm8)`

**x86 指令**: `VPERMPD`

**描述**: Shuffle double-precision (64-bit) floating-point elements in "a" across lanes using the control in "imm8", and store the results in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_permutevar8x32_epi32`

**AVX2 签名**: `__m256i _mm256_permutevar8x32_epi32(__m256i a, __m256i idx)`

**x86 指令**: `VPERMD`

**描述**: Shuffle 32-bit integers in "a" across lanes using the corresponding index in "idx", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_permutevar8x32_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, idx)
```

---

### `_mm256_permutevar8x32_ps`

**AVX2 签名**: `__m256 _mm256_permutevar8x32_ps(__m256 a, __m256i idx)`

**x86 指令**: `VPERMPS`

**描述**: Shuffle single-precision (32-bit) floating-point elements in "a" across lanes using the corresponding index in "idx".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm256_shuffle_epi32`

**AVX2 签名**: `__m256i _mm256_shuffle_epi32(__m256i a, const int imm8)`

**x86 指令**: `VPSHUFD`

**描述**: Shuffle 32-bit integers in "a" within 128-bit lanes using the control in "imm8", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_shuffle_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_shuffle_epi8`

**AVX2 签名**: `__m256i _mm256_shuffle_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPSHUFB`

**描述**: Shuffle 8-bit integers in "a" within 128-bit lanes according to shuffle control mask in the corresponding 8-bit element of "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_shuffle_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_shufflehi_epi16`

**AVX2 签名**: `__m256i _mm256_shufflehi_epi16(__m256i a, const int imm8)`

**x86 指令**: `VPSHUFHW`

**描述**: Shuffle 16-bit integers in the high 64 bits of 128-bit lanes of "a" using the control in "imm8". Store the results in the high 64 bits of 128-bit lanes of "dst", with the low 64 bits of 128-bit lanes being copied from from "a" to "dst".

**SVE 对应指令**:

1. `svuint16_t sveor[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t sveor[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t sveor[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t sveor[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t sveor[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_shufflehi_epi16
// SVE: sveor[_u16]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_shufflelo_epi16`

**AVX2 签名**: `__m256i _mm256_shufflelo_epi16(__m256i a, const int imm8)`

**x86 指令**: `VPSHUFLW`

**描述**: Shuffle 16-bit integers in the low 64 bits of 128-bit lanes of "a" using the control in "imm8". Store the results in the low 64 bits of 128-bit lanes of "dst", with the high 64 bits of 128-bit lanes being copied from from "a" to "dst".

**SVE 对应指令**:

1. `svuint16_t sveor[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t sveor[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t sveor[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t sveor[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t sveor[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_shufflelo_epi16
// SVE: sveor[_u16]_m(svptrue_b8(), a, imm8)
```

---

### `_mm256_unpackhi_epi16`

**AVX2 签名**: `__m256i _mm256_unpackhi_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKHWD`

**描述**: Unpack and interleave 16-bit integers from the high half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpackhi_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpackhi_epi32`

**AVX2 签名**: `__m256i _mm256_unpackhi_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKHDQ`

**描述**: Unpack and interleave 32-bit integers from the high half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpackhi_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpackhi_epi64`

**AVX2 签名**: `__m256i _mm256_unpackhi_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKHQDQ`

**描述**: Unpack and interleave 64-bit integers from the high half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpackhi_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpackhi_epi8`

**AVX2 签名**: `__m256i _mm256_unpackhi_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKHBW`

**描述**: Unpack and interleave 8-bit integers from the high half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpackhi_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpacklo_epi16`

**AVX2 签名**: `__m256i _mm256_unpacklo_epi16(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKLWD`

**描述**: Unpack and interleave 16-bit integers from the low half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint16_t svand[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t svand[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t svand[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t svand[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t svand[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpacklo_epi16
// SVE: svand[_u16]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpacklo_epi32`

**AVX2 签名**: `__m256i _mm256_unpacklo_epi32(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKLDQ`

**描述**: Unpack and interleave 32-bit integers from the low half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpacklo_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpacklo_epi64`

**AVX2 签名**: `__m256i _mm256_unpacklo_epi64(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKLQDQ`

**描述**: Unpack and interleave 64-bit integers from the low half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint64_t svand[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t svand[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t svand[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t svand[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t svand[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpacklo_epi64
// SVE: svand[_u64]_m(svptrue_b8(), a, b)
```

---

### `_mm256_unpacklo_epi8`

**AVX2 签名**: `__m256i _mm256_unpacklo_epi8(__m256i a, __m256i b)`

**x86 指令**: `VPUNPCKLBW`

**描述**: Unpack and interleave 8-bit integers from the low half of each 128-bit lane in "a" and "b", and store the results in "dst".

**SVE 对应指令**:

1. `svuint8_t svand[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t svand[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t svand[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t svand[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t svand[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm256_unpacklo_epi8
// SVE: svand[_u8]_m(svptrue_b8(), a, b)
```

---

### `_mm_blend_epi32`

**AVX2 签名**: `__m128i _mm_blend_epi32(__m128i a, __m128i b, const int imm8)`

**x86 指令**: `VPBLENDD`

**描述**: Blend packed 32-bit integers from "a" and "b" using control mask "imm8", and store the results in "dst".

**SVE 对应指令**:

1. `svuint32_t svand[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t svand[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t svand[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t svand[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t svand[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_blend_epi32
// SVE: svand[_u32]_m(svptrue_b8(), a, b)
```

---

### `_mm_broadcastb_epi8`

**AVX2 签名**: `__m128i _mm_broadcastb_epi8(__m128i a)`

**x86 指令**: `VPBROADCASTB`

**描述**: Broadcast the low packed 8-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint8_t sveor[_u8]_m(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
2. `svuint8_t sveor[_u8]_x(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
3. `svuint8_t sveor[_u8]_z(svbool_t pg, svuint8_t op1, svuint8_t op2)` — SME and SME2, SVE
4. `svuint8_t sveor[_n_u8]_m(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE
5. `svuint8_t sveor[_n_u8]_x(svbool_t pg, svuint8_t op1, uint8_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_broadcastb_epi8
// SVE: sveor[_u8]_m(svptrue_b8(), a)
```

---

### `_mm_broadcastd_epi32`

**AVX2 签名**: `__m128i _mm_broadcastd_epi32(__m128i a)`

**x86 指令**: `VPBROADCASTD`

**描述**: Broadcast the low packed 32-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint32_t sveor[_u32]_m(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
2. `svuint32_t sveor[_u32]_x(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
3. `svuint32_t sveor[_u32]_z(svbool_t pg, svuint32_t op1, svuint32_t op2)` — SME and SME2, SVE
4. `svuint32_t sveor[_n_u32]_m(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE
5. `svuint32_t sveor[_n_u32]_x(svbool_t pg, svuint32_t op1, uint32_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_broadcastd_epi32
// SVE: sveor[_u32]_m(svptrue_b8(), a)
```

---

### `_mm_broadcastq_epi64`

**AVX2 签名**: `__m128i _mm_broadcastq_epi64(__m128i a)`

**x86 指令**: `VPBROADCASTQ`

**描述**: Broadcast the low packed 64-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint64_t sveor[_u64]_m(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
2. `svuint64_t sveor[_u64]_x(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
3. `svuint64_t sveor[_u64]_z(svbool_t pg, svuint64_t op1, svuint64_t op2)` — SME and SME2, SVE
4. `svuint64_t sveor[_n_u64]_m(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE
5. `svuint64_t sveor[_n_u64]_x(svbool_t pg, svuint64_t op1, uint64_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_broadcastq_epi64
// SVE: sveor[_u64]_m(svptrue_b8(), a)
```

---

### `_mm_broadcastsd_pd`

**AVX2 签名**: `__m128d _mm_broadcastsd_pd(__m128d a)`

**x86 指令**: `MOVDDUP`

**描述**: Broadcast the low double-precision (64-bit) floating-point element from "a" to all elements of "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm_broadcastsi128_si256`

**AVX2 签名**: `__m256i _mm_broadcastsi128_si256(__m128i a)`

**x86 指令**: `VBROADCASTI128`

**描述**: Broadcast 128 bits of integer data from "a" to all 128-bit lanes in "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm_broadcastss_ps`

**AVX2 签名**: `__m128 _mm_broadcastss_ps(__m128 a)`

**x86 指令**: `VBROADCASTSS`

**描述**: Broadcast the low single-precision (32-bit) floating-point element from "a" to all elements of "dst".

**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON

---

### `_mm_broadcastw_epi16`

**AVX2 签名**: `__m128i _mm_broadcastw_epi16(__m128i a)`

**x86 指令**: `VPBROADCASTW`

**描述**: Broadcast the low packed 16-bit integer from "a" to all elements of "dst".

**SVE 对应指令**:

1. `svuint16_t sveor[_u16]_m(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
2. `svuint16_t sveor[_u16]_x(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
3. `svuint16_t sveor[_u16]_z(svbool_t pg, svuint16_t op1, svuint16_t op2)` — SME and SME2, SVE
4. `svuint16_t sveor[_n_u16]_m(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE
5. `svuint16_t sveor[_n_u16]_x(svbool_t pg, svuint16_t op1, uint16_t op2)` — SME and SME2, SVE

**迁移示例** (假设 VL=256-bit):
```c
// AVX2: _mm_broadcastw_epi16
// SVE: sveor[_u16]_m(svptrue_b8(), a)
```

---

