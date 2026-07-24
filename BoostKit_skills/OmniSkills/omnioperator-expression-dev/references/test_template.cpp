/*
* Copyright (c) Huawei Technologies Co., Ltd. 2026-2026. All rights reserved.
* Description: Unit test template for vectorized functions
*/

#include <gtest/gtest.h>
#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <limits>

#include "test/util/test_util.h"
#include "vectorization/registration/Register.h"
#include "vectorization/ExprEval.h"
#include "vectorization/VectorFunction.h"
#include "expression/expressions.h"
#include "type/data_type.h"
#include "vector/vector_helper.h"
// Include the specific function header if directly testing the function class:
// #include "vectorization/functions/<FunctionName>.h"

using namespace omniruntime;
using namespace omniruntime::vec;
using namespace omniruntime::vectorization;
using namespace omniruntime::op;
using namespace omniruntime::expressions;
using namespace omniruntime::TestUtil;

// ============================================================================
// Registration setup (choose one):
//
// Option A: Global test environment (recommended, registers once for all tests)
// ============================================================================
class <FunctionName>TestEnvironment : public ::testing::Environment {
public:
    void SetUp() override {
        RegisterFunctions::RegisterAllFunctions("");
    }
};
::testing::Environment* const <function_name>_test_env =
    ::testing::AddGlobalTestEnvironment(new <FunctionName>TestEnvironment);

// Option B: Test fixture with SetUp (if you need per-test setup)
// ============================================================================
// class <FunctionName>Test : public ::testing::Test {
// protected:
//     void SetUp() override {
//         RegisterFunctions::RegisterAllFunctions("");
//     }
// };

// ============================================================================
// Pattern 1: ExprEval path — most common, tests end-to-end expression evaluation
//   Use this for: arithmetic, bitwise, comparison, conditional functions
// ============================================================================

TEST(VectorizationTest, <FunctionName>Basic) {
    int rowSize = 8;

    // 1. Define types
    auto type = std::make_shared<DataType>(OMNI_<TYPE>);

    // 2. Build expression tree
    //    Unary:  {new FieldExpr(0, type)}
    //    Binary: {new FieldExpr(0, type), new FieldExpr(1, type)}
    std::vector<Expr*> args = {new FieldExpr(0, type), new FieldExpr(1, type)};
    auto funcExpr = new FuncExpr("<function_name>", args, type);

    // 3. Verify function is registered
    ASSERT_NE(funcExpr->vectorFunction, nullptr);

    // 4. Create input data and VectorBatch
    <CppType> col1[rowSize] = { /* input values */ };
    <CppType> col2[rowSize] = { /* input values */ };
    std::vector<std::shared_ptr<DataType>> vecOfTypes = {type, type};
    DataTypes inputTypes(vecOfTypes);
    VectorBatch* input = CreateVectorBatch(inputTypes, rowSize, col1, col2);

    // 5. Execute via ExprEval
    auto context = new ExecutionContext();
    context->SetResultRowSize(rowSize);
    ExprEval e(input, context);
    e.Visit(*funcExpr);
    auto result = e.GetResult();

    // 6. Assert results
    auto* resultVector = dynamic_cast<Vector<<CppType>>*>(result);
    ASSERT_NE(resultVector, nullptr);
    EXPECT_EQ(resultVector->GetValue(0), /* expected */);

    // 7. Cleanup
    delete input;
    delete funcExpr;
    delete context;
}

TEST(VectorizationTest, <FunctionName>NullInput) {
    int rowSize = 4;

    auto type = std::make_shared<DataType>(OMNI_<TYPE>);
    std::vector<Expr*> args = {new FieldExpr(0, type), new FieldExpr(1, type)};
    auto funcExpr = new FuncExpr("<function_name>", args, type);

    <CppType> col1[rowSize] = { /* values */ };
    <CppType> col2[rowSize] = { /* values */ };
    std::vector<std::shared_ptr<DataType>> vecOfTypes = {type, type};
    DataTypes inputTypes(vecOfTypes);
    VectorBatch* input = CreateVectorBatch(inputTypes, rowSize, col1, col2);

    // Set null at specific positions
    input->Get(0)->SetNull(1);

    auto context = new ExecutionContext();
    context->SetResultRowSize(rowSize);
    ExprEval e(input, context);
    e.Visit(*funcExpr);
    auto result = e.GetResult();

    auto* resultVector = dynamic_cast<Vector<<CppType>>*>(result);
    EXPECT_TRUE(resultVector->IsNull(1));

    delete input;
    delete funcExpr;
    delete context;
}

