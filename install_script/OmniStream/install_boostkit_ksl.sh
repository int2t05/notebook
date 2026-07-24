mkdir -p /opt/buildtools/boostkit-ksl && cd /opt/buildtools/boostkit-ksl
wget --no-check-certificate https://kunpeng-repo.obs.cn-north-4.myhuaweicloud.com/Kunpeng%20BoostKit/Kunpeng%20BoostKit%2025.1.RC1/BoostKit-ksl_2.5.1.zip
unzip /opt/buildtools/boostkit-ksl/BoostKit-ksl_*.zip && rpm -ivh boostkit-ksl-*.aarch64.rpm

echo 'export C_INCLUDE_PATH=/usr/local/ksl/include:$C_INCLUDE_PATH' >> /etc/profile
echo 'export CPLUS_INCLUDE_PATH=/usr/local/ksl/include:$CPLUS_INCLUDE_PATH' >> /etc/profile
echo 'export LIBRARY_PATH=/usr/local/ksl/lib:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/usr/local/ksl/lib:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile