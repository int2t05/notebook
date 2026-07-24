#!/bin/bash

# 通过rsync将本地代码同步到远程服务器
# 用法: ./rsync_sync.sh [选项] [源路径] [目标路径]
# 配置优先级: 命令行参数 > config.ini > 默认值

# 加载公共函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 默认配置
DEFAULT_REMOTE_HOST="remote_host"
DEFAULT_REMOTE_USER="username"
DEFAULT_REMOTE_PASSWORD="password"
DEFAULT_REMOTE_PORT="ssh_port"
DEFAULT_SOURCE_PATH="."
DEFAULT_TARGET_PATH="/home/code/"
DEFAULT_EXCLUDE_FILE=""
DEFAULT_DELETE_MODE="false"
DEFAULT_DRY_RUN="false"
DEFAULT_VERBOSE="false"

# 显示使用说明
show_usage() {
    echo -e "${YELLOW}Rsync代码同步脚本使用说明:${NC}"
    echo "用法: $0 [选项] [源路径] [目标路径]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -H, --host HOST         远程主机地址"
    echo "  -u, --user USER         远程用户名"
    echo "  -p, --port PORT         SSH端口 (默认: 22)"
    echo "  -w, --password PWD      SSH密码"
    echo "  -i, --identity FILE     SSH私钥文件"
    echo "  -s, --source PATH       源路径 (本地路径)"
    echo "  -t, --target PATH       目标路径 (远程路径)"
    echo "  -e, --exclude FILE      排除文件列表"
    echo "  -d, --delete            删除目标中多余的文件"
    echo "  -n, --dry-run           预演模式，不实际执行"
    echo "  -v, --verbose           显示详细信息"
    echo "  -c, --config FILE       指定配置文件路径"
    echo ""
    echo "配置优先级: 命令行参数 > config.ini > 默认值"
}

