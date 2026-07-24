
"""MCP server: SSH to a host and run Spark-Test-Tool test-all.sh.
Configure via env: SSH_HOST, SSH_USER, SSH_PASSWORD, SSH_PORT, REMOTE_SCRIPT, REMOTE_WORKDIR（仅相对路径脚本时先 cd）,
REMOTE_OPERATOR_DIR, REMOTE_OPERATOR_SCRIPT, SSH_IDENTITY,
REMOTE_FLAME_DIR（远端 profiler HTML，默认 /opt/async）, FLAME_LOCAL_DIR（本机保存根目录，默认 spark_remote_mcp/flame_exports）,
COMPILE_OMNI_SCRIPT（默认 /home/omni/compile_omni.sh，脚本接受位置参数 $1=OmniURL $2=OmniBranch）,
COMPILE_GLUTEN_SCRIPT（默认 /home/omni/compile_gluten.sh，脚本接受位置参数 $1=OmniURL $2=OmniBranch $3=GlutenURL $4=GlutenBranch）,
PROJECT_ROOT（默认 = server.py 上一级目录；compile_omni / compile_gluten 在未传 URL 时会从
 PROJECT_ROOT/OmniOperator 与 PROJECT_ROOT/Gluten 的 git origin 自动读取仓库 URL）,
COMPILE_OMNI_TIMEOUT_SECONDS、COMPILE_GLUTEN_TIMEOUT_SECONDS（未设置时取 max(7200, SSH_TIMEOUT_SECONDS) 秒）,
E2E_SQL_SCRIPT（默认 /home/omni/run_e2e_sql.sh，脚本接受位置参数 $1=SQL语句，以 Omni/Gluten 引擎执行并返回结果）,
E2E_SQL_TIMEOUT_SECONDS（默认 300 秒），
SHS_BASE_URL（Spark History Server 地址，默认空字符串 ""；如需启用 run_e2e_sql 的 SHS 截图功能
 必须显式配置，形如 http://<host>:18080），
SHS_INIT_WAIT_SECONDS（run_e2e_sql 查 SHS 前的初始等待秒数，默认 12；SHS 默认每 10s 刷新一次 event log）。
debug_e2e_sql_columnar 可在正确性调试时逐个关闭列式算子配置，定位结果不一致或异常消失的可疑开关。
若设置 SSH_PASSWORD，远程命令可用 Paramiko；否则远程命令走系统 ssh。拉取火焰图始终用 Paramiko，无密码时请配置 SSH_IDENTITY。
出于安全考虑：SSH_HOST / SSH_USER 没有硬编码默认值，必须在 .env 显式配置，缺失时 main() 启动会 SystemExit。
"""

from __future__ import annotations

import asyncio
import base64
import json as _json
import logging
import os
import posixpath
import re
import shlex
import stat
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import paramiko
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "spark-remote-test",
    instructions=(
        "在配置的远程 Linux 主机上通过 SSH 执行 Spark-Test-Tool。"
        " 【工具用途区分——必读】"
        " run_e2e_sql：正确性校验专用，每次只应调用一次，返回查询结果行用于与基准对比；"
        " 禁止用 run_e2e_sql 做性能计时或重复执行以获取热启动数据。"
        " debug_e2e_sql_columnar：正确性调试专用，围绕同一 SQL 多轮执行，逐个关闭列式算子配置，"
        " 用于定位哪个 columnar 开关会让结果恢复一致或异常消失；不用于性能计时。"
        " run_spark_test_operator：性能测试专用，**每次只跑 1 次**，返回该次端到端耗时；"
        " 若要冷启动+热启动数据需由调用方连续多次调用（典型：冷 1 次 + 热 3 次，取热均值）。"
        " 默认不抓火焰图；需要画像时传 flame_enabled=true 单独跑一次，再调用 fetch_spark_flame_graphs。"
        " 不返回查询结果内容，不用于正确性校验。"
        " 【其他工具】"
        " fetch_spark_flame_graphs：经 SFTP 将远端 REMOTE_FLAME_DIR 下 .html 拉到本机，返回 file:// 路径。"
        " compile_omni：在 Docker 容器(mgx_omni_compiler1)内编译 OmniOperator 并运行 GTest UT，产物留在容器内不部署到宿主机。"
        " compile_gluten：在容器内编译 Omni+Gluten，完成后 docker cp 将 omni-operator 目录部署到宿主机 /home/omni/omni-operator。"
        " 可设置 SSH_PASSWORD 或 SSH_IDENTITY。"
    ),
)

# Paramiko 默认把握手日志打到 ERROR，在 Cursor MCP 日志里会像故障；不影响功能
logging.getLogger("paramiko").setLevel(logging.WARNING)

DEFAULT_COLUMNAR_TOGGLES = [
    "spark.gluten.sql.columnar.project",
    "spark.gluten.sql.columnar.filter",
    "spark.gluten.sql.columnar.hashagg",
    "spark.gluten.sql.columnar.broadcastJoin",
    "spark.gluten.sql.columnar.shuffledHashJoin",
    "spark.gluten.sql.columnar.sortMergeJoin",
    "spark.gluten.sql.columnar.sort",
    "spark.gluten.sql.columnar.window",
    "spark.gluten.sql.columnar.filescan",
    "spark.gluten.sql.columnar.columnarToRow",
]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _project_root() -> Path:
    """Return the workspace root containing OmniOperator/, Gluten/, etc.

    Defaults to the parent of this server.py file (spark_remote_mcp/ → workspace root).
    Override with PROJECT_ROOT env var when the layout differs.
    """
    override = _env("PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def _resolve_git_remote_url(subdir: str, remote: str = "origin") -> str:
    """Return `git remote get-url <remote>` for PROJECT_ROOT/subdir, or "" on failure.

    Used so MCP callers can omit git_repo_url and the server will auto-pick whichever
    fork lives at the canonical subdir (OmniOperator/, Gluten/, ...).
    """
    repo_dir = _project_root() / subdir
    if not (repo_dir / ".git").exists():
        return ""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "get-url", remote],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _build_remote_shell_command() -> str:
    workdir = _env("REMOTE_WORKDIR")
    script = _env("REMOTE_SCRIPT", "/usr/local/Spark-Test-Tool/script/test-all.sh")
    if not script:
        raise ValueError("REMOTE_SCRIPT 不能为空")
    parts: list[str] = []
    # 绝对路径：先进入脚本所在目录再执行 ./xxx，便于脚本内相对路径与 source
    if script.startswith("/"):
        d = posixpath.dirname(script) or "/"
        b = posixpath.basename(script)
        if not b:
            raise ValueError("REMOTE_SCRIPT 缺少文件名")
        parts.append(f"cd {shlex.quote(d)}")
        parts.append(f"bash {shlex.quote('./' + b)}")
    else:
        if workdir:
            parts.append(f"cd {shlex.quote(workdir)}")
        parts.append(f"bash {shlex.quote(script)}")
    return " && ".join(parts)


def _build_operator_shell_command(flame_enabled: bool = False) -> str:
    """进入 REMOTE_OPERATOR_DIR，执行 REMOTE_OPERATOR_SCRIPT（相对该目录的文件名）。"""
    d = _env("REMOTE_OPERATOR_DIR", "/usr/local/Spark-Test-Tool/script")
    script = _env("REMOTE_OPERATOR_SCRIPT", "test-all-operator.sh")
    if not script:
        raise ValueError("REMOTE_OPERATOR_SCRIPT 不能为空")
    if script.startswith("/"):
        raise ValueError("REMOTE_OPERATOR_SCRIPT 请填文件名，例如 test-all-operator.sh（在 REMOTE_OPERATOR_DIR 下执行）")
    flame = "1" if flame_enabled else "0"
    return f"cd {shlex.quote(d)} && OMNI_FLAME_ENABLED={flame} bash {shlex.quote('./' + script)}"


def _remote_query_sql_quoted_paths() -> tuple[str, str, str]:
    """返回 (原始目录, shlex 后的目录, shlex 后的 q1.sql 路径)。"""
    qdir = _env("REMOTE_QUERY_SQL_DIR", "/usr/local/Spark-Test-Tool/sql/query_sql")
    if not qdir:
        raise ValueError("REMOTE_QUERY_SQL_DIR 不能为空")
    qdir_q = shlex.quote(qdir)
    q1_q = shlex.quote(posixpath.join(qdir, "q1.sql"))
    return qdir, qdir_q, q1_q


def _build_query_sql_clear_fragment(qdir_q: str) -> str:
    """远端：mkdir + 清空该目录下直接子项（含子目录）。"""
    return (
        f"mkdir -p {qdir_q} && "
        f"find {qdir_q} -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +"
    )


def _build_query_sql_prep_write_q1_fragment(sql_text: str) -> str:
    """在清空 query_sql 后，将 UTF-8 SQL 经 base64 解码写入 q1.sql。"""
    _, qdir_q, q1_q = _remote_query_sql_quoted_paths()
    b64 = base64.b64encode(sql_text.encode("utf-8")).decode("ascii")
    b64_q = shlex.quote(b64)
    return f"{_build_query_sql_clear_fragment(qdir_q)} && printf '%s' {b64_q} | base64 -d > {q1_q}"


def _build_query_sql_prep_write_fragment(sql_text: str, query_id: str) -> str:
    """在清空 query_sql 后，将 UTF-8 SQL 写入 {query_id}.sql（保留查询编号，火焰图命名正确）。"""
    qdir = _env("REMOTE_QUERY_SQL_DIR", "/usr/local/Spark-Test-Tool/sql/query_sql")
    if not qdir:
        raise ValueError("REMOTE_QUERY_SQL_DIR 不能为空")
    qdir_q = shlex.quote(qdir)
    dst_q = shlex.quote(posixpath.join(qdir, f"{query_id}.sql"))
    b64 = base64.b64encode(sql_text.encode("utf-8")).decode("ascii")
    b64_q = shlex.quote(b64)
    return f"{_build_query_sql_clear_fragment(qdir_q)} && printf '%s' {b64_q} | base64 -d > {dst_q}"


def _build_query_sql_prep_copy_tpcds_fragment() -> str:
    """在清空 query_sql 后，将 REMOTE_TPCDS_QUERY_SOURCE_DIR 下内容拷贝入 query_sql。"""
    _, qdir_q, _ = _remote_query_sql_quoted_paths()
    src = _env("REMOTE_TPCDS_QUERY_SOURCE_DIR", "/opt/hive-testbench-hdp3/spark-queries-tpcds")
    if not src:
        raise ValueError("REMOTE_TPCDS_QUERY_SOURCE_DIR 不能为空")
    src_q = shlex.quote(src.rstrip("/"))
    return f"{_build_query_sql_clear_fragment(qdir_q)} && cp -a {src_q}/. {qdir_q}/"


