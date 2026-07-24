# OmniOperator Project Structure Reference

## Directory Layout

> **IMPORTANT:** The directory layout below represents the structure at the time
> this skill was last updated. Before creating files, ALWAYS verify the target
> directory exists using `glob` or `ls`. If a directory does not exist, create it
> with `mkdir -p` and note this in your design document.

```
<project_root>/                        # Actual root directory varies by environment
├── OmniOperator/                      # Main project
│   ├── core/
│   │   ├── src/vectorization/
│   │   │   ├── functions/            # Function implementations (.h/.cpp)
│   │   │   │   ├── Arithmetic.h      # Basic arithmetic (+, -, *, /)
│   │   │   │   ├── MathFunctions.h   # Math functions (sin, cos, sqrt, etc.)
│   │   │   │   ├── Bitwise.h         # Bitwise operations
│   │   │   │   ├── Comparisons.h     # Comparison operators
│   │   │   │   ├── String.h          # String operations
│   │   │   │   ├── Cast.h            # Type cast/conversion
│   │   │   │   ├── Coalesce.h        # Conditional (coalesce, if, isnull, in)
│   │   │   │   ├── AddMonths.h       # Date/time functions (30+ files)
│   │   │   │   ├── ArrayAppendFunction.h  # Array functions (30+ files)
│   │   │   │   ├── MapFunction.h     # Map functions
│   │   │   │   ├── FromJson.h        # JSON functions
│   │   │   │   ├── RegexpExtract.h   # Regex functions
│   │   │   │   ├── GetStructField.h  # Struct functions
│   │   │   │   └── ...               # Other function categories
│   │   │   ├── registration/         # Function registration files
│   │   │   │   ├── Register.h/.cpp   # Main registration entry
│   │   │   │   ├── RegisterMath.cpp
│   │   │   │   ├── RegisterBitwise.cpp
│   │   │   │   ├── RegisterString.cpp
│   │   │   │   ├── RegisterArray.cpp
│   │   │   │   ├── RegisterComparison.cpp
│   │   │   │   ├── RegisterConditional.cpp
│   │   │   │   ├── RegisterConversion.cpp
│   │   │   │   ├── RegisterDateTime.cpp
│   │   │   │   ├── RegisterHash.cpp
│   │   │   │   ├── RegisterJson.cpp
│   │   │   │   ├── RegisterLambda.cpp
│   │   │   │   ├── RegisterMap.cpp
│   │   │   │   ├── RegisterMisc.cpp
│   │   │   │   ├── RegisterPredicate.cpp
│   │   │   │   ├── RegisterRegexp.cpp
│   │   │   │   ├── RegisterStruct.cpp
│   │   │   │   ├── RegisterCollection.cpp
│   │   │   │   ├── RegistrationHelpers.h
│   │   │   │   └── SimpleFunctionRegistry.h/.cpp
│   │   │   ├── ExprEval.h/.cpp       # Expression evaluator
│   │   │   ├── SimpleFunction.h       # Simple function base
│   │   │   ├── VectorFunction.h/.cpp  # Vector function base
│   │   │   ├── Status.h/.cpp          # Status and error handling
│   │   │   └── SelectivityVector.h/.cpp
│   │   ├── src/vector/               # Vector data containers
│   │   ├── src/expression/           # Expression parsing
│   │   ├── src/type/                 # Type definitions (DataType, DataTypeId)
│   │   └── test/vectorization/       # Unit tests (120+ files)
│   │       ├── MathFunctionTest.cpp
│   │       ├── BitwiseTest.cpp
│   │       ├── DateAddTest.cpp
│   │       ├── ArrayFunctionTest.cpp
│   │       └── ...
│   └── docs/
│       └── expression-design/        # Design documents go here
├── Gluten/                            # Spark integration layer
│   ├── backends-omni/                # OmniOperator backend for Spark
│   ├── cpp-omni/                     # C++ native layer for Omni
│   └── gluten-substrait/             # Substrait plan conversion
└── velox/                             # Reference implementation
    └── velox/functions/
        ├── lib/                      # Shared implementation utilities
        ├── prestosql/
        │   ├── registration/
        │   └── ...
        └── sparksql/
            ├── registration/
            └── ...
```

## Registration File Mapping

> **IMPORTANT:** The mapping table below reflects the project structure at the
> time this skill was last updated. The project may have evolved since then. Use
> this table as a reference, but ALWAYS verify against the actual codebase by
> running `grep` for similar functions in `Register*.cpp` files. If there is any
> inconsistency, trust the actual code over this table.

