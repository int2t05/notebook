cd /opt/buildtools
# 安装abseil-cpp
git clone https://gitee.com/mirrors/abseil-cpp.git && cd abseil-cpp && git checkout tags/20250127.0
mkdir -p build && cd build && cmake .. -DCMAKE_CXX_STANDARD=17 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DABSL_PROPAGATE_CXX_STD=ON -DBUILD_SHARED_LIBS=OFF -DCMAKE_POSITION_INDEPENDENT_CODE=ON && make install -j8
# 安装re2
git clone https://gitee.com/mirrors/re2.git && cd re2 && git checkout tags/2024-07-02
mkdir build && cd build
cmake .. -DCMAKE_CXX_STANDARD=17 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_CXX_FLAGS="-fPIC"
make install -j8