#!/bin/bash
# list_containers.sh — Run on remote host to list all dev containers.
# Usage: ssh <host> 'bash -s' < list_containers.sh

set -e

echo "=== 开发容器列表 ==="
echo

# Check Docker availability
if ! command -v docker &>/dev/null; then
    echo "Docker 未安装或不可用"
    exit 1
fi

HOST_IP=$(hostname -I | awk '{print $1}')

# Detect auth mode: try Docker label first, fall back to sshd -T
detect_auth() {
    local cname="$1"
    # Try label (set by create_container.sh)
    local label_auth
    label_auth=$(docker inspect -f '{{ index .Config.Labels "dev.auth_mode" }}' "$cname" 2>/dev/null || echo "")
    if [ -n "$label_auth" ] && [ "$label_auth" != "<no value>" ]; then
        echo "$label_auth"
        return
    fi
    # Fallback: check sshd config inside container
    if docker exec "$cname" sh -c 'sshd -T 2>/dev/null | grep "^passwordauthentication" | awk "{print \$2}"' 2>/dev/null | grep -q "yes"; then
        local pubkey
        pubkey=$(docker exec "$cname" sh -c 'sshd -T 2>/dev/null | grep "^pubkeyauthentication" | awk "{print \$2}"' 2>/dev/null || echo "no")
        if [ "$pubkey" = "yes" ]; then
            echo "both"
        else
            echo "password"
        fi
    else
        echo "key"
    fi
}

CONTAINERS=$(docker ps -a --filter "name=dev_container_" --format '{{.Names}}' 2>/dev/null || true)

if [ -z "$CONTAINERS" ]; then
    echo "暂无开发容器"
    echo
else
    printf "%-30s %-12s %-12s %-10s %-8s %-10s %-12s %-20s\n" \
        "容器名" "用户" "CPU范围" "内存" "端口" "认证" "状态" "镜像"
    printf "%s\n" "-----------------------------------------------------------------------------------------------------------------------------------------"

    for cname in $CONTAINERS; do
        STATUS=$(docker inspect -f '{{.State.Status}}' "$cname" 2>/dev/null || echo "unknown")
        IMAGE=$(docker inspect -f '{{.Config.Image}}' "$cname" 2>/dev/null || echo "unknown")
        CPUSET=$(docker inspect -f '{{.HostConfig.CpusetCpus}}' "$cname" 2>/dev/null || echo "-")
        MEM_BYTES=$(docker inspect -f '{{.HostConfig.Memory}}' "$cname" 2>/dev/null || echo "0")
        if [ "$MEM_BYTES" != "0" ]; then
            MEM_GiB=$((MEM_BYTES / 1073741824))
            MEM_STR="${MEM_GiB}G"
        else
            MEM_STR="未限制"
        fi
        PORTS=$(docker port "$cname" 2>/dev/null | awk -F' -> ' '{print $1}' | tr '\n' ',' | sed 's/,$//')
        [ -z "$PORTS" ] && PORTS="-"
        USERNAME=$(echo "$cname" | sed 's/^dev_container_//')
        AUTH=$(detect_auth "$cname")

        AUTH_LABEL="未知"
        case "$AUTH" in
            password) AUTH_LABEL="密码" ;;
            key) AUTH_LABEL="密钥" ;;
            both) AUTH_LABEL="密码+密钥" ;;
        esac

        printf "%-30s %-12s %-12s %-10s %-8s %-10s %-12s %-20s\n" \
            "$cname" "$USERNAME" "$CPUSET" "$MEM_STR" "$PORTS" "$AUTH_LABEL" "$STATUS" "$IMAGE"
    done
fi

echo
echo "=== 容器详情 ==="

for cname in $CONTAINERS; do
    STATUS=$(docker inspect -f '{{.State.Status}}' "$cname" 2>/dev/null || echo "unknown")
    CPUSET=$(docker inspect -f '{{.HostConfig.CpusetCpus}}' "$cname" 2>/dev/null || echo "-")
    MEM_BYTES=$(docker inspect -f '{{.HostConfig.Memory}}' "$cname" 2>/dev/null || echo "0")
    MEM_GiB=$((MEM_BYTES / 1073741824))
    PORTS=$(docker port "$cname" 2>/dev/null | awk -F' -> ' '{print $1}' | head -1)
    USERNAME=$(echo "$cname" | sed 's/^dev_container_//')
    CREATED=$(docker inspect -f '{{.Created}}' "$cname" 2>/dev/null | cut -d'T' -f1,2 | cut -d'.' -f1)
    AUTH=$(detect_auth "$cname")
    SSH_PORT="${PORTS%%:*}"

    echo "--- $cname ---"
    echo "  用户:     $USERNAME"
    echo "  状态:     $STATUS"
    echo "  CPU范围:  $CPUSET"
    echo "  内存限制: ${MEM_GiB}G"
    echo "  SSH端口:  $PORTS"
    echo "  认证方式: $AUTH"
    echo "  创建时间: $CREATED"

    case "$AUTH" in
        password)
            echo "  SSH连接:  ssh -p $SSH_PORT root@$HOST_IP" ;;
        key)
            echo "  SSH连接:  ssh -i dev_container_${USERNAME}_key -p $SSH_PORT root@$HOST_IP" ;;
        both)
            echo "  SSH连接(密码): ssh -p $SSH_PORT root@$HOST_IP"
            echo "  SSH连接(密钥): ssh -i dev_container_${USERNAME}_key -p $SSH_PORT root@$HOST_IP" ;;
        *)
            echo "  SSH连接:  ssh -p $SSH_PORT root@$HOST_IP" ;;
    esac
    echo
done

# --- Summary ---
echo "=== 资源总览 ==="
TOTAL_CPU_USED=0
TOTAL_MEM_USED=0

for cname in $CONTAINERS; do
    STATUS=$(docker inspect -f '{{.State.Status}}' "$cname" 2>/dev/null || echo "unknown")
    if [ "$STATUS" = "running" ]; then
        CPUSET=$(docker inspect -f '{{.HostConfig.CpusetCpus}}' "$cname" 2>/dev/null || echo "0")
        if echo "$CPUSET" | grep -q '-'; then
            START=$(echo "$CPUSET" | cut -d'-' -f1)
            END=$(echo "$CPUSET" | cut -d'-' -f2)
            COUNT=$((END - START + 1))
        else
            COUNT=$(echo "$CPUSET" | tr ',' '\n' | wc -l)
        fi
        TOTAL_CPU_USED=$((TOTAL_CPU_USED + COUNT))

        MEM_BYTES=$(docker inspect -f '{{.HostConfig.Memory}}' "$cname" 2>/dev/null || echo "0")
        MEM_GiB=$((MEM_BYTES / 1073741824))
        TOTAL_MEM_USED=$((TOTAL_MEM_USED + MEM_GiB))
    fi
done

TOTAL_CPU=$(nproc)
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')

echo "  CPU:  ${TOTAL_CPU_USED}/${TOTAL_CPU} 核已分配"
echo "  内存: ${TOTAL_MEM_USED}G/${TOTAL_MEM}G 已分配"
