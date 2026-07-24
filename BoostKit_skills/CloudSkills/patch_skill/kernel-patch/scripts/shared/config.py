"""
Kernel Patch Skill Configuration
内核补丁 Skill 配置
"""

import os
import tempfile
from pathlib import PurePosixPath

# Skill 配置
SKILL_NAME = "kernel_patch"
SKILL_VERSION = "3.1.0"

# 默认配置（使用系统临时目录以提高可移植性）
DEFAULT_PATCH_DIR = os.path.join(tempfile.gettempdir(), "patches")
DEFAULT_REJECT_DIR = os.path.join(tempfile.gettempdir(), "rejects")
DEFAULT_TEST_BRANCH_PREFIX = "auto-patch-"

# Git 配置
GIT_AM_TIMEOUT = 300  # 5 分钟

# Config 文件分类
CONFIG_DEFINITION_BASENAMES = {"Kconfig"}
CONFIG_MAPPING_SUFFIXES = (".config", ".cfg")
CONFIG_MAPPING_NAME_PATTERNS = ("defconfig",)


def _basename(path: str) -> str:
    return PurePosixPath(path).name


def is_config_definition_path(path: str) -> bool:
    basename = _basename(path)
    return basename in CONFIG_DEFINITION_BASENAMES or basename.startswith("Kconfig.")


def is_config_mapping_source_path(path: str) -> bool:
    if is_config_definition_path(path):
        return False
    basename = _basename(path)
    lowered = basename.lower()
    return lowered.endswith(CONFIG_MAPPING_SUFFIXES) or any(pattern in lowered for pattern in CONFIG_MAPPING_NAME_PATTERNS)


def is_config_target_path(path: str) -> bool:
    if is_config_definition_path(path):
        return False
    lowered = _basename(path).lower()
    return lowered.endswith(CONFIG_MAPPING_SUFFIXES) or lowered.startswith("config.")

VALIDATION_PASS_STATUSES = {
    "identical",
    "config-mapped-equivalent",
}

VALIDATION_STOP_STATUSES = {
    "missing-hunk",
    "different",
    "semantic-substitution-suspected",
    "config-mapped-incomplete",
    "config-target-missing",
    "config-unmapped",
}

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
