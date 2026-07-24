#!/bin/bash
set -e

workspace=$(pwd)
open_source_dir="open_source"
folly_tag="v2024.07.01.00"
folly_repo="https://gitee.com/mirrors/folly.git"
folly_source_dir="${workspace}/${open_source_dir}/folly"
folly_default_home="/usr/local"

echo "Start build folly"
echo "Start to clone folly-${folly_tag} source code and build..."
rm -rf ${folly_source_dir} && mkdir -p ${folly_source_dir}
git clone --branch ${folly_tag} --depth=1 ${folly_repo} ${folly_source_dir}
cd ${folly_source_dir}
mkdir -p build && cd build

cmake ..   -DFOLLY_HAVE_INT128_T=ON   -DBUILD_SHARED_LIBS=OFF   -DBUILD_TESTS=OFF   -DCMAKE_POSITION_INDEPENDENT_CODE=ON

make -j$(nproc)
make install

echo "folly-${folly_tag} build and install completed successfully."
export FOLLY_HOME=${folly_default_home}
echo "Set FOLLY_HOME=$FOLLY_HOME automatically after folly install."

