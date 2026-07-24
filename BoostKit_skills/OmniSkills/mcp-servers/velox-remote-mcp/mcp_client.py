import asyncio
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))

# 连接信息一律从环境变量读取，请勿在源码中硬编码服务器地址或密码。
# 运行前请先在 shell / .env 中设置：
#   SSH_HOST、SSH_USER、SSH_PASSWORD（或 SSH_IDENTITY）、SSH_PORT、
#   REMOTE_WORKDIR、E2E_VELOX_SCRIPT 等（默认值见 server.py 顶部说明）。
if not os.environ.get("SSH_HOST"):
    print(
        "warning: SSH_HOST 未设置。请通过环境变量提供连接信息，例如：\n"
        "  set SSH_HOST=<host> & set SSH_USER=<user> & set SSH_PASSWORD=<password>\n"
        "（PowerShell: $env:SSH_HOST='<host>' 等）",
        file=sys.stderr,
    )

from server import mcp


def _usage() -> None:
    print("Available tools:")
    for name in mcp._tool_manager._tools.keys():
        print(f"  - {name}")
    print()
    print("Usage examples:")
    print("  python mcp_client.py velox_ssh_check")
    print("  python mcp_client.py compile_velox <git_repo_url> <branch>")
    print("  python mcp_client.py compile_gluten_velox <git_repo_url> <branch>")
    print("  python mcp_client.py run_velox_ut [build_dir] [test_regex] [timeout_sec]")
    print("  python mcp_client.py run_e2e_sql_velox <sql_file_or_'-'> [database] [timeout_sec]")
    print("  python mcp_client.py get_compile_log [tail_lines]")
    print("  python mcp_client.py read_remote_file <remote_path> [tail_lines]")
    print("  python mcp_client.py run_tpcds_99_velox <run_label> [database] [sql_dir] [timeout_sec]")
    print("  python mcp_client.py diff_tpcds_results <label_a> <label_b>")
    print("  python mcp_client.py run_velox_perf_test [query_id] [query_sql]")
    print("  python mcp_client.py fetch_velox_flame_graphs [remote_dir] [session_folder_name]")
    print("  python mcp_client.py run_velox_perf_and_fetch_flames [query_id] [query_sql]")
    print("  python mcp_client.py drop_cluster_caches")


async def main() -> None:
    if len(sys.argv) < 2:
        _usage()
        return

    tool_name = sys.argv[1]
    tools = mcp._tool_manager._tools

    if tool_name not in tools:
        print(f"Unknown tool: {tool_name}\n")
        _usage()
        return

    fn = tools[tool_name].fn

    if tool_name == "velox_ssh_check":
        result = await fn()
    elif tool_name == "compile_velox":
        if len(sys.argv) < 4:
            print("Usage: python mcp_client.py compile_velox <git_repo_url> <branch>")
            return
        result = await fn(git_repo_url=sys.argv[2], branch=sys.argv[3])
    elif tool_name == "compile_gluten_velox":
        if len(sys.argv) < 4:
            print("Usage: python mcp_client.py compile_gluten_velox <git_repo_url> <branch>")
            return
        result = await fn(git_repo_url=sys.argv[2], branch=sys.argv[3])
    elif tool_name == "run_velox_ut":
        build_dir = sys.argv[2] if len(sys.argv) > 2 else "_build/release"
        test_regex = sys.argv[3] if len(sys.argv) > 3 else ""
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 7200
        result = await fn(
            build_dir=build_dir,
            test_regex=test_regex,
            timeout_sec=timeout,
        )
    elif tool_name == "run_e2e_sql_velox":
        if len(sys.argv) < 3:
            print(
                "Usage: python mcp_client.py run_e2e_sql_velox <sql_file_or_'-'> "
                "[database] [timeout_sec]\n"
                "  If first arg is '-', read SQL from stdin."
            )
            return
        src = sys.argv[2]
        if src == "-":
            sql = sys.stdin.read()
        else:
            with open(src, "r", encoding="utf-8") as f:
                sql = f.read()
        database = sys.argv[3] if len(sys.argv) > 3 else ""
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 600
        result = await fn(sql=sql, database=database, timeout_sec=timeout)
    elif tool_name == "get_compile_log":
        tail = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        result = await fn(tail_lines=tail)
    elif tool_name == "read_remote_file":
        if len(sys.argv) < 3:
            print("Usage: python mcp_client.py read_remote_file <remote_path> [tail_lines]")
            return
        tail = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        result = await fn(remote_path=sys.argv[2], tail_lines=tail)
    elif tool_name == "run_tpcds_99_velox":
        if len(sys.argv) < 3:
            print(
                "Usage: python mcp_client.py run_tpcds_99_velox <run_label> "
                "[database=tpcds_bin_partitioned_decimal_orc_10] [sql_dir] [timeout_sec=3600]"
            )
            return
        run_label = sys.argv[2]
        database = sys.argv[3] if len(sys.argv) > 3 else "tpcds_bin_partitioned_decimal_orc_10"
        sql_dir = sys.argv[4] if len(sys.argv) > 4 else ""
        timeout = int(sys.argv[5]) if len(sys.argv) > 5 else 3600
        result = await fn(
            run_label=run_label, database=database, sql_dir=sql_dir, timeout_sec=timeout
        )
    elif tool_name == "diff_tpcds_results":
        if len(sys.argv) < 4:
            print("Usage: python mcp_client.py diff_tpcds_results <label_a> <label_b>")
            return
        result = await fn(label_a=sys.argv[2], label_b=sys.argv[3])
    elif tool_name == "run_velox_perf_test":
        query_id = sys.argv[2] if len(sys.argv) > 2 else ""
        query_sql = sys.argv[3] if len(sys.argv) > 3 else ""
        result = await fn(query_id=query_id, query_sql=query_sql)
    elif tool_name == "fetch_velox_flame_graphs":
        remote_dir = sys.argv[2] if len(sys.argv) > 2 else ""
        session_folder_name = sys.argv[3] if len(sys.argv) > 3 else ""
        result = await fn(remote_dir=remote_dir, session_folder_name=session_folder_name)
    elif tool_name == "run_velox_perf_and_fetch_flames":
        query_id = sys.argv[2] if len(sys.argv) > 2 else ""
        query_sql = sys.argv[3] if len(sys.argv) > 3 else ""
        result = await fn(query_id=query_id, query_sql=query_sql)
    elif tool_name == "drop_cluster_caches":
        result = await fn()
    else:
        result = f"Tool {tool_name} 暂未在 mcp_client.py 中绑定 CLI 参数；请直接通过 MCP 调用。"

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