# 读取配置文件
read_sync_config() {
    local config_file="$1"

    if [[ ! -f "$config_file" ]]; then
        return 1
    fi

    echo -e "${BLUE}读取配置文件: $config_file${NC}"

    read_remote_config "$config_file"

    CONFIG_SOURCE_PATH=$(grep -E "^source_path\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_TARGET_PATH=$(grep -E "^target_path\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_EXCLUDE_FILE=$(grep -E "^exclude_file\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_DELETE_MODE=$(grep -E "^delete_mode\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_DRY_RUN=$(grep -E "^dry_run\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_VERBOSE=$(grep -E "^verbose\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')

    return 0
}

# 自动安装rsync和sshpass
install_dependencies() {
    local pkg_manager=$(detect_package_manager)
    local missing_packages=()

    if ! command -v rsync &> /dev/null; then
        missing_packages+=("rsync")
    fi

    if [[ "$USE_PASSWORD" == true ]] && ! command -v sshpass &> /dev/null; then
        missing_packages+=("sshpass")
    fi

    if [[ ${#missing_packages[@]} -eq 0 ]]; then
        return 0
    fi

    echo -e "${YELLOW}正在安装依赖包: ${missing_packages[*]}...${NC}"

    case $pkg_manager in
        "apt")
            sudo apt-get update && sudo apt-get install -y "${missing_packages[@]}"
            ;;
        "yum")
            sudo yum install -y "${missing_packages[@]}"
            ;;
        "dnf")
            sudo dnf install -y "${missing_packages[@]}"
            ;;
        "brew")
            brew install "${missing_packages[@]}"
            ;;
        *)
            echo -e "${RED}错误: 未识别的包管理器，请手动安装: ${missing_packages[*]}${NC}"
            return 1
            ;;
    esac

    for package in "${missing_packages[@]}"; do
        if ! command -v "$package" &> /dev/null; then
            echo -e "${RED}$package 安装失败${NC}"
            return 1
        fi
    done

    echo -e "${GREEN}依赖包安装成功${NC}"
    return 0
}

# 创建示例配置文件
create_sample_config() {
    local config_file="$1"

    cat > "$config_file" << EOF
# Rsync同步配置文件
# 配置优先级: 命令行参数 > config.ini > 默认值

[remote]
host=$DEFAULT_REMOTE_HOST
user=$DEFAULT_REMOTE_USER
password=$DEFAULT_REMOTE_PASSWORD
port=$DEFAULT_REMOTE_PORT

[sync]
source_path=$DEFAULT_SOURCE_PATH
target_path=$DEFAULT_TARGET_PATH
exclude_file=$DEFAULT_EXCLUDE_FILE
delete_mode=$DEFAULT_DELETE_MODE
dry_run=$DEFAULT_DRY_RUN
verbose=$DEFAULT_VERBOSE
EOF

    echo -e "${GREEN}已创建示例配置文件: $config_file${NC}"
}

# 验证路径
validate_paths() {
    if [[ ! -e "$SOURCE_PATH" ]]; then
        echo -e "${RED}错误: 源路径不存在: $SOURCE_PATH${NC}"
        return 1
    fi
    if [[ -n "$EXCLUDE_FILE" && ! -f "$EXCLUDE_FILE" ]]; then
        echo -e "${RED}错误: 排除文件不存在: $EXCLUDE_FILE${NC}"
        return 1
    fi
    if [[ "$USE_PASSWORD" == false && ! -f "$SSH_KEY_FILE" ]]; then
        echo -e "${RED}错误: SSH密钥文件不存在: $SSH_KEY_FILE${NC}"
        return 1
    fi
    return 0
}

# 执行rsync同步
execute_rsync() {
    local rsync_opts="-avz"

    [[ "$DELETE_MODE" == true ]] && rsync_opts="${rsync_opts} --delete"
    [[ "$DRY_RUN" == true ]] && rsync_opts="${rsync_opts} --dry-run"

    local exclude_opt=""
    [[ -n "$EXCLUDE_FILE" ]] && exclude_opt="--exclude-from=${EXCLUDE_FILE}"

    export RSYNC_RSH="ssh -o StrictHostKeyChecking=accept-new -p ${REMOTE_PORT}"
    if [[ "$USE_PASSWORD" == false ]]; then
        export RSYNC_RSH="${RSYNC_RSH} -i ${SSH_KEY_FILE}"
    fi

    echo -e "${BLUE}执行命令:${NC}"
    if [[ "$USE_PASSWORD" == true ]]; then
        echo "RSYNC_RSH=\"${RSYNC_RSH}\" sshpass -e rsync ${rsync_opts} ${exclude_opt} ${SOURCE_PATH} ${REMOTE_USER}@${REMOTE_HOST}:${TARGET_PATH}"
    else
        echo "RSYNC_RSH=\"${RSYNC_RSH}\" rsync ${rsync_opts} ${exclude_opt} ${SOURCE_PATH} ${REMOTE_USER}@${REMOTE_HOST}:${TARGET_PATH}"
    fi
    echo ""

    local exit_code
    if [[ "$USE_PASSWORD" == true && -n "$REMOTE_PASSWORD" ]]; then
        export SSHPASS="$REMOTE_PASSWORD"
    fi

    if [[ "$USE_PASSWORD" == true ]]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$MSYSTEM" ]]; then
            echo -e "${YELLOW}检测到Windows/Git Bash环境${NC}"
            echo -e "${YELLOW}sshpass在Windows下不兼容，rsync将提示输入密码${NC}"
            echo -e "${GREEN}推荐: 配置SSH密钥实现免密同步 (运行: ./ssh_connect.sh --setup-key)${NC}"
            echo ""
            MSYS_NO_PATHCONV=1 rsync ${rsync_opts} ${exclude_opt} "${SOURCE_PATH}" "${REMOTE_USER}@${REMOTE_HOST}:${TARGET_PATH}"
            exit_code=$?
        else
            MSYS_NO_PATHCONV=1 sshpass -e rsync ${rsync_opts} ${exclude_opt} "${SOURCE_PATH}" "${REMOTE_USER}@${REMOTE_HOST}:${TARGET_PATH}"
            exit_code=$?
        fi
    else
        MSYS_NO_PATHCONV=1 rsync ${rsync_opts} ${exclude_opt} "${SOURCE_PATH}" "${REMOTE_USER}@${REMOTE_HOST}:${TARGET_PATH}"
        exit_code=$?
    fi

    unset SSHPASS
    return $exit_code
}

# 显示同步信息
show_sync_info() {
    echo -e "${GREEN}=== Rsync同步配置信息 ===${NC}"
    echo "远程主机: $REMOTE_HOST"
    echo "远程用户: $REMOTE_USER"
    echo "远程端口: $REMOTE_PORT"
    echo "认证方式: $([ "$USE_PASSWORD" == true ] && echo "密码" || echo "SSH密钥 ($SSH_KEY_FILE)")"
    echo "源路径: $SOURCE_PATH"
    echo "目标路径: $TARGET_PATH"
    echo "删除模式: $([ "$DELETE_MODE" == true ] && echo "启用" || echo "禁用")"
    echo "预演模式: $([ "$DRY_RUN" == true ] && echo "启用" || echo "禁用")"
    echo "详细模式: $([ "$VERBOSE" == true ] && echo "启用" || echo "禁用")"
    [[ -n "$EXCLUDE_FILE" ]] && echo "排除文件: $EXCLUDE_FILE"
    echo -e "${GREEN}================================${NC}"
}

# 主函数
main() {
    REMOTE_HOST="$DEFAULT_REMOTE_HOST"
    REMOTE_USER="$DEFAULT_REMOTE_USER"
    REMOTE_PASSWORD="$DEFAULT_REMOTE_PASSWORD"
    REMOTE_PORT="$DEFAULT_REMOTE_PORT"
    SOURCE_PATH="$DEFAULT_SOURCE_PATH"
    TARGET_PATH="$DEFAULT_TARGET_PATH"
    EXCLUDE_FILE="$DEFAULT_EXCLUDE_FILE"
    DELETE_MODE="$DEFAULT_DELETE_MODE"
    DRY_RUN="$DEFAULT_DRY_RUN"
    VERBOSE="$DEFAULT_VERBOSE"
    SSH_KEY_FILE=""
    USE_PASSWORD=true
    CUSTOM_CONFIG_FILE=""

    local cmd_host=""
    local cmd_user=""
    local cmd_password=""
    local cmd_port=""
    local cmd_source=""
    local cmd_target=""
    local cmd_verbose=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage; exit 0
                ;;
            -H|--host)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -H/--host 需要指定主机地址${NC}"; exit 1; }
                REMOTE_HOST="$2"; cmd_host="$2"; shift 2
                ;;
            -u|--user)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -u/--user 需要指定用户名${NC}"; exit 1; }
                REMOTE_USER="$2"; cmd_user="$2"; shift 2
                ;;
            -p|--port)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -p/--port 需要指定端口号${NC}"; exit 1; }
                REMOTE_PORT="$2"; cmd_port="$2"; shift 2
                ;;
            -w|--password)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -w/--password 需要指定密码${NC}"; exit 1; }
                REMOTE_PASSWORD="$2"; cmd_password="$2"; USE_PASSWORD=true; shift 2
                ;;
            -i|--identity)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -i/--identity 需要指定密钥文件路径${NC}"; exit 1; }
                SSH_KEY_FILE="$2"; USE_PASSWORD=false; shift 2
                ;;
            -s|--source)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -s/--source 需要指定源路径${NC}"; exit 1; }
                SOURCE_PATH="$2"; cmd_source="$2"; shift 2
                ;;
            -t|--target)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -t/--target 需要指定目标路径${NC}"; exit 1; }
                TARGET_PATH="$2"; cmd_target="$2"; shift 2
                ;;
            -e|--exclude)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -e/--exclude 需要指定排除文件路径${NC}"; exit 1; }
                EXCLUDE_FILE="$2"; shift 2
                ;;
            -d|--delete)
                DELETE_MODE=true; shift
                ;;
            -n|--dry-run)
                DRY_RUN=true; shift
                ;;
            -v|--verbose)
                VERBOSE=true; cmd_verbose=true; shift
                ;;
            -c|--config)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -c/--config 需要指定配置文件路径${NC}"; exit 1; }
                CUSTOM_CONFIG_FILE="$2"; shift 2
                ;;
            --create-config)
                create_sample_config "$CONFIG_FILE"; exit 0
                ;;
            -*)
                echo -e "${RED}未知选项: $1${NC}"; show_usage; exit 1
                ;;
            *)
                if [[ -z "$POSITIONAL_SOURCE" ]]; then
                    POSITIONAL_SOURCE="$1"
                elif [[ -z "$POSITIONAL_TARGET" ]]; then
                    POSITIONAL_TARGET="$1"
                else
                    echo -e "${RED}错误: 过多的位置参数${NC}"; show_usage; exit 1
                fi
                shift
                ;;
        esac
    done

    local config_to_use="$CONFIG_FILE"
    [[ -n "$CUSTOM_CONFIG_FILE" ]] && config_to_use="$CUSTOM_CONFIG_FILE"

    if read_sync_config "$config_to_use"; then
        [[ -z "$cmd_host" && -n "$CONFIG_HOST" ]] && REMOTE_HOST="$CONFIG_HOST"
        [[ -z "$cmd_user" && -n "$CONFIG_USER" ]] && REMOTE_USER="$CONFIG_USER"
        [[ -z "$cmd_password" && -n "$CONFIG_PASSWORD" ]] && REMOTE_PASSWORD="$CONFIG_PASSWORD"
        [[ -z "$cmd_port" && -n "$CONFIG_PORT" ]] && REMOTE_PORT="$CONFIG_PORT"
        [[ -z "$cmd_source" && -n "$CONFIG_SOURCE_PATH" ]] && SOURCE_PATH="$CONFIG_SOURCE_PATH"
        [[ -z "$cmd_target" && -n "$CONFIG_TARGET_PATH" ]] && TARGET_PATH="$CONFIG_TARGET_PATH"
        [[ -z "$cmd_verbose" && "$CONFIG_VERBOSE" == "true" ]] && VERBOSE=true
        [[ -n "$CONFIG_EXCLUDE_FILE" && -z "$EXCLUDE_FILE" ]] && EXCLUDE_FILE="$CONFIG_EXCLUDE_FILE"
        [[ "$CONFIG_DELETE_MODE" == "true" && "$DELETE_MODE" == "$DEFAULT_DELETE_MODE" ]] && DELETE_MODE=true
        [[ "$CONFIG_DRY_RUN" == "true" && "$DRY_RUN" == "$DEFAULT_DRY_RUN" ]] && DRY_RUN=true
    fi

    [[ -n "$POSITIONAL_SOURCE" ]] && SOURCE_PATH="$POSITIONAL_SOURCE"
    [[ -n "$POSITIONAL_TARGET" ]] && TARGET_PATH="$POSITIONAL_TARGET"

    if [[ -z "$REMOTE_HOST" || -z "$REMOTE_USER" || -z "$SOURCE_PATH" || -z "$TARGET_PATH" ]]; then
        echo -e "${RED}错误: 缺少必需参数${NC}"; show_usage; exit 1
    fi

    if ! validate_paths; then
        exit 1
    fi

    if ! install_dependencies; then
        echo -e "${RED}依赖安装失败，无法继续${NC}"; exit 1
    fi

    show_sync_info
    echo -e "${GREEN}开始同步...${NC}"

    execute_rsync
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            echo -e "${GREEN}预演完成 - 以上是将要同步的文件${NC}"
        else
            echo -e "${GREEN}同步完成${NC}"

            # 仅在 Windows 环境下执行 dos2unix
            if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$MSYSTEM" ]]; then
                echo -e "${BLUE}正在转换.sh文件的换行符...${NC}"
                local dos2unix_cmd="cd ${TARGET_PATH} && find . -name '*.sh' -type f -exec dos2unix {} \;"
                ssh -o StrictHostKeyChecking=accept-new -p "${REMOTE_PORT}" "${REMOTE_USER}@${REMOTE_HOST}" "$dos2unix_cmd"
                if [[ $? -eq 0 ]]; then
                    echo -e "${GREEN}换行符转换完成${NC}"
                else
                    echo -e "${YELLOW}警告: 换行符转换失败，请检查远程服务器是否安装了dos2unix${NC}"
                fi
            fi
        fi
    else
        echo -e "${RED}同步失败 (退出码: $exit_code)${NC}"
        exit $exit_code
    fi
}

main "$@"
