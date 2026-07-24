cd /opt/buildtools
git clone https://atomgit.com/openeuler/OmniStateStore.git
cd /opt/buildtools/OmniStateStore && git checkout tags/tag_BeiMing_25.3.0.B030_002

# OmniStateStore的编译依赖：googletest, lz4, libboundscheck, spdlog
cd /opt/buildtools/OmniStateStore/3rdparty/googletest && git clone https://github.com/google/googletest.git
cd /opt/buildtools/OmniStateStore/3rdparty/googletest/googletest && git checkout tags/release-1.10.0

cd /opt/buildtools/OmniStateStore/3rdparty/lz4 && git clone https://github.com/lz4/lz4.git
cd /opt/buildtools/OmniStateStore/3rdparty/lz4/lz4 && git checkout tags/v1.10.0

cd /opt/buildtools/OmniStateStore/3rdparty/secure && git clone https://atomgit.com/openeuler/libboundscheck.git
cd /opt/buildtools/OmniStateStore/3rdparty/secure/libboundscheck && git checkout tags/v1.1.16

cd /opt/buildtools/OmniStateStore/3rdparty/spdlog && git clone https://github.com/gabime/spdlog.git
cd /opt/buildtools/OmniStateStore/3rdparty/spdlog/spdlog && git checkout tags/v1.17.0

# 编译OmniStateStore
bash /opt/buildtools/OmniStateStore/scripts/build.sh -t release

echo 'export C_INCLUDE_PATH=/opt/buildtools/OmniStateStore/src/core/include/:$C_INCLUDE_PATH' >> /etc/profile
echo 'export CPLUS_INCLUDE_PATH=/opt/buildtools/OmniStateStore/src/core/include:$CPLUS_INCLUDE_PATH' >> /etc/profile
echo 'export LIBRARY_PATH=/opt/buildtools/OmniStateStore/build/src/core/jni:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/opt/buildtools/OmniStateStore/build/src/core/jni:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile