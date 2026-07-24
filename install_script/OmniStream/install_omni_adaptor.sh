cd /opt/buildtools/
git clone https://atomgit.com/openeuler/OmniAdaptor.git -b 2026_930_poc
cd /opt/buildtools/OmniAdaptor/omnistream/omniop-flink-extension/omni-flink-bundle/
# 后面的参数是关闭证书校验，非必选
mvn clean package -DskipTests -Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true