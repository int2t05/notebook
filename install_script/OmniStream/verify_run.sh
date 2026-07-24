#!/bin/bash
set -x
source /etc/profile
export FLINK_HOME=/opt/flink
export PATH=$FLINK_HOME/bin:$PATH
export FLINK_PERFORMANCE=false
export WRITE_TO_FILE=TRUE

echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"

# clean cluster
stop-cluster.sh
sleep 2
pkill -9 -f taskexecutor 2>/dev/null
pkill -9 -f standalonesession 2>/dev/null
sleep 2
rm -f /tmp/flink_output.txt

# start cluster
start-cluster.sh
sleep 8
echo "=== JPS ==="
jps

echo "=== SUBMIT SQL ==="
$FLINK_HOME/bin/sql-client.sh -f /tmp/verify_expr.sql
