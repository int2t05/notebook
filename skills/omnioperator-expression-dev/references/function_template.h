/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2026-2026. All rights reserved.
 * Description: Template for function implementation (.h)
 */

#pragma once
#include "util/compiler_util.h"
#include "vectorization/Status.h"
#include <cmath>

namespace omniruntime::vectorization {

// ============================================================================
// Pattern 1: Status-returning call() — used by arithmetic, math, bitwise, etc.
//   - Returns Status::OK() on success, Status::UserError(...) on error.
//   - Null inputs are handled by the vector framework (not in function body).
// ============================================================================

// Unary function (e.g., Abs, Ceil, Floor)
template <typename T>
struct UnaryFunctionTemplate {
    template <typename TInput>
    ALWAYS_INLINE Status call(TInput& result, const TInput& input)
    {
        result = /* computation with input */;
        return Status::OK();
    }
};

// Binary function (e.g., Plus, BitwiseAnd, Mod)
template <typename T>
struct BinaryFunctionTemplate {
    template <typename TInput>
    ALWAYS_INLINE Status call(TInput& result, const TInput& left, const TInput& right)
    {
        result = /* computation with left and right */;
        return Status::OK();
    }
};

// Ternary function (e.g., Substr with 3 args, Round with scale)
template <typename T>
struct TernaryFunctionTemplate {
    template <typename TResult, typename TInput1, typename TInput2, typename TInput3>
    ALWAYS_INLINE Status call(TResult& result, const TInput1& input1, const TInput2& input2, const TInput3& input3)
    {
        result = /* computation with input1, input2, and input3 */;
        return Status::OK();
    }
};

// ============================================================================
// Pattern 2: bool-returning call() — used by string/comparison functions.
//   - Returns true when result is valid, false means NULL output.
//   - The bool return value becomes the null flag in the output vector.
// ============================================================================

template <typename T>
struct BoolReturnFunctionTemplate {
    ALWAYS_INLINE bool call(bool& result, const std::string_view& input1, const std::string_view& input2)
    {
        // Return false to signal NULL output
        result = /* computation */;
        return true; // or false for NULL
    }
};

// ============================================================================
// Pattern 3: callNullable() — for functions that inspect null inputs directly.
//   - Input pointers are nullable: const T* (nullptr means NULL input).
//   - Returns true when result is valid, false means NULL output.
// ============================================================================

template <typename T>
struct NullableFunctionTemplate {
    ALWAYS_INLINE bool callNullable(std::string& result, const std::string_view* input)
    {
        if (input == nullptr) {
            return false; // NULL input -> NULL output
        }
        result = /* computation with *input */;
        return true;
    }
};

// ============================================================================
// Pattern 4: void-returning call() — always produces non-NULL result.
//   - The framework treats the result as always valid (notNull = true).
// ============================================================================

template <typename T>
struct VoidReturnFunctionTemplate {
    template <typename TInput>
    ALWAYS_INLINE void call(TInput& result, const TInput& input)
    {
        result = /* computation — result is always valid */;
    }
};

} // namespace omniruntime::vectorization
