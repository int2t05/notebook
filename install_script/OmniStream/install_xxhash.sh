cd /opt/buildtools
git clone https://github.com/Cyan4973/xxHash.git
cd /opt/buildtools/xxHash && git checkout tags/v0.8.2
mkdir -p cmake_unofficial/build && cd cmake_unofficial/build
cmake ..
make -j && make install