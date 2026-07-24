#!/bin/bash
# Incremental rebuild of OmniStream (reuse existing cmake configuration).
source /etc/profile
export HOME=/opt/buildtools/
LOG=/tmp/omnistream_build.log
# stop any in-flight build
pkill -f 'make install' 2>/dev/null || true
sleep 2
cd /opt/buildtools/OmniStream/cpp/build || exit 1
echo "=== incremental build start $(date) ===" > "$LOG"
make install -j >> "$LOG" 2>&1
RC=$?
echo "=== make rc=$RC $(date) ===" >> "$LOG"
if [ $RC -eq 0 ]; then echo "BUILD_SUCCESS" >> "$LOG"; else echo "BUILD_FAILED" >> "$LOG"; fi
exit $RC
