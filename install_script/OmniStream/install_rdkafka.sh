cd /opt/buildtools
git clone https://gitcode.com/toljr/OmniStream.git -b 2026_930_poc
cd OmniStream
#git reset --hard a85c5ec5b81678d8ec5ccef860f12cd6b50c1332 # 当前主线有bug，暂时采用该节点
cd /opt/buildtools
git clone https://github.com/confluentinc/librdkafka.git
cd /opt/buildtools/librdkafka && git checkout tags/v2.6.1
git apply "/opt/buildtools/OmniStream/cpp/connector/kafka/omni_kafka_opt.patch"
./configure --CFLAGS="-O3" --CXXFLAGS="-O3"
make -j && make install