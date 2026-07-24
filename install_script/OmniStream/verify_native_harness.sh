#!/bin/bash
source /etc/profile
export FLINK_HOME=/opt/flink
export PATH=$FLINK_HOME/bin:$PATH
export FLINK_PERFORMANCE=false
export WRITE_TO_FILE=TRUE

CONF=/opt/nexmark/conf/nexmark.yaml
cp -f $CONF ${CONF}.bak_expr

echo "=== patch workload: small events + add q_expr ==="
sed -i 's/nexmark.workload.suite.100m.events.num: .*/nexmark.workload.suite.100m.events.num: 5000/' $CONF
sed -i 's/nexmark.workload.suite.100m.tps: .*/nexmark.workload.suite.100m.tps: 1000/' $CONF
sed -i 's/nexmark.workload.suite.100m.warmup.duration: .*/nexmark.workload.suite.100m.warmup.duration: 1s/' $CONF
sed -i 's/nexmark.workload.suite.100m.warmup.events.num: .*/nexmark.workload.suite.100m.warmup.events.num: 5000/' $CONF
sed -i 's/nexmark.workload.suite.100m.warmup.tps: .*/nexmark.workload.suite.100m.warmup.tps: 1000/' $CONF
sed -i '34s/q22"/q22,q_expr"/' $CONF
grep -nE '100m.events.num|100m.tps|100m.queries:' $CONF | head

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
echo "=== run q_expr via harness (BEFORE welcome=$BEFORE) ==="
timeout 60 bash /opt/nexmark/bin/run_query.sh q_expr >/tmp/qexpr.log 2>&1
sleep 3
AFTER=$(grep -c 'welcome to native' /opt/flink/log/flink-root-taskexecutor-0-ljr_flink_dev.out)
echo "welcome-to-native: BEFORE=$BEFORE AFTER=$AFTER"
echo "output rows:" $(wc -l < /tmp/flink_output.txt 2>/dev/null)
echo "=== sample output (first 12) ==="
head -n 12 /tmp/flink_output.txt 2>/dev/null

echo "=== restore nexmark.yaml ==="
mv -f ${CONF}.bak_expr $CONF
echo "restored"
