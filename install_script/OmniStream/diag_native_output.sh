#!/bin/bash
echo "===== 1) flink_output.txt exists? ====="
ls -l /tmp/flink_output.txt 2>&1 || echo "NOT FOUND"

echo
echo "===== 2) cluster procs ====="
JM=$(pgrep -f StandaloneSessionClusterEntrypoint | head -n1)
TM=$(pgrep -f TaskManagerRunner | head -n1)
echo "JM pid=$JM  TM pid=$TM"

echo
echo "===== 3) TM environment: WRITE_TO_FILE / FLINK_PERFORMANCE ====="
if [ -n "$TM" ]; then
    tr '\0' '\n' < /proc/$TM/environ | grep -E 'WRITE_TO_FILE|FLINK_PERFORMANCE|OMNI_HOME|LD_LIBRARY_PATH' || echo "(none of these vars in TM env)"
else
    echo "TM not running"
fi

echo
echo "===== 4) current shell-exported vars (this ssh session) ====="
echo "WRITE_TO_FILE=$WRITE_TO_FILE  FLINK_PERFORMANCE=$FLINK_PERFORMANCE"

echo
echo "===== 5) welcome-to-native count in TM .out ====="
OUT=$(ls -t /opt/flink/log/flink-root-taskexecutor-*.out 2>/dev/null | head -n1)
echo "TM out file: $OUT"
if [ -n "$OUT" ]; then
    echo "welcome to native count: $(grep -c 'welcome to native' "$OUT")"
    echo "--- last 15 lines of TM .out ---"
    tail -n 15 "$OUT"
fi

echo
echo "===== 6) recent jobs via REST ====="
curl -s http://localhost:8081/jobs/overview 2>/dev/null | head -c 1200
echo

echo
echo "===== 7) last q1 submit result in nexmark log ====="
grep -E 'Job ID|Execute statement|Submitting|Exception|ERROR|not running' /opt/nexmark/log/nexmark-flink.log 2>/dev/null | tail -n 15
