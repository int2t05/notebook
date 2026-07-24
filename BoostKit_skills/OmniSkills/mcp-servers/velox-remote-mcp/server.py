"""
MCP server: SSH to a host and run Velox / Gluten+Velox compile scripts.

Configure via env (与 spark_remote_mcp 同源)：
  SSH_HOST、SSH_USER、SSH_PASSWORD、SSH_PORT、SSH_IDENTITY、SSH_TIMEOUT_SECONDS
  REMOTE_WORKDIR              远端脚本所在目录（默认 /path/to/incubator-gluten/dev）
  COMPILE_VELOX_SCRIPT        Velox 编译脚本文件名（默认 compile_velox.sh，相对 REMOTE_WORKDIR）
  COMPILE_GLUTEN_VELOX_SCRIPT Velox+Gluten 编译脚本文件名（默认 compile_gluten_velox.sh）
  COMPILE_VELOX_TIMEOUT_SECONDS / COMPILE_GLUTEN_VELOX_TIMEOUT_SECONDS
                              未设置时取 max(7200, SSH_TIMEOUT_SECONDS) 秒
  COMPILE_LOG_DIR             本机日志目录（默认 velox_remote_mcp/compile_logs/）
  E2E_VELOX_SCRIPT            远端 spark-sql 启动脚本（默认 /path/to/run_exec_velox.sh，
                              脚本本身不接受 SQL 参数，MCP 端从 stdin 喂 SQL）
  E2E_VELOX_TIMEOUT_SECONDS   e2e 默认超时秒数（未设置时由调用方 timeout_sec 决定，最低 600s）

若设置 SSH_PASSWORD，远程命令走 Paramiko；否则走系统 ssh（需配 SSH_IDENTITY）。
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import posixpath
import re
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path

import paramiko
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "velox-remote-test",
    instructions=(
        "在配置的远程 Linux 主机上通过 SSH 编译 Velox / Gluten+Velox。"
        " 【工具】"
        " compile_velox：仅编译 velox（runs compile_velox.sh <git_repo_url> <branch>）；"
        " compile_gluten_velox：编译 velox + gluten 集成版本（runs compile_gluten_velox.sh <git_repo_url> <branch>）；"
        " run_e2e_sql_velox：在远端用 Gluten+Velox 后端跑 SQL，返回查询结果（用于正确性校验）；"
        " get_compile_log：读最新一次编译日志末尾若干行；"
        " velox_ssh_check：检查 SSH 连通性；"
        " read_remote_file：读远端文件末尾若干行（默认 100）。"
        " 可设置 SSH_PASSWORD 或 SSH_IDENTITY。"
    ),
)

logging.getLogger("paramiko").setLevel(logging.WARNING)


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _remote_workdir() -> str:
    return _env("REMOTE_WORKDIR", "/path/to/incubator-gluten/dev")


def _resolve_remote_script(env_name: str, default_basename: str) -> tuple[str, str]:
    """返回 (远端目录, 脚本文件名)。
    若 env 值是绝对路径则按其目录/文件名拆分，否则按 REMOTE_WORKDIR + basename 处理。
    """
    raw = _env(env_name, default_basename)
    if not raw:
        raise ValueError(f"{env_name} 不能为空")
    if raw.startswith("/"):
        d = posixpath.dirname(raw) or "/"
        b = posixpath.basename(raw)
        if not b:
            raise ValueError(f"{env_name} 缺少文件名")
        return d, b
    return _remote_workdir(), raw


def _build_compile_velox_cmd(git_repo_url: str, branch: str) -> str:
    d, script = _resolve_remote_script("COMPILE_VELOX_SCRIPT", "compile_velox.sh")
    return (
        f"cd {shlex.quote(d)} && bash {shlex.quote('./' + script)} "
        f"{shlex.quote(git_repo_url)} {shlex.quote(branch)}"
    )


def _remote_velox_home() -> str:
    return _env(
        "REMOTE_VELOX_HOME",
        "/path/to/incubator-gluten/ep/build-velox/build/velox_ep",
    )


def _remote_velox_compile_config() -> str:
    return _env(
        "VELOX_COMPILE_CONFIG",
        "/path/to/incubator-gluten/dev/velox_compile_config.sh",
    )


def _velox_ut_jobs_expr() -> str:
    return '${VELOX_UT_JOBS:-$(nproc)}'


def _build_velox_full_ut_cmd(build_dir: str | None = None) -> str:
    velox_home = _remote_velox_home()
    compile_config = _remote_velox_compile_config()
    build_dir = (build_dir or _env("VELOX_UT_BUILD_DIR", "_build/release")).strip()
    if not build_dir:
        build_dir = "_build/release"

    jobs = _velox_ut_jobs_expr()
    return "\n".join(
        [
            "bash -lc " + shlex.quote(
                "\n".join(
                    [
                        "set -euo pipefail",
                        f"cd {shlex.quote(velox_home)}",
                        "mkdir -p _build/include",
                        (
                            "if [ -L _build/include/re2 ] || "
                            "[ ! -e _build/include/re2 ]; then "
                            "ln -sfn /path/to/re2-src/re2 _build/include/re2; fi"
                        ),
                        'export CXXFLAGS="${CXXFLAGS:-}"',
                        f"source {shlex.quote(compile_config)}",
                        f"cmake -S . -B {shlex.quote(build_dir)} -GNinja "
                        "-DCMAKE_BUILD_TYPE=Release "
                        "-DCMAKE_CXX_FLAGS='-Wno-missing-field-initializers' "
                        "-DVELOX_ENABLE_PARQUET=ON "
                        "-DVELOX_BUILD_TESTING=ON "
                        "-DVELOX_BUILD_TEST_UTILS=ON "
                        "-DVELOX_ENABLE_DUCKDB=ON "
                        "-DVELOX_MONO_LIBRARY=ON "
                        "-DVELOX_BUILD_RUNNER=OFF "
                        "-DVELOX_ENABLE_HDFS=ON",
                        f"cmake --build {shlex.quote(build_dir)} -j {jobs}",
                        f"cd {shlex.quote(build_dir)}",
                        f"ctest -j {jobs} --output-on-failure",
                    ]
                )
            )
        ]
    )


def _build_run_velox_ut_cmd(build_dir: str, test_regex: str) -> str:
    velox_home = _remote_velox_home()
    build_dir = (build_dir or _env("VELOX_UT_BUILD_DIR", "_build/release")).strip()
    if not build_dir:
        build_dir = "_build/release"

    jobs = _velox_ut_jobs_expr()
    ctest_cmd = f"ctest -j {jobs} --output-on-failure"
    if test_regex.strip():
        ctest_cmd += f" -R {shlex.quote(test_regex.strip())}"

    return "bash -lc " + shlex.quote(
        "\n".join(
            [
                "set -euo pipefail",
                f"cd {shlex.quote(velox_home)}",
                f"cd {shlex.quote(build_dir)}",
                ctest_cmd,
            ]
        )
    )


def _build_compile_gluten_velox_cmd(git_repo_url: str, branch: str) -> str:
    d, script = _resolve_remote_script(
        "COMPILE_GLUTEN_VELOX_SCRIPT", "compile_gluten_velox.sh"
    )
    return (
        f"cd {shlex.quote(d)} && bash {shlex.quote('./' + script)} "
        f"{shlex.quote(git_repo_url)} {shlex.quote(branch)}"
    )


def _ssh_argv(remote_cmd: str) -> list[str]:
    host = _env("SSH_HOST")
    if not host:
        raise ValueError("SSH_HOST 未配置：请通过环境变量设置远端主机地址。")
    user = _env("SSH_USER")
    port = _env("SSH_PORT", "22")
    identity = _env("SSH_IDENTITY")

    target = f"{user}@{host}" if user else host
    argv: list[str] = [
        "ssh",
        "-p", port,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
    ]
    if identity:
        argv.extend(["-i", identity])
    argv.extend([target, "bash", "-lc", remote_cmd])
    return argv


def _paramiko_connect() -> paramiko.SSHClient:
    host = _env("SSH_HOST")
    if not host:
        raise ValueError("SSH_HOST 未配置：请通过环境变量设置远端主机地址。")
    user = _env("SSH_USER", "root")
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
    host = _env("SSH_HOST")
    user = _env("SSH_USER", "root")
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


def _default_compile_log_dir() -> str:
    return _env("COMPILE_LOG_DIR") or str(
        Path(__file__).resolve().parent / "compile_logs"
    )


def _new_compile_log_path(label: str) -> str:
    log_dir = _default_compile_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(log_dir, f"{label}_{stamp}.log")
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
    """Paramiko 流式执行：与 client.exec_command 同路径，保证远端 stdout 完整收齐。

    早期版本用 `chan.exit_status_ready()` + 单次 drain 在 spark-sql 这类长命令上会
    丢掉尾部 stdout。现在直接复用 `client.exec_command(get_pty=True)`，与同步路径
    `_run_via_paramiko_password` 完全一致的读取方式（stdout 是 paramiko ChannelFile），
    在主线程边读边写日志、边追加超时检测，最后阻塞拿 exit code。
    """
    client = _paramiko_connect()
    try:
        wrapped = f"bash -lc {shlex.quote(remote_cmd)}"
        stdin, stdout, stderr = client.exec_command(wrapped, get_pty=True)
        # PTY 下 stderr 已合到 stdout；我们仍写入 stdin EOF
        try:
            stdin.close()
        except Exception:
            pass

        chan = stdout.channel
        buf: list[str] = []
        deadline = time.monotonic() + timeout_sec
        timed_out = False
        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            # chunk read：与 _run_via_paramiko_password 的 stdout.read() 同一 API，
            # 阻塞读直到 channel close。spark-sql 的 prompt 没有 \n，readline 模式会
            # 错误触发 EOF；chunk 模式只有真 channel close 才返回空串。
            while True:
                chunk = stdout.read(8192)
                if not chunk:
                    break
                text = chunk if isinstance(chunk, str) else chunk.decode(
                    "utf-8", errors="replace"
                )
                buf.append(text)
                f.write(text)
                f.flush()
                if time.monotonic() > deadline:
                    timed_out = True
                    f.write(f"\n[MCP] 超时（{timeout_sec}s），强制断开。\n")
                    try:
                        chan.close()
                    except Exception:
                        pass
                    break

        try:
            code = chan.recv_exit_status()
        except Exception:
            code = -1
        if timed_out and code == -1:
            code = 124
        return "".join(buf), code
    finally:
        client.close()


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
    timeout = (
        timeout_sec
        if timeout_sec is not None
        else int(_env("SSH_TIMEOUT_SECONDS", "3600") or "3600")
    )

    if _env("SSH_PASSWORD"):
        meta = (
            f"paramiko {_env('SSH_USER', 'root')}@{_env('SSH_HOST')}:"
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

    return proc.returncode, _format_run_result(
        proc.stdout or "", proc.stderr or "", proc.returncode
    )


def _run_remote(remote_cmd: str, *, timeout_sec: int | None = None) -> str:
    _code, text = _run_remote_with_exit(remote_cmd, timeout_sec=timeout_sec)
    return text


def _run_remote_with_exit_and_log(
    remote_cmd: str, log_path: str, timeout_sec: int
) -> tuple[int | None, str]:
    """执行远端命令，将输出实时流式写入 log_path，返回 (exit_code, formatted_text)。"""
    if _env("SSH_PASSWORD"):
        meta = (
            f"paramiko {_env('SSH_USER', 'root')}@{_env('SSH_HOST')}:"
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
    v = _env(env_var)
    if v:
        return int(v)
    ssh = _env("SSH_TIMEOUT_SECONDS", "3600") or "3600"
    n = int(ssh)
    return n if n >= 7200 else 7200


def _extract_compile_digest(log_text: str) -> str:
    """从编译日志中提取关键信息：关键错误行（去重，最多 30 条）+ 末尾 50 行。"""
    lines = log_text.splitlines()

    err_re = re.compile(
        r"(?i)(\berror\b|\bFATAL\b|make:\s+\*\*\*|ninja:\s+build\s+stopped"
        r"|CMake Error|BUILD FAILURE|undefined reference|cannot find -l"
        r"|fatal error:|\[\s*FAILED\s*\])"
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
    if deduped:
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
            "请重点查看下方编译错误摘要。\n\n"
            + detail
        )
    return (
        f"【{name_cn} 编译成功】远程整条命令退出码为 **0**。"
        "（若脚本内部仍有问题但未以非 0 退出，请以日志为准。）\n\n"
        + detail
    )


@mcp.tool()
async def velox_ssh_check() -> str:
    """快速检查能否 SSH 登录：远端执行 echo / hostname / pwd。exit code 为 0 且 stdout 含 VELOX_MCP_OK 即表示连上。"""
    check_cmd = _env(
        "SSH_CHECK_COMMAND",
        "echo VELOX_MCP_OK && hostname && pwd && ls " + shlex.quote(_remote_workdir()),
    )
    to = int(_env("SSH_CHECK_TIMEOUT", "30") or "30")
    return await asyncio.to_thread(_run_remote, check_cmd, timeout_sec=to)


@mcp.tool()
async def compile_velox(git_repo_url: str, branch: str) -> str:
    """在远端 REMOTE_WORKDIR 下执行 ./compile_velox.sh <git_repo_url> <branch>，仅编译 Velox。

    脚本默认位置：/path/to/incubator-gluten/dev/compile_velox.sh
    传入位置参数：$1 = 代码仓 URL，$2 = 分支名（例如 gluten-1.3.0）

    两个参数均为必填；缺任一则返回中文提示且不连接服务器。
    执行结束后按退出码给出【成功/失败/未完成】摘要；非 0 时包含关键编译错误行（去重）、日志末尾 50 行。
    可用 get_compile_log 读取完整日志。
    超时：COMPILE_VELOX_TIMEOUT_SECONDS（未设置时默认至少 7200 秒）。
    """
    gr = (git_repo_url or "").strip()
    br = (branch or "").strip()
    missing: list[str] = []
    if not gr:
        missing.append(
            "代码仓地址（参数 git_repo_url，例如 https://<git-host>/<org>/<repo>.git）"
        )
    if not br:
        missing.append("分支名（参数 branch，例如 gluten-1.3.0）")
    if missing:
        return (
            "无法执行 Velox 编译：缺少或未填写必填参数，请先向用户确认后再调用本工具。\n"
            "必须提供：\n- "
            + "\n- ".join(missing)
        )

    try:
        cmd = _build_compile_velox_cmd(gr, br)
    except ValueError as e:
        return f"配置错误: {e}"

    timeout = _compile_job_timeout_seconds("COMPILE_VELOX_TIMEOUT_SECONDS")
    log_path = _new_compile_log_path("compile_velox")

    def _go() -> str:
        code, _raw = _run_remote_with_exit_and_log(cmd, log_path, timeout)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        except OSError:
            log_text = _raw
        digest = _extract_compile_digest(log_text)
        summary = _summarize_named_compile_outcome(
            "Velox",
            "compile_velox.sh 中的 git clone / cmake / ninja / make 步骤",
            code,
            digest,
        )
        return summary + f"\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


@mcp.tool()
async def compile_gluten_velox(git_repo_url: str, branch: str) -> str:
    """在远端 REMOTE_WORKDIR 下执行 ./compile_gluten_velox.sh <git_repo_url> <branch>，编译 Velox + Gluten 集成版本。

    脚本默认位置：/path/to/incubator-gluten/dev/compile_gluten_velox.sh
    传入位置参数：$1 = 代码仓 URL，$2 = 分支名（例如 gluten-1.3.0）

    与 compile_velox 相同的代码仓与分支即可（脚本内部既会编译 Velox 也会编译 Gluten 集成层）。
    两个参数均为必填；缺任一则返回中文提示且不连接服务器。
    执行结束后按退出码给出【成功/失败/未完成】摘要；非 0 时包含关键编译错误行（去重）、日志末尾 50 行。
    可用 get_compile_log 读取完整日志。
    超时：COMPILE_GLUTEN_VELOX_TIMEOUT_SECONDS（未设置时默认至少 7200 秒）。
    """
    gr = (git_repo_url or "").strip()
    br = (branch or "").strip()
    missing: list[str] = []
    if not gr:
        missing.append(
            "代码仓地址（参数 git_repo_url，例如 https://<git-host>/<org>/<repo>.git）"
        )
    if not br:
        missing.append("分支名（参数 branch，例如 gluten-1.3.0）")
    if missing:
        return (
            "无法执行 Gluten+Velox 编译：缺少或未填写必填参数，请先向用户确认后再调用本工具。\n"
            "必须提供：\n- "
            + "\n- ".join(missing)
        )

    try:
        cmd = _build_compile_gluten_velox_cmd(gr, br)
    except ValueError as e:
        return f"配置错误: {e}"

    timeout = _compile_job_timeout_seconds("COMPILE_GLUTEN_VELOX_TIMEOUT_SECONDS")
    log_path = _new_compile_log_path("compile_gluten_velox")

    def _go() -> str:
        code, _raw = _run_remote_with_exit_and_log(cmd, log_path, timeout)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        except OSError:
            log_text = _raw
        digest = _extract_compile_digest(log_text)
        summary = _summarize_named_compile_outcome(
            "Gluten+Velox",
            "compile_gluten_velox.sh 中的 git clone / Velox cmake / Gluten cmake / mvn package 步骤",
            code,
            digest,
        )
        return summary + f"\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


@mcp.tool()
async def run_velox_ut(
    build_dir: str = "_build/release",
    test_regex: str = "",
    timeout_sec: int = 7200,
) -> str:
    """Run Velox unit tests from an existing CMake build directory on the remote host.

    By default this runs the full CTest suite from REMOTE_VELOX_HOME/_build/release.
    Pass test_regex to run a subset, e.g. ^velox_base_test$.
    """
    bd = (build_dir or "_build/release").strip()
    regex = (test_regex or "").strip()
    timeout = max(60, int(timeout_sec or 7200))
    cmd = _build_run_velox_ut_cmd(bd, regex)
    log_path = _new_compile_log_path("velox_ut")

    def _go() -> str:
        code, _raw = _run_remote_with_exit_and_log(cmd, log_path, timeout)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log_text = f.read()
        except OSError:
            log_text = _raw
        tail = "\n".join(log_text.splitlines()[-80:])
        status = "SUCCESS" if code == 0 else "FAILED"
        return (
            f"Velox UT {status} (exit code={code})\n"
            f"build_dir={bd}\n"
            f"test_regex={regex or '<all>'}\n\n"
            f"Last log lines:\n{tail}\n\n"
            f"日志已保存：{log_path}"
        )

    return await asyncio.to_thread(_go)


@mcp.tool()
async def get_compile_log(tail_lines: int = 80) -> str:
    """读取最新一次编译（compile_velox 或 compile_gluten_velox）的实时日志末尾若干行（默认 80 行）。

    编译进行中可随时调用以查看当前进度；编译结束后同样可用。
    日志目录：COMPILE_LOG_DIR（未设置则为 velox_remote_mcp/compile_logs/）。
    """
    def _read() -> str:
        log_dir = _default_compile_log_dir()
        pointer = os.path.join(log_dir, "latest.log")
        log_path: str | None = None

        if os.path.exists(pointer):
            try:
                with open(pointer, "r", encoding="utf-8") as f:
                    candidate = f.read().strip()
                if candidate and os.path.exists(candidate):
                    log_path = candidate
            except OSError:
                pass

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


def _sftp_put_text(remote_path: str, content: str) -> None:
    """通过 paramiko SFTP 把文本写到远端文件。

    为什么用 SFTP 而不是命令行 base64：99 条 SQL 拼起来上百 KB，base64 后作为
    `printf '%s' <b64>` 命令行参数会超过 ARG_MAX，报 `/bin/bash: Argument list too long`。
    SFTP 直接走文件流，不受命令行长度限制。
    """
    client = _paramiko_connect()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_path, "w") as f:
                f.write(content)
        finally:
            sftp.close()
    finally:
        client.close()


def _remote_tmp_sql_path(tag: str) -> str:
    import uuid
    return f"/tmp/mcp_velox_{tag}_{uuid.uuid4().hex[:12]}.sql"


def _default_remote_tpcds_dir() -> str:
    return _env("REMOTE_TPCDS_QUERY_DIR", "/path/to/spark-queries-tpcds")


def _build_run_cmd(remote_sql_path: str, database: str = "") -> str:
    """跑 run_exec_velox.sh <sqlfile> <database>。

    run_exec_velox.sh 已照 omni run_e2e_sql.sh 改成吃 $1=sql 文件、$2=database
    （末尾 `$DB_ARGS -f "$SQL_FILE"`），所以这里直接调，不再需要 wrapper/sed hack。
    2>&1 合并 stderr；跑完删除临时 sql 文件。
    """
    script_path = _env("E2E_VELOX_SCRIPT", "/path/to/run_exec_velox.sh")
    sp = shlex.quote(script_path)
    sf = shlex.quote(remote_sql_path)
    db = shlex.quote(database) if database else "''"
    return f"bash {sp} {sf} {db} 2>&1; _ec=$?; rm -f {sf}; exit $_ec"


_QSTART = "===MCP_QSTART"
_QEND = "===MCP_QEND"


def _build_99_per_query_cmd(database: str, src_dir: str) -> str:
    """逐条独立进程跑：远端 for 循环，每条 query 单独起一个 spark-sql 进程。

    为什么逐条而不是拼一个大文件单 session：Velox 1.3 baseline 在部分 query 上会
    native crash（如 q6 SIGSEGV）。单 session 下任何一条 crash 整个进程死、后面全不跑，
    且 native crash 无法用 SQL 层 hive.cli.errors.ignore 容错。逐条独立进程则一条 crash
    只杀那条，for 循环继续下一条 —— 这是可靠筛选「哪些 query 跑不通」的唯一办法。

    每条 query 临时文件 = join 兼容 SET（规避 MergeJoin NOT_IMPLEMENTED）+ 原 query，
    用 run_exec_velox.sh（yarn）跑。yarn 模式 HDFS 正常（local 模式 driver 直连 HDFS 会
    在 libhdfs.so JNI 崩，已验证不可用）。

    输出用 `===MCP_QSTART_<qid>===` / `===MCP_QEND_<qid>_EXIT_<code>===` 标记每条边界与
    退出码，供 _split 切分判定 OK / crash / fail。
    """
    script_path = _env("E2E_VELOX_SCRIPT", "/path/to/run_exec_velox.sh")
    sp = shlex.quote(script_path)
    src = shlex.quote(src_dir)
    db = shlex.quote(database) if database else "''"
    setup = (
        "SET spark.gluten.sql.columnar.forceShuffledHashJoin=true;\\n"
        "SET spark.sql.join.preferSortMergeJoin=false;\\n"
    )
    return (
        f"for f in $(ls {src}/q*.sql | sort -V); do "
        f"qid=$(basename \"$f\" .sql); "
        f"TMP=/tmp/mcp_q_$qid.sql; "
        f"printf '{setup}' > \"$TMP\"; cat \"$f\" >> \"$TMP\"; "
        f"echo \"{_QSTART}_$qid===\"; "
        f"bash {sp} \"$TMP\" {db} 2>&1; "
        f"echo \"{_QEND}_${{qid}}_EXIT_$?===\"; "
        f"rm -f \"$TMP\"; "
        f"done"
    )


def _list_remote_tpcds_qids(src_dir: str) -> list[str]:
    """SFTP 列出远端 src_dir 下的 q*.sql，返回去 .sql 的 qid 列表（自然序）。"""
    client = _paramiko_connect()
    try:
        sftp = client.open_sftp()
        try:
            names = [
                n[:-4] for n in sftp.listdir(src_dir)
                if n.startswith("q") and n.endswith(".sql")
            ]
        finally:
            sftp.close()
    finally:
        client.close()
    names.sort(key=_natural_query_key)
    return names


def _parse_velox_e2e_output(merged_output: str) -> str:
    """从 spark-sql 输出中提取 App ID、耗时、Fallback 告警、查询结果。"""
    lines = merged_output.splitlines()

    log_re = re.compile(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}|^(?:INFO|WARN|ERROR|DEBUG) ")
    log_lines = [l for l in lines if log_re.match(l)]
    result_lines = [l for l in lines if not log_re.match(l) and l.strip()]

    app_id = "未找到"
    for line in lines:
        m = re.search(r"(local-\d+|application_\d{13}_\d{4,})", line)
        if m:
            app_id = m.group(1)
            break

    time_taken = "未知"
    query_failed = False
    for line in reversed(lines):
        m = re.search(r"Time taken:\s*([\d.]+)\s*seconds.*Fetched", line)
        if m:
            time_taken = m.group(1) + "s"
            break
    if time_taken == "未知":
        error_kws = (
            "VeloxException", "Exception in thread", "FAILED",
            "Error running query", "SparkException", "VeloxRuntimeError",
            "VeloxUserError",
        )
        for line in lines:
            if any(k in line for k in error_kws):
                query_failed = True
                break
        if query_failed:
            time_taken = "查询失败（未完成）"
        else:
            for line in reversed(lines):
                m = re.search(r"Time taken:\s*([\d.]+)\s*seconds", line)
                if m:
                    time_taken = m.group(1) + "s"
                    break

    fallback_kws = (
        "FallbackNode", "Validation failed", "native validation failed",
        "GlutenFallbackReporter", "fell back to", "fallback to vanilla",
    )
    fallback_lines = [
        l for l in log_lines if any(k.lower() in l.lower() for k in fallback_kws)
    ]

    velox_ops: dict[str, int] = {}
    op_pattern = re.compile(r"(Velox\w+(?:Exec|Transformer\w*)|Columnar\w*Exec)")
    for line in log_lines:
        for m in op_pattern.finditer(line):
            name = m.group(1)
            velox_ops[name] = velox_ops.get(name, 0) + 1

    parts: list[str] = []
    parts.append(f"App ID : {app_id}  |  耗时 : {time_taken}")
    parts.append("")

    parts.append("─── Velox / Gluten 算子（日志扫描）──────────")
    if velox_ops:
        for name, cnt in sorted(velox_ops.items()):
            parts.append(f"  ✅ {name}  ×{cnt}")
    else:
        parts.append("  ⚠️  未检测到 Velox/Gluten 算子（可能全部 Fallback 或日志未打印 plan）")
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
    if result_lines:
        show = result_lines[-40:] if len(result_lines) > 40 else result_lines
        if len(result_lines) > 40:
            parts.append(f"  （共 {len(result_lines)} 行，显示末尾 40 行）")
        parts.extend(show)
    else:
        parts.append("  （无查询输出行）")

    return "\n".join(parts)


@mcp.tool()
async def run_e2e_sql_velox(
    sql: str, database: str = "", timeout_sec: int = 600
) -> str:
    """【正确性校验专用】在远端用 Gluten + Velox 后端执行 SQL，返回查询结果用于与基准对比。

    ⚠️  本工具用于正确性校验。性能基线/对比建议另起脚本。

    脚本默认位置：/path/to/run_exec_velox.sh
    该脚本是纯 spark-sql 启动器（不接受参数），MCP 端通过 stdin 重定向把 SQL 喂进去。

    sql 参数支持**多条语句**（用 ; 分隔），所有语句在同一个 spark-sql session 中
    按顺序执行。DDL（CREATE TABLE / INSERT）与测试查询可合并为一次调用：

      sql = \"\"\"
        CREATE TABLE test_input (a INT, b STRING);
        INSERT INTO test_input VALUES (1,'x'),(2,'y');
        SELECT a, b FROM test_input;
      \"\"\"

    参数说明：
      sql         一条或多条 SQL（分号分隔），通过远端临时文件 + stdin 传入。
      database    Hive/Spark 数据库名（如 tpcds_sf1）；非空时自动在最前面插入 USE <database>;
      timeout_sec 超时秒数，默认 600s（YARN 调度 + Spark 启动一般 60~120s，留余量）；
                  也可通过 E2E_VELOX_TIMEOUT_SECONDS 环境变量覆盖

    返回内容：
      - 查询结果（末尾 40 行）← 正确性校验的核心依据
      - Velox / Gluten 算子（日志扫描计数，仅供参考）
      - Fallback 告警摘要（Validation failed / FallbackNode 等）
      - Spark App ID 及单次耗时（仅供参考）
      - 完整日志本地路径
    """
    sql_s = (sql or "").strip()
    if not sql_s:
        return "无法执行：sql 参数为空，请传入有效的 SQL 语句。"

    db_s = (database or "").strip()

    env_to = _env("E2E_VELOX_TIMEOUT_SECONDS")
    to = int(env_to) if env_to else max(600, timeout_sec)

    log_path = _new_compile_log_path("e2e_sql_velox")

    def _go() -> str:
        remote_sql = _remote_tmp_sql_path("e2e")
        try:
            _sftp_put_text(remote_sql, sql_s)
        except Exception as e:
            return f"【Velox E2E 执行失败】SFTP 上传 SQL 到远端失败：{e}"
        # database 走 run_exec_velox.sh 的 $2（--database），不再在 SQL 里加 USE
        cmd = _build_run_cmd(remote_sql, db_s)
        code, _body = _run_remote_with_exit_and_log(cmd, log_path, to)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                full_output = f.read()
        except OSError:
            full_output = _body

        summary = _parse_velox_e2e_output(full_output)
        db_hint = f"  数据库 : {db_s}\n" if db_s else ""
        status = (
            "【Velox E2E 执行成功】" if code == 0
            else f"【Velox E2E 执行失败（退出码 {code}）】"
        )
        return f"{status}\n{db_hint}\n{summary}\n\n日志已保存：{log_path}"

    return await asyncio.to_thread(_go)


def _default_tpcds_results_dir() -> str:
    return _env("TPCDS_RESULTS_DIR") or str(
        Path(__file__).resolve().parent / "tpcds_results"
    )


def _natural_query_key(qid: str) -> tuple:
    """q1 < q2 < ... < q9 < q10 < ... < q14a < q14b < q15 ..."""
    m = re.match(r"^q(\d+)([a-z]*)$", qid)
    if not m:
        return (10**9, qid)
    return (int(m.group(1)), m.group(2))


_BANNER_BEGIN = "MCP_TPCDS_BANNER_BEGIN"
_BANNER_END = "MCP_TPCDS_BANNER_END"


def _split_99_sql_output(merged_output: str, query_ids: list[str]) -> dict[str, dict]:
    """按 ===MCP_QSTART_<qid>=== / ===MCP_QEND_<qid>_EXIT_<code>=== 切分逐条输出。

    每条判定 status：
      - exit 0 且有 `Time taken: ... Fetched` → ok
      - exit 134/139（SIGABRT/SIGSEGV）→ crash（Velox native 崩溃）
      - 其它非 0，或有 VeloxException/AnalysisException 等 → fail
      - 未出现该 qid 的 QSTART → 未运行（理论上逐条不会，除非整体中断）

    返回：{ qid: { "result_lines", "time_taken", "exit_code", "status",
                   "fallback": bool, "error" } }
    """
    lines = merged_output.splitlines()
    log_re = re.compile(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}|^(?:INFO|WARN|ERROR|DEBUG) ")
    # 启动噪音：每条 query 独立进程都会打这些，且含 App Id / pid / 时间戳（每次不同），
    # 必须从结果行剔除，否则 diff 必假阳性。
    noise_re = re.compile(
        r"^Setting default log level"
        r"|^To adjust logging level"
        r"|^Spark Web UI"
        r"|^Spark master:"
        r"|Application Id:"
        r"|Hive Session ID"
        r"|^[WIEF]\d{8} \d{2}:\d{2}:\d{2}"          # velox glog: W20260520 08:39:33...
        r"|^SLF4J:"
        r"|NativeCodeLoader"
    )
    start_re = re.compile(rf"^{re.escape(_QSTART)}_(\S+?)===$")
    end_re = re.compile(rf"^{re.escape(_QEND)}_(.+?)_EXIT_(-?\d+)===$")

    out: dict[str, dict] = {
        qid: {"raw_lines": [], "time_taken": "未运行", "result_lines": [],
              "exit_code": None, "status": "未运行", "fallback": False, "error": None}
        for qid in query_ids
    }
    current: str | None = None
    for line in lines:
        s = line.strip()
        m_start = start_re.match(s)
        if m_start:
            current = m_start.group(1)
            out.setdefault(current, {"raw_lines": [], "time_taken": "未运行",
                                     "result_lines": [], "exit_code": None,
                                     "status": "未运行", "fallback": False, "error": None})
            continue
        m_end = end_re.match(s)
        if m_end:
            qid_e, code = m_end.group(1), int(m_end.group(2))
            if qid_e in out:
                out[qid_e]["exit_code"] = code
            current = None
            continue
        if current is not None:
            out[current]["raw_lines"].append(line)

    error_kws = (
        "VeloxException", "Exception in thread", "Error running query",
        "SparkException", "VeloxRuntimeError", "VeloxUserError",
        "AnalysisException", "ParseException",
    )
    fb_kws = ("Validation failed", "FallbackReporter", "fell back to", "fallback to vanilla")
    for qid, info in out.items():
        for line in info["raw_lines"]:
            if log_re.match(line) or noise_re.search(line) or not line.strip():
                continue
            if "Time taken:" in line:
                continue
            # SET 回显行（spark.gluten... / spark.sql...）不是结果
            if re.match(r"^spark\.", line.strip()):
                continue
            info["result_lines"].append(line.rstrip())
        for line in info["raw_lines"]:
            if any(k.lower() in line.lower() for k in fb_kws):
                info["fallback"] = True
                break
        for line in reversed(info["raw_lines"]):
            m = re.search(r"Time taken:\s*([\d.]+)\s*seconds.*Fetched", line)
            if m:
                info["time_taken"] = m.group(1) + "s"
                break
        code = info["exit_code"]
        if code in (134, 139):
            info["status"] = "crash"
            info["time_taken"] = f"crash(exit {code})"
            for line in info["raw_lines"]:
                if "SIGSEGV" in line or "SIGABRT" in line or "core dumped" in line:
                    info["error"] = line.strip()[:300]
                    break
        elif code == 0 and info["time_taken"].endswith("s"):
            info["status"] = "ok"
        elif code is None:
            info["status"] = "未运行"
        else:
            info["status"] = "fail"
            for line in info["raw_lines"]:
                if any(k in line for k in error_kws):
                    info["error"] = line.strip()[:300]
                    break
            if info["time_taken"] == "未运行":
                info["time_taken"] = f"fail(exit {code})"
    return out


def _write_99_sql_results(
    run_label: str, splits: dict[str, dict], full_output_path: str, app_id: str
) -> str:
    """把切分后的结果落盘到 tpcds_results/<run_label>/。

    每条 qN 一个 .txt（只保留结果行，便于 diff），加一个 metadata.json 汇总。
    """
    import json as _json
    root = Path(_default_tpcds_results_dir()) / run_label
    root.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_label": run_label,
        "app_id": app_id,
        "full_session_log": full_output_path,
        "queries": [],
    }
    for qid in sorted(splits.keys(), key=_natural_query_key):
        info = splits[qid]
        body = "\n".join(info["result_lines"])
        (root / f"{qid}.txt").write_text(body + "\n", encoding="utf-8")
        meta["queries"].append({
            "qid": qid,
            "status": info.get("status"),
            "exit_code": info.get("exit_code"),
            "time_taken": info["time_taken"],
            "result_line_count": len(info["result_lines"]),
            "fallback": info.get("fallback"),
            "error": info["error"],
        })
    (root / "metadata.json").write_text(
        _json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return str(root)


@mcp.tool()
async def run_tpcds_99_velox(
    run_label: str,
    database: str = "tpcds",
    sql_dir: str = "",
    timeout_sec: int = 3600,
) -> str:
    """【正确性校验·批量】一次性跑完 TPC-DS 99 条 query，落盘按 query 切分的结果。

    用途：
      - baseline 跑一次保存为 run_label="baseline_<commit_sha>"，跨多个文件修改复用
      - 改完一个文件用 run_label="sve256_<file>_<sha>" 再跑一次
      - 然后用 diff_tpcds_results(baseline, modified) 字面对比

    实现要点：
      - SQL 直接用**远端** TPC-DS 目录（默认 /path/to/spark-queries-tpcds），
        不依赖本机文件、不上传——在远端 for 循环拼接，天然避开 ARG_MAX
      - 99 条 SQL 同一个 spark-sql session 跑完（避免 99 次 Spark 启动开销）
      - 每条 query 前后插 SELECT 文本 banner（不用 SQL 注释，spark-sql 可能不 echo 注释）
      - 输出按 banner 切分，每条 qN 的结果写到 tpcds_results/<run_label>/qN.txt
      - 同时写 metadata.json（耗时、错误、结果行数）

    参数：
      run_label   必填。本次运行的标识，决定结果落盘目录名。建议格式：
                  baseline_<sha>、sve256_<file>_<sha>。仅含 [A-Za-z0-9_.-]。
      database    Hive/Spark 数据库名，默认 tpcds
                  （hive-testbench 生成的 sf10 ORC 库，已 string 化避免 varchar fallback）。
                  走 run_exec_velox.sh 的 --database $2，不在 SQL 里加 USE。
      sql_dir     **远端** SQL 目录，默认 /path/to/spark-queries-tpcds。
      timeout_sec 整批 timeout，默认 3600s。也可通过 TPCDS_99_TIMEOUT_SECONDS 覆盖。

    返回：
      汇总文本（成功 query 数、失败 query 列表、总耗时摘要、落盘目录路径）。
      详细结果在 tpcds_results/<run_label>/，用 diff_tpcds_results 对比。
    """
    rl = (run_label or "").strip()
    if not rl or not re.match(r"^[A-Za-z0-9_.-]+$", rl):
        return ("无法执行：run_label 必填且只能含 [A-Za-z0-9_.-]。\n"
                "示例：baseline_2026-05-19、sve256_BitPackDecoder_abc1234")

    src_dir = (sql_dir or "").strip() or _default_remote_tpcds_dir()
    try:
        qids = _list_remote_tpcds_qids(src_dir)
    except Exception as e:
        return f"无法执行：列远端 SQL 目录失败 {src_dir}: {e}"
    if not qids:
        return f"无法执行：远端 {src_dir} 没找到 q*.sql"

    env_to = _env("TPCDS_99_TIMEOUT_SECONDS")
    to = int(env_to) if env_to else max(1800, timeout_sec)

    cmd = _build_99_per_query_cmd((database or "").strip(), src_dir)
    log_path = _new_compile_log_path(f"tpcds99_{rl}")

    def _go() -> str:
        code, _body = _run_remote_with_exit_and_log(cmd, log_path, to)
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                full_output = f.read()
        except OSError:
            full_output = _body

        app_id_m = re.search(
            r"(local-\d+|application_\d{13}_\d{4,})", full_output
        )
        app_id = app_id_m.group(1) if app_id_m else "未找到"

        splits = _split_99_sql_output(full_output, qids)
        result_dir = _write_99_sql_results(rl, splits, log_path, app_id)

        ok = [q for q in qids if splits[q]["status"] == "ok"]
        crashed = [q for q in qids if splits[q]["status"] == "crash"]
        failed = [q for q in qids if splits[q]["status"] == "fail"]
        skipped = [q for q in qids if splits[q]["status"] == "未运行"]
        fb = [q for q in qids if splits[q].get("fallback")]

        parts: list[str] = []
        parts.append(f"【TPC-DS 99 条 逐条执行完毕】（整批 wrapper 退出码 {code}）")
        parts.append(f"  run_label : {rl}")
        parts.append(f"  数据库    : {database}")
        parts.append(f"  App ID(末): {app_id}")
        parts.append(f"  ✅ 成功 : {len(ok)} / {len(qids)}")
        parts.append(f"  💥 崩溃 : {len(crashed)} → {crashed}" if crashed else "  💥 崩溃 : 0")
        parts.append(f"  ❌ 失败 : {len(failed)} → {failed}" if failed else "  ❌ 失败 : 0")
        parts.append(f"  ⏭️  未运行: {len(skipped)} → {skipped}" if skipped else "  ⏭️  未运行: 0")
        parts.append(f"  ⚠️  含 Fallback : {len(fb)} → {fb[:30]}" if fb else "  ⚠️  含 Fallback : 0")
        parts.append(f"  结果目录  : {result_dir}")
        parts.append(f"  会话日志  : {log_path}")
        return "\n".join(parts)

    return await asyncio.to_thread(_go)


@mcp.tool()
async def diff_tpcds_results(label_a: str, label_b: str) -> str:
    """字面对比两次 run_tpcds_99_velox 的结果，列出差异 query。

    参数：
      label_a   基线 run_label（如 baseline_2026-05-19）
      label_b   对比 run_label（如 sve256_BitPackDecoder_abc1234）

    返回：每条 query 一行 [OK]/[DIFF]/[MISSING]，含差异 query 的前 20 行差异预览。
    """
    a = (label_a or "").strip()
    b = (label_b or "").strip()
    if not a or not b:
        return "无法执行：label_a 和 label_b 都必填"

    root = Path(_default_tpcds_results_dir())
    da, db_ = root / a, root / b
    if not da.is_dir():
        return f"无法执行：baseline 目录不存在 {da}"
    if not db_.is_dir():
        return f"无法执行：modified 目录不存在 {db_}"

    qids_a = {p.stem for p in da.glob("q*.txt")}
    qids_b = {p.stem for p in db_.glob("q*.txt")}
    all_qids = sorted(qids_a | qids_b, key=_natural_query_key)

    import difflib
    ok_count = 0
    diff_count = 0
    miss_count = 0
    parts: list[str] = []

    for qid in all_qids:
        fa, fb = da / f"{qid}.txt", db_ / f"{qid}.txt"
        if not fa.exists():
            parts.append(f"  [MISSING-A] {qid} 在 baseline 不存在")
            miss_count += 1
            continue
        if not fb.exists():
            parts.append(f"  [MISSING-B] {qid} 在 modified 不存在")
            miss_count += 1
            continue
        ta = fa.read_text(encoding="utf-8", errors="replace").splitlines()
        tb = fb.read_text(encoding="utf-8", errors="replace").splitlines()
        if ta == tb:
            ok_count += 1
            continue
        diff_count += 1
        diff_lines = list(difflib.unified_diff(ta, tb, fromfile=f"{a}/{qid}", tofile=f"{b}/{qid}", lineterm=""))
        preview = "\n      ".join(diff_lines[:20])
        parts.append(f"  [DIFF] {qid} (baseline {len(ta)} 行 vs modified {len(tb)} 行)")
        parts.append(f"      {preview}")
        if len(diff_lines) > 20:
            parts.append(f"      ... 另有 {len(diff_lines) - 20} 行 diff")

    header = (
        f"【TPC-DS 结果 diff】{a}  vs  {b}\n"
        f"  ✅ 一致 : {ok_count}\n"
        f"  ❌ 差异 : {diff_count}\n"
        f"  ⚠️  缺失 : {miss_count}\n"
        f"{'─' * 60}\n"
    )
    return header + ("\n".join(parts) if parts else "（无差异详情）")


@mcp.tool()
async def read_remote_file(remote_path: str, tail_lines: int = 100) -> str:
    """读取远端文件末尾若干行（默认 100 行）；若 remote_path 是目录则 ls -la。

    常用于查看远端编译目录内容或脚本日志。
    """
    rp = (remote_path or "").strip()
    if not rp:
        return "错误：remote_path 不能为空"
    cmd = (
        f"if [ -d {shlex.quote(rp)} ]; then ls -la {shlex.quote(rp)}; "
        f"else tail -n {tail_lines} {shlex.quote(rp)}; fi"
    )
    return await asyncio.to_thread(_run_remote, cmd, timeout_sec=30)


# ============================================================================
# 性能测试 + 火焰图
#
# 远端 REMOTE_PERF_SCRIPT（默认 test-all-velox-1t.sh）source common_utils_velox.sh，对
# REMOTE_PERF_QUERY_SQL_DIR（…/sql/query_sql）下每个 .sql 用 spark-sql --master yarn
# + spark-velox-1t.conf 跑；async-profiler agent 把 CPU 火焰图写到各 executor 节点
# REMOTE_FLAME_DIR（/tmp/flame_graphs），脚本每条 query 末尾在 driver 保留一张并改名 ${query}.html。
# 本组工具：准备 query_sql → 跑脚本 → 归集各 worker 火焰图 → SFTP 拉回本机。
# ============================================================================


def _perf_script_dir() -> str:
    return _env("REMOTE_PERF_SCRIPT_DIR", "/path/to/spark-test-tool/script")


def _perf_query_sql_dir() -> str:
    return _env("REMOTE_PERF_QUERY_SQL_DIR", "/path/to/spark-test-tool/sql/query_sql")


def _default_flame_local_root() -> str:
    raw = _env("FLAME_LOCAL_DIR")
    if raw:
        return raw
    return str(Path(__file__).resolve().parent / "flame_exports")


def _build_perf_query_prep(query_sql: str, query_id: str) -> str:
    """准备 REMOTE_PERF_QUERY_SQL_DIR 内容（先清空该目录直接子项）：
      query_id+sql -> 写 {query_id}.sql
      query_id     -> 从 REMOTE_TPCDS_QUERY_DIR 复制 {query_id}.sql（保留文件名 → 火焰图/日志按查询号命名）
      sql          -> 写 q1.sql
      都空         -> 复制全量 TPC-DS 查询集
    """
    qdir = _perf_query_sql_dir()
    qdir_q = shlex.quote(qdir)
    clear = f"mkdir -p {qdir_q} && find {qdir_q} -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +"
    qs = (query_sql or "").strip()
    qid = (query_id or "").strip().lower()
    src = _default_remote_tpcds_dir().rstrip("/")
    if qid:
        dst_q = shlex.quote(posixpath.join(qdir.rstrip("/"), f"{qid}.sql"))
        if qs:
            b64 = base64.b64encode(qs.encode("utf-8")).decode("ascii")
            return f"{clear} && printf '%s' {shlex.quote(b64)} | base64 -d > {dst_q}"
        return f"{clear} && cp {shlex.quote(posixpath.join(src, qid + '.sql'))} {dst_q}"
    if qs:
        dst_q = shlex.quote(posixpath.join(qdir.rstrip("/"), "q1.sql"))
        b64 = base64.b64encode(qs.encode("utf-8")).decode("ascii")
        return f"{clear} && printf '%s' {shlex.quote(b64)} | base64 -d > {dst_q}"
    return f"{clear} && cp -a {shlex.quote(src)}/. {qdir_q}/"


def _build_run_perf_script_fragment() -> str:
    d = shlex.quote(_perf_script_dir())
    script = _env("REMOTE_PERF_SCRIPT", "test-all-velox-1t.sh")
    if script.startswith("/"):
        raise ValueError("REMOTE_PERF_SCRIPT 请填文件名（在 REMOTE_PERF_SCRIPT_DIR 下执行）")
    return f"cd {d} && bash {shlex.quote('./' + script)}"


def _build_collect_worker_flames_fragment() -> str:
    """脚本跑完后把各 worker 节点 /tmp/flame_graphs 下 .html 归集到本节点（best-effort，不影响 exit code）。"""
    flame_dir_q = shlex.quote(_env("REMOTE_FLAME_DIR", "/tmp/flame_graphs"))
    workers_file_q = shlex.quote(
        _env("HADOOP_WORKERS_FILE", "/path/to/hadoop/etc/hadoop/workers")
    )
    return (
        f"mkdir -p {flame_dir_q}; "
        f"_self_host=$(hostname); _self_ip=$(hostname -I | awk '{{print $1}}'); "
        f"if [ -f {workers_file_q} ]; then "
        f"while IFS= read -r _w || [ -n \"$_w\" ]; do "
        f"_w=$(echo \"$_w\" | tr -d '[:space:]'); [ -z \"$_w\" ] && continue; "
        f"{{ [ \"$_w\" = \"$_self_host\" ] || [ \"$_w\" = \"$_self_ip\" ]; }} && continue; "
        f"_htmls=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 "
        f"root@\"$_w\" \"ls {flame_dir_q}/*.html 2>/dev/null\" 2>/dev/null) || continue; "
        f"[ -z \"$_htmls\" ] && continue; "
        f"echo \"$_htmls\" | while read -r _f; do "
        f"scp -o BatchMode=yes -o StrictHostKeyChecking=no -q "
        f"root@\"$_w\":\"$_f\" {flame_dir_q}/ 2>/dev/null || true; "
        f"done; "
        f"done < {workers_file_q}; "
        f"fi; true"
    )


def _build_drop_caches_fragment() -> str:
    workers_file_q = shlex.quote(
        _env("HADOOP_WORKERS_FILE", "/path/to/hadoop/etc/hadoop/workers")
    )
    return (
        "sync && echo 3 > /proc/sys/vm/drop_caches; "
        f"_self_host=$(hostname); _self_ip=$(hostname -I | awk '{{print $1}}'); "
        f"if [ -f {workers_file_q} ]; then "
        f"while IFS= read -r _w || [ -n \"$_w\" ]; do "
        f"_w=$(echo \"$_w\" | tr -d '[:space:]'); [ -z \"$_w\" ] && continue; "
        f"{{ [ \"$_w\" = \"$_self_host\" ] || [ \"$_w\" = \"$_self_ip\" ]; }} && continue; "
        f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=5 "
        f"root@\"$_w\" 'sync && echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true; "
        f"done < {workers_file_q}; fi; echo '[drop_caches] done on driver + workers'; true"
    )


def _build_velox_perf_command(query_sql: str, query_id: str) -> str:
    prep = _build_perf_query_prep(query_sql, query_id)
    run = _build_run_perf_script_fragment()
    collect = _build_collect_worker_flames_fragment()
    return f"{prep} && {run}; {collect}"


def _perf_timeout() -> int:
    return int(_env("PERF_VELOX_TIMEOUT_SECONDS", _env("SSH_TIMEOUT_SECONDS", "3600")) or "3600")


def _perf_logs_dir() -> str:
    return _env("REMOTE_PERF_LOGS_DIR", "/path/to/spark-test-tool/logs")


def _perf_db() -> str:
    return _env("REMOTE_PERF_DB", "tpcds")


def _perf_results_summary(query_id: str = "", tail_lines: int = 40) -> str:
    """读 perf 跑完后的 .result（spark-sql 纯 stdout 查询输出，可直接用于正确性 sanity check）。

    test-all-velox-1t.sh 把每条 query 的结果 `1>${query}.result`（stderr 才 `2>${query}.log`），
    脚本末尾 del_tmplog 把 .result 归到 ${LOGPATH}/<db>/。所以性能跑完无需另跑 run_e2e_sql_velox
    即可拿到结果行做正确性比对（velox perf 与 run_e2e_sql_velox 同一 SQL 源 /path/to/
    spark-queries-tpcds，join 算法切换不改结果，可比）。
    """
    logs = posixpath.join(_perf_logs_dir(), _perf_db())
    d = shlex.quote(logs)
    qid = (query_id or "").strip().lower()
    pat = f"{qid}.sql.result" if qid else "*.result"
    cmd = (
        f"d={d}; for r in $d/{pat}; do "
        f"[ -f \"$r\" ] || continue; n=$(wc -l < \"$r\"); "
        f"echo \"===RESULT $(basename \"$r\") rows=$n===\"; "
        f"tail -n {int(tail_lines)} \"$r\"; "
        f"done; true"
    )
    out = _run_remote(cmd, timeout_sec=60)
    body = out.split("--- stdout ---", 1)[-1].split("--- exit code ---", 1)[0].strip() if "--- stdout ---" in out else out.strip()
    if not body:
        return "（未找到 .result：该 query 可能失败，或 del_tmplog 未归档；可 read_remote_file 查 logs/<db>/<q>.sql.log）"
    return body


def _parse_velox_perf_output(text: str) -> str:
    times = re.findall(r"QUERY TIME:\s*([0-9.]+)\s*seconds", text)
    fails = re.findall(r"the query SQL:\s*(\S+)\s*execute failed", text)
    lines: list[str] = []
    if times:
        lines.append("每条 QUERY TIME(s)：" + ", ".join(times))
    if fails:
        lines.append(f"⚠️ 失败 {len(fails)} 条：" + ", ".join(fails))
    if not lines:
        lines.append(
            "（未从 stdout 解析到 QUERY TIME；可 read_remote_file 查远端 logs-velox-1t-* 与 query_*.report）"
        )
    return "\n".join(lines)


def _fetch_flame_htmls_sync(remote_dir=None, session_folder_name=None) -> str:
    """SFTP 把远端目录下 .html 拉到本机时间戳子目录，返回 file:// 链接。"""
    remote_root = (
        remote_dir.strip()
        if remote_dir and remote_dir.strip()
        else _env("REMOTE_FLAME_DIR", "/tmp/flame_graphs")
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
        return f"SFTP 连接失败: {e}\n请确认 SSH_PASSWORD/SSH_IDENTITY 配置正确。"
    lines = [f"远端目录: {remote_root}", f"本机目录: {os.path.abspath(local_session)}", ""]
    downloaded: list[str] = []
    errors: list[str] = []
    try:
        sftp = client.open_sftp()
        try:
            try:
                entries = sftp.listdir_attr(remote_root)
            except OSError as e:
                return f"无法访问远端目录 {remote_root}: {e}"
            for attr in entries:
                name = attr.filename
                if name in (".", "..") or not name.lower().endswith(".html"):
                    continue
                safe = posixpath.basename(name)
                if not safe or safe != name:
                    continue
                rp = posixpath.join(remote_root, safe)
                lp = os.path.join(local_session, safe)
                try:
                    sftp.get(rp, lp)
                    downloaded.append(os.path.abspath(lp))
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
        lines.append("未找到 .html 火焰图（可能尚未写出，或路径不对）。可调 REMOTE_FLAME_DIR 或传 remote_dir。")
        return "\n".join(lines)
    lines.append(f"已下载 {len(downloaded)} 个 HTML 火焰图。复制下面 file:// 链接到浏览器查看：")
    lines.append("")
    for p in downloaded:
        lines.append(Path(p).resolve().as_uri())
    return "\n".join(lines)


def _run_perf_then_fetch_sync(query_sql: str, query_id: str) -> str:
    try:
        remote = _build_velox_perf_command(query_sql or "", query_id or "")
    except ValueError as e:
        return f"配置错误: {e}"
    log_path = _new_compile_log_path("perf_velox_flame")
    code, run_out = _run_remote_with_exit_and_log(remote, log_path, _perf_timeout())
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            full = f.read()
    except OSError:
        full = run_out
    summary = _parse_velox_perf_output(full)
    results = _perf_results_summary(query_id or "")
    fetch_out = _fetch_flame_htmls_sync()
    status = (
        "【Velox 性能测试 + 火焰图】"
        if code == 0
        else f"【Velox 性能测试退出码 {code}（火焰图仍尝试拉取）】"
    )
    return (
        f"{status}\n{summary}\n\n"
        f"───── 查询结果（.result，可作正确性 sanity check）─────\n{results}\n\n"
        f"日志已保存：{log_path}"
        f"\n\n===== 火焰图（SFTP 已拉取到本机） =====\n\n{fetch_out}"
    )


@mcp.tool()
async def run_velox_perf_test(query_id: str = "", query_sql: str = "") -> str:
    """【性能测试专用】YARN 集群上用 Gluten+Velox 执行 SQL 测端到端耗时（驱动 test-all-velox-1t.sh）。

    ⚠️ 只用于性能计时，不返回查询结果内容；正确性校验请用 run_e2e_sql_velox。
    每次调用 = 跑一遍脚本（对 query_sql 目录里的 query 各跑一次）。冷/热由多次调用 + cache
    状态决定（冷跑前可先 drop_cluster_caches）。

    参数（优先 query_id）：
      query_id   TPC-DS 查询编号如 "q7"。非空时从 REMOTE_TPCDS_QUERY_DIR 复制 {query_id}.sql
                 进 query_sql（保留文件名 → 火焰图/日志按查询号命名）。
      query_sql  自定义 SQL；与 query_id 同传写 {query_id}.sql，单独传写 q1.sql；都空跑全量。

    返回每条 QUERY TIME + 本机日志路径；明细可 read_remote_file 看远端 logs-velox-1t-* 与 query_*.report。
    """
    try:
        remote = _build_velox_perf_command(query_sql or "", query_id or "")
    except ValueError as e:
        return f"配置错误: {e}"
    log_path = _new_compile_log_path("perf_velox")
    code, text = await asyncio.to_thread(
        _run_remote_with_exit_and_log, remote, log_path, _perf_timeout()
    )
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            full = f.read()
    except OSError:
        full = text
    status = "【Velox 性能测试完成】" if code == 0 else f"【Velox 性能测试退出码 {code}】"
    results = await asyncio.to_thread(_perf_results_summary, query_id or "")
    return (
        f"{status}\n{_parse_velox_perf_output(full)}\n\n"
        f"───── 查询结果（.result，可作正确性 sanity check）─────\n{results}\n\n"
        f"日志已保存：{log_path}"
    )


@mcp.tool()
async def fetch_velox_flame_graphs(remote_dir: str = "", session_folder_name: str = "") -> str:
    """SFTP 把远端 REMOTE_FLAME_DIR（默认 /tmp/flame_graphs）下所有 .html（async-profiler CPU 火焰图）拉到本机。

    本机根目录 FLAME_LOCAL_DIR（默认 velox_remote_mcp/flame_exports），每次新建时间戳子目录。
    返回 file:// 链接，复制到 Chrome/Edge 打开。
    """
    rd = remote_dir.strip() or None
    sf = session_folder_name.strip() or None
    return await asyncio.to_thread(_fetch_flame_htmls_sync, rd, sf)


@mcp.tool()
async def run_velox_perf_and_fetch_flames(query_id: str = "", query_sql: str = "") -> str:
    """先按 run_velox_perf_test 跑 test-all-velox-1t.sh，结束后归集各 worker 火焰图并 SFTP 拉 .html 回本机。

    query_id / query_sql 规则同 run_velox_perf_test；推荐传 query_id（如 "q7"）保证火焰图文件名正确。
    """
    return await asyncio.to_thread(_run_perf_then_fetch_sync, query_sql or "", query_id or "")


@mcp.tool()
async def drop_cluster_caches() -> str:
    """清空 driver + 所有 worker 节点的 OS page cache（sync; echo 3 > drop_caches），用于性能冷跑前。"""
    return await asyncio.to_thread(_run_remote, _build_drop_caches_fragment(), timeout_sec=120)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
