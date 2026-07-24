
cmake_minimum_required(VERSION 3.16)

# Project name
project(OmniStream)
set(CMAKE_VERBOSE_MAKEFILE ON)

# ccache 加速增量编译(自动探测, 未装则 no-op; 仅作编译启动器, 不影响产物)
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
    message(STATUS "Using ccache: ${CCACHE_PROGRAM}")
endif()

set(CMAKE_CXX_STANDARD 17)
if(DEFINED ENV{OMNI_HOME})
    set(CMAKE_INSTALL_PREFIX $ENV{OMNI_HOME} CACHE PATH "Install path prefix" FORCE)
endif()
option(WITH_OMNISTATESTORE "Enable to build with OmniStateStore" OFF)
add_library(project_config INTERFACE)
if(WITH_OMNISTATESTORE)
    target_compile_definitions(project_config INTERFACE WITH_OMNISTATESTORE)
endif()
# 批量安装全部头文件到 include/(保留子目录结构; .h + .hpp; 排除 build/ 生成文件)
# 替代原 6 个 install(DIRECTORY) + install_headers() 逐文件安装 —— 后者对上千头文件各生成一条 install(FILES) 规则, make install 末尾逐个 cp 卡死
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/ DESTINATION include
        FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
        PATTERN "build" EXCLUDE)
message(STATUS "CMAKE_INSTALL_PREFIX is.   ${CMAKE_INSTALL_PREFIX}")

# third party for data stream
include_directories(include)
install(DIRECTORY conf/ DESTINATION ${CMAKE_INSTALL_PREFIX}/conf)


# 头文件已由上方 install(DIRECTORY) 批量装到 include/(原 install_headers() 逐文件装到 OmniStream/ 的逻辑已移除: 慢 + 无消费方引用该路径)

option(FLAME_GRAPH "Enable settings for capturing flame graphs." OFF)
option(SVE "Enable SVE instruction set" OFF)

if (SVE)
    include(CheckCXXCompilerFlag)

    # Check if the compiler supports SVE
    check_cxx_compiler_flag("-march=armv8-a+sve -msve-vector-bits=256" COMPILER_SUPPORTS_SVE)

    if (COMPILER_SUPPORTS_SVE)
        message(STATUS "Compiling with SVE support.")
    else ()
        message(FATAL_ERROR "Compiler does not support SVE.")
    endif ()
endif ()


if (FLAME_GRAPH)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -fno-omit-frame-pointer")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g -fno-omit-frame-pointer")
endif ()

###### Third party Dependency

##### nlohmann ############
#########################

# path for nlohmann
# list(APPEND CMAKE_PREFIX_PATH "/opt/nlohmann" "/opt/googletest/build")
# include_directories("/opt/nlohmann/include")


##### JNI #################
###########################
##### require JAVA_HOME ####

find_package(JNI REQUIRED)

find_library(JEMALLOC_LIB jemalloc)
# Optional
find_path(JEMALLOC_INCLUDE_DIR jemalloc/jemalloc.h)

set (JEMALLOC_LIB "")
if (JEMALLOC_LIB)
    message(STATUS "jemalloc found at ${JEMALLOC_LIB}")

    # Add jemalloc include directory if needed
    if (JEMALLOC_INCLUDE_DIR)
        include_directories(${JEMALLOC_INCLUDE_DIR})
    endif()

    # Set LD_PRELOAD for jemalloc
    set(ENV{LD_PRELOAD} ${JEMALLOC_LIB} $ENV{LD_PRELOAD})
else()
    message(STATUS "jemalloc not found, proceeding without it")
endif()


##### LLVM ################
###########################
# Find LLVM
# Please set path to your LLVM-description.cmake for cmake to find it
# set(LLVM_DIR "/home/xichen/opt/llvm-project/build/lib/cmake/llvm")
find_package(LLVM REQUIRED CONFIG)
include_directories(${LLVM_INCLUDE_DIRS})
link_directories("${LLVM_INCLUDE_DIRS}/../lib")

##### Build Type #################
### Default - no build type is release

if (DEFINED COVERAGE)
    if (${COVERAGE} STREQUAL "ON")
        #        set(DEBUG_COMPILE_LEVEL "-O2 -fsanitize=address -fsanitize-recover=address,all -static-libasan")
        set(DEBUG_COMPILE_LEVEL "-O0 -fsanitize=address -fsanitize-recover=address,all")
        if (DEFINED ENABLE_DT AND ENABLE_DT STREQUAL "ON")
            set(DEBUG_COMPILE_LEVEL "-fsanitize=address -fsanitize-coverage=trace-pc")
        endif ()
    else ()
        set(DEBUG_COMPILE_LEVEL "-O0")
    endif ()
elseif(DEFINED TRACE)
    set(DEBUG_COMPILE_LEVEL "-O3 -s")
else ()
    set(DEBUG_COMPILE_LEVEL "-O0")
endif ()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fpermissive")
if(CMAKE_BUILD_TYPE MATCHES Debug)
    message(STATUS "Building with Debug Mode")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${DEBUG_COMPILE_LEVEL} -DDEBUG")
elseif (CMAKE_BUILD_TYPE MATCHES CPP_E2E)
    message(STATUS "Building with Debug Mode and enable E2E test exporting")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DDEBUG")
    add_compile_definitions(CPP_E2E)
