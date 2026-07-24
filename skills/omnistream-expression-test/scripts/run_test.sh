#!/bin/bash
# 服务端测试脚本: 跑 native(OmniStream 向量化) + vanilla(Flink 原生) + compare,
# 把结构化结果输出到 stdout (不生成报告文件 —— 报告由本地 run_local.sh 组装)。
# 服务器只留临时输出, 结束时清理。
#
# 用法: bash run_test.sh <name>
#   前提: /tmp/<name>.csv 与 /tmp/<name>.sql 已上传; 本脚本 + compare.sh 也在 /tmp/
#   由本地 run_local.sh scp 上传后 ssh 调用, 一般不单独手工跑。
# 不用 set -u: source /etc/profile 会引用未绑定变量 (HISTCONTROL 等) 触发 unbound variable 退出
NAME=${1:?usage: $0 <name>}
source /etc/profile
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"   # 共享常量 (FLINK_HOME/FLINK_LOG_DIR/CONFIG_SH 等)
export FLINK_HOME
export PATH=$FLINK_HOME/bin:$PATH
SQL_FILE="/tmp/${NAME}.sql"
TS=$(date +%Y%m%d_%H%M%S)

# 结构化输出 (@@@<SECTION>@@@ 为分隔符, 本地 run_local.sh 据此解析; 内容不会含此标记)
echo "@@@META@@@"
echo "name: ${NAME}"
echo "timestamp: ${TS}"
echo "sql_file: ${SQL_FILE}"
echo "cluster: $(hostname)"

# ---------- 1. native (OmniStream) ----------
stop-cluster.sh >/dev/null 2>&1; sleep 2
pkill -9 -f taskexecutor 2>/dev/null; pkill -9 -f standalonesession 2>/dev/null; sleep 2
rm -f /tmp/flink_output.txt /tmp/native_sql.log
export FLINK_PERFORMANCE=1
export WRITE_TO_FILE=TRUE
start-cluster.sh >/dev/null 2>&1; sleep 12
LOG=$(ls -t ${FLINK_LOG_DIR}/flink-*-taskexecutor-0-*.out 2>/dev/null | head -1)
BEFORE=$(grep -c "welcome to native" "$LOG" 2>/dev/null); BEFORE=${BEFORE:-0}
timeout 120 sql-client.sh -f "$SQL_FILE" > /tmp/native_sql.log 2>&1
sleep 8
AFTER=$(grep -c "welcome to native" "$LOG" 2>/dev/null); AFTER=${AFTER:-0}
NATIVE_ROWS=$(wc -l < /tmp/flink_output.txt 2>/dev/null); NATIVE_ROWS=${NATIVE_ROWS:-0}
NATIVE_OUT=$(cat /tmp/flink_output.txt 2>/dev/null)
unset FLINK_PERFORMANCE WRITE_TO_FILE

echo "@@@WELCOME@@@"
echo "before: ${BEFORE}"
echo "after: ${AFTER}"

echo "@@@NATIVE_OUT@@@"
printf '%s\n' "$NATIVE_OUT"

# ---------- 2. vanilla (Flink 原生) ----------
# 切 vanilla: 去 config.sh 里 flink-tnel.jar 前置 (PATCH 行) + 恢复原 classpath echo
CONFIG_SH="$CONFIG_SH" TNEL_JAR_NAME="$TNEL_JAR_NAME" python3 - <<'PYEOF'
import os
p=os.environ['CONFIG_SH']; jar=os.environ['TNEL_JAR_NAME']
lines=open(p).read().split('\n'); out=[]
for l in lines:
    if 'PATCH=' in l and jar in l: continue
    if l.strip().startswith('echo') and '$PATCH' in l: continue
    if l.strip().startswith('# echo "$FLINK_CLASSPATH""$FLINK_DIST"'): l=l.replace('# echo','echo')
    out.append(l)
open(p,'w').write('\n'.join(out))
PYEOF
grep -q 'PATCH=' "$CONFIG_SH" || echo "(vanilla: config.sh PATCH 已移除)"
stop-cluster.sh >/dev/null 2>&1; sleep 2; pkill -9 -f taskexecutor 2>/dev/null; pkill -9 -f standalonesession 2>/dev/null; sleep 2
start-cluster.sh >/dev/null 2>&1; sleep 12
rm -f /tmp/vanilla_out.txt
timeout 120 sql-client.sh -f "$SQL_FILE" > /tmp/vanilla_sql.log 2>&1
sleep 8
VLOG=$(ls -t ${FLINK_LOG_DIR}/flink-*-taskexecutor-0-*.out 2>/dev/null | head -1)
grep -E '^\+I' "$VLOG" 2>/dev/null > /tmp/vanilla_out.txt
VANILLA_ROWS=$(wc -l < /tmp/vanilla_out.txt 2>/dev/null); VANILLA_ROWS=${VANILLA_ROWS:-0}
VANILLA_OUT=$(cat /tmp/vanilla_out.txt 2>/dev/null)

echo "@@@VANILLA_OUT@@@"
printf '%s\n' "$VANILLA_OUT"

# 恢复 config.sh (重新使能 OmniStream) + 重启回 native 集群
cp ${CONFIG_SH_BAK} ${CONFIG_SH} 2>/dev/null
stop-cluster.sh >/dev/null 2>&1; sleep 2; pkill -9 -f taskexecutor 2>/dev/null; pkill -9 -f standalonesession 2>/dev/null; sleep 2
start-cluster.sh >/dev/null 2>&1

# ---------- 3. compare (归一化 + diff) ----------
touch /tmp/flink_output.txt /tmp/vanilla_out.txt
DIFF_OUT=$(bash "$SCRIPT_DIR/compare.sh" /tmp/flink_output.txt /tmp/vanilla_out.txt 2>&1)
echo "@@@DIFF@@@"
printf '%s\n' "$DIFF_OUT"

# ---------- 4. verdict ----------
echo "@@@VERDICT@@@"
if printf '%s' "$DIFF_OUT" | grep -q "RESULT: IDENTICAL" && [ "${AFTER:-0}" -gt "${BEFORE:-0}" ]; then
    echo "PASS  (native==vanilla, welcome ${BEFORE}->${AFTER}, native ${NATIVE_ROWS} rows / vanilla ${VANILLA_ROWS} rows)"
else
    echo "FAIL  (welcome ${BEFORE}->${AFTER}, native ${NATIVE_ROWS} rows / vanilla ${VANILLA_ROWS} rows)"
fi

# 清理服务端临时文件 (不留报告 / 不留输出)
rm -f /tmp/flink_output.txt /tmp/vanilla_out.txt /tmp/_cmp.txt /tmp/_native_norm.txt \
      /tmp/_vanilla_norm.txt /tmp/_expr_diff.txt /tmp/native_sql.log /tmp/vanilla_sql.log
