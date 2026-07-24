#!/bin/bash

# 建立SSH连接到远程服务器
# 用法: ./ssh_connect.sh [用户名@主机] [密码]

# 加载公共函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 默认连接参数
DEFAULT_REMOTE_HOST="remote_host"
DEFAULT_USER="username"
DEFAULT_PASSWORD="password"
DEFAULT_REMOTE_PORT="ssh_port"

# 显示使用说明
show_usage() {
    echo -e "${YELLOW}SSH连接脚本使用说明:${NC}"
    echo "用法: $0 [选项] [用户名@主机] [密码]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -p, --port PORT     指定SSH端口 (默认: 22)"
    echo "  -w, --password PWD  指定连接密码"
    echo "  -i, --identity FILE 使用SSH私钥文件进行认证"
    echo "  -v, --verbose       显示详细连接信息"
    echo "  -c, --config FILE   指定配置文件路径"
    echo "  --setup-key         配置SSH密钥免密登录"
    echo ""
    echo "示例:"
    echo "  $0                                    # 使用默认配置连接"
    echo "  $0 user@192.168.1.100                # 连接到指定主机"
    echo "  $0 -p 2222 user@example.com          # 使用自定义端口"
    echo "  $0 -i ~/.ssh/id_rsa user@example.com # 使用SSH密钥认证"
    echo "  $0 --setup-key                       # 配置SSH密钥免密登录"
    echo ""
    echo "配置优先级: 命令行参数 > config.ini > 默认值"
}

# 生成并配置SSH密钥
setup_ssh_key() {
    local user="$1"
    local host="$2"
    local port="$3"
    local password="$4"

    local ssh_dir="$HOME/.ssh"
    local key_file="$ssh_dir/id_rsa"

    echo -e "${BLUE}=== SSH密钥免密登录配置 ===${NC}"

    if [[ ! -d "$ssh_dir" ]]; then
        mkdir -p "$ssh_dir"
        chmod 700 "$ssh_dir"
        echo -e "${GREEN}已创建 .ssh 目录${NC}"
    fi

    if [[ -f "$key_file" ]]; then
        echo -e "${YELLOW}已存在SSH密钥: $key_file${NC}"
        read -p "是否使用现有密钥? (y/n): " use_existing
        if [[ "$use_existing" != "y" && "$use_existing" != "Y" ]]; then
            key_file="$ssh_dir/id_rsa_new"
            echo -e "${BLUE}将生成新密钥: $key_file${NC}"
        fi
    fi

    if [[ ! -f "$key_file" ]]; then
        echo -e "${BLUE}正在生成SSH密钥对...${NC}"
        ssh-keygen -t ed25519 -f "$key_file" -N "" -q
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}SSH密钥生成成功${NC}"
        else
            echo -e "${RED}SSH密钥生成失败${NC}"
            return 1
        fi
    fi

    echo -e "${BLUE}正在配置远程服务器...${NC}"
    echo -e "${YELLOW}需要输入远程服务器密码${NC}"

    local pub_key=$(cat "${key_file}.pub")
    ssh -o StrictHostKeyChecking=accept-new -p "$port" "$user@$host" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$pub_key' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH密钥已添加'"

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}SSH密钥配置成功！${NC}"
        echo -e "${GREEN}现在可以使用以下命令免密登录:${NC}"
        echo -e "${BLUE}  ssh -i $key_file -p $port $user@$host${NC}"
        echo -e "${BLUE}或者使用本脚本: ./ssh_connect.sh -i $key_file${NC}"
        return 0
    else
        echo -e "${RED}SSH密钥配置失败${NC}"
        return 1
    fi
}

# 创建示例配置文件
create_sample_config() {
    local config_file="$1"

    cat > "$config_file" << EOF
# 统一配置文件 (SSH和Rsync共用)
# 配置优先级: 命令行参数 > config.ini > 默认值

[remote]
host=$DEFAULT_REMOTE_HOST
user=$DEFAULT_USER
password=$DEFAULT_PASSWORD
port=$DEFAULT_REMOTE_PORT

[sync]
source_path=.
target_path=/home/omni/
exclude_file=
delete_mode=false
dry_run=false
verbose=false

[ssh]
verbose=false
EOF

    echo -e "${GREEN}已创建示例配置文件: $config_file${NC}"
}

