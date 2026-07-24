mkdir -p /opt/buildtools
cd /opt/buildtools
git clone https://gitcode.com/toljr/OmniOperator_dependencies.git
cd OmniOperator_dependencies
git lfs install
git lfs pull
cd /opt/buildtools
mv /opt/buildtools/OmniOperator_dependencies/pkg_tmp /opt/buildtools
rm -rf OmniOperator_dependencies