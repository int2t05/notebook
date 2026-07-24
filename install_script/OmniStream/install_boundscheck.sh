cd /opt/buildtools
git clone https://atomgit.com/openeuler/libboundscheck.git
cd /opt/buildtools/libboundscheck && git checkout tags/v1.1.16
make CC=gcc
echo 'export C_INCLUDE_PATH=/opt/buildtools:/opt/buildtools/libboundscheck/include:$C_INCLUDE_PATH' >> /etc/profile
echo 'export CPLUS_INCLUDE_PATH=/opt/buildtools:/opt/buildtools/libboundscheck/include:$CPLUS_INCLUDE_PATH' >> /etc/profile
echo 'export LIBRARY_PATH=/opt/buildtools/libboundscheck/lib:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/opt/buildtools/libboundscheck/lib:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile