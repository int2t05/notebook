cd /opt/buildtools
git clone https://github.com/google/googletest.git
cd /opt/buildtools/googletest && git checkout tags/release-1.10.0
mkdir -p /opt/buildtools/googletest/build && cd /opt/buildtools/googletest/build
cmake ..
make -j
make install