# 主函数
main() {
    local user_host="$DEFAULT_USER@$DEFAULT_REMOTE_HOST"
    local password="$DEFAULT_PASSWORD"
    local port="$DEFAULT_REMOTE_PORT"
    local key_file=""
    local use_password=true
    local verbose=false
    local custom_config_file=""

    local cmd_user_host=""
    local cmd_password=""
    local cmd_port=""
    local cmd_verbose=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage; exit 0
                ;;
            -p|--port)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -p/--port 需要指定端口号${NC}"; exit 1; }
                port="$2"; cmd_port="$2"; shift 2
                ;;
            -w|--password)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -w/--password 需要指定密码${NC}"; exit 1; }
                password="$2"; cmd_password="$2"; use_password=true; shift 2
                ;;
            -i|--identity)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -i/--identity 需要指定密钥文件路径${NC}"; exit 1; }
                key_file="$2"; use_password=false; shift 2
                ;;
            -v|--verbose)
                verbose=true; cmd_verbose=true; shift
                ;;
            -c|--config)
                [[ -z "$2" ]] && { echo -e "${RED}错误: -c/--config 需要指定配置文件路径${NC}"; exit 1; }
                custom_config_file="$2"; shift 2
                ;;
            --create-config)
                create_sample_config "$CONFIG_FILE"; exit 0
                ;;
            --setup-key)
                local config_to_use="$CONFIG_FILE"
                [[ -n "$custom_config_file" ]] && config_to_use="$custom_config_file"

                if read_remote_config "$config_to_use"; then
                    setup_ssh_key "$CONFIG_USER" "$CONFIG_HOST" "${CONFIG_PORT:-22}" "$CONFIG_PASSWORD"
                else
                    echo -e "${YELLOW}未找到配置文件，使用默认配置${NC}"
                    setup_ssh_key "$DEFAULT_USER" "$DEFAULT_REMOTE_HOST" "22" "$DEFAULT_PASSWORD"
                fi
                exit 0
                ;;
            -*)
                echo -e "${RED}未知选项: $1${NC}"; show_usage; exit 1
                ;;
            *)
                if [[ "$1" == *"@"* ]]; then
                    user_host="$1"; cmd_user_host="$1"
                else
                    password="$1"; cmd_password="$1"
                fi
                shift
                ;;
        esac
    done

    local config_to_use="$CONFIG_FILE"
    [[ -n "$custom_config_file" ]] && config_to_use="$custom_config_file"

    if read_remote_config "$config_to_use"; then
        if [[ -z "$cmd_user_host" && -n "$CONFIG_HOST" && -n "$CONFIG_USER" ]]; then
            user_host="$CONFIG_USER@$CONFIG_HOST"
        fi
        [[ -z "$cmd_password" && -n "$CONFIG_PASSWORD" ]] && password="$CONFIG_PASSWORD"
        [[ -z "$cmd_port" && -n "$CONFIG_PORT" ]] && port="$CONFIG_PORT"
        [[ -z "$cmd_verbose" && "$CONFIG_VERBOSE" == "true" ]] && verbose=true
    fi

    local user=$(echo "$user_host" | cut -d'@' -f1)
    local host=$(echo "$user_host" | cut -d'@' -f2)

    if [[ -z "$user" || -z "$host" ]]; then
        echo -e "${RED}错误: 无效的用户名@主机格式${NC}"; show_usage; exit 1
    fi

    echo -e "${GREEN}正在连接到服务器...${NC}"
    echo "用户: $user"
    echo "主机: $host"
    echo "端口: $port"

    # 检查网络连通性
    echo -e "${BLUE}检查网络连通性...${NC}"
    if command -v nc &> /dev/null; then
        if nc -zv "$host" "$port" 2>&1 | grep -q -e "succeeded" -e "open"; then
            echo -e "${GREEN}端口 $port 可达${NC}"
        else
            echo -e "${RED}无法连接到 $host:$port${NC}"
            echo -e "${YELLOW}请检查: 1) 主机IP是否正确 2) 网络是否连通 3) 防火墙设置${NC}"
        fi
    fi

    if [[ "$verbose" == true ]]; then
        echo "完整连接字符串: $user@$host:$port"
    fi

    local ssh_opts="-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=3 -p $port"

    if [[ "$use_password" == true ]]; then
        echo "认证方式: 密码"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$MSYSTEM" ]]; then
            echo -e "${YELLOW}检测到Windows/Git Bash环境${NC}"
            echo -e "${GREEN}推荐: 使用SSH密钥实现免密登录 (运行: ./ssh_connect.sh --setup-key)${NC}"
            echo -e "${YELLOW}请手动输入密码${NC}"
            if [[ "$verbose" == true ]]; then
                ssh -v $ssh_opts "$user@$host"
            else
                ssh $ssh_opts "$user@$host"
            fi
        elif check_and_install_sshpass; then
            export SSHPASS="$password"
            if [[ "$verbose" == true ]]; then
                sshpass -e ssh -v $ssh_opts "$user@$host"
            else
                sshpass -e ssh $ssh_opts "$user@$host"
            fi
            unset SSHPASS
        else
            echo -e "${YELLOW}无法使用sshpass，将使用手动输入密码方式${NC}"
            if [[ "$verbose" == true ]]; then
                ssh -v $ssh_opts "$user@$host"
            else
                ssh $ssh_opts "$user@$host"
            fi
        fi
    else
        echo "认证方式: SSH密钥 ($key_file)"
        if [[ ! -f "$key_file" ]]; then
            echo -e "${RED}错误: SSH密钥文件不存在: $key_file${NC}"; exit 1
        fi
        if [[ "$verbose" == true ]]; then
            ssh -v -i "$key_file" $ssh_opts "$user@$host"
        else
            ssh -i "$key_file" $ssh_opts "$user@$host"
        fi
    fi

    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}SSH连接已断开${NC}"
    else
        echo -e "${RED}SSH连接失败 (退出码: $exit_code)${NC}"
        exit $exit_code
    fi
}

main "$@"