def _build_query_sql_prep_copy_single_tpcds_fragment(query_id: str) -> str:
    """在清空 query_sql 后，从 REMOTE_TPCDS_QUERY_SOURCE_DIR 复制单个查询文件并保留原始文件名。

    保留文件名（如 q7.sql）可确保性能测试脚本和火焰图输出以正确的查询编号命名，
    而非全部被覆盖为 q1。
    """
    qdir = _env("REMOTE_QUERY_SQL_DIR", "/usr/local/Spark-Test-Tool/sql/query_sql")
    if not qdir:
        raise ValueError("REMOTE_QUERY_SQL_DIR 不能为空")
    qdir_q = shlex.quote(qdir)
    src = _env("REMOTE_TPCDS_QUERY_SOURCE_DIR", "/opt/hive-testbench-hdp3/spark-queries-tpcds")
    if not src:
        raise ValueError("REMOTE_TPCDS_QUERY_SOURCE_DIR 不能为空")
    src_q = shlex.quote(posixpath.join(src.rstrip("/"), f"{query_id}.sql"))
    dst_q = shlex.quote(posixpath.join(qdir.rstrip("/"), f"{query_id}.sql"))
    return f"{_build_query_sql_clear_fragment(qdir_q)} && cp {src_q} {dst_q}"


def _build_collect_worker_flames_fragment() -> str:
    """在测试脚本执行完毕后，将各 Worker 节点上的 .html 火焰图归集到 Driver 本机的 REMOTE_FLAME_DIR。

    逻辑：
    1. 读取 Hadoop workers 文件（可通过 HADOOP_WORKERS_FILE 覆盖），逐行取 hostname。
    2. 跳过与本机 hostname / IP 相同的节点（本机文件已在目标目录）。
    3. 对每台远端 Worker，通过 SSH（BatchMode，不验证 hostkey）执行 ls 找到 .html，
       再用 scp 拉回 REMOTE_FLAME_DIR；两步均静默忽略错误，不中断主流程。
    执行此片段不影响整体 exit code（以 true 结尾）。
    """
    flame_dir = _env("REMOTE_FLAME_DIR", "/opt/async")
    flame_dir_q = shlex.quote(flame_dir)
    workers_file = _env("HADOOP_WORKERS_FILE", "/usr/local/hadoop/etc/hadoop/workers")
    workers_file_q = shlex.quote(workers_file)
    # 整段写成一个内联 bash，末尾 true 保证不影响调用方 exit code
    fragment = (
        f"mkdir -p {flame_dir_q}; "
        f"_self_host=$(hostname); "
        f"_self_ip=$(hostname -I | awk '{{print $1}}'); "
        f"if [ -f {workers_file_q} ]; then "
        f"  while IFS= read -r _w || [ -n \"$_w\" ]; do "
        f"    _w=$(echo \"$_w\" | tr -d '[:space:]'); "
        f"    [ -z \"$_w\" ] && continue; "
        f"    [ \"$_w\" = \"$_self_host\" ] || [ \"$_w\" = \"$_self_ip\" ] && continue; "
        f"    _htmls=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 "
        f"root@\"$_w\" \"ls {flame_dir_q}/*.html 2>/dev/null\" 2>/dev/null) || continue; "
        f"    [ -z \"$_htmls\" ] && continue; "
        f"    echo \"$_htmls\" | while read -r _f; do "
        f"      scp -o BatchMode=yes -o StrictHostKeyChecking=no -q "
        f"root@\"$_w\":\"$_f\" {flame_dir_q}/ 2>/dev/null || true; "
        f"    done; "
        f"  done < {workers_file_q}; "
        f"fi; "
        f"true"
    )
    return fragment


def _build_drop_caches_fragment() -> str:
    """在测试脚本执行完毕后，清除 Driver + 所有 Worker 节点的 OS page cache。

    确保下一次独立调用的「冷跑」是真正的冷启动（HDFS 数据不在内存中）。
    整段以 true 结尾，不影响调用方 exit code。
    """
    workers_file = _env("HADOOP_WORKERS_FILE", "/usr/local/hadoop/etc/hadoop/workers")
    workers_file_q = shlex.quote(workers_file)
    fragment = (
        "sync && echo 3 > /proc/sys/vm/drop_caches; "
        f"_self_host=$(hostname); "
        f"_self_ip=$(hostname -I | awk '{{print $1}}'); "
        f"if [ -f {workers_file_q} ]; then "
        f"  while IFS= read -r _w || [ -n \"$_w\" ]; do "
        f"    _w=$(echo \"$_w\" | tr -d '[:space:]'); "
        f"    [ -z \"$_w\" ] && continue; "
        f"    [ \"$_w\" = \"$_self_host\" ] || [ \"$_w\" = \"$_self_ip\" ] && continue; "
        f"    ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 "
        f"root@\"$_w\" 'sync && echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true; "
        f"  done < {workers_file_q}; "
        f"fi; "
        f"echo '[drop_caches] done on driver + workers'; "
        f"true"
    )
    return fragment


def _resolve_query_prep(query_sql: str, query_id: str) -> str:
    """根据 query_id / query_sql 组合决定 query_sql 目录的准备方式：

    - query_id 非空 + query_sql 非空 → 写入 {query_id}.sql（内容来自 query_sql）
    - query_id 非空 + query_sql 为空 → 从服务器源目录复制 {query_id}.sql（保留文件名）
    - query_id 为空 + query_sql 非空 → 写入 q1.sql（旧行为，向后兼容）
    - 两者均空              → 复制全量 TPC-DS 查询集
    """
    qs = (query_sql or "").strip()
    qid = (query_id or "").strip().lower()
    if qid:
        return _build_query_sql_prep_write_fragment(qs, qid) if qs else _build_query_sql_prep_copy_single_tpcds_fragment(qid)
    return _build_query_sql_prep_write_q1_fragment(qs) if qs else _build_query_sql_prep_copy_tpcds_fragment()


def _build_remote_test_all_command(query_sql: str, query_id: str = "") -> str:
    prep = _resolve_query_prep(query_sql, query_id)
    collect = _build_collect_worker_flames_fragment()
    return f"{prep} && {_build_remote_shell_command()}; {collect}"


def _build_remote_test_operator_command(query_sql: str, query_id: str = "", flame_enabled: bool = False) -> str:
    prep = _resolve_query_prep(query_sql, query_id)
    run = _build_operator_shell_command(flame_enabled)
    if not flame_enabled:
        return f"{prep} && {run}"
    collect = _build_collect_worker_flames_fragment()
    return f"{prep} && {run}; {collect}"


def _fetch_shs_plan_info(app_id: str) -> dict:
    """查询 Spark History Server REST API，返回执行计划中 Omni 算子的统计信息。

    返回字典：
      omni_ops   : {算子名: 出现次数}，跨所有 SQL query 累计
      query_count: 该 App 共有多少个 SQL 执行记录
      error      : 字符串（请求失败时非空）
    """
    shs_base = _env("SHS_BASE_URL", "")
    url = f"{shs_base}/api/v1/applications/{app_id}/sql?details=true"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            queries: list[dict] = _json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"omni_ops": {}, "query_count": 0, "error": str(exc)}

    omni_ops: dict[str, int] = {}
    # Omni 算子名出现在 planDescription 字段（物理计划文本）
    op_pattern = re.compile(r"Omni\w+(?:Exec|Transformer\w*|Exchange\w*|ToRow\w*)")
    for q in queries:
        plan = q.get("planDescription", "") or ""
        for m in op_pattern.finditer(plan):
            name = m.group()
            omni_ops[name] = omni_ops.get(name, 0) + 1

    return {"omni_ops": omni_ops, "query_count": len(queries), "error": None}


def _scrape_shs_screenshots(app_id: str) -> list[str]:
    """用 scrape_spark_execution.py 对该 App 所有 SQL query 截图，返回保存的文件路径列表。

    仅抓取 planDescription 非空（有实际执行计划）的 query，跳过纯 DDL。
    若脚本或 Playwright 不可用则静默返回空列表。
    """
    shs_base = _env("SHS_BASE_URL", "")
    scraper_path = Path(
        _env("SCRAPE_SPARK_EXECUTION_PATH")
        or str(
            Path(__file__).resolve().parent.parent.parent
            / "omni-sql-perf-improvement"
            / "scripts"
            / "scrape_spark_execution.py"
        )
    )
    if not scraper_path.exists():
        logging.warning(
            "[scrape_shs_screenshots] 截图脚本不存在，跳过 SHS 截图：%s "
            "（可通过环境变量 SCRAPE_SPARK_EXECUTION_PATH 覆盖路径）",
            scraper_path,
        )
        return []

    # 先拿 query 列表，只截有计划数据的 query
    try:
        url = f"{shs_base}/api/v1/applications/{app_id}/sql?details=true"
        with urllib.request.urlopen(url, timeout=10) as resp:
            queries: list[dict] = _json.loads(resp.read().decode("utf-8"))
    except Exception:
        return []

    saved: list[str] = []
    for q in queries:
        if not (q.get("planDescription") or "").strip():
            continue
        qid = q.get("id", 0)
        try:
            result = subprocess.run(
                ["python", str(scraper_path),
                 "-e", app_id, "-q", str(qid), "-b", shs_base],
                capture_output=True, timeout=30,
            )
            # scraper 输出含中文，用 errors='replace' 解码；路径行带 .png 扩展名
            stdout = result.stdout.decode("utf-8", errors="replace")
            for line in stdout.splitlines():
                stripped = line.strip()
                # 匹配形如 "截图已保存: D:\...\xxx.png" 或直接以 .png 结尾的行
                m = re.search(r"([A-Za-z]:[/\\].+\.png)", stripped)
                if m:
                    p = m.group(1)
                    if Path(p).exists():
                        saved.append(p)
        except Exception:
            continue

    return saved


def _build_e2e_sql_command(sql: str, database: str = "") -> str:
    """将 SQL 写入远端临时文件后用 -f 执行，规避命令行特殊字符转义问题。

    远端脚本接受两个位置参数：$1=临时 SQL 文件路径，$2=数据库名（可为空）。
    """
    script_path = _env("E2E_SQL_SCRIPT", "/home/omni/run_e2e_sql.sh")
    # 先在远端写临时 SQL 文件，再调脚本；用 printf '%s' 避免 echo 解释转义序列
    sql_file = "/tmp/mcp_e2e_$$.sql"
    write_cmd = f"printf '%s' {shlex.quote(sql)} > {sql_file}"
    run_cmd = "bash " + shlex.quote(script_path) + " " + sql_file + " " + shlex.quote(database or "")
    cleanup = f"rm -f {sql_file}"
    return f"{write_cmd} && {run_cmd}; {cleanup}"


