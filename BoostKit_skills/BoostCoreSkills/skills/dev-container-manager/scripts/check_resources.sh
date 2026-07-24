#!/bin/bash
# check_resources.sh — Run on remote host to collect system resource info.
# Outputs JSON for programmatic parsing.
# Usage: ssh <host> 'bash -s' < check_resources.sh

set -e

echo "{"

# --- OS info ---
echo "  \"os\": {"
echo "    \"name\": \"$(cat /etc/os-release | grep '^PRETTY_NAME=' | cut -d= -f2 | tr -d '"')\","
echo "    \"kernel\": \"$(uname -r)\","
echo "    \"arch\": \"$(uname -m)\""
echo "  },"

# --- CPU info ---
TOTAL_CORES=$(nproc)
MODEL=$(lscpu | grep "Model name:" | head -1 | sed 's/Model name:\s*//')
SOCKETS=$(lscpu | grep "Socket(s):" | awk '{print $2}')
THREADS_PER_CORE=$(lscpu | grep "Thread(s) per core:" | awk '{print $4}')
CORES_PER_SOCKET=$(lscpu | grep "Core(s) per socket:" | awk '{print $4}')
LOAD=$(top -bn1 | grep "load average:" | awk -F': ' '{print $2}' | cut -d',' -f1 | tr -d ' ')

echo "  \"cpu\": {"
echo "    \"model\": \"$MODEL\","
echo "    \"total_cores\": $TOTAL_CORES,"
echo "    \"sockets\": $SOCKETS,"
echo "    \"threads_per_core\": $THREADS_PER_CORE,"
echo "    \"cores_per_socket\": $CORES_PER_SOCKET,"
echo "    \"load_1m\": $LOAD"
echo "  },"

# --- NUMA topology ---
echo "  \"numa\": ["
if command -v numactl &>/dev/null; then
    NODES=$(numactl --hardware 2>/dev/null | grep "available:" | awk '{print $2}')
    NODE_IDX=0
    while IFS= read -r line; do
        if echo "$line" | grep -qE "^node [0-9]+ cpus:"; then
            NODE_NUM=$(echo "$line" | awk '{print $2}')
            CPUS=$(echo "$line" | sed 's/.*cpus: //')
            SIZE_LINE=$(numactl --hardware 2>/dev/null | grep "node $NODE_NUM size:")
            FREE_LINE=$(numactl --hardware 2>/dev/null | grep "node $NODE_NUM free:")
            SIZE=$(echo "$SIZE_LINE" | awk '{print $4}')
            FREE=$(echo "$FREE_LINE" | awk '{print $4}')
            [ $NODE_IDX -gt 0 ] && echo ","
            echo -n "    {\"id\": $NODE_NUM, \"cpus\": \"$CPUS\", \"size_mb\": $SIZE, \"free_mb\": $FREE}"
            NODE_IDX=$((NODE_IDX + 1))
        fi
    done < <(numactl --hardware 2>/dev/null)
    echo ""
else
    echo "    {\"id\": 0, \"cpus\": \"0-$((TOTAL_CORES-1))\", \"size_mb\": 0, \"free_mb\": 0}"
fi
echo "  ],"

# --- Memory ---
MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
MEM_USED=$(free -m | awk '/^Mem:/{print $3}')
MEM_FREE=$(free -m | awk '/^Mem:/{print $4}')
MEM_AVAIL=$(free -m | awk '/^Mem:/{print $7}')

echo "  \"memory\": {"
echo "    \"total_mb\": $MEM_TOTAL,"
echo "    \"used_mb\": $MEM_USED,"
echo "    \"free_mb\": $MEM_FREE,"
echo "    \"available_mb\": $MEM_AVAIL"
echo "  },"

# --- Docker info ---
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    DOCKER_VER=$(docker info 2>/dev/null | grep "Server Version:" | awk '{print $3}')
    echo "  \"docker\": {"
    echo "    \"version\": \"$DOCKER_VER\","
    echo "    \"available\": true"
    echo "  },"
else
    echo "  \"docker\": {"
    echo "    \"version\": \"none\","
    echo "    \"available\": false"
    echo "  },"
fi

# --- Existing dev containers ---
echo "  \"existing_containers\": ["
CONTAINERS=$(docker ps -a --filter "name=dev_container_" --format '{{.Names}}' 2>/dev/null || true)
FIRST=true
for cname in $CONTAINERS; do
    # Skip empty
    [ -z "$cname" ] && continue
    STATUS=$(docker inspect -f '{{.State.Status}}' "$cname" 2>/dev/null || echo "unknown")
    IMAGE=$(docker inspect -f '{{.Config.Image}}' "$cname" 2>/dev/null || echo "unknown")
    CPUSET=$(docker inspect -f '{{.HostConfig.CpusetCpus}}' "$cname" 2>/dev/null || echo "")
    MEM=$(docker inspect -f '{{.HostConfig.Memory}}' "$cname" 2>/dev/null || echo "0")
    MEM_GiB=$((MEM / 1073741824))
    PORTS=$(docker port "$cname" 2>/dev/null | head -1 || echo "none")
    USERNAME=$(echo "$cname" | sed 's/^dev_container_//')

    [ "$FIRST" = false ] && echo ","
    FIRST=false
    echo -n "    {\"name\": \"$cname\", \"username\": \"$USERNAME\", \"status\": \"$STATUS\", \"image\": \"$IMAGE\", \"cpuset_cpus\": \"$CPUSET\", \"memory_gib\": $MEM_GiB, \"ports\": \"$PORTS\"}"
done
echo ""
echo "  ],"

# --- Used ports ---
echo "  \"used_ports\": ["
USED_PORTS=$(ss -tlnp 2>/dev/null | awk 'NR>1 {split($4,a,":"); print a[length(a)]}' | sort -n | uniq)
FIRST=true
for port in $USED_PORTS; do
    [ "$FIRST" = false ] && echo ","
    FIRST=false
    echo -n "    $port"
done
echo ""
echo "  ]"

echo "}"
