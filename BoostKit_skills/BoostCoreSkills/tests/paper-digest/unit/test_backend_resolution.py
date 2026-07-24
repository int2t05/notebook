"""Tests for the auto/cli/api backend choice in run.build_llm.

Covers the Q5 promise: API key is truly optional, CLI is the default path
when an agent CLI is on PATH.
"""
import os
import pytest
from unittest.mock import patch

from scripts.run import _resolve_backend_choice, build_llm
from scripts.utils import LLMClient, CLISubprocessLLM


def _cfg(cli_binary="claude", api_key_env="PAPER_DIGEST_LLM_API_KEY"):
    return {
        "llm": {
            "api": {"api_key_env": api_key_env,
                    "base_url_default": "https://api.deepseek.com/v1",
                    "model_flash": "deepseek-chat",
                    "model_strong": "deepseek-reasoner"},
            "cli_backend": {"binary": cli_binary,
                             "prompt_arg": "-p", "model_arg": "--model",
                             "extra_args": ["--no-session-persistence"],
                             "model_flash": "haiku", "model_strong": "sonnet"},
        }
    }


def test_explicit_api_returned_unchanged():
    assert _resolve_backend_choice(_cfg(), "api") == "api"


def test_explicit_cli_returned_unchanged():
    assert _resolve_backend_choice(_cfg(), "cli") == "cli"


def test_auto_prefers_cli_when_binary_on_path(monkeypatch):
    monkeypatch.setattr("scripts.run.shutil.which",
                         lambda b: "/usr/local/bin/" + b)
    monkeypatch.delenv("PAPER_DIGEST_LLM_API_KEY", raising=False)
    assert _resolve_backend_choice(_cfg(), "auto") == "cli"


def test_auto_falls_back_to_api_when_no_cli_but_key_set(monkeypatch):
    monkeypatch.setattr("scripts.run.shutil.which", lambda b: None)
    monkeypatch.setenv("PAPER_DIGEST_LLM_API_KEY", "sk-test")
    assert _resolve_backend_choice(_cfg(), "auto") == "api"


def test_auto_raises_when_neither_available(monkeypatch):
    monkeypatch.setattr("scripts.run.shutil.which", lambda b: None)
    monkeypatch.delenv("PAPER_DIGEST_LLM_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="No LLM backend available"):
        _resolve_backend_choice(_cfg(), "auto")


def test_build_llm_cli_returns_cli_instance(monkeypatch):
    monkeypatch.setattr("scripts.run.shutil.which",
                         lambda b: "/usr/local/bin/" + b)
    llm = build_llm(_cfg(), max_budget=10_000, backend="cli")
    assert isinstance(llm, CLISubprocessLLM)
    assert llm.binary == "claude"
    assert llm.model_map == {"flash": "haiku", "strong": "sonnet"}


def test_build_llm_api_returns_api_instance(monkeypatch):
    monkeypatch.setenv("PAPER_DIGEST_LLM_API_KEY", "sk-fake")
    llm = build_llm(_cfg(), max_budget=10_000, backend="api")
    assert isinstance(llm, LLMClient)


def test_build_llm_api_without_key_errors(monkeypatch):
    monkeypatch.delenv("PAPER_DIGEST_LLM_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="requires env var"):
        build_llm(_cfg(), max_budget=10_000, backend="api")


def test_build_llm_respects_custom_cli_binary(monkeypatch):
    """Q3: switching to gemini/codex requires no code change, only config."""
    cfg = _cfg(cli_binary="gemini")
    cfg["llm"]["cli_backend"].update({
        "binary": "gemini", "prompt_arg": "-p", "model_arg": "-m",
        "extra_args": [],
        "model_flash": "gemini-2.5-flash",
        "model_strong": "gemini-2.5-pro",
    })
    monkeypatch.setattr("scripts.run.shutil.which",
                         lambda b: "/usr/bin/" + b)
    llm = build_llm(cfg, max_budget=10_000, backend="cli")
    assert llm.binary == "gemini"
    assert llm.model_map["strong"] == "gemini-2.5-pro"
    assert llm.extra_args == []
