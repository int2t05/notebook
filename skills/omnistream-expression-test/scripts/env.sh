# Shared env constants for run_local.sh (local) + run_test.sh (remote).
# LOCAL: derives all from repo-root AGENTS.md §5 (single source, omnistream-env-init generated).
# REMOTE: AGENTS.md absent (this script is scp'd to /tmp); derives FLINK_HOME-based vars from
# /etc/profile's FLINK_HOME (run_test.sh sources /etc/profile before this). Do NOT edit values.

_AGENTS_MD="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." 2>/dev/null && pwd)/AGENTS.md"
if [ -f "$_AGENTS_MD" ]; then
  # local: eval the §5 bash block only (scoped between §5 and §6 headers, future-proof)
  eval "$(awk '/^## 5\./,/^## 6\./' "$_AGENTS_MD" | sed -n '/^```bash$/,/^```$/p' | sed -e '1d' -e '$d')"
else
  # remote: AGENTS.md not present; caller must have sourced /etc/profile so FLINK_HOME is set
  : "${FLINK_HOME:?env.sh: FLINK_HOME not set (remote: source /etc/profile first; local: run omnistream-env-init to generate AGENTS.md)}"
fi

# Always derive FLINK_HOME-based helpers (local: FLINK_HOME from AGENTS.md; remote: from /etc/profile).
# Redundant but harmless locally; required remotely.
FLINK_LOG_DIR="${FLINK_HOME}/log"
FLINK_BIN_DIR="${FLINK_HOME}/bin"
CONFIG_SH="${FLINK_BIN_DIR}/config.sh"
CONFIG_SH_BAK="${FLINK_BIN_DIR}/config.sh.bak"
TNEL_JAR_NAME=flink-tnel-0.1-SNAPSHOT.jar
