import asyncio
import json
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))


def _load_mcp_env() -> None:
    """Load spark-remote-test env from the repo-level .mcp.json when available."""
    candidate_roots = [
        THIS_DIR.parent.parent,  # repo root: OmniSkills/
        Path.cwd(),
    ]
    for root in candidate_roots:
        mcp_json = root / ".mcp.json"
        if not mcp_json.exists():
            continue
        try:
            data = json.loads(mcp_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        env = (
            data.get("mcpServers", {})
            .get("spark-remote-test", {})
            .get("env", {})
        )
        if not isinstance(env, dict):
            continue
        for key, value in env.items():
            if isinstance(value, str):
                os.environ[key] = value
        return


_load_mcp_env()

from server import mcp

async def main():
    if len(sys.argv) < 2:
        print("Available tools:")
        for name, tool in mcp._tool_manager._tools.items():
            print(f"  - {name}")
        return
    
    tool_name = sys.argv[1]
    
    if tool_name == "compile_omni":
        if len(sys.argv) < 4:
            print("Usage: python mcp_client.py compile_omni <git_repo_url> <branch>")
            return
        result = await mcp._tool_manager._tools["compile_omni"].fn(
            git_repo_url=sys.argv[2],
            branch=sys.argv[3]
        )
        print(result)
    
    elif tool_name == "compile_gluten":
        if len(sys.argv) < 6:
            print("Usage: python mcp_client.py compile_gluten <omni_url> <omni_branch> <gluten_url> <gluten_branch>")
            return
        result = await mcp._tool_manager._tools["compile_gluten"].fn(
            omni_git_repo_url=sys.argv[2],
            omni_branch=sys.argv[3],
            gluten_git_repo_url=sys.argv[4],
            gluten_branch=sys.argv[5]
        )
        print(result)

    elif tool_name == "run_e2e_sql":
        if len(sys.argv) < 3:
            print("Usage: python mcp_client.py run_e2e_sql <sql_file> [database] [timeout_sec]")
            return
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            sql = f.read()
        database = sys.argv[3] if len(sys.argv) > 3 else ""
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        result = await mcp._tool_manager._tools["run_e2e_sql"].fn(
            sql=sql,
            database=database,
            timeout_sec=timeout
        )
        print(result)
    
    elif tool_name == "run_e2e_sql_native":
        if len(sys.argv) < 3:
            print("Usage: python mcp_client.py run_e2e_sql_native <sql_file> [database] [timeout_sec]")
            return
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            sql = f.read()
        database = sys.argv[3] if len(sys.argv) > 3 else ""
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        result = await mcp._tool_manager._tools["run_e2e_sql_native"].fn(
            sql=sql,
            database=database,
            timeout_sec=timeout
        )
        print(result)

    elif tool_name == "debug_e2e_sql_columnar":
        if len(sys.argv) < 3:
            print("Usage: python mcp_client.py debug_e2e_sql_columnar <sql_file> [database] [timeout_sec] [toggle1,toggle2,...] [stop_on_match] [include_native_baseline]")
            return
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            sql = f.read()
        database = sys.argv[3] if len(sys.argv) > 3 else ""
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        toggles = None
        if len(sys.argv) > 5 and sys.argv[5].strip():
            toggles = [x.strip() for x in sys.argv[5].split(",") if x.strip()]
        stop_on_match = True
        if len(sys.argv) > 6:
            stop_on_match = sys.argv[6].lower() in ("1", "true", "yes", "on")
        include_native_baseline = True
        if len(sys.argv) > 7:
            include_native_baseline = sys.argv[7].lower() in ("1", "true", "yes", "on")
        result = await mcp._tool_manager._tools["debug_e2e_sql_columnar"].fn(
            sql=sql,
            database=database,
            toggles=toggles,
            timeout_sec=timeout,
            stop_on_match=stop_on_match,
            include_native_baseline=include_native_baseline,
        )
        print(result)
    
    elif tool_name == "run_spark_test_operator":
        query_sql = ""
        query_id = ""
        if len(sys.argv) >= 3:
            arg = sys.argv[2]
            if os.path.isfile(arg):
                with open(arg, 'r', encoding='utf-8') as f:
                    query_sql = f.read()
            else:
                query_id = arg
        flame_enabled = False
        if len(sys.argv) >= 4:
            flame_enabled = sys.argv[3].lower() in ("1", "true", "yes", "on", "flame")
        result = await mcp._tool_manager._tools["run_spark_test_operator"].fn(
            query_sql=query_sql,
            query_id=query_id,
            flame_enabled=flame_enabled,
        )
        print(result)
    
    elif tool_name == "run_spark_test_all":
        query_sql = ""
        if len(sys.argv) >= 3:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                query_sql = f.read()
        result = await mcp._tool_manager._tools["run_spark_test_all"].fn(
            query_sql=query_sql
        )
        print(result)
    
    elif tool_name == "fetch_spark_flame_graphs":
        remote_dir = sys.argv[2] if len(sys.argv) > 2 else ""
        if remote_dir in ("-", "auto", "AUTO"):
            remote_dir = ""
        session_folder = sys.argv[3] if len(sys.argv) > 3 else ""
        max_files = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        result = await mcp._tool_manager._tools["fetch_spark_flame_graphs"].fn(
            remote_dir=remote_dir,
            session_folder_name=session_folder,
            max_files=max_files,
        )
        print(result)
    
    elif tool_name == "drop_cluster_caches":
        result = await mcp._tool_manager._tools["drop_cluster_caches"].fn()
        print(result)
    
    elif tool_name == "get_compile_log":
        tail_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        result = await mcp._tool_manager._tools["get_compile_log"].fn(tail_lines=tail_lines)
        print(result)

    elif tool_name == "spark_ssh_check":
        result = await mcp._tool_manager._tools["spark_ssh_check"].fn()
        print(result)

    elif tool_name == "read_remote_file":
        if len(sys.argv) < 3:
            print("Usage: python mcp_client.py read_remote_file <remote_path> [tail_lines]")
            return
        tail_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        result = await mcp._tool_manager._tools["read_remote_file"].fn(
            remote_path=sys.argv[2],
            tail_lines=tail_lines,
        )
        print(result)
    
    else:
        print(f"Unknown tool: {tool_name}")

if __name__ == "__main__":
    asyncio.run(main())