def _extract_query_rows(lines: list[str]) -> list[str]:
    """Extract actual query result rows from spark-sql mixed stdout/stderr output."""
    query_rows: list[str] = []
    capture = False
    spark_set_output_re = re.compile(r"^spark\.[A-Za-z0-9_.-]+\t.*$")

    ignore_prefixes = (
        "Warning:",
        "Setting default log level",
        "To adjust logging level",
        "Spark Web UI available at ",
        "Spark master:",
    )
    ignore_contains = (
        "Application Id:",
        "Time taken:",
    )

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("Time taken:"):
            capture = False
            continue

        if stripped in ("", "spark-sql>"):
            continue

        if stripped.startswith("use "):
            continue

        if stripped.startswith("ERROR: ld.so:"):
            continue

        # `SET spark.xxx=false;` in spark-sql prints one tab-separated config row
        # before the real query result. Treat it as command echo, not result data.
        if spark_set_output_re.match(stripped):
            continue

        if any(stripped.startswith(prefix) for prefix in ignore_prefixes):
            continue

        if any(token in stripped for token in ignore_contains):
            continue

        if re.match(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", stripped):
            continue
        if re.match(r"^(?:INFO|WARN|ERROR|DEBUG) ", stripped):
            continue

        if stripped == "Time taken":
            continue

        if capture:
            query_rows.append(line)
            continue

        if "\t" in line:
            query_rows.append(line)
            capture = True

    return query_rows


def _extract_fetched_count(lines: list[str]) -> int | None:
    for line in reversed(lines):
        m = re.search(r"Fetched\s+(\d+)\s+row\(s\)", line)
        if m:
            return int(m.group(1))
    return None


def _parse_spark_e2e_output(merged_output: str, shs_info: dict | None = None) -> str:
    """从合并的 spark-sql 输出中提取 App ID、耗时、Omni 算子、Fallback 告警及查询结果。

    spark-sql 日志行以 "YY/MM/DD HH:MM:SS" 时间戳或 INFO/WARN/ERROR 开头；其余行为查询结果。
    shs_info: 由 _fetch_shs_plan_info 返回的字典；提供时用 SHS 物理计划替代日志扫描来检测 Omni 算子。
    """
    lines = merged_output.splitlines()

    log_re = re.compile(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}|^(?:INFO|WARN|ERROR|DEBUG) ")
    log_lines = [l for l in lines if log_re.match(l)]
    query_rows = _extract_query_rows(lines)
    fetched_count = _extract_fetched_count(lines)

    # App ID（local-XXXXXXXXXX 或 application_XXXXX_XXXX）—— 搜全部行，含控制台输出
    app_id = "未找到"
    for line in lines:
        m = re.search(r"(local-\d+|application_\d{13}_\d{4})", line)
        if m:
            app_id = m.group(1)
            break

    # Time taken（spark-sql 在查询结束后打印）
    # 优先取含 "Fetched" 的行（SELECT 成功），避免误取 SET 语句的时间
    time_taken = "未知"
    query_failed = False
    for line in reversed(lines):
        m = re.search(r"Time taken: ([\d.]+) seconds.*Fetched", line)
        if m:
            time_taken = m.group(1) + "s"
            break
    if time_taken == "未知":
        # 没有含 Fetched 的 Time taken → 检查是否有查询异常
        error_kws = ("MEM_CAP_EXCEEDED", "OmniException", "Exception in thread",
                     "FAILED", "Error running query", "SparkException")
        for line in lines:
            if any(k in line for k in error_kws):
                query_failed = True
                break
        if query_failed:
            time_taken = "查询失败（未完成）"
        else:
            # 没有 Fetched 也没有异常，退回最后一个 Time taken（可能是 DDL/DML）
            for line in reversed(lines):
                m = re.search(r"Time taken: ([\d.]+) seconds", line)
                if m:
                    time_taken = m.group(1) + "s"
                    break

    # Fallback 告警
    fallback_kws = (
        "FallbackNode", "Validation failed", "native validation failed",
        "GlutenFallbackReporter", "fell back to",
    )
    fallback_lines = [
        l for l in log_lines if any(k.lower() in l.lower() for k in fallback_kws)
    ]

    parts: list[str] = []
    parts.append(f"App ID : {app_id}  |  耗时 : {time_taken}")
    parts.append("")

    # ── Omni 算子下推：优先使用 SHS 物理计划，回退到控制台日志扫描 ──────────
    parts.append("─── Omni 算子下推 ──────────────────────────")
    if shs_info is not None:
        shs_err = shs_info.get("error")
        if shs_err:
            parts.append(f"  ⚠️  SHS 查询失败：{shs_err}")
            parts.append("  （无法通过执行计划确认算子下推情况）")
        else:
            omni_ops = shs_info.get("omni_ops", {})
            if omni_ops:
                for name, cnt in sorted(omni_ops.items()):
                    parts.append(f"  ✅ {name}  ×{cnt}")
            else:
                parts.append("  ⚠️  未检测到 Omni 算子（SHS 物理计划中无 Omni 节点，可能全部 Fallback）")
            parts.append(f"  来源：Spark History Server（共 {shs_info.get('query_count', 0)} 个 SQL）")
    else:
        # 无 SHS 数据时，回退到控制台日志扫描（覆盖率有限）
        omni_ops_log: dict[str, int] = {}
        for line in log_lines:
            for m in re.finditer(r"Omni\w+(?:Exec|Transformer\w*)", line):
                name = m.group()
                omni_ops_log[name] = omni_ops_log.get(name, 0) + 1
        if omni_ops_log:
            for name, cnt in sorted(omni_ops_log.items()):
                parts.append(f"  ✅ {name}  ×{cnt}")
        else:
            parts.append("  ⚠️  未检测到 Omni 算子（SHS 不可用，仅扫描控制台日志，覆盖率有限）")
    parts.append("")

    parts.append(f"─── Fallback 告警（{len(fallback_lines)} 条）────────────────")
    if fallback_lines:
        for line in fallback_lines[:15]:
            parts.append(f"  ⚠️  {line.strip()}")
        if len(fallback_lines) > 15:
            parts.append(f"  ... 另有 {len(fallback_lines) - 15} 条，查看完整日志")
    else:
        parts.append("  ✅ 无 Fallback 告警")
    parts.append("")

    parts.append("─── 查询结果 ────────────────────────────────")
    if query_rows:
        show = query_rows[-40:] if len(query_rows) > 40 else query_rows
        total_rows = fetched_count if fetched_count is not None else len(query_rows)
        if len(query_rows) > 40:
            parts.append(f"  （共 {total_rows} 行，显示末尾 40 行）")
        parts.extend(show)
        if fetched_count is not None and fetched_count != len(query_rows):
            parts.append(f"  （Spark 统计返回 {fetched_count} 行，本地提取到 {len(query_rows)} 行结果）")
    else:
        parts.append("  （无查询输出行）")

    return "\n".join(parts)


def _build_e2e_sql_native_command(sql: str, database: str = "") -> str:
    """将 SQL 写入远端临时文件后用原生 Spark（无 Gluten/Omni）执行。

    远端脚本接受两个位置参数：$1=临时 SQL 文件路径，$2=数据库名（可为空）。
    """
    script_path = _env("E2E_SQL_NATIVE_SCRIPT", "/home/omni/run_e2e_sql_native.sh")
    sql_file = "/tmp/mcp_e2e_native_$$.sql"
    write_cmd = f"printf '%s' {shlex.quote(sql)} > {sql_file}"
    run_cmd = "bash " + shlex.quote(script_path) + " " + sql_file + " " + shlex.quote(database or "")
    cleanup = f"rm -f {sql_file}"
    return f"{write_cmd} && {run_cmd}; {cleanup}"


def _parse_spark_native_output(merged_output: str) -> str:
    """从原生 Spark 输出中提取 App ID、耗时及查询结果（无 Omni/Fallback 部分）。"""
    lines = merged_output.splitlines()

    log_re = re.compile(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}|^(?:INFO|WARN|ERROR|DEBUG) ")
    log_lines = [l for l in lines if log_re.match(l)]
    query_rows = _extract_query_rows(lines)
    fetched_count = _extract_fetched_count(lines)

    app_id = "未找到"
    for line in lines:
        m = re.search(r"(local-\d+|application_\d{13}_\d{4})", line)
        if m:
            app_id = m.group(1)
            break

    # 优先取含 "Fetched" 的 Time taken 行（SELECT 成功），避免误取 SET 语句的时间
    time_taken = "未知"
    for line in reversed(lines):
        m = re.search(r"Time taken: ([\d.]+) seconds.*Fetched", line)
        if m:
            time_taken = m.group(1) + "s"
            break
    if time_taken == "未知":
        error_kws = ("MEM_CAP_EXCEEDED", "OmniException", "Exception in thread",
                     "FAILED", "Error running query", "SparkException")
        query_failed = False
        for line in lines:
            if any(k in line for k in error_kws):
                query_failed = True
                break
        if query_failed:
            time_taken = "查询失败（未完成）"
        else:
            for line in reversed(lines):
                m = re.search(r"Time taken: ([\d.]+) seconds", line)
                if m:
                    time_taken = m.group(1) + "s"
                    break

    parts: list[str] = []
    parts.append(f"App ID : {app_id}  |  耗时 : {time_taken}")
    parts.append("")
    parts.append("─── 查询结果 ────────────────────────────────")
    if query_rows:
        show = query_rows[-40:] if len(query_rows) > 40 else query_rows
        total_rows = fetched_count if fetched_count is not None else len(query_rows)
        if len(query_rows) > 40:
            parts.append(f"  （共 {total_rows} 行，显示末尾 40 行）")
        parts.extend(show)
        if fetched_count is not None and fetched_count != len(query_rows):
            parts.append(f"  （Spark 统计返回 {fetched_count} 行，本地提取到 {len(query_rows)} 行结果）")
    else:
        parts.append("  （无查询输出行）")

    return "\n".join(parts)


def _extract_e2e_digest(merged_output: str) -> dict:
    """Extract a stable digest from spark-sql output for debug comparisons."""
    lines = merged_output.splitlines()
    query_rows = [l.rstrip() for l in _extract_query_rows(lines)]
    fetched_count = _extract_fetched_count(lines)

    app_id = "未找到"
    for line in lines:
        m = re.search(r"(local-\d+|application_\d{13}_\d{4})", line)
        if m:
            app_id = m.group(1)
            break

    time_taken = "未知"
    for line in reversed(lines):
        m = re.search(r"Time taken: ([\d.]+) seconds.*Fetched", line)
        if m:
            time_taken = m.group(1) + "s"
            break
    if time_taken == "未知":
        for line in reversed(lines):
            m = re.search(r"Time taken: ([\d.]+) seconds", line)
            if m:
                time_taken = m.group(1) + "s"
                break

    error_kws = (
        "MEM_CAP_EXCEEDED", "OmniException", "Exception in thread",
        "FAILED", "Error running query", "SparkException",
    )
    error_lines = [l.strip() for l in lines if any(k in l for k in error_kws)]

    fallback_kws = (
        "FallbackNode", "Validation failed", "native validation failed",
        "GlutenFallbackReporter", "fell back to",
    )
    fallback_lines = [
        l.strip() for l in lines if any(k.lower() in l.lower() for k in fallback_kws)
    ]

    omni_ops: dict[str, int] = {}
    for line in lines:
        for m in re.finditer(r"Omni\w+(?:Exec|Transformer\w*|Exchange\w*|ToRow\w*)", line):
            name = m.group()
            omni_ops[name] = omni_ops.get(name, 0) + 1

    return {
        "app_id": app_id,
        "time_taken": time_taken,
        "result_lines": query_rows,
        "result_tail": query_rows[-40:] if len(query_rows) > 40 else query_rows,
        "result_count": fetched_count if fetched_count is not None else len(query_rows),
        "query_row_count": len(query_rows),
        "fetched_count": fetched_count,
        "error_lines": error_lines,
        "fallback_count": len(fallback_lines),
        "fallback_sample": fallback_lines[:5],
        "omni_ops": omni_ops,
    }


def _compare_result_rows(actual: list[str], baseline: list[str] | None) -> dict[str, bool | None]:
    if baseline is None:
        return {"exact": None, "sorted": None}
    return {
        "exact": actual == baseline,
        "sorted": sorted(actual) == sorted(baseline),
    }


def _run_e2e_sql_once(sql: str, database: str, timeout_sec: int, native: bool, log_prefix: str) -> dict:
    """Run one E2E SQL command and return raw output plus parsed digest."""
    final_sql = f"USE {database};\n{sql}" if database else sql
    cmd = (
        _build_e2e_sql_native_command(final_sql, database)
        if native else
        _build_e2e_sql_command(final_sql, database)
    )
    log_path = _new_compile_log_path(log_prefix)
    code, body = _run_remote_with_exit_and_log(cmd, log_path, timeout_sec)

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            full_output = f.read()
    except OSError:
        full_output = body

    digest = _extract_e2e_digest(full_output)
    digest.update({
        "exit_code": code,
        "success": code == 0 and not digest["error_lines"],
        "log_path": log_path,
    })
    return digest


def _build_compile_omni_remote_command(git_repo_url: str, branch: str) -> str:
    """直接将 URL 与分支作为位置参数传给脚本（$1 $2），脚本内 compile_op 使用 $1/$2 完成 clone。"""
    script_path = _env("COMPILE_OMNI_SCRIPT", "/home/omni/compile_omni.sh")
    return "bash " + shlex.quote(script_path) + " " + shlex.quote(git_repo_url) + " " + shlex.quote(branch)


def _build_compile_gluten_remote_command(
    omni_git_repo_url: str,
    omni_branch: str,
    gluten_git_repo_url: str,
    gluten_branch: str,
) -> str:
    """直接将四个位置参数传给脚本（$1 Omni URL，$2 Omni 分支，$3 Gluten URL，$4 Gluten 分支）。"""
    script_path = _env("COMPILE_GLUTEN_SCRIPT", "/home/omni/compile_gluten.sh")
    return (
        "bash "
        + shlex.quote(script_path)
        + " " + shlex.quote(omni_git_repo_url)
        + " " + shlex.quote(omni_branch)
        + " " + shlex.quote(gluten_git_repo_url)
        + " " + shlex.quote(gluten_branch)
    )


def _ssh_argv(remote_cmd: str) -> list[str]:
    host = _env("SSH_HOST", "")
    user = _env("SSH_USER")
    port = _env("SSH_PORT", "22")
    identity = _env("SSH_IDENTITY")

    target = f"{user}@{host}" if user else host
    argv: list[str] = [
        "ssh",
        "-p",
        port,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    if identity:
        argv.extend(["-i", identity])
    argv.extend([target, "bash", "-lc", remote_cmd])
    return argv


def _paramiko_connect() -> paramiko.SSHClient:
    """与远端建立 SSH（密码或 SSH_IDENTITY 密钥；二者皆无则尝试 Paramiko 默认密钥/代理）。"""
    host = _env("SSH_HOST", "")
    user = _env("SSH_USER", "")
    password = _env("SSH_PASSWORD")
    port_s = _env("SSH_PORT", "22") or "22"
    port = int(port_s)
    identity = _env("SSH_IDENTITY")
    timeout = int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kw: dict = {
        "hostname": host,
        "port": port,
        "username": user,
        "timeout": min(60, max(10, timeout)),
        "banner_timeout": 30,
        "auth_timeout": 30,
    }
    if password:
        kw["password"] = password
    if identity:
        kw["key_filename"] = identity
    client.connect(**kw)
    return client


def _run_via_paramiko_password(remote_cmd: str) -> tuple[str, str, int, str]:
    """使用 Paramiko 执行 remote_cmd。返回 (stdout, stderr, exit_code, 摘要说明)。"""
    host = _env("SSH_HOST", "")
    user = _env("SSH_USER", "")
    port_s = _env("SSH_PORT", "22") or "22"
    port = int(port_s)
    meta = f"paramiko {user}@{host}:{port} bash -lc <remote>"

    client = _paramiko_connect()
    try:
        wrapped = f"bash -lc {shlex.quote(remote_cmd)}"
        stdin, stdout, stderr = client.exec_command(wrapped, get_pty=True)
        stdin.close()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return out, err, code, meta
    finally:
        client.close()


def _default_flame_local_root() -> str:
    return _env("FLAME_LOCAL_DIR") or str(Path(__file__).resolve().parent / "flame_exports")


def _default_compile_log_dir() -> str:
    return _env("COMPILE_LOG_DIR") or str(Path(__file__).resolve().parent / "compile_logs")


def _new_compile_log_path(label: str) -> str:
    """生成带时间戳的日志路径，同时在日志目录下维护 latest.log 软链/占位文件记录最新路径。"""
    log_dir = _default_compile_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(log_dir, f"{label}_{stamp}.log")
    # 写一个 latest.log 纯文本指针，方便 get_compile_log 找到最新日志
    pointer = os.path.join(log_dir, "latest.log")
    try:
        with open(pointer, "w", encoding="utf-8") as f:
            f.write(log_path)
    except OSError:
        pass
    return log_path


def _run_via_paramiko_streaming(
    remote_cmd: str, log_path: str, timeout_sec: int
) -> tuple[str, int]:
    """Paramiko 流式执行：分块读取输出并实时写入 log_path，返回 (merged_output, exit_code)。"""
    client = _paramiko_connect()
    try:
        wrapped = f"bash -lc {shlex.quote(remote_cmd)}"
        transport = client.get_transport()
        assert transport is not None
        chan = transport.open_session()
        chan.get_pty()
        chan.exec_command(wrapped)

        buf: list[str] = []
        deadline = time.monotonic() + timeout_sec
        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            while True:
                if chan.recv_ready():
                    chunk = chan.recv(8192).decode("utf-8", errors="replace")
                    if chunk:
                        buf.append(chunk)
                        f.write(chunk)
                        f.flush()
                elif chan.exit_status_ready():
                    # 退出后排空残余输出
                    while chan.recv_ready():
                        chunk = chan.recv(8192).decode("utf-8", errors="replace")
                        if chunk:
                            buf.append(chunk)
                            f.write(chunk)
                            f.flush()
                    break
                elif time.monotonic() > deadline:
                    f.write(f"\n[MCP] 超时（{timeout_sec}s），强制断开。\n")
                    chan.close()
                    break
                else:
                    time.sleep(0.2)

        code = chan.recv_exit_status()
        return "".join(buf), code
    finally:
        client.close()


def _fetch_flame_htmls_sync(
    remote_dir: str | None = None,
    session_folder_name: str | None = None,
    max_files: int = 10,
) -> str:
    """SFTP 将远端目录下 .html 拉到本机子目录，返回说明与 file:// 链接。"""
    auto_pick_latest_subdir = not (remote_dir and remote_dir.strip())
    remote_root = (
        remote_dir.strip()
        if remote_dir and remote_dir.strip()
        else _env("REMOTE_FLAME_DIR", "/opt/async")
    ).rstrip("/")
    base_local = _default_flame_local_root()
    stamp = (
        session_folder_name.strip()
        if session_folder_name and session_folder_name.strip()
        else datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    local_session = os.path.join(base_local, stamp)
    os.makedirs(local_session, exist_ok=True)

    try:
        client = _paramiko_connect()
    except Exception as e:
        return (
            f"SFTP 连接失败: {e}\n"
            "请配置 SSH_PASSWORD，或配置 SSH_IDENTITY 指向私钥，并确保 Paramiko 能登录该主机。"
        )

    lines: list[str] = [
        f"远端目录: {remote_root}",
        f"本机目录: {os.path.abspath(local_session)}",
        "",
    ]
    downloaded: list[str] = []
    errors: list[str] = []
    skipped_count = 0

    try:
        sftp = client.open_sftp()
        try:
            try:
                entries = sftp.listdir_attr(remote_root)
            except OSError as e:
                return f"无法访问远端目录 {remote_root}: {e}"
            picked_subdir = ""
            html_entries = []
            for attr in entries:
                name = attr.filename
                if name in (".", "..") or not name.lower().endswith(".html"):
                    continue
                safe = posixpath.basename(name)
                if not safe or safe != name:
                    continue
                html_entries.append(attr)
            if not html_entries and auto_pick_latest_subdir:
                subdirs = []
                for attr in entries:
                    name = attr.filename
                    if name in (".", ".."):
                        continue
                    safe = posixpath.basename(name)
                    if not safe or safe != name:
                        continue
                    if stat.S_ISDIR(getattr(attr, "st_mode", 0) or 0):
                        subdirs.append(attr)
                subdirs.sort(key=lambda a: getattr(a, "st_mtime", 0) or 0, reverse=True)
                for subdir in subdirs:
                    candidate_root = posixpath.join(remote_root, subdir.filename)
                    try:
                        candidate_entries = sftp.listdir_attr(candidate_root)
                    except OSError:
                        continue
                    candidate_htmls = []
                    for attr in candidate_entries:
                        name = attr.filename
                        if name in (".", "..") or not name.lower().endswith(".html"):
                            continue
                        safe = posixpath.basename(name)
                        if not safe or safe != name:
                            continue
                        candidate_htmls.append(attr)
                    if candidate_htmls:
                        picked_subdir = candidate_root
                        remote_root = candidate_root
                        html_entries = candidate_htmls
                        break
            if picked_subdir:
                lines[0] = f"远端目录: {remote_root}"
                lines.insert(1, f"自动选择最新火焰图子目录: {picked_subdir}")
            html_entries.sort(key=lambda a: getattr(a, "st_mtime", 0) or 0, reverse=True)
            if max_files > 0:
                skipped_count = max(0, len(html_entries) - max_files)
                html_entries = html_entries[:max_files]
            for attr in html_entries:
                safe = posixpath.basename(attr.filename)
                remote_path = posixpath.join(remote_root, safe)
                local_path = os.path.join(local_session, safe)
                try:
                    sftp.get(remote_path, local_path)
                    downloaded.append(os.path.abspath(local_path))
                except OSError as e:
                    errors.append(f"{safe}: {e}")
        finally:
            sftp.close()
    finally:
        client.close()

    if errors:
        lines.append("--- 部分失败 ---")
        lines.extend(errors)
        lines.append("")

    if not downloaded:
        lines.append("未找到 .html 文件（火焰图可能尚未写出，或路径不对）。")
        lines.append("可调环境变量 REMOTE_FLAME_DIR 或传参 remote_dir。")
        return "\n".join(lines)

    lines.append(f"已下载 {len(downloaded)} 个 HTML 文件。在资源管理器中打开本机目录后双击即可用浏览器查看；")
    if skipped_count:
        lines.append(f"Only downloaded the latest {len(downloaded)} file(s); skipped {skipped_count} older HTML file(s).")
    lines.append("也可复制下列 file:// 链接到浏览器地址栏（Chrome/Edge 通常支持本地 file URL）：")
    lines.append("")
    for p in downloaded:
        uri = Path(p).resolve().as_uri()
        lines.append(uri)
    return "\n".join(lines)


def _format_run_result(proc_stdout: str, proc_stderr: str, code: int) -> str:
    out: list[str] = []
    if proc_stdout.strip():
        out.append("--- stdout ---\n" + proc_stdout.rstrip())
    if proc_stderr.strip():
        out.append("--- stderr ---\n" + proc_stderr.rstrip())
    out.append(f"--- exit code ---\n{code}")
    if out:
        return "\n\n".join(out)
    return f"(无输出)\n\n--- exit code ---\n{code}"


def _run_remote_with_exit(
    remote_cmd: str, *, timeout_sec: int | None = None
) -> tuple[int | None, str]:
    """在远端执行一条 shell 命令。

    返回 (exit_code, text)。exit_code 为 None 表示未执行到远端命令结束（连接/超时/本机 ssh 缺失等）；
    否则为远端 bash -lc 整条流水线的退出码（含 python3 改写脚本失败或 compile_omni.sh 非 0）。
    """
    timeout = (
        timeout_sec
        if timeout_sec is not None
        else int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    )

    if _env("SSH_PASSWORD"):
        meta = (
            f"paramiko {_env('SSH_USER', '')}@{_env('SSH_HOST', '')}:"
            f"{_env('SSH_PORT', '22') or '22'} bash -lc <remote>"
        )
        try:
            proc_stdout, proc_stderr, code, _ = _run_via_paramiko_password(remote_cmd)
        except paramiko.AuthenticationException:
            return None, f"SSH 认证失败（用户名或密码错误）。\n{meta}"
        except paramiko.SSHException as e:
            return None, f"SSH 错误: {e}\n{meta}"
        except OSError as e:
            return None, f"网络或连接错误: {e}\n{meta}"
        except Exception as e:
            return None, f"执行失败: {e}\n{meta}"
        return code, _format_run_result(proc_stdout, proc_stderr, code)

    argv = _ssh_argv(remote_cmd)
    meta = f"$ {' '.join(shlex.quote(a) for a in argv[:6])} ... bash -lc <remote>"

    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"SSH 执行超时（{timeout} 秒）。\n命令概要: {meta}"
    except FileNotFoundError:
        return None, (
            "未找到 ssh 可执行文件。请在 Windows「可选功能」中安装 OpenSSH 客户端，"
            "或确保 ssh 在 PATH 中。\n"
            f"命令概要: {meta}"
        )
    except Exception as e:
        return None, f"执行失败: {e}\n命令概要: {meta}"

    return proc.returncode, _format_run_result(proc.stdout or "", proc.stderr or "", proc.returncode)


def _run_remote(remote_cmd: str, *, timeout_sec: int | None = None) -> str:
    """在远端执行一条 shell 命令（与登录方式一致），返回格式化的 stdout/stderr/exit code。"""
    _code, text = _run_remote_with_exit(remote_cmd, timeout_sec=timeout_sec)
    return text


def _run_remote_with_exit_and_log(
    remote_cmd: str, log_path: str, timeout_sec: int
) -> tuple[int | None, str]:
    """执行远端命令，同时将输出实时流式写入 log_path。

    优先使用 Paramiko 流式读取；SSH_PASSWORD 未设置时退回 subprocess（Popen 逐行写日志）。
    返回 (exit_code, formatted_text)，exit_code 为 None 表示连接/超时异常。
    """
    if _env("SSH_PASSWORD"):
        meta = (
            f"paramiko {_env('SSH_USER', '')}@{_env('SSH_HOST', '')}:"
            f"{_env('SSH_PORT', '22') or '22'} [streaming → {log_path}]"
        )
        try:
            out, code = _run_via_paramiko_streaming(remote_cmd, log_path, timeout_sec)
        except paramiko.AuthenticationException:
            return None, f"SSH 认证失败（用户名或密码错误）。\n{meta}"
        except paramiko.SSHException as e:
            return None, f"SSH 错误: {e}\n{meta}"
        except OSError as e:
            return None, f"网络或连接错误: {e}\n{meta}"
        except Exception as e:
            return None, f"执行失败: {e}\n{meta}"
        return code, _format_run_result(out, "", code)

    # subprocess 路径：用 Popen 逐行写日志
    argv = _ssh_argv(remote_cmd)
    meta = f"ssh [streaming → {log_path}]"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            buf: list[str] = []
            assert proc.stdout is not None
            deadline = time.monotonic() + timeout_sec
            for line in proc.stdout:
                buf.append(line)
                lf.write(line)
                lf.flush()
                if time.monotonic() > deadline:
                    proc.kill()
                    lf.write(f"\n[MCP] 超时（{timeout_sec}s），强制终止。\n")
                    break
            proc.wait()
        code = proc.returncode
        return code, _format_run_result("".join(buf), "", code)
    except FileNotFoundError:
        return None, (
            "未找到 ssh 可执行文件。请在 Windows「可选功能」中安装 OpenSSH 客户端，"
            f"或确保 ssh 在 PATH 中。\n命令概要: {meta}"
        )
    except Exception as e:
        return None, f"执行失败: {e}\n命令概要: {meta}"


def _compile_job_timeout_seconds(env_var: str) -> int:
    """长耗时编译：env_var 有值则用其秒数；否则取 max(7200, SSH_TIMEOUT_SECONDS)。"""
    v = _env(env_var)
    if v:
        return int(v)
    ssh = _env("SSH_TIMEOUT_SECONDS", "3600") or "3600"
    n = int(ssh)
    return n if n >= 7200 else 7200


def _extract_compile_digest(log_text: str) -> str:
    """从编译+UT 日志中提取关键信息，供 agent 快速定位问题。

    提取：
      1. GTest 摘要行（PASSED/FAILED 统计 + 失败用例名）
      2. 关键编译错误行（error:/FATAL/make:***…），去重最多 30 条
      3. 日志末尾 50 行（兜底）
    """
    lines = log_text.splitlines()

    # ── GTest 结果 ───────────────────────────────────────────────────
    gtest_summary: list[str] = []
    failed_cases: list[str] = []
    gtest_re = re.compile(
        r"\[(?:={10}|-{10}| RUN  |  OK  | FAILED | PASSED | DISABLED )\]"
    )
    for line in lines:
        if gtest_re.search(line):
            gtest_summary.append(line.rstrip())
        if re.search(r"\[\s*FAILED\s*\]", line) and "listed below" not in line:
            failed_cases.append(line.rstrip())

    # ── 编译错误关键行 ────────────────────────────────────────────────
    err_re = re.compile(
        r"(?i)(\berror\b|\bFATAL\b|make:\s+\*\*\*|ninja:\s+build\s+stopped"
        r"|CMake Error|BUILD FAILURE|\[\s*FAILED\s*\])"
    )
    error_lines = [l.rstrip() for l in lines if err_re.search(l)]
    seen: set[str] = set()
    deduped: list[str] = []
    for l in error_lines:
        k = l.strip()
        if k not in seen:
            seen.add(k)
            deduped.append(l)

    parts: list[str] = []

    if gtest_summary:
        parts.append("─── UT（GTest）结果 ─────────────────────────────")
        # 过滤掉 RUN/OK 的逐行记录，只保留汇总与失败行
        shown = [l for l in gtest_summary if not re.search(r"\[ RUN  \]|\[  OK  \]", l)]
        parts.extend(shown[-60:])
        if failed_cases:
            parts.append("")
            parts.append("失败用例（最多 40 条）：")
            parts.extend(failed_cases[:40])

    if deduped:
        parts.append("")
        parts.append("─── 关键错误行（去重，最多 30 条）─────────────────")
        parts.extend(deduped[-30:])

    parts.append("")
    parts.append("─── 日志末尾 50 行 ─────────────────────────────────")
    parts.extend(lines[-50:])

    return "\n".join(parts)


def _summarize_named_compile_outcome(
    name_cn: str,
    fail_steps_cn: str,
    exit_code: int | None,
    detail: str,
) -> str:
    if exit_code is None:
        return (
            f"【{name_cn} 编译】未能完成远程执行（连接中断、超时或本机 SSH 异常等）。"
            "以下为本工具返回的说明与可能的报错输出。\n\n"
            + detail
        )
    if exit_code != 0:
        return (
            f"【{name_cn} 编译失败】远程整条命令已结束，**退出码为 {exit_code}（非 0）**。"
            f"失败可能发生在：{fail_steps_cn}。"
            "请重点查看下方 UT/编译错误摘要。\n\n"
            + detail
        )
    return (
        f"【{name_cn} 编译成功】远程整条命令退出码为 **0**。"
        "（若脚本内部仍有问题但未以非 0 退出，请以日志为准。）\n\n"
        + detail
    )



@mcp.tool()
async def drop_cluster_caches() -> str:
    """清除 Driver + 所有 Worker 节点的 OS page cache（sync && echo 3 > /proc/sys/vm/drop_caches）。

    用于性能测试之间：确保下一次运行的「冷跑」是真正的冷启动（HDFS/ORC 数据不在 page cache 中）。
    在每次 run_spark_test_operator / run_spark_test_all 调用之前手动调用此工具。
    """
    cmd = _build_drop_caches_fragment()
    return await asyncio.to_thread(_run_remote, cmd, timeout_sec=60)


@mcp.tool()
async def spark_ssh_check() -> str:
    """快速检查能否 SSH 登录：远端执行 echo / hostname / pwd。exit code 为 0 且 stdout 含 SPARK_MCP_OK 即表示连上。"""
    check_cmd = _env("SSH_CHECK_COMMAND", "echo SPARK_MCP_OK && hostname && pwd")
    to = int(_env("SSH_CHECK_TIMEOUT", "30") or "30")
    return await asyncio.to_thread(_run_remote, check_cmd, timeout_sec=to)


@mcp.tool()
async def run_spark_test_all(query_sql: str = "", query_id: str = "") -> str:
    """连接 SSH_HOST 执行 test-all.sh（Native Spark 全量测试）。

    参数说明（优先使用 query_id）：
      query_id  TPC-DS 查询编号，如 "q7"。非空时从服务器复制对应 SQL 文件并保留文件名，
                确保火焰图和日志以正确查询编号命名。
      query_sql 自定义 SQL 文本；与 query_id 同时传时写入 {query_id}.sql，
                单独传时写入 q1.sql；两者均空则复制全量 TPC-DS 查询集。

    日志自动保存到 COMPILE_LOG_DIR（默认 spark_remote_mcp/compile_logs/）下，文件名含时间戳。
    """
    try:
        remote = _build_remote_test_all_command(query_sql or "", query_id or "")
    except ValueError as e:
        return f"配置错误: {e}"
    log_path = _new_compile_log_path("perf_native")
    timeout = int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    # 必须在线程里跑阻塞 SSH：否则会卡住 stdio MCP 的事件循环，收尾时出现 BrokenResourceError
    code, text = await asyncio.to_thread(
        _run_remote_with_exit_and_log, remote, log_path, timeout
    )
    return text + f"\n\n日志已保存：{log_path}"


@mcp.tool()
async def run_spark_test_operator(query_sql: str = "", query_id: str = "", flame_enabled: bool = False) -> str:
    """【性能测试专用】在集群上执行 SQL **一次**并返回端到端耗时，用于 Omni-Before / Omni-After 性能对比。

    ⚠️  本工具专用于性能计时，不返回查询结果内容，不用于正确性校验。
        正确性校验（结果对比、算子下推验证）请使用 run_e2e_sql。

    单次行为说明：
      - 远端 test-all-operator.sh **每次调用只跑 1 次** SQL，返回这一次的端到端耗时。
      - 想要冷启动 + 热启动数据需**由调用方连续多次调用本工具**：
          * 第 1 次：冷启动（page cache 未预热，Yarn cache 已清），记录冷启动时延
          * 第 2~4 次：热启动（数据已在 cache），取三次均值作为性能基准
      - 默认 flame_enabled=false，不加载 async-profiler，不产生火焰图，用于纯性能计时。
      - 需要画像时单独调用一次 flame_enabled=true，再通过 fetch_spark_flame_graphs 拉到本地。

    典型使用场景：
      - Phase 1 Baseline：连续调本工具 4 次（冷 1 + 热 3，flame_enabled=false），建立 Omni-Before 热均值基线
      - Phase 6 性能验证：连续调本工具 4 次（冷 1 + 热 3，flame_enabled=false），获取 Omni-After 热均值，与 Before 对比
      - Phase 2/6b Profiling：额外调 1 次（flame_enabled=true）生成火焰图；这次不纳入热均值

    参数说明（优先使用 query_id）：
      query_id    TPC-DS 查询编号，如 "q7"、"q17"、"q47"。
                  非空时直接从服务器 REMOTE_TPCDS_QUERY_SOURCE_DIR 复制对应 SQL 文件，
                  保留文件名（q7.sql），确保火焰图和日志以正确查询编号命名。
                  推荐方式：服务器上已有标准 TPC-DS SQL，直接传 query_id 即可。
      query_sql   自定义 SQL 文本。与 query_id 同时传时，写入 {query_id}.sql；
                  单独传时写入 q1.sql（火焰图将命名为 q1，仅用于非 TPC-DS 场景）。
                  两者均为空则复制全量 TPC-DS 查询集。
      flame_enabled 是否开启 async-profiler。默认 false；true 时向远端脚本注入
                  OMNI_FLAME_ENABLED=1。

    内部实现：清空 REMOTE_QUERY_SQL_DIR（默认 …/sql/query_sql），
    准备好 SQL 文件后进入 REMOTE_OPERATOR_DIR 执行 test-all-operator.sh。
    日志自动保存到 COMPILE_LOG_DIR（默认 spark_remote_mcp/compile_logs/）。
    """
    try:
        remote = _build_remote_test_operator_command(query_sql or "", query_id or "", bool(flame_enabled))
    except ValueError as e:
        return f"配置错误: {e}"
    log_path = _new_compile_log_path("perf_omni")
    timeout = int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    code, text = await asyncio.to_thread(
        _run_remote_with_exit_and_log, remote, log_path, timeout
    )
    return text + f"\n\n日志已保存：{log_path}"


@mcp.tool()
async def compile_omni(branch: str, git_repo_url: str = "") -> str:
    """在 Docker 容器内编译 OmniOperator 并运行全量 UT，**不**将产物部署到宿主机。

    宿主机脚本 COMPILE_OMNI_SCRIPT（默认 /home/omni/compile_omni.sh）通过
    `docker exec mgx_omni_compiler1 /home/omni/compile_omni.sh $1 $2` 在容器内执行：
      1. git clone <git_repo_url> -b <branch> → /home/omni/OmniOperator
      2. bash build_scripts/build.sh release:java
      3. mvn clean install（Java bindings，aarch64，跳过测试）
      4. /home/omni/OmniOperator/build/core/test/omtest（GTest 全量 UT）

    编译产物留在容器内，**不 docker cp 到宿主机**。
    若只需验证 Omni 代码可编译并通过 UT，使用本工具；
    若需将新版本部署到宿主机供性能测试使用，请改用 compile_gluten。

    必须提供 branch；git_repo_url 可省略，省略时自动从本地仓
    `PROJECT_ROOT/OmniOperator` 的 origin 读取（PROJECT_ROOT 默认 = server.py 上一级目录）。
    执行结束后按退出码给出【成功/失败/未完成】摘要；非 0 时包含 GTest UT 摘要、编译错误行（去重）、日志末尾 50 行。
    可用 get_compile_log 读取完整日志。
    超时：COMPILE_OMNI_TIMEOUT_SECONDS（未设置时默认至少 7200 秒）。
    """
    br = (branch or "").strip()
    gr = (git_repo_url or "").strip()
    if not gr:
        gr = _resolve_git_remote_url("OmniOperator")
    missing: list[str] = []
    if not gr:
        missing.append(
            "gitcode 代码仓地址（参数 git_repo_url，例如 https://gitcode.com/<your_fork>/OmniOperator.git；"
            "或在 PROJECT_ROOT/OmniOperator 下配置 git remote 让本工具自动读取）"
        )
    if not br:
        missing.append("分支名（参数 branch，例如 2026_330_poc）")
    if missing:
        return (
            "无法执行 Omni 编译：缺少或未填写必填参数，请先向用户确认后再调用本工具。\n"
            "必须提供：\n- "
            + "\n- ".join(missing)
        )
    cmd = _build_compile_omni_remote_command(gr, br)
    timeout = _compile_job_timeout_seconds("COMPILE_OMNI_TIMEOUT_SECONDS")
    log_path = _new_compile_log_path("compile_omni")

    def _go() -> str:
        code, _raw = _run_remote_with_exit_and_log(cmd, log_path, timeout)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        except OSError:
            log_text = _raw
        digest = _extract_compile_digest(log_text)
        summary = _summarize_named_compile_outcome(
            "Omni",
            "git clone / build.sh / mvn / omtest UT",
            code,
            digest,
        )
        return summary + f"\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


def _resolve_gluten_compile_inputs(
    omni_branch: str,
    gluten_branch: str,
    omni_git_repo_url: str,
    gluten_git_repo_url: str,
) -> tuple[str, str, str, str, list[str]]:
    """Resolve common Omni/Gluten compile inputs and return missing-field messages."""
    o_br = (omni_branch or "").strip()
    g_br = (gluten_branch or "").strip()
    o_url = (omni_git_repo_url or "").strip()
    g_url = (gluten_git_repo_url or "").strip()
    if not o_url:
        o_url = _resolve_git_remote_url("OmniOperator")
    if not g_url:
        g_url = _resolve_git_remote_url("Gluten")
    missing: list[str] = []
    if not o_url:
        missing.append(
            "Omni 的 gitcode 代码仓地址（参数 omni_git_repo_url，例如 https://gitcode.com/<your_fork>/OmniOperator.git；"
            "或在 PROJECT_ROOT/OmniOperator 下配置 git remote 让本工具自动读取）"
        )
    if not o_br:
        missing.append("Omni 的分支名（参数 omni_branch，例如 2026_330_poc）")
    if not g_url:
        missing.append(
            "Gluten 的 gitcode 代码仓地址（参数 gluten_git_repo_url，例如 https://gitcode.com/<your_fork>/Gluten.git；"
            "或在 PROJECT_ROOT/Gluten 下配置 git remote 让本工具自动读取）"
        )
    if not g_br:
        missing.append("Gluten 的分支名（参数 gluten_branch，例如 2026_330_poc）")
    return o_url, o_br, g_url, g_br, missing


@mcp.tool()
async def compile_gluten(
    omni_branch: str,
    gluten_branch: str,
    omni_git_repo_url: str = "",
    gluten_git_repo_url: str = "",
) -> str:
    """在 Docker 容器内编译 OmniOperator + Gluten，完成后将产物 docker cp 到宿主机，供性能测试使用。

    宿主机脚本 COMPILE_GLUTEN_SCRIPT（默认 /home/omni/compile_gluten.sh）执行两步：
      步骤1 — docker exec mgx_omni_compiler1 /home/omni/compile_gluten.sh $1 $2 $3 $4
        容器内依次：
          a. git clone <omni_url> -b <omni_branch> → 编译 OmniOperator（build.sh + mvn）
          b. git clone <gluten_url> -b <gluten_branch> → 编译 Gluten native lib（cmake）
          c. mvn package（Gluten Java 包）
          d. 将 libspark_columnar_plugin.so 和 gluten-omni-bundle-*.jar 写入容器内 /home/omni/omni-operator/lib
      步骤2 — docker cp mgx_omni_compiler1:/home/omni/omni-operator /home/omni/
        将容器内完整的 omni-operator 目录拷贝到宿主机，覆盖旧版本，供性能测试脚本直接加载。

    两个 branch 参数必填；两个 URL 可省略，省略时分别从本地仓
    `PROJECT_ROOT/OmniOperator`、`PROJECT_ROOT/Gluten` 的 origin 自动读取。
    执行结束后按退出码给出【Gluten 编译成功/失败/未完成】摘要；非 0 时包含关键编译错误行（去重）、日志末尾 50 行。
    可用 get_compile_log 读取完整日志。
    超时：COMPILE_GLUTEN_TIMEOUT_SECONDS（未设置时默认至少 7200 秒）。
    """
    o_url, o_br, g_url, g_br, missing = _resolve_gluten_compile_inputs(
        omni_branch, gluten_branch, omni_git_repo_url, gluten_git_repo_url
    )
    if missing:
        return (
            "无法执行 Gluten 编译：缺少或未填写必填参数，请先向用户确认后再调用本工具。\n"
            "必须提供以下四项：\n- "
            + "\n- ".join(missing)
        )
    cmd = _build_compile_gluten_remote_command(o_url, o_br, g_url, g_br)
    timeout = _compile_job_timeout_seconds("COMPILE_GLUTEN_TIMEOUT_SECONDS")
    log_path = _new_compile_log_path("compile_gluten")

    def _go() -> str:
        code, _raw = _run_remote_with_exit_and_log(cmd, log_path, timeout)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        except OSError:
            log_text = _raw
        digest = _extract_compile_digest(log_text)
        summary = _summarize_named_compile_outcome(
            "Gluten",
            "compile_op / compile_gluten 中的 git clone / build.sh / cmake / mvn 步骤",
            code,
            digest,
        )
        return summary + f"\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


@mcp.tool()
async def get_compile_log(tail_lines: int = 80) -> str:
    """读取最新一次编译（compile_omni 或 compile_gluten）的实时日志末尾若干行（默认 80 行）。

    编译进行中可随时调用以查看当前进度；编译结束后同样可用。
    日志目录：COMPILE_LOG_DIR（未设置则为 spark_remote_mcp/compile_logs/）。
    """
    def _read() -> str:
        log_dir = _default_compile_log_dir()
        pointer = os.path.join(log_dir, "latest.log")
        log_path: str | None = None

        # latest.log 保存的是实际日志文件的路径
        if os.path.exists(pointer):
            try:
                with open(pointer, "r", encoding="utf-8") as f:
                    candidate = f.read().strip()
                if candidate and os.path.exists(candidate):
                    log_path = candidate
            except OSError:
                pass

        # 兜底：按修改时间找最新的非 latest.log 日志文件
        if not log_path:
            try:
                candidates = sorted(
                    (p for p in Path(log_dir).glob("*.log") if p.name != "latest.log"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if candidates:
                    log_path = str(candidates[0])
            except OSError:
                pass

        if not log_path:
            return f"暂无编译日志。日志目录：{log_dir}"

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            return f"读取日志失败：{e}\n路径：{log_path}"

        n = max(1, tail_lines)
        tail = lines[-n:] if len(lines) > n else lines
        header = (
            f"【编译日志】{log_path}\n"
            f"共 {len(lines)} 行，显示末尾 {len(tail)} 行\n"
            f"{'─' * 60}\n"
        )
        return header + "".join(tail)

    return await asyncio.to_thread(_read)


@mcp.tool()
async def run_e2e_sql(sql: str, database: str = "", timeout_sec: int = 300) -> str:
    """【正确性校验专用】在远端以 Omni 引擎（Gluten 插件）执行 SQL，返回查询结果用于与基准对比。

    ⚠️  禁止将本工具用于性能计时或重复执行以获取热启动数据。
        性能测试（端到端耗时）请使用 run_spark_test_operator，按需连续多次调用拿冷/热数据。

    典型使用场景（每次只调用一次）：
      - Phase 1：记录正确性基准（保存查询结果行）
      - Phase 5 正确性校验循环：对比优化后结果与基准是否一致
      - 算子 E2E 验证：确认目标算子已下推、Fallback 为 0

    sql 参数支持**多条语句**（用 ; 分隔），所有语句在同一个 spark-sql session 中
    按顺序执行。DDL（CREATE TABLE / INSERT）与测试查询应合并为一次调用：

      sql = \"\"\"
        CREATE TABLE test_input (a INT, b STRING);
        INSERT INTO test_input VALUES (1,'x'),(2,'y');
        SELECT a, b FROM test_input CROSS JOIN test_input t2;
      \"\"\"

    如果测试查询依赖已存在的 Hive 持久表（如 TPC-DS 正式数据集），
    可将各条查询分开调用，每次只传查询 SQL 并指定 database。

    参数说明：
      sql         一条或多条 SQL（分号分隔）。通过临时文件传递，支持任意长度和
                  特殊字符，不受命令行限制。
      database    Hive/Spark 数据库名（如 tpcds_bin_partitioned_decimal_orc_1000）；非空时自动在最前面添加
                  USE <database>;。若 sql 自身已含 USE 语句则留空。
      timeout_sec 超时秒数，默认 300s；也可通过 E2E_SQL_TIMEOUT_SECONDS 环境变量设置

    返回内容：
      - 查询结果（末尾 40 行）← 正确性校验的核心依据
      - Omni 算子下推情况（哪些算子命中 Omni 执行，命中次数）
      - Fallback 告警摘要（Validation failed / FallbackNode 等）
      - Spark App ID 及单次耗时（仅供参考，不可作为性能基准）
      - 完整日志本地路径（供 get_compile_log 进一步分析）
    """
    sql_s = (sql or "").strip()
    if not sql_s:
        return "无法执行：sql 参数为空，请传入有效的 SQL 语句。"

    db_s = (database or "").strip()
    # 若指定数据库，在 SQL 前插入 USE 语句
    final_sql = f"USE {db_s};\n{sql_s}" if db_s else sql_s

    env_to = _env("E2E_SQL_TIMEOUT_SECONDS")
    to = int(env_to) if env_to else max(60, timeout_sec)

    cmd = _build_e2e_sql_command(final_sql, db_s)
    log_path = _new_compile_log_path("e2e_sql")

    def _go() -> str:
        code, _body = _run_remote_with_exit_and_log(cmd, log_path, to)

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                full_output = f.read()
        except OSError:
            full_output = _body

        # 从输出中提取 App ID，然后查 SHS 获取物理计划中的 Omni 算子
        # SHS 需要几秒处理 event log，等待后重试最多 3 次
        shs_info: dict | None = None
        app_id_m = re.search(r"(local-\d+|application_\d{13}_\d{4})", full_output)
        if app_id_m:
            _aid = app_id_m.group(1)
            # SHS 默认每 10s 扫一次 event log，app 结束后需等它刷新才能查到
            # 初始等待由 SHS_INIT_WAIT_SECONDS 控制（默认 12s）；之后每 5s 重试共 3 次
            _init_wait = int(_env("SHS_INIT_WAIT_SECONDS", "12"))
            time.sleep(_init_wait)
            for _attempt in range(3):
                shs_info = _fetch_shs_plan_info(_aid)
                if shs_info.get("error") is None or "404" not in shs_info.get("error", ""):
                    break
                time.sleep(5)

        # 异步截图（不阻塞主流程，截图失败不影响结果输出）
        screenshots: list[str] = []
        if app_id_m and shs_info and not shs_info.get("error"):
            screenshots = _scrape_shs_screenshots(app_id_m.group(1))

        summary = _parse_spark_e2e_output(full_output, shs_info=shs_info)
        db_hint = f"  数据库 : {db_s}\n" if db_s else ""
        status = "【E2E 执行成功】" if code == 0 else f"【E2E 执行失败（退出码 {code}）】"

        screenshot_hint = ""
        if screenshots:
            paths = "\n".join(f"  file:///{p.replace(chr(92), '/')}" for p in screenshots)
            screenshot_hint = f"\n\n─── 执行计划截图 ────────────────────────────\n{paths}"

        return f"{status}\n{db_hint}\n{summary}{screenshot_hint}\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


@mcp.tool()
async def run_e2e_sql_native(sql: str, database: str = "", timeout_sec: int = 300) -> str:
    """在远端以原生 Spark（不加载 Gluten/Omni 插件）执行 SQL，用于与 Omni 结果/性能对比。

    与 run_e2e_sql 逻辑完全相同，仅使用 E2E_SQL_NATIVE_SCRIPT
    （默认 /home/omni/run_e2e_sql_native.sh），该脚本不包含 Gluten/Omni 相关 --conf。

    sql 参数支持**多条语句**（用 ; 分隔），所有语句在同一个 spark-sql session 中
    按顺序执行。DDL（CREATE TABLE / INSERT）与查询应合并为一次调用：

      sql = \"\"\"
        CREATE TABLE test_input (a INT, b STRING);
        INSERT INTO test_input VALUES (1,'x'),(2,'y');
        SELECT a, b FROM test_input CROSS JOIN test_input t2;
      \"\"\"

    参数说明：
      sql         一条或多条 SQL（分号分隔），通过临时文件传递。
      database    Hive/Spark 数据库名（如 tpcds_bin_partitioned_decimal_orc_1000）；非空时自动在最前面添加
                  USE <database>;。若 sql 自身已含 USE 语句则留空。
      timeout_sec 超时秒数，默认 300s；也可通过 E2E_SQL_TIMEOUT_SECONDS 环境变量设置

    返回内容：
      - Spark App ID 及耗时
      - 查询结果（末尾 40 行）
      - 完整日志本地路径

    典型用途：
      先用 run_e2e_sql_native 获取原生 Spark 耗时作为基准，
      再用 run_e2e_sql 获取 Omni 耗时，对比加速比。
    """
    sql_s = (sql or "").strip()
    if not sql_s:
        return "无法执行：sql 参数为空，请传入有效的 SQL 语句。"

    db_s = (database or "").strip()
    final_sql = f"USE {db_s};\n{sql_s}" if db_s else sql_s

    env_to = _env("E2E_SQL_TIMEOUT_SECONDS")
    to = int(env_to) if env_to else max(60, timeout_sec)

    cmd = _build_e2e_sql_native_command(final_sql, db_s)
    log_path = _new_compile_log_path("e2e_sql_native")

    def _go() -> str:
        code, _body = _run_remote_with_exit_and_log(cmd, log_path, to)

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                full_output = f.read()
        except OSError:
            full_output = _body

        summary = _parse_spark_native_output(full_output)
        db_hint = f"  数据库 : {db_s}\n" if db_s else ""
        status = "【Native 执行成功】" if code == 0 else f"【Native 执行失败（退出码 {code}）】"
        return f"{status}\n{db_hint}\n{summary}\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


@mcp.tool()
async def debug_e2e_sql_columnar(
    sql: str,
    database: str = "",
    toggles: list[str] | None = None,
    timeout_sec: int = 300,
    stop_on_match: bool = True,
    include_native_baseline: bool = True,
) -> str:
    """【正确性调试专用】逐个关闭列式算子配置，定位 Omni SQL 结果不一致或异常的可疑开关。

    本工具会围绕同一条 SQL 做多轮执行：
      1. 可选执行 Native Spark，作为正确性基线；
      2. 执行原始 Omni SQL；
      3. 对 toggles 中的配置逐个追加 `SET <key>=false;` 后执行 Omni SQL；
      4. 对比每轮查询结果与 Native 基线（若启用），报告哪个开关让结果恢复一致或异常消失。

    参数说明：
      sql                     一条或多条 SQL（分号分隔）。
      database                Hive/Spark 数据库名；非空时自动添加 USE <database>;。
      toggles                 待测试的 Spark/Gluten 配置 key 列表。为空时使用内置高频列式算子开关。
      timeout_sec             每一轮执行的超时秒数，默认 300s；也可通过 E2E_SQL_TIMEOUT_SECONDS 环境变量覆盖。
      stop_on_match           找到首个与 Native 结果一致的 toggle 后是否停止，默认 True。
      include_native_baseline 是否先跑 Native Spark 作为基线，默认 True。

    返回 Markdown 调试报告。不要把本工具用于性能计时。
    """
    sql_s = (sql or "").strip()
    if not sql_s:
        return "无法执行：sql 参数为空，请传入有效的 SQL 语句。"

    db_s = (database or "").strip()
    env_to = _env("E2E_SQL_TIMEOUT_SECONDS")
    to = int(env_to) if env_to else max(60, timeout_sec)

    raw_toggles = toggles if toggles is not None else DEFAULT_COLUMNAR_TOGGLES
    cleaned_toggles: list[str] = []
    seen: set[str] = set()
    for item in raw_toggles:
        key = (item or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        cleaned_toggles.append(key)

    if not cleaned_toggles:
        return "无法执行：toggles 为空，请传入至少一个 Spark/Gluten columnar 配置 key。"

    def _go() -> str:
        parts: list[str] = []
        parts.append("# Columnar Debug Report")
        parts.append("")
        if db_s:
            parts.append(f"- 数据库：`{db_s}`")
        parts.append(f"- 每轮超时：`{to}s`")
        parts.append(f"- stop_on_match：`{stop_on_match}`")
        parts.append(f"- include_native_baseline：`{include_native_baseline}`")
        parts.append("")

        baseline_result: list[str] | None = None
        native_digest: dict | None = None
        if include_native_baseline:
            native_digest = _run_e2e_sql_once(
                sql_s, db_s, to, native=True, log_prefix="debug_e2e_native"
            )
            baseline_result = native_digest["result_lines"]

        original = _run_e2e_sql_once(
            sql_s, db_s, to, native=False, log_prefix="debug_e2e_omni_original"
        )
        original_match = _compare_result_rows(original["result_lines"], baseline_result)
        original_error_signature = bool(original["error_lines"])

        trials: list[dict] = []
        first_exact_match: dict | None = None
        first_sorted_match: dict | None = None
        first_error_recovery: dict | None = None
        skip_trials_reason = ""

        if baseline_result is not None and original_match["exact"]:
            skip_trials_reason = "Original Omni 已与 Native 基线严格一致。"
        elif baseline_result is not None and original_match["sorted"]:
            skip_trials_reason = "Original Omni 与 Native 基线仅存在顺序差异。"
        else:
            for idx, key in enumerate(cleaned_toggles, start=1):
                trial_sql = f"SET {key}=false;\n{sql_s}"
                digest = _run_e2e_sql_once(
                    trial_sql, db_s, to, native=False, log_prefix=f"debug_e2e_toggle_{idx}"
                )
                match = _compare_result_rows(digest["result_lines"], baseline_result)
                error_recovered = original_error_signature and not digest["error_lines"] and digest["exit_code"] == 0
                row = {
                    "idx": idx,
                    "toggle": key,
                    "digest": digest,
                    "match_exact": match["exact"],
                    "match_sorted": match["sorted"],
                    "error_recovered": error_recovered,
                }
                trials.append(row)
                if row["match_exact"] and first_exact_match is None:
                    first_exact_match = row
                if row["match_sorted"] and first_sorted_match is None:
                    first_sorted_match = row
                if error_recovered and first_error_recovery is None:
                    first_error_recovery = row
                if stop_on_match and (row["match_exact"] or row["match_sorted"] or error_recovered):
                    break

        parts.append("## Baseline")
        if native_digest is None:
            parts.append("- Native Spark：未执行")
        else:
            native_status = "成功" if native_digest["success"] else f"失败(exit={native_digest['exit_code']})"
            parts.append(
                f"- Native Spark：{native_status}，结果行数 `{native_digest['result_count']}`，"
                f"耗时 `{native_digest['time_taken']}`，日志 `{native_digest['log_path']}`"
            )
        original_status = "成功" if original["success"] else f"失败(exit={original['exit_code']})"
        match_exact_text = "yes" if original_match["exact"] else ("no" if baseline_result is not None else "n/a")
        match_sorted_text = "yes" if original_match["sorted"] else ("no" if baseline_result is not None else "n/a")
        parts.append(
            f"- Original Omni：{original_status}，结果行数 `{original['result_count']}`，"
            f"match_exact `{match_exact_text}`，match_sorted `{match_sorted_text}`，"
            f"Fallback `{original['fallback_count']}`，日志 `{original['log_path']}`"
        )
        if original["error_lines"]:
            parts.append(f"- Original Omni 错误样例：`{original['error_lines'][0][:180]}`")
        parts.append("")

        parts.append("## Trials")
        if skip_trials_reason:
            parts.append(f"- 已跳过 toggle trials：{skip_trials_reason}")
        else:
            parts.append("| # | Toggle | Status | Match Exact | Match Sorted | Error Recovered | Rows | Fallback | Time | Log |")
            parts.append("|---|--------|--------|-------------|--------------|-----------------|------|----------|------|-----|")
            for row in trials:
                digest = row["digest"]
                status = "success" if digest["success"] else f"fail({digest['exit_code']})"
                match_exact = "yes" if row["match_exact"] else ("no" if baseline_result is not None else "n/a")
                match_sorted = "yes" if row["match_sorted"] else ("no" if baseline_result is not None else "n/a")
                recovered = "yes" if row["error_recovered"] else "no"
                parts.append(
                    f"| {row['idx']} | `{row['toggle']}=false` | {status} | {match_exact} | {match_sorted} | "
                    f"{recovered} | {digest['result_count']} | {digest['fallback_count']} | "
                    f"{digest['time_taken']} | `{digest['log_path']}` |"
                )
        parts.append("")

        parts.append("## Conclusion")
        if baseline_result is not None and original_match["exact"]:
            parts.append("- Original Omni 已与 Native 基线严格一致，无需继续关闭 columnar toggle。")
        elif baseline_result is not None and original_match["sorted"]:
            parts.append("- Original Omni 与 Native 基线仅存在顺序差异，无需继续关闭 columnar toggle。")
        elif first_exact_match is not None:
            parts.append(
                f"- 首个让 Omni 结果与 Native 基线严格一致的配置："
                f"`{first_exact_match['toggle']}=false`。"
            )
        elif first_sorted_match is not None:
            parts.append(
                f"- 首个让 Omni 结果在排序后与 Native 基线一致的配置："
                f"`{first_sorted_match['toggle']}=false`。"
            )
        elif first_error_recovery is not None:
            parts.append(
                f"- 首个让原始 Omni 异常消失的配置："
                f"`{first_error_recovery['toggle']}=false`。"
            )
        elif baseline_result is None:
            parts.append("- 未启用 Native 基线，仅完成各 toggle 执行状态采集。")
        else:
            parts.append("- 本轮测试未发现单个 columnar toggle 能让结果严格一致，或仅通过排序后与 Native 基线一致。")

        if first_exact_match is not None or first_sorted_match is not None or first_error_recovery is not None:
            parts.append("- 建议下一步围绕该配置对应的算子查看物理计划、Fallback 告警和执行日志。")

        return "\n".join(parts)

    return await asyncio.to_thread(_go)


def _run_test_all_then_fetch_sync(query_sql: str = "", query_id: str = "") -> str:
    try:
        remote = _build_remote_test_all_command(query_sql or "", query_id or "")
    except ValueError as e:
        return f"配置错误: {e}"
    log_path = _new_compile_log_path("perf_native_flame")
    timeout = int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    _code, run_out = _run_remote_with_exit_and_log(remote, log_path, timeout)
    fetch_out = _fetch_flame_htmls_sync()
    return run_out + f"\n\n日志已保存：{log_path}" + "\n\n========== 火焰图（SFTP 已拉取到本机） ==========\n\n" + fetch_out


@mcp.tool()
async def fetch_spark_flame_graphs(remote_dir: str = "", session_folder_name: str = "", max_files: int = 10) -> str:
    """经 SFTP 将远端目录下最近的 .html（async-profiler 火焰图）下载到本机。

    默认远端目录为环境变量 REMOTE_FLAME_DIR（未设置则用 /opt/async）；如果目录下没有 HTML，会自动选择最近修改且包含 HTML 的子目录（如 /opt/async/q1.sql）。
    每次下载会新建子文件夹（默认可用时间戳，也可传 session_folder_name）。
    max_files 默认 10，按远端文件修改时间倒序取最新文件；传 0 或负数表示不限制。
    返回结果中含 file:// URL，可复制到 Chrome/Edge 打开；或在资源管理器中打开本机目录双击 HTML。
    """
    rd = remote_dir.strip() if remote_dir.strip() else None
    sf = session_folder_name.strip() if session_folder_name.strip() else None
    return await asyncio.to_thread(_fetch_flame_htmls_sync, rd, sf, max_files)


@mcp.tool()
async def run_spark_test_all_and_fetch_flames(query_sql: str = "", query_id: str = "") -> str:
    """先按 run_spark_test_all 同步 query_sql 目录并执行 test-all.sh，结束后自动 SFTP 拉取 REMOTE_FLAME_DIR 下 .html 到本机并返回 file:// 链接。

    query_id / query_sql 参数规则与 run_spark_test_all 相同；推荐传 query_id（如 "q7"）以确保火焰图文件名正确。
    """
    return await asyncio.to_thread(_run_test_all_then_fetch_sync, query_sql or "", query_id or "")


@mcp.tool()
async def read_remote_file(remote_path: str, tail_lines: int = 100) -> str:
    """读取远端文件末尾若干行（默认 100 行）。

    常用于查看远端 Spark 日志，例如：
      /usr/local/Spark-Test-Tool/logs-operator/q1.sql.log
      /usr/local/Spark-Test-Tool/logs/q1.sql.log
    """
    rp = (remote_path or "").strip()
    if not rp:
        return "错误：remote_path 不能为空"
    # 如果路径是目录则 ls，否则 tail
    cmd = (
        f"if [ -d {shlex.quote(rp)} ]; then ls -la {shlex.quote(rp)}; "
        f"else tail -n {tail_lines} {shlex.quote(rp)}; fi"
    )
    return await asyncio.to_thread(_run_remote, cmd, timeout_sec=30)


def _validate_required_env() -> None:
    """启动时校验必需环境变量；缺失则报错并退出，避免运行到一半才报莫名连接错误。

    任意一个工具被调用前都会先走到这里。SSH_HOST / SSH_USER 任一为空都会让 _ssh_argv /
    _paramiko_connect 拿到 "@host" / "root@" 之类残缺目标，错误信息晦涩，因此把检查前置到
    main() 启动阶段。出于安全考虑，本服务不默认 SSH_USER=root 或 SSH_USER=omni，强制调用方
    在 .env 显式声明连接身份。
    """
    missing: list[str] = []
    if not _env("SSH_HOST"):
        missing.append(
            "SSH_HOST（远端主机 IP/域名，例：SSH_HOST=10.0.0.1；必填）"
        )
    if not _env("SSH_USER"):
        missing.append(
            "SSH_USER（远端 SSH 用户名，例：SSH_USER=omni 或 SSH_USER=ubuntu；必填。"
            "出于安全考虑，本服务不提供默认用户名，必须由 .env 显式配置）"
        )
    if missing:
        raise SystemExit(
            "[spark-remote-mcp] 启动失败：以下必需环境变量未设置或为空：\n  - "
            + "\n  - ".join(missing)
            + "\n请将它们写入 .env 或在启动命令前 export，参考同目录 README.md 的「环境变量」小节。"
        )


def main() -> None:
    _validate_required_env()
    mcp.run()


if __name__ == "__main__":
    main()
