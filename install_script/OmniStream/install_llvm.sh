mkdir -p /opt/buildtools/llvm && cd /opt/buildtools/llvm
cp /opt/buildtools/pkg_tmp/llvmorg-15.0.4.tar.gz /opt/buildtools/llvm
#wget --no-check-certificate https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-15.0.4.tar.gz
tar -zxvf /opt/buildtools/llvm/*llvmorg-*.tar.gz
mkdir -p /opt/buildtools/llvm/llvm-project-llvmorg-15.0.4/build && cd /opt/buildtools/llvm/llvm-project-llvmorg-15.0.4/build
cmake -G "Unix Makefiles" -DLLVM-TARGETS_TO_BUILD="host;ARM;X86;AArch64;BPE" -DCMAKE_BUILD_TYPE=Release -DLLVM_BUILD_LLVM_DYLIB=true -DLLVM_ENABLE_RTTI=ON -DLLVM_ENABLE_PROJECTS="clang;lld;libunwind;compiler-rt;lldb" -DCMAKE_INSTALL_PREFIX=/usr/local/ ../llvm
make -j && make install
sed -i '/LLVM_DIR/d' /etc/profile

echo 'export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile