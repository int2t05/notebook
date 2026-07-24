#!/bin/bash

# 公共函数库 - 由 rsync_sync.sh / remote_exec.sh / ssh_connect.sh 共享
# 不要直接运行此文件

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置文件路径（基于调用者脚本所在目录）
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
CONFIG_FILE="$_SCRIPT_DIR/config.ini"

# 检测系统包管理器
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v brew &> /dev/null; then
        echo "brew"
    else
        echo "unknown"
    fi
}

# 自动安装sshpass
install_sshpass() {
    local pkg_manager=$(detect_package_manager)

    echo -e "${YELLOW}正在安装sshpass...${NC}"

    case $pkg_manager in
        "apt")
            sudo apt-get update && sudo apt-get install -y sshpass
            ;;
        "yum")
            sudo yum install -y sshpass
            ;;
        "dnf")
            sudo dnf install -y sshpass
            ;;
        "brew")
            brew install hudochenkov/sshpass/sshpass
            ;;
        *)
            echo -e "${RED}错误: 未识别的包管理器，请手动安装sshpass${NC}"
            return 1
            ;;
    esac

    if command -v sshpass &> /dev/null; then
        echo -e "${GREEN}sshpass安装成功${NC}"
        return 0
    else
        echo -e "${RED}sshpass安装失败${NC}"
        return 1
    fi
}

# 检查并安装sshpass
check_and_install_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        echo -e "${YELLOW}未找到sshpass，正在尝试自动安装...${NC}"
        if install_sshpass; then
            return 0
        else
            echo -e "${RED}自动安装失败，请手动安装sshpass${NC}"
            return 1
        fi
    fi
    return 0
}

# 从 config.ini 读取 [remote] 段的基础连接信息
# 输出变量：CONFIG_HOST, CONFIG_USER, CONFIG_PASSWORD, CONFIG_PORT
read_remote_config() {
    local config_file="$1"

    if [[ ! -f "$config_file" ]]; then
        return 1
    fi

    CONFIG_HOST=$(grep -E "^host\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_USER=$(grep -E "^user\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_PASSWORD=$(grep -E "^password\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_PORT=$(grep -E "^port\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')

    return 0
}

# 从 config.ini 获取指定任务的命令内容（兼容 Bash 3.x，无需关联数组）
# 用法: get_task_command <config_file> <task_name>
# 返回: 通过全局变量 TASK_COMMAND 输出结果
get_task_command() {
    local config_file="$1"
    local task_name="$2"
    TASK_COMMAND=""

    if [[ ! -f "$config_file" ]]; then
        return 1
    fi

    local current_value=""
    local in_multiline=false
    local found=false

    while IFS= read -r line; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue

        if [[ "$line" =~ ^task_${task_name}[[:space:]]*= ]]; then
            found=true
            current_value=$(echo "$line" | cut -d'=' -f2- | sed 's/^[[:space:]]*//')
            if [[ "$current_value" =~ \\[[:space:]]*$ ]]; then
                current_value="${current_value%\\*}"
                in_multiline=true
            else
                in_multiline=false
            fi
        elif [[ "$found" == true && "$in_multiline" == true ]]; then
            local line_content=$(echo "$line" | sed 's/^[[:space:]]*//')
            if [[ "$line_content" =~ \\[[:space:]]*$ ]]; then
                current_value="$current_value ${line_content%\\*}"
            else
                current_value="$current_value $line_content"
                in_multiline=false
                break
            fi
        fi
    done < "$config_file"

    if [[ "$found" == true ]]; then
        TASK_COMMAND="$current_value"
        return 0
    fi
    return 1
}

# 列出 config.ini 中所有预定义任务名（兼容 Bash 3.x）
# 用法: list_task_names <config_file>
# 输出: 每行一个任务名
list_task_names() {
    local config_file="$1"

    if [[ ! -f "$config_file" ]]; then
        return 1
    fi

    grep -oE '^task_[a-zA-Z0-9_]+' "$config_file" | sed 's/^task_//'
}
