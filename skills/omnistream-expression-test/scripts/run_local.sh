#!/bin/bash
# Path/host/user constants come from env.sh (derived from repo-root AGENTS.md by
# omnistream-env-init). Ensure env.sh is sourced below; do not hardcode here.
#
# 本地驱动 (Windows Git Bash 运行): 上传 test -> 服务器 /tmp, ssh 跑 run_test.sh
# (native + vanilla + compare), 取回结构化结果, 在本地组装富报告。
#
# 报告纯本地: <flink-test>/report/<name>/<name>.report.md
# 服务器不留报告 (run_test.sh 只输出到 stdout + 临时文件, 结束清理)。
#
# 用法: bash run_local.sh <name>
#   <name> = <flink-test>/test/<name>/ 下的测试名 (文件为 <name>.csv / <name>.sql)
#   SQL 里 csv path 须为 /tmp/<name>.csv (run_local.sh 会 scp csv 到此路径)
#
# 环境变量:
#   FLINK_TEST_DIR  本地 flink-test 工作区根 (默认 $LOCAL_FLINK_TEST)
set -u
NAME=${1:?usage: $0 <name>}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/env.sh"   # 共享常量 (REMOTE 等,与 build-deploy config.ini 一致)
FLINK_TEST_DIR="${FLINK_TEST_DIR:-$LOCAL_FLINK_TEST}"
TEST_DIR="${FLINK_TEST_DIR}/test/${NAME}"
REPORT_DIR="${FLINK_TEST_DIR}/report/${NAME}"
CSV="${TEST_DIR}/${NAME}.csv"
SQL="${TEST_DIR}/${NAME}.sql"
REPORT="${REPORT_DIR}/${NAME}.report.md"

if [ ! -f "$CSV" ] || [ ! -f "$SQL" ]; then
  echo "ERROR: 测试文件不存在:" >&2
  echo "  ${CSV}" >&2
  echo "  ${SQL}" >&2
  echo "  期望布局: \${FLINK_TEST_DIR}/test/${NAME}/${NAME}.{csv,sql}" >&2
  exit 1
fi

echo "[1/4] 上传 test + 脚本到 ${REMOTE}:/tmp/ ..."
scp "$CSV" "$SQL" "$SCRIPT_DIR/run_test.sh" "$SCRIPT_DIR/compare.sh" "$SCRIPT_DIR/env.sh" "${REMOTE}:/tmp/" >/dev/null 2>&1 \
  || { echo "ERROR: scp 上传失败" >&2; exit 1; }
echo "      -> /tmp/${NAME}.csv, /tmp/${NAME}.sql, /tmp/run_test.sh, /tmp/compare.sh, /tmp/env.sh"

echo "[2/4] ssh 跑 native + vanilla + compare (约 2-3 分钟, 多次重启集群) ..."
RESULT=$(ssh "${REMOTE}" "bash /tmp/run_test.sh ${NAME}" 2>&1)
SSH_RC=$?
[ "$SSH_RC" -ne 0 ] && echo "      (ssh 退出码 $SSH_RC, 结果可能不完整; 常见是 stop-cluster 触发的连接抖动, 重跑即可)"

echo "[3/4] 本地组装报告 ..."
mkdir -p "$REPORT_DIR"

# 解析 @@@<SECTION>@@@ 之间的内容 (内容不含此标记, 安全)
getsec() {
  awk -v s="@@@$1@@@" 'BEGIN{f=0} $0==s{f=1;next} /^@@@.*@@@$/{f=0} f' <<<"$RESULT"
}
META=$(getsec META)
WELCOME=$(getsec WELCOME)
NATIVE_OUT=$(getsec NATIVE_OUT)
VANILLA_OUT=$(getsec VANILLA_OUT)
DIFF=$(getsec DIFF)
VERDICT=$(getsec VERDICT)

W_BEFORE=$(printf '%s\n' "$WELCOME"  | awk -F': ' '/^before:/{print $2}'); W_BEFORE=${W_BEFORE:-0}
W_AFTER=$(printf  '%s\n' "$WELCOME"  | awk -F': ' '/^after:/{print $2}');  W_AFTER=${W_AFTER:-0}
TS=$(printf      '%s\n' "$META"      | awk -F': ' '/^timestamp:/{print $2}')
CLUSTER=$(printf '%s\n' "$META"      | awk -F': ' '/^cluster:/{print $2}')
NROWS=$(printf  '%s\n' "$NATIVE_OUT" | grep -cve '^$')
VROWS=$(printf  '%s\n' "$VANILLA_OUT" | grep -cve '^$')
CSV_ROWS=$(grep -cve '^$' "$CSV")
SQL_CONTENT=$(cat "$SQL")

if printf '%s' "$VERDICT" | grep -q "^PASS"; then
  CONCLUSION="✅ PASS — native == vanilla, welcome ${W_BEFORE}→${W_AFTER}, ${NROWS} 行逐行一致"
else
  CONCLUSION="❌ FAIL — welcome ${W_BEFORE}→${W_AFTER}, native ${NROWS} 行 / vanilla ${VROWS} 行 (见上方 diff 定位)"
fi

{
printf '# %s 测试报告\n\n' "$NAME"
printf -- '- 测试时间: %s\n' "${TS:-unknown}"
printf -- '- 测试名: %s\n' "$NAME"
printf -- '- 服务器: %s (%s)\n' "$REMOTE" "${CLUSTER:-}"
printf -- '- 输入 CSV: %s (%s 行)\n' "$CSV" "$CSV_ROWS"
printf -- '- SQL 文件: %s\n\n' "$SQL"

printf '## 测试内容\n\n'
printf 'native (OmniStream 向量化) vs vanilla (Flink 原生) 黄金对比, 验证两者语义一致。\n\n'
printf 'SQL:\n\n'
printf '```sql\n%s\n```\n\n' "$SQL_CONTENT"

printf '## 1. Native (OmniStream)\n\n'
printf -- '- welcome to native: %s → %s (OmniTask.cpp:315, native Task 实际运行)\n' "$W_BEFORE" "$W_AFTER"
printf -- '- 输出 (%s 行, 格式 +I,v1,v2, WRITE_TO_FILE=TRUE 落盘 /tmp/flink_output.txt):\n\n' "$NROWS"
printf '```\n%s\n```\n\n' "$NATIVE_OUT"

printf '## 2. Vanilla (Flink 原生)\n\n'
printf -- '- 输出 (%s 行, 格式 +I[v1, v2], print sink → TM .out):\n\n' "$VROWS"
printf '```\n%s\n```\n\n' "$VANILLA_OUT"

printf '## 3. 正确性对比 (native vs vanilla)\n\n'
printf '归一化 (去 +I/方括号/空格, 逗号→|, 排序) 后 diff:\n\n'
printf '```\n%s\n```\n\n' "$DIFF"

printf '## 结论\n\n'
printf '%s\n' "$CONCLUSION"
} > "$REPORT"

echo "[4/4] 报告已生成: ${REPORT}"
echo
echo "=== ${CONCLUSION} ==="
