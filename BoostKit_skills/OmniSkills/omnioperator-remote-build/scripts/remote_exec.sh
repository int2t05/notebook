#!/bin/bash

# 通过SSH在远程服务器上执行指定命令
# 用法: ./remote_exec.sh [选项] [命令]
# 配置优先级: 命令行参数 > config.ini > 默认值

# 加载公共函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 默认配置
DEFAULT_REMOTE_HOST="remote_host"
DEFAULT_REMOTE_USER="username"
DEFAULT_REMOTE_PASSWORD="password"
DEFAULT_REMOTE_PORT="ssh_port"
DEFAULT_COMMAND=""
DEFAULT_VERBOSE="false"
DEFAULT_KEEP_ALIVE="false"

# 显示使用说明
show_usage() {
    echo -e "${YELLOW}远程命令执行脚本使用说明:${NC}"
    echo "用法: $0 [选项] [命令]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -H, --host HOST         远程主机地址"
    echo "  -u, --user USER         远程用户名"
    echo "  -p, --port PORT         SSH端口 (默认: 22)"
    echo "  -w, --password PWD      SSH密码"
    echo "  -i, --identity FILE     SSH私钥文件"
    echo "  -c, --config FILE       指定配置文件路径"
    echo "  -v, --verbose           显示详细信息"
    echo "  -k, --keep-alive        保持连接，支持交互式命令"
    echo "  -t, --task TASK         执行预定义任务"
    echo "  --list-tasks            列出所有可用任务"
    echo ""
    echo "示例:"
    echo "  $0                                    # 执行配置文件中的默认命令"
    echo "  $0 'ls -la'                          # 执行简单命令"
    echo "  $0 'cd /var/log && tail -f syslog'  # 执行复合命令"
    echo "  $0 -k 'top'                         # 执行交互式命令"
    echo "  $0 -t sysinfo                       # 执行预定义任务"
    echo "  $0 -t diskinfo                      # 执行磁盘信息任务"
    echo "  $0 -H 192.168.1.100 -u admin 'ps aux' # 指定主机和用户"
    echo "  $0 --create-config                  # 创建示例配置文件"
    echo ""
    echo "配置优先级: 命令行参数 > config.ini > 默认值"
}

