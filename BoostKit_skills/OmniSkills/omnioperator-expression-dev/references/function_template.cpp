/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2026-2026. All rights reserved.
 * Description: Template for function implementation (.cpp)
 *
 * .cpp files are needed when:
 *   1. The function uses the VectorFunction path (Path B) with custom Apply() logic
 *   2. The function has complex logic not suitable for header-only templates
 *   3. The function needs template helper methods with explicit instantiation
 *
 * Simple functions (arithmetic, math, bitwise) are often header-only and
 * registered via the SimpleFunction path (Path A) — they don't need .cpp files.
 */

#include "vectorization/functions/<FunctionName>.h"
#include "vectorization/VectorFunction.h"
#include "vectorization/SelectivityVector.h"
#include "vector/vector_helper.h"
#include "util/bit_util.h"

namespace omniruntime::vectorization {
using namespace omniruntime::vec;
using namespace omniruntime::type;

// ============================================================================
// Pattern A: VectorFunction with Apply() override
//   Used for functions that need custom batch-level processing.
//   Registered via VectorFunction::RegisterVectorFunction() (Path B).
// ============================================================================

namespace {
class <FunctionName>Impl : public VectorFunction {
public:
    void Apply(std::stack<BaseVector *> &args, const DataTypePtr &outputType,
        BaseVector *&result, op::ExecutionContext *context) const override
    {
        // 1. Pop arguments from stack (right-to-left order)
        auto rightArg = args.top();
        args.pop();
        auto leftArg = args.top();
        args.pop();

        auto rowSize = context->GetResultRowSize();

        // 2. Create result vector
        if (result == nullptr) {
            result = VectorHelper::CreateFlatVector(outputType->GetId(), rowSize);
        }

        // 3. Get raw value pointers for fast access
        auto *resultVector = static_cast<Vector<ResultType>*>(result);
        auto *resultRaw = unsafe::UnsafeVector::GetRawValues(resultVector);
        auto *leftVector = static_cast<Vector<InputType>*>(leftArg);
        const auto *leftRaw = unsafe::UnsafeVector::GetRawValues(leftVector);

        // 4. Copy null bits from input to result
        const auto *inputNulls = reinterpret_cast<uint64_t *>(
            unsafe::UnsafeBaseVector::GetNulls(leftArg));
        auto *resultNulls = reinterpret_cast<uint64_t *>(
            unsafe::UnsafeBaseVector::GetNulls(result));
        memcpy(resultNulls, inputNulls, BitUtil::Nbytes(rowSize));

        // 5. Process only non-null rows using SelectivityVector
        SelectivityVector rows(rowSize);
        rows.setFromBitsNegate(inputNulls, rowSize);

        rows.applyToSelected([&](vector_size_t i) {
            resultRaw[i] = /* computation with leftRaw[i] */;
            result->SetNotNull(i);
        });

        // 6. Cleanup input vectors
        delete leftArg;
        delete rightArg;
    }
};
} // namespace

// Registration function called from Register<Category>Functions
void Register<FunctionName>Function(const std::string &name)
{
    VectorFunction::RegisterVectorFunction(name,
        {OMNI_INPUT_TYPE}, OMNI_RESULT_TYPE,
        std::make_shared<<FunctionName>Impl>());
}

// ============================================================================
// Pattern B: Template helper methods with explicit instantiation
//   Used when Apply() dispatches to type-specific template methods.
// ============================================================================

// Template method definition (declared in .h)
// template <typename T>
// void <FunctionName>::ProcessData(BaseVector *input, BaseVector *&result,
//     int32_t rowSize, DataTypeId typeId) const
// {
//     auto *inputVec = static_cast<Vector<T>*>(input);
//     // ... implementation
// }

// Explicit template instantiation at end of file
// template void <FunctionName>::ProcessData<int8_t>(BaseVector *, BaseVector *&, int32_t, DataTypeId) const;
// template void <FunctionName>::ProcessData<int16_t>(BaseVector *, BaseVector *&, int32_t, DataTypeId) const;
// template void <FunctionName>::ProcessData<int32_t>(BaseVector *, BaseVector *&, int32_t, DataTypeId) const;
// template void <FunctionName>::ProcessData<int64_t>(BaseVector *, BaseVector *&, int32_t, DataTypeId) const;

} // namespace omniruntime::vectorization
