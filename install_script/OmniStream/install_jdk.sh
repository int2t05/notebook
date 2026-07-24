mkdir -p /opt/buildtools/jdk && cd /opt/buildtools/jdk
wget --no-check-certificate https://mirrors.huaweicloud.com/kunpeng/archive/compiler/bisheng_jdk/bisheng-jdk-8u472-b11-linux-aarch64.tar.gz
tar -zxvf /opt/buildtools/jdk/bisheng-jdk-*-linux-aarch64.tar.gz
chown -R root:root /opt/buildtools/jdk
sed -i '/JAVA_HOME/d' /etc/profile
echo "export JAVA_HOME=/opt/buildtools/jdk/bisheng-jdk1.8.0_472" >> /etc/profile
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile
echo 'export C_INCLUDE_PATH=$JAVA_HOME/include:$JAVA_HOME/include/linux:$C_INCLUDE_PATH' >> /etc/profile
echo 'export CPLUS_INCLUDE_PATH=$JAVA_HOME/include:$JAVA_HOME/include/linux:$CPLUS_INCLUDE_PATH' >> /etc/profile
echo 'export LIBRARY_PATH=$JAVA_HOME/jre/lib/aarch64/server:$JAVA_HOME/jre/lib/aarch64:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=$JAVA_HOME/jre/lib/aarch64/server:$JAVA_HOME/jre/lib/aarch64:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile