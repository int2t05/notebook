
mode=$1 # Release or Debug

mkdir -p /opt/buildtools/OmniStream/cpp/build && cd /opt/buildtools/OmniStream/cpp/build

export HOME=/opt/buildtools/
cmake -DCMAKE_BUILD_TYPE=${mode}   ..
make install -j