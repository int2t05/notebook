from unittest.mock import patch, MagicMock
import subprocess
import pytest

from scripts.utils import (
    CLISubprocessLLM, BudgetExceeded, _strip_markdown_fence,
)


def test_strip_markdown_fence_handles_json_block():
    assert _strip_markdown_fence('```json\n{"a":1}\n```') == '{"a":1}'
    assert _strip_markdown_fence('```\n{"a":1}\n```') == '{"a":1}'
    assert _strip_markdown_fence('{"a":1}') == '{"a":1}'


def test_resolve_model_maps_flash_and_strong():
    cli = CLISubprocessLLM()
    assert cli._resolve_model("flash") == "haiku"
    assert cli._resolve_model("strong") == "sonnet"
    assert cli._resolve_model("custom") == "custom"  # passthrough


def test_call_invokes_subprocess_with_claude_defaults(monkeypatch):
    cli = CLISubprocessLLM(max_budget=10_000)
    captured = {}
    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return MagicMock(returncode=0, stdout='{"keywords":["x"]}', stderr="")
    monkeypatch.setattr("scripts.utils.subprocess.run", fake_run)
    text, used = cli.call("hello world", model="flash", json_mode=True)
    assert text == '{"keywords":["x"]}'
    assert used > 0
    # Default invocation: claude --no-session-persistence --model haiku -p <prompt>
    assert captured["cmd"][0] == "claude"
    assert "--no-session-persistence" in captured["cmd"]
    assert captured["cmd"][-2] == "-p"


def test_call_for_gemini_uses_different_flags(monkeypatch):
    """Generic CLI backend handles any agent CLI's flag layout."""
    cli = CLISubprocessLLM(
        max_budget=10_000,
        binary="gemini", prompt_arg="-p", model_arg="-m",
        extra_args=[],
        model_map={"flash": "gemini-2.5-flash", "strong": "gemini-2.5-pro"},
    )
    captured = {}
    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return MagicMock(returncode=0, stdout='{"ok":1}', stderr="")
    monkeypatch.setattr("scripts.utils.subprocess.run", fake_run)
    cli.call("hi", model="strong", json_mode=True)
    assert captured["cmd"][0] == "gemini"
    assert "-m" in captured["cmd"] and "gemini-2.5-pro" in captured["cmd"]
    # No claude-specific --no-session-persistence
    assert "--no-session-persistence" not in captured["cmd"]


def test_call_can_omit_model_arg(monkeypatch):
    """Pass model_arg='' for CLIs that use a single binary per model variant."""
    cli = CLISubprocessLLM(binary="foo", model_arg="", extra_args=[])
    captured = {}
    monkeypatch.setattr("scripts.utils.subprocess.run",
                         lambda cmd, **kw: (captured.update(cmd=cmd) or
                                            MagicMock(returncode=0, stdout="ok",
                                                      stderr="")))
    cli.call("p", model="flash")
    # No "--model" / "haiku" tokens
    assert "--model" not in captured["cmd"]
    assert "haiku" not in captured["cmd"]


def test_call_strips_markdown_fence_in_json_mode(monkeypatch):
    cli = CLISubprocessLLM(max_budget=10_000)
    fake = MagicMock(returncode=0, stdout='```json\n{"k":1}\n```', stderr="")
    monkeypatch.setattr("scripts.utils.subprocess.run", lambda *a, **kw: fake)
    text, _ = cli.call("p", model="flash", json_mode=True)
    assert text == '{"k":1}'


def test_call_raises_on_nonzero_exit(monkeypatch):
    cli = CLISubprocessLLM(max_budget=10_000)
    fake = MagicMock(returncode=1, stdout="", stderr="auth failed")
    monkeypatch.setattr("scripts.utils.subprocess.run", lambda *a, **kw: fake)
    with pytest.raises(RuntimeError, match="claude CLI exited 1"):
        cli.call("p", model="flash")


def test_call_raises_budget_after_use(monkeypatch):
    cli = CLISubprocessLLM(max_budget=10)
    fake = MagicMock(returncode=0,
                     stdout="x" * 200,  # ~50 tokens
                     stderr="")
    monkeypatch.setattr("scripts.utils.subprocess.run", lambda *a, **kw: fake)
    with pytest.raises(BudgetExceeded):
        cli.call("a longer prompt that pushes us over", model="flash")
