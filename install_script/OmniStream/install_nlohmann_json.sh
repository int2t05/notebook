cd /opt/buildtools
git clone https://github.com/nlohmann/json.git -b v3.11.3
cd /opt/buildtools/json && mkdir -p build && cd build
cmake ..
make -j && make install