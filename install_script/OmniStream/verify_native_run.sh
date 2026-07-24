#!/bin/bash
source /etc/profile
export FLINK_HOME=/opt/flink
export PATH=$FLINK_HOME/bin:$PATH
export FLINK_PERFORMANCE=false
export WRITE_TO_FILE=TRUE

echo "=== ensure classloader.resolve-order: parent-first ==="
if ! grep -qE '^classloader.resolve-order:[[:space:]]*parent-first' /opt/flink/conf/flink-conf.yaml; then
  echo 'classloader.resolve-order: parent-first' >> /opt/flink/conf/flink-conf.yaml
  echo "added parent-first"
else
  echo "already parent-first"
fi

echo "=== restart cluster cleanly ==="
stop-cluster.sh
sleep 2
pkill -9 -f taskexecutor 2>/dev/null
pkill -9 -f standalonesession 2>/dev/null
sleep 2
start-cluster.sh
sleep 10

rm -f /tmp/flink_output.txt
BEFORE=$(grep -c 'welcome to native' /opt/flink/log/flink-root-taskexecutor-0-ljr_flink_dev.out)
echo "=== submit MY native SQL (BEFORE welcome=$BEFORE) ==="
sql-client.sh -f /tmp/verify_expr_native.sql 2>&1 | grep -iE 'Job ID'
sleep 15
AFTER=$(grep -c 'welcome to native' /opt/flink/log/flink-root-taskexecutor-0-ljr_flink_dev.out)
echo "MY job welcome-to-native: BEFORE=$BEFORE AFTER=$AFTER"
echo "MY output rows:" $(wc -l < /tmp/flink_output.txt 2>/dev/null)
echo "=== MY sample output (first 8) ==="
head -n 8 /tmp/flink_output.txt 2>/dev/null
