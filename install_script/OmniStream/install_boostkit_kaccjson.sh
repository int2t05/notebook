mkdir -p /opt/buildtools/boostkit-kaccjson && cd /opt/buildtools/boostkit-kaccjson
wget --no-check-certificate https://boostkit-bigdata-public.obs.cn-north-4.myhuaweicloud.com/artifact/OmniStream/OmniStream_rely/BoostKit-kaccjson_1.1.0.zip
unzip /opt/buildtools/boostkit-kaccjson/BoostKit-kaccjson_1.1.0.zip
echo 'export LIBRARY_PATH=/opt/buildtools/boostkit-kaccjson:$LIBRARY_PATH' >> /etc/profile
echo 'export LD_LIBRARY_PATH=/opt/buildtools/boostkit-kaccjson:$LD_LIBRARY_PATH' >> /etc/profile
source /etc/profile