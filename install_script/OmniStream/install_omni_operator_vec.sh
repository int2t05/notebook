yum install -y double-conversion-devel libevent-devel openssl-devel glog-devel gflags-devel google-benchmark-devel fmt-devel
bash build_folly.sh
mode=$1
cd /opt/buildtools
git clone https://gitcode.com/toljr/OmniOperator.git -b 2026_930_poc OmniOperatorJIT
cd OmniOperatorJIT
source /etc/profile
mkdir -p /opt/buildtools/omni_home/omni-operator/lib
cp /opt/buildtools/pkg_tmp/Dependency_library_Gluten/* /opt/buildtools/omni_home/omni-operator/lib
export OMNI_HOME=/opt/buildtools/omni_home/omni-operator
export LIBRARY_PATH=$OMNI_HOME/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=$OMNI_HOME/lib:$LD_LIBRARY_PATH

#拷贝arrow cmake
cp -r /opt/buildtools/pkg_tmp/cmake/Arrow /usr/local/lib64/cmake/
#拷贝arrow so
cp /opt/buildtools/omni_home/omni-operator/lib/libarrow.so.1100 /usr/local/lib64/libarrow.so.1100.0.0
#拷贝arrow 头文件
cp -r /opt/buildtools/pkg_tmp/omni_include/arrow/ /usr/local/include

#拷贝parquet cmake
cp -r /opt/buildtools/pkg_tmp/cmake/Parquet/ /usr/local/lib64/cmake/
#拷贝parquet so
cp /opt/buildtools/omni_home/omni-operator/lib/libparquet.so.1100 /usr/local/lib64/libparquet.so.1100.0.0
#拷贝parquet 头文件
cp -r /opt/buildtools/pkg_tmp/omni_include/parquet/ /usr/local/include

#拷贝ArrowDataset cmake
cp -r /opt/buildtools/pkg_tmp/cmake/ArrowDataset/ /usr/local/lib64/cmake/
#拷贝ArrowDataset so
cp /opt/buildtools/omni_home/omni-operator/lib/libarrow_dataset.so.1100 /usr/local/lib64/libarrow_dataset.so.1100.0.0

#拷贝orc 头文件
cp -r /opt/buildtools/pkg_tmp/omni_include/orc/ /usr/local/include
cp -r /usr/local/include/orc/* /usr/local/include

#拷贝protobuf so和头文件
cp /opt/buildtools/pkg_tmp/protobuf_pkg/libprotobuf* /usr/local/lib
mkdir -p /usr/local/include/google
cp -r /opt/buildtools/pkg_tmp/protobuf /usr/local/include/google

#拷贝hdfs so和头文件
cp /opt/buildtools/omni_home/omni-operator/lib/libhdfs.so.0.0.0 /opt/buildtools/omni_home/omni-operator/lib/libhdfs.so
cp /opt/buildtools/pkg_tmp/omni_include/hdfs.h /usr/local/include

#拷贝lz4 so和头文件
cp /opt/buildtools/omni_home/omni-operator/lib/liblz4.so.1 /opt/buildtools/omni_home/omni-operator/lib/liblz4.so
cp /opt/buildtools/pkg_tmp/omni_include/lz4*.h /usr/local/include

#拷贝zstd so和头文件
cp /opt/buildtools/omni_home/omni-operator/lib/libzstd.so.1 /opt/buildtools/omni_home/omni-operator/lib/libzstd.so
cp /opt/buildtools/pkg_tmp/omni_include/zstd*.h /usr/local/include

#拷贝rapidjson头文件
#wget --no-check-certificate https://github.com/Tencent/rapidjson/archive/refs/tags/v1.1.0.zip
cp /opt/buildtools/pkg_tmp/rapidjson-1.1.0.zip .
unzip rapidjson-1.1.0.zip
cp -r  rapidjson-1.1.0/include/rapidjson/ /usr/local/include/

bash build_scripts/build.sh ${mode}:java --exclude-test

echo 'export LIBRARY_PATH=/opt/buildtools/omni_home/omni-operator/lib:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/opt/buildtools/omni_home/omni-operator/lib:$LD_LIBRARY_PATH' >> /etc/profile