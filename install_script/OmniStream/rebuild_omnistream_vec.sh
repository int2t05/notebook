#!/bin/bash
# Rebuild OmniStream against the vectorized OmniOperator build products.
source /etc/profile
export HOME=/opt/buildtools/
MODE=${1:-Release}
LOG=/tmp/omnistream_build.log
echo "=== build start $(date) mode=$MODE ===" > "$LOG"
echo "LIBRARY_PATH=$LIBRARY_PATH" >> "$LOG"
rm -rf /opt/buildtools/OmniStream/cpp/build
mkdir -p /opt/buildtools/OmniStream/cpp/build
cd /opt/buildtools/OmniStream/cpp/build || exit 1
cmake -DCMAKE_BUILD_TYPE=${MODE} .. >> "$LOG" 2>&1
CMAKE_RC=$?
echo "=== cmake rc=$CMAKE_RC ===" >> "$LOG"
if [ $CMAKE_RC -ne 0 ]; then
    echo "CMAKE_FAILED" >> "$LOG"
    exit 1
fi
make install -j >> "$LOG" 2>&1
MAKE_RC=$?
echo "=== make rc=$MAKE_RC $(date) ===" >> "$LOG"
if [ $MAKE_RC -eq 0 ]; then
    echo "BUILD_SUCCESS" >> "$LOG"
else
    echo "BUILD_FAILED" >> "$LOG"
fi
exit $MAKE_RC
