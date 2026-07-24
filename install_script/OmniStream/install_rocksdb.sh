cd /opt/buildtools
git clone https://github.com/facebook/rocksdb.git
cd /opt/buildtools/rocksdb && git checkout tags/v8.11.4
mkdir -p /opt/buildtools/rocksdb/build && cd /opt/buildtools/rocksdb/build
cmake .. -DWITH_SNAPPY=1 -DCMAKE_BUILD_TYPE=Release -DUSE_RTTI=1 -DWITH_GFLAGS=0
make -j && make install