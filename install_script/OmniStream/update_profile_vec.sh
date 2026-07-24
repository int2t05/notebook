#!/bin/bash
# Append OmniOperatorVec vectorized build product lib paths to /etc/profile (idempotent)
set -e
cp -n /etc/profile /etc/profile.bak.omnivec 2>/dev/null || true
if ! grep -q 'OmniOperatorVec vectorized' /etc/profile; then
cat >> /etc/profile <<'EOF'

# OmniOperatorVec vectorized build products
export LIBRARY_PATH=/opt/buildtools/omni_home/omni-operator/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/buildtools/omni_home/omni-operator/lib:$LD_LIBRARY_PATH
EOF
fi
echo '--- tail of /etc/profile ---'
tail -n 6 /etc/profile
