cd /opt/buildtools
git clone https://github.com/jemalloc/jemalloc.git
cd /opt/buildtools/jemalloc && git checkout tags/5.3.0
./autogen.sh --disable-initial-exec-tls --with-lg-page=16
make -j && make install