| Function Type | Registration File |
|---------------|-------------------|
| Add, Subtract, Multiply, Divide | `RegisterMath.cpp` |
| Modulo, Remainder, Div | `RegisterMath.cpp` |
| Abs, Sign, Positive, Negative | `RegisterMath.cpp` |
| Round, Ceil, Floor, Rint | `RegisterMath.cpp` |
| Sin, Cos, Tan, Sqrt, Exp, Log, etc. | `RegisterMath.cpp` |
| Pmod, Power, Hypot | `RegisterMath.cpp` |
| Bitwise AND, OR, XOR, NOT | `RegisterBitwise.cpp` |
| ShiftLeft, ShiftRight | `RegisterBitwise.cpp` |
| BitCount, BitGet | `RegisterBitwise.cpp` |
| String operations (concat, substr, etc.) | `RegisterString.cpp` |
| Array operations (append, sort, etc.) | `RegisterArray.cpp` |
| Map operations | `RegisterMap.cpp` |
| Comparison (<, >, =, !=, etc.) | `RegisterComparison.cpp` |
| Conditional (coalesce, if, isnull, in) | `RegisterConditional.cpp` |
| Cast/conversion | `RegisterConversion.cpp` |
| DateTime operations (30+ functions) | `RegisterDateTime.cpp` |
| Hash (sha1, sha2, md5, crc32) | `RegisterHash.cpp` |
| JSON operations | `RegisterJson.cpp` |
| Lambda (transform, filter, exists) | `RegisterLambda.cpp` |
| Misc functions (nanvl, isnan, etc.) | `RegisterMisc.cpp` |
| Predicate (and, or, not) | `RegisterPredicate.cpp` |
| Regex (like, rlike, regexp_extract) | `RegisterRegexp.cpp` |
| Struct (get_struct_field, named_struct) | `RegisterStruct.cpp` |
| Collection (size, cardinality, slice, sort_array) | `RegisterCollection.cpp` |

## Registration Architecture

### Two Registration Paths

**Path A — SimpleFunction (most functions):**
Uses `RegisterFunction<>()` which inserts into `simpleFunctionFactoryMap_`.
The function struct is wrapped by `FunctionHolder` -> `SimpleFunctionAdapterFactory` -> `SimpleFunction`.

```cpp
template <template <class> typename Func, typename TReturn, typename... TArgs>
bool RegisterFunction(const std::string &name, std::vector<DataTypeId> paramsType,
    DataTypeId returnType);
```
Note: `Func<TReturn>` is instantiated — `TReturn` fills the dummy template parameter `T`.

**Path B — VectorFunction (complex functions like concat, split, LIKE):**
Uses `VectorFunction::RegisterVectorFunction()` which inserts a pre-built shared_ptr into `functionMap_`.
Used when a function needs custom batch-level processing logic.

### Main Entry Point

```cpp
// Register.cpp
void RegisterFunctions::RegisterAllFunctions(const std::string &prefix) {
    RegisterArrayFunctions(prefix);
    RegisterCompareFunctions(prefix);
    RegisterConditionalFunctions(prefix);
    RegisterConversionFunctions(prefix);
    RegisterDateTimeFunctions(prefix);
    // ... 16 category registration calls total
}
```

Registration also occurs via static initialization (`Register.h`).
For explicit runtime registration, use `link_register_functions()`.

## Common Helper Templates

Located in `RegistrationHelpers.h`:

- `RegisterBinaryIntegral<T>` — Registers for int8_t, int16_t, int32_t, int64_t (same in/out type)
- `RegisterBinaryFloatingPoint<T>` — Registers for float, double
- `RegisterBinaryNumeric<T>` — Both integral + floating point
- `RegisterUnaryIntegral<T>` — Registers for bool only
- `RegisterUnaryIntegralSameType<T>` — Registers for int8..int64, same input/output type
- `RegisterUnaryNumeric<T>` — Integral + floating point + decimal
- `RegisterRoundNumericWithScale<T>` — 2-arg round with scale parameter
- `RegisterString<T>` — Registers for `string_view, string_view -> bool`
- `RegisterCompareIntegral<T>` — Registers for int8..int64 -> bool
- `RegisterFunction<Func, Return, Input...>` — Generic registration (full control)

## Data Type Constants

```cpp
// Boolean
OMNI_BOOLEAN       // bool

// Integers
OMNI_BYTE          // int8_t (tinyint)
OMNI_SHORT         // int16_t (smallint)
OMNI_INT           // int32_t (int)
OMNI_LONG          // int64_t (bigint)

// Floating point
OMNI_FLOAT         // float
OMNI_DOUBLE        // double

// String/Binary
OMNI_VARCHAR       // std::string_view
OMNI_CHAR          // std::string_view
OMNI_VARBINARY     // std::string_view

// Decimal
OMNI_DECIMAL64     // int64_t
OMNI_DECIMAL128    // Decimal128

// Complex types
OMNI_ARRAY         // ArrayVector
OMNI_MAP           // MapVector
```

## Search Patterns

```bash
# Find similar function by name
grep -r "function_name" OmniOperator/core/src/vectorization/

# Find registration for a function
grep -r "prefix + \"function_name\"" OmniOperator/core/src/vectorization/registration/

# Find function implementation
grep -r "FunctionNameFunction" OmniOperator/core/src/vectorization/functions/

# Find tests for a function
grep -r "function_name" OmniOperator/core/test/vectorization/
```

## Velox Reference Search

```bash
# Find function in Velox
find velox/velox/functions -name "*<function>*"

# Search Velox for implementation pattern
grep -r "class.*Function" velox/velox/functions --include="*.cpp" | grep <function_name>

# Shared implementations used by both prestosql and sparksql
ls velox/velox/functions/lib/
```