# 读取配置文件（仅读取 exec 段，remote 段由 common.sh 的 read_remote_config 处理）
read_exec_config() {
    local config_file="$1"

    if [[ ! -f "$config_file" ]]; then
        return 1
    fi

    echo -e "${BLUE}读取配置文件: $config_file${NC}"

    read_remote_config "$config_file"

    CONFIG_VERBOSE=$(grep -E "^verbose\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_KEEP_ALIVE=$(grep -E "^keep_alive\s*=" "$config_file" | cut -d'=' -f2 | tr -d ' ')
    CONFIG_COMMAND=$(grep -E "^command\s*=" "$config_file" | cut -d'=' -f2- | sed 's/^[[:space:]]*//')

    return 0
}

# 创建示例配置文件
create_sample_config() {
    local config_file="$1"

    cat > "$config_file" << EOF
# 统一配置文件 (SSH、Rsync和远程执行共用)
# 配置优先级: 命令行参数 > config.ini > 默认值

[remote]
host=$DEFAULT_REMOTE_HOST
user=$DEFAULT_REMOTE_USER
password=$DEFAULT_REMOTE_PASSWORD
port=$DEFAULT_REMOTE_PORT

[sync]
source_path=.
target_path=/home/code/
exclude_file=
delete_mode=false
dry_run=false
verbose=false

[ssh]
verbose=false

[exec]
verbose=$DEFAULT_VERBOSE
keep_alive=$DEFAULT_KEEP_ALIVE
command=ls -la
task_sysinfo=echo "=== 系统信息 ===" && hostname && whoami && date && uptime
task_diskinfo=echo "=== 磁盘使用情况 ===" && df -h
task_meminfo=echo "=== 内存使用情况 ===" && free -h
task_procinfo=echo "=== 进程信息 ===" && ps aux | head -10
task_netinfo=echo "=== 网络信息 ===" && netstat -tuln | head -10
task_logcheck=echo "=== 系统日志 ===" && tail -20 /var/log/syslog 2>/dev/null || tail -20 /var/log/messages 2>/dev/null || echo "无法访问系统日志"
EOF

    echo -e "${GREEN}已创建示例配置文件: $config_file${NC}"
}

# 显示执行信息
show_exec_info() {
    echo -e "${GREEN}=== 远程命令执行配置信息 ===${NC}"
    echo "远程主机: $REMOTE_HOST"
    echo "远程用户: $REMOTE_USER"
    echo "远程端口: $REMOTE_PORT"
    echo "认证方式: $([ "$USE_PASSWORD" == true ] && echo "密码" || echo "SSH密钥 ($SSH_KEY_FILE)")"
    echo "详细模式: $([ "$VERBOSE" == true ] && echo "启用" || echo "禁用")"
    echo "保持连接: $([ "$KEEP_ALIVE" == true ] && echo "启用" || echo "禁用")"

    if [[ -n "$COMMAND" ]]; then
        echo "执行命令: $COMMAND"
    elif [[ -n "$TASK_NAME" ]]; then
        echo "执行任务: $TASK_NAME"
    fi

    echo -e "${GREEN}================================${NC}"
}

# 执行远程命令
execute_remote_command() {
    local ssh_options="-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -p $REMOTE_PORT"
    local ssh_cmd=""

    if [[ "$USE_PASSWORD" == false ]]; then
        ssh_options="$ssh_options -i $SSH_KEY_FILE"
    fi

    if [[ "$VERBOSE" == true ]]; then
        ssh_options="$ssh_options -v"
    fi

    if [[ "$USE_PASSWORD" == true ]]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$MSYSTEM" ]]; then
            echo -e "${YELLOW}检测到Windows/Git Bash环境${NC}"
            echo -e "${YELLOW}sshpass在Windows下不兼容，将使用手动密码输入${NC}"
            ssh_cmd="ssh $ssh_options $REMOTE_USER@$REMOTE_HOST"
        elif check_and_install_sshpass; then
            ssh_cmd="sshpass -e ssh $ssh_options $REMOTE_USER@$REMOTE_HOST"
        else
            echo -e "${YELLOW}无法使用sshpass，将使用手动密码输入${NC}"
            ssh_cmd="ssh $ssh_options $REMOTE_USER@$REMOTE_HOST"
        fi
    else
        ssh_cmd="ssh $ssh_options $REMOTE_USER@$REMOTE_HOST"
    fi

    echo -e "${CYAN}开始执行远程命令...${NC}"
    echo -e "${YELLOW}提示: 使用 Ctrl+C 可以中断命令执行${NC}"
    echo ""

    local wrapped_command="bash -l -c \"$COMMAND\""

    if [[ "$USE_PASSWORD" == true && -n "$REMOTE_PASSWORD" ]]; then
        export SSHPASS="$REMOTE_PASSWORD"
    fi

    if [[ "$KEEP_ALIVE" == true ]]; then
        echo -e "${BLUE}进入交互模式，执行命令: $COMMAND${NC}"
        eval "$ssh_cmd -t" '"$wrapped_command"'
    else
        echo -e "${BLUE}执行命令: $COMMAND${NC}"
        eval "$ssh_cmd" '"$wrapped_command"'
    fi

    unset SSHPASS

    local exit_code=$?
    echo ""

    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}远程命令执行完成${NC}"
    else
        echo -e "${RED}远程命令执行失败 (退出码: $exit_code)${NC}"
    fi

    return $exit_code
}

