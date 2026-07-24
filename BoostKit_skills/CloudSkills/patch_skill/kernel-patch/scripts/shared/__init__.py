"""
Shared modules for kernel_patch skill
内核补丁 Skill 的共享模块
"""

from .config import (
    SKILL_NAME,
    SKILL_VERSION,
    DEFAULT_PATCH_DIR,
    DEFAULT_REJECT_DIR,
    DEFAULT_TEST_BRANCH_PREFIX,
    GIT_AM_TIMEOUT,
    CONFIG_DEFINITION_BASENAMES,
    CONFIG_MAPPING_SUFFIXES,
    CONFIG_MAPPING_NAME_PATTERNS,
    is_config_definition_path,
    is_config_mapping_source_path,
    is_config_target_path,
    VALIDATION_PASS_STATUSES,
    VALIDATION_STOP_STATUSES,
    LOG_LEVEL,
    LOG_FORMAT
)

from .git_helpers import branch_exists, is_git_repo, get_commit_message, safe_git_command
from .paths import resolve_user_path, to_repo_relative, normalize_repo_paths
from .cli import emit_json, load_json_arg, load_json_file, exit_with_json
__all__ = [
    # Config
    'SKILL_NAME',
    'SKILL_VERSION',
    'DEFAULT_PATCH_DIR',
    'DEFAULT_REJECT_DIR',
    'DEFAULT_TEST_BRANCH_PREFIX',
    'GIT_AM_TIMEOUT',
    'CONFIG_DEFINITION_BASENAMES',
    'CONFIG_MAPPING_SUFFIXES',
    'CONFIG_MAPPING_NAME_PATTERNS',
    'is_config_definition_path',
    'is_config_mapping_source_path',
    'is_config_target_path',
    'VALIDATION_PASS_STATUSES',
    'VALIDATION_STOP_STATUSES',
    'LOG_LEVEL',
    'LOG_FORMAT',
    # Git helpers
    'branch_exists',
    'is_git_repo',
    'get_commit_message',
    'safe_git_command',
    # Paths
    'resolve_user_path',
    'to_repo_relative',
    'normalize_repo_paths',
    # CLI
    'emit_json',
    'load_json_arg',
    'load_json_file',
    'exit_with_json',
]
