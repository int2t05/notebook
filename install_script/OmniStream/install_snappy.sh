cd /opt/buildtools
git clone https://atomgit.com/src-openeuler/snappy.git
cd /opt/buildtools/snappy && git checkout tags/openEuler-24.03-LTS-SP1-release
tar -zxvf snappy-1.1.10.tar.gz
cd snappy-1.1.10 && patch -p1 < ../add-option-to-enable-rtti-set-default-to-current-ben.patch && patch -p1 < ../remove-dependency-on-google-benchmark-and-gmock.patch
mkdir -p /opt/buildtools/snappy/snappy-1.1.10/build && cd /opt/buildtools/snappy/snappy-1.1.10/build
cmake -DSNAPPY_BUILD_BENCHMARKS=OFF -DSNAPPY_BUILD_TESTS=OFF -DBUILD_SHARED_LIBS=ON -DCMAKE_POSITION_INDEPENDENT_CODE=ON  .. 
make -j && make install
echo 'export LIBRARY_PATH=/usr/local/lib64:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/usr/local/lib64:$LD_LIBRARY_PATH' >> /etc/profile