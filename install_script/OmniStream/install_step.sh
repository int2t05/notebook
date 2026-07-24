
bash ./install_base.sh
bash ./install_patch.sh

bash ./install_jdk.sh
bash ./install_boostkit_ksl.sh
bash ./install_boostkit_kaccjson.sh
bash ./install_llvm.sh
bash ./install_googletest.sh
bash ./install_jemalloc.sh
bash ./install_nlohmann_json.sh
bash ./install_snappy.sh
bash ./install_rocksdb.sh
bash ./install_xxhash.sh

bash ./install_rdkafka.sh

sed -i 's/option(WITH_OMNISTATESTORE "Enable to build with OmniStateStore" ON)/option(WITH_OMNISTATESTORE "Enable to build with OmniStateStore" OFF)/' /opt/buildtools/OmniStream/cpp/CMakeLists.txt

bash ./install_boundscheck.sh
bash ./install_abseil_re2.sh

source /etc/profile

bash ./install_omni_operator_vec.sh release # release or debug

source /etc/profile

bash ./install_omni_adaptor.sh
bash ./install_omni_stream.sh Release # Release or Debug

# note: install_omni_operator 和 install_omni_stream 需同时为release或debug