// ============================================================================
// Pattern 2: VectorFunction::Find + Apply — direct function testing without ExprEval
//   Use this for: math functions, date functions, and when you need precise
//   control over input vectors (e.g., NaN/Inf testing, custom vector construction)
// ============================================================================

TEST(VectorizationTest, <FunctionName>Direct) {
    int rowSize = 4;
    DataTypeId typeId = OMNI_<TYPE>;

    // 1. Create input vectors via VectorHelper
    BaseVector* rawInput = VectorHelper::CreateFlatVector(typeId, rowSize);
    auto* inputVector = static_cast<Vector<<CppType>>*>(rawInput);
    <CppType> inputData[rowSize] = { /* values */ };
    for (int32_t i = 0; i < rowSize; ++i) {
        inputVector->SetValue(i, inputData[i]);
        inputVector->SetNotNull(i);
    }

    // 2. Lookup function via FunctionSignature
    auto signature = std::make_shared<FunctionSignature>(
        "<function_name>",
        std::vector<DataTypeId>{OMNI_<TYPE>},  // arg types
        typeId                                   // return type
    );
    auto vectorFunction = VectorFunction::Find(signature);
    ASSERT_NE(vectorFunction, nullptr);

    // 3. Execute via Apply
    ExecutionContext context;
    context.SetResultRowSize(rowSize);
    std::stack<BaseVector*> args;
    args.push(rawInput);
    BaseVector* rawResult = nullptr;
    auto resultType = std::make_shared<DataType>(typeId);
    vectorFunction->Apply(args, resultType, rawResult, &context);

    // 4. Verify (use EXPECT_NEAR for floating point)
    auto* resultVector = static_cast<Vector<<CppType>>*>(rawResult);
    EXPECT_EQ(resultVector->GetValue(0), /* expected */);

    delete rawResult;
}

// ============================================================================
// Pattern 3: String function testing — uses VarcharVector and string_view
// ============================================================================

// TEST(VectorizationTest, <StringFunctionName>Basic) {
//     using VarcharVector = Vector<LargeStringContainer<std::string_view>>;
//
//     int rowSize = 4;
//     BaseVector* inputVec = VectorHelper::CreateFlatVector(OMNI_VARCHAR, rowSize);
//     auto* inputVector = dynamic_cast<VarcharVector*>(inputVec);
//     std::string values[] = { "hello", "world", "test", "" };
//     for (int32_t i = 0; i < rowSize; ++i) {
//         std::string_view lsv(values[i]);
//         inputVector->SetValue(i, lsv);
//         inputVector->SetNotNull(i);
//     }
//
//     auto signature = std::make_shared<FunctionSignature>(
//         "<function_name>", {OMNI_VARCHAR}, OMNI_VARCHAR);
//     auto vectorFunction = VectorFunction::Find(signature);
//     ASSERT_NE(vectorFunction, nullptr);
//
//     ExecutionContext context;
//     context.SetResultRowSize(rowSize);
//     std::stack<BaseVector*> args;
//     args.push(inputVec);
//     BaseVector* result = nullptr;
//     auto resultType = std::make_shared<DataType>(OMNI_VARCHAR);
//     vectorFunction->Apply(args, resultType, result, &context);
//
//     auto* resultVector = dynamic_cast<VarcharVector*>(result);
//     std::string actual(resultVector->GetValue(0));
//     EXPECT_EQ(actual, /* expected */);
//
//     delete result;
// }