# 主函数
main() {
    REMOTE_HOST="$DEFAULT_REMOTE_HOST"
    REMOTE_USER="$DEFAULT_REMOTE_USER"
    REMOTE_PASSWORD="$DEFAULT_REMOTE_PASSWORD"
    REMOTE_PORT="$DEFAULT_REMOTE_PORT"
    COMMAND="$DEFAULT_COMMAND"
    VERBOSE="$DEFAULT_VERBOSE"
    KEEP_ALIVE="$DEFAULT_KEEP_ALIVE"
    SSH_KEY_FILE=""
    USE_PASSWORD=true
    TASK_NAME=""
    CUSTOM_CONFIG_FILE=""

    local cmd_host=""
    local cmd_user=""
    local cmd_password=""
    local cmd_port=""
    local cmd_verbose=""
    local cmd_keep_alive=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
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
            -c|--config)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -c/--config 需要指定配置文件路径${NC}"; exit 1; }
                CUSTOM_CONFIG_FILE="$2"; shift 2
                ;;
            -v|--verbose)
                VERBOSE=true; cmd_verbose=true; shift
                ;;
            -k|--keep-alive)
                KEEP_ALIVE=true; cmd_keep_alive=true; shift
                ;;
            -t|--task)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -t/--task 需要指定任务名称${NC}"; exit 1; }
                TASK_NAME="$2"; shift 2
                ;;
            --create-config)
                create_sample_config "$CONFIG_FILE"; exit 0
                ;;
            --list-tasks)
                local config_to_use="$CONFIG_FILE"
                [[ -n "$CUSTOM_CONFIG_FILE" ]] && config_to_use="$CUSTOM_CONFIG_FILE"

                if [[ -f "$config_to_use" ]]; then
                    echo -e "${YELLOW}可用的预定义任务:${NC}"
                    local tasks=$(list_task_names "$config_to_use")
                    if [[ -z "$tasks" ]]; then
                        echo "  (无预定义任务)"
                    else
                        echo "$tasks" | while read -r task; do
                            get_task_command "$config_to_use" "$task"
                            echo -e "  ${GREEN}$task${NC}: $TASK_COMMAND"
                        done
                    fi
                    echo ""
                    local default_cmd=$(grep -E "^command\s*=" "$config_to_use" | cut -d'=' -f2- | sed 's/^[[:space:]]*//')
                    if [[ -n "$default_cmd" ]]; then
                        echo -e "${YELLOW}默认命令:${NC} $default_cmd"
                    fi
                else
                    echo -e "${RED}无法读取配置文件: $config_to_use${NC}"
                fi
                exit 0
                ;;
            -*)
                echo -e "${RED}未知选项: $1${NC}"; show_usage; exit 1
                ;;
            *)
                COMMAND="$*"; break
                ;;
        esac
    done

    local config_to_use="$CONFIG_FILE"
    [[ -n "$CUSTOM_CONFIG_FILE" ]] && config_to_use="$CUSTOM_CONFIG_FILE"

    if read_exec_config "$config_to_use"; then
        [[ -z "$cmd_host" && -n "$CONFIG_HOST" ]] && REMOTE_HOST="$CONFIG_HOST"
        [[ -z "$cmd_user" && -n "$CONFIG_USER" ]] && REMOTE_USER="$CONFIG_USER"
        [[ -z "$cmd_password" && -n "$CONFIG_PASSWORD" ]] && REMOTE_PASSWORD="$CONFIG_PASSWORD"
        [[ -z "$cmd_port" && -n "$CONFIG_PORT" ]] && REMOTE_PORT="$CONFIG_PORT"
        [[ -z "$cmd_verbose" && "$CONFIG_VERBOSE" == "true" ]] && VERBOSE=true
        [[ -z "$cmd_keep_alive" && "$CONFIG_KEEP_ALIVE" == "true" ]] && KEEP_ALIVE=true

        [[ -z "$COMMAND" && -z "$TASK_NAME" && -n "$CONFIG_COMMAND" ]] && COMMAND="$CONFIG_COMMAND"
    fi

    if [[ -n "$TASK_NAME" ]]; then
        if get_task_command "$config_to_use" "$TASK_NAME"; then
            COMMAND="$TASK_COMMAND"
            echo -e "${BLUE}选择任务: $TASK_NAME${NC}"
        else
            echo -e "${RED}错误: 未找到任务 '$TASK_NAME'${NC}"
            echo -e "${YELLOW}可用任务:${NC}"
            list_task_names "$config_to_use" | while read -r task; do
                echo "  - $task"
            done
            exit 1
        fi
    fi

    if [[ -z "$REMOTE_HOST" || -z "$REMOTE_USER" ]]; then
        echo -e "${RED}错误: 缺少必需参数 (主机和用户)${NC}"
        show_usage; exit 1
    fi

    if [[ -z "$COMMAND" ]]; then
        echo -e "${RED}错误: 必须指定要执行的命令或任务${NC}"
        show_usage; exit 1
    fi

    if [[ "$USE_PASSWORD" == false && ! -f "$SSH_KEY_FILE" ]]; then
        echo -e "${RED}错误: SSH密钥文件不存在: $SSH_KEY_FILE${NC}"
        exit 1
    fi

    show_exec_info
    execute_remote_command
    local exit_code=$?

    echo -e "${GREEN}返回本地控制台${NC}"
    exit $exit_code
}

main "$@"