elseif (CMAKE_BUILD_TYPE MATCHES COVERAGE_TEST)
    message(STATUS "Building with coverage  Mode")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${DEBUG_COMPILE_LEVEL} -fprofile-arcs -ftest-coverage")
elseif (CMAKE_BUILD_TYPE MATCHES PERF_TEST)
    message(STATUS "Building with Performance mode but with fake operator")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
    add_compile_definitions(PERF_TEST)
else()
    message(STATUS "Building with Performance  Mode")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
endif()

# Adding Secure Compiler Options
set(CMAKE_SKIP_RPATH TRUE)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} -lrt -fno-var-tracking-assignments -pipe -g -Wall -fPIC -fno-omit-frame-pointer -fno-common -fno-stack-protector")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} -lrt -fno-var-tracking-assignments -Wno-terminate -Wno-delete-incomplete -pipe -Wall -Wno-strict-aliasing -Wtrampolines -D_FORTIFY_SOURCE=2 -fPIC -finline-functions -fstack-protector-strong -s -Wl,-z,noexecstack -Wl,-z,relro,-z,now -finline-limit=6000 --param inline-unit-growth=300")
add_compile_options("-march=armv8-a+sve")

# Default including directory
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/core/include/" "${CMAKE_CURRENT_SOURCE_DIR}"
        "${CMAKE_CURRENT_SOURCE_DIR}/codegen/"
        "${CMAKE_CURRENT_SOURCE_DIR}/core/"
        "${CMAKE_CURRENT_SOURCE_DIR}/expression/"
        "${CMAKE_CURRENT_SOURCE_DIR}/jni/"
        "${CMAKE_CURRENT_SOURCE_DIR}/runtime/"
        "${CMAKE_CURRENT_SOURCE_DIR}/streaming/"
        "${CMAKE_CURRENT_SOURCE_DIR}/table/"
        "${CMAKE_CURRENT_SOURCE_DIR}/connector/"
        # "${CMAKE_CURRENT_SOURCE_DIR}/util/"
)

# set directory for OmniRuntime: we assume OmniRuntime is installed in HOME now. and omniruntime library is in /opt


# Assume contain will have and only container has /repo dur
set(CONTAINER_DIR "/repo")

if(EXISTS "${CONTAINER_DIR}")
    set(OMNIRUNTIME_DIR "$ENV{OMNI_HOME}")
    set(OMNIRUNTIME_LIB_DIR "${OMNIRUNTIME_DIR}/lib")
    set(OMNIRUNTIME_SRC_DIR "/repo/codehub")
else()
    set(OMNIRUNTIME_DIR "$ENV{HOME}")
    set(OMNIRUNTIME_LIB_DIR "${OMNIRUNTIME_DIR}/opt/lib")
    set(OMNIRUNTIME_SRC_DIR "${OMNIRUNTIME_DIR}")
endif()

include_directories("${OMNIRUNTIME_SRC_DIR}/")
include_directories("${OMNIRUNTIME_SRC_DIR}/OmniOperatorJIT/")
include_directories("${OMNIRUNTIME_SRC_DIR}/OmniOperatorJIT/core")
include_directories("${OMNIRUNTIME_SRC_DIR}/OmniOperatorJIT/core/src")


OPTION(ENABLE_ORT_1_7 "Enable Using OmniRuntime 1.7.0" OFF)

if(ENABLE_ORT_1_7)
    set(ORT_VEC_SO boostkit-omniop-vector-1.7.0-aarch64)
    set(ORT_CODEGEN_SO boostkit-omniop-codegen-1.7.0-aarch64)
    set(ORT_OP_SO boostkit-omniop-operator-1.7.0-aarch64)
else ()
    set(ORT_VEC_SO boostkit-omniop-vector-2.2.0-aarch64)
    set(ORT_CODEGEN_SO boostkit-omniop-codegen-2.2.0-aarch64)
    set(ORT_OP_SO boostkit-omniop-operator-2.2.0-aarch64)
endif()

option(ENABLE_TSHOOT "Enable trouble shooting macro" OFF)

if(ENABLE_TSHOOT)
    add_definitions(-DTROUBLE_SHOOTING=1) # or whatever value you need
endif()


MESSAGE(STATUS "OmniRuntime Dir ${OMNIRUNTIME_DIR} ${OMNIRUNTIME_LIB_DIR} ${OMNIRUNTIME_SRC_DIR}")
# common libraries for all modules
add_subdirectory(translate/basictypes)
add_subdirectory(translate/functions)
add_subdirectory(translate/thirdlibrary)
add_subdirectory(core)
add_subdirectory(table)
add_subdirectory(jni)
add_subdirectory(runtime)
add_subdirectory(datagen)
# /streaming and /util has no cpp yet. There's no need to add this subdirectory
add_subdirectory(streaming)
# add_subdirectory(util)
# add_subdirectory(zemo)
add_subdirectory(connector)

# Use OmniOperatorJIT's codegen and expression instead
# add_subdirectory(codegen)
# add_subdirectory(expression)

option(ENABLE_TESTS "Provide unit tests" ON)
if (ENABLE_TESTS)
    add_subdirectory(test)
endif ()

enable_testing()

message(STATUS "Compiler options: ${CMAKE_CXX_FLAGS}")