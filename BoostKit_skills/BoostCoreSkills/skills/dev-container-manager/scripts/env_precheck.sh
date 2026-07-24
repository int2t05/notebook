#!/bin/bash
# env_precheck.sh — Run on remote host to check Docker environment health.
# Checks: Docker Hub accessibility, registry mirrors, disk space.
# Outputs JSON for programmatic parsing.
# Usage: ssh <host> 'bash -s' < env_precheck.sh

set -e

echo "{"

# ============================================
# Check 1: Docker Hub accessibility
# ============================================
echo "  \"dockerhub_check\": {"

HUB_REACHABLE=false
# Try multiple Docker registry endpoints
for endpoint in "https://registry-1.docker.io/v2/" "https://hub.docker.com/" "https://index.docker.io/v1/"; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$endpoint" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" != "000" ]; then
        HUB_REACHABLE=true
        echo "    \"reachable\": true,"
        echo "    \"tested_endpoint\": \"$endpoint\","
        echo "    \"http_code\": \"$HTTP_CODE\","
        break
    fi
done

if [ "$HUB_REACHABLE" = false ]; then
    echo "    \"reachable\": false,"
    echo "    \"error\": \"All Docker Hub endpoints unreachable\","
fi

# Check existing registry mirrors
MIRRORS=$(cat /etc/docker/daemon.json 2>/dev/null | python3 -c "
import json, sys
try:
    cfg = json.load(sys.stdin)
    mirrors = cfg.get('registry-mirrors', [])
    print(json.dumps(mirrors))
except: print('[]')
" 2>/dev/null || echo "[]")

echo "    \"existing_mirrors\": $MIRRORS,"

# Recommend mirrors if hub unreachable and no mirrors configured
if [ "$HUB_REACHABLE" = false ] && [ "$MIRRORS" = "[]" ]; then
    echo "    \"action_needed\": \"add_mirrors\","
    echo "    \"recommended_mirrors\": ["
    echo "      \"https://docker.1ms.run\","
    echo "      \"https://dockerproxy.net\","
    echo "      \"https://proxy.vvvv.ee\","
    echo "      \"https://dockerproxy.link\""
    echo "    ]"
else
    echo "    \"action_needed\": \"none\""
fi

echo "  },"

# ============================================
# Check 2: Disk space
# Checks three paths:
#   1. docker_root     — actual configured data-root (from daemon.json or default)
#   2. var_lib_docker  — default /var/lib/docker location (may differ from data-root)
#   3. tmp             — /tmp for build artifacts
# ============================================
echo "  \"disk_check\": {"

THRESHOLD_GB=128

# --- Check 2a: Actual Docker data root ---
DOCKER_DATA_ROOT="/var/lib/docker"
if [ -f /etc/docker/daemon.json ]; then
    CONFIG_ROOT=$(python3 -c "import json,sys; cfg=json.load(open('/etc/docker/daemon.json')); print(cfg.get('data-root',''))" 2>/dev/null || echo "")
    [ -n "$CONFIG_ROOT" ] && DOCKER_DATA_ROOT="$CONFIG_ROOT"
fi
echo "    \"docker_data_root\": \"$DOCKER_DATA_ROOT\","

compute_disk() {
    # $1 = path, outputs: free_gb total_gb mount
    local path="$1"
    if [ -d "$path" ] || [ -e "$(dirname "$path" 2>/dev/null)" ]; then
        local target="$path"
        [ -d "$target" ] || target="$(dirname "$path")"
        local free_kb=$(df -k "$target" 2>/dev/null | awk 'NR==2 {print $4}')
        local total_kb=$(df -k "$target" 2>/dev/null | awk 'NR==2 {print $2}')
        local mount=$(df "$target" 2>/dev/null | awk 'NR==2 {print $6}')
        local free_gb=$((free_kb / 1024 / 1024))
        local total_gb=$((total_kb / 1024 / 1024))
        echo "$free_gb $total_gb $mount"
    else
        echo "0 0 unknown"
    fi
}

read -r DOCKER_ROOT_FREE_GB DOCKER_ROOT_TOTAL_GB DOCKER_ROOT_MOUNT <<< "$(compute_disk "$DOCKER_DATA_ROOT")"

echo "    \"docker_root\": {"
echo "      \"path\": \"$DOCKER_DATA_ROOT\","
echo "      \"mount\": \"$DOCKER_ROOT_MOUNT\","
echo "      \"total_gb\": $DOCKER_ROOT_TOTAL_GB,"
echo "      \"free_gb\": $DOCKER_ROOT_FREE_GB"
echo "    },"

# --- Check 2b: Default /var/lib/docker location ---
# Always check this path even if data-root is customized elsewhere.
# The system partition hosting /var/lib/docker may be small and could
# constrain logs, temporary overlays, or fallback operations.
VARLIB_PATH="/var/lib/docker"
read -r VARLIB_FREE_GB VARLIB_TOTAL_GB VARLIB_MOUNT <<< "$(compute_disk "$VARLIB_PATH")"

echo "    \"var_lib_docker\": {"
echo "      \"path\": \"$VARLIB_PATH\","
echo "      \"mount\": \"$VARLIB_MOUNT\","
echo "      \"total_gb\": $VARLIB_TOTAL_GB,"
echo "      \"free_gb\": $VARLIB_FREE_GB"
echo "    },"

# --- Check 2c: /tmp ---
read -r TMP_FREE_GB TMP_TOTAL_GB TMP_MOUNT <<< "$(compute_disk "/tmp")"

echo "    \"tmp\": {"
echo "      \"path\": \"/tmp\","
echo "      \"mount\": \"$TMP_MOUNT\","
echo "      \"total_gb\": $TMP_TOTAL_GB,"
echo "      \"free_gb\": $TMP_FREE_GB"
echo "    },"

# --- Determine if any path needs attention ---
NEEDS_ALT=false
[ "$DOCKER_ROOT_FREE_GB" -lt "$THRESHOLD_GB" ] && NEEDS_ALT=true
[ "$VARLIB_FREE_GB" -lt "$THRESHOLD_GB" ] && NEEDS_ALT=true
[ "$TMP_FREE_GB" -lt "$THRESHOLD_GB" ] && NEEDS_ALT=true

echo "    \"threshold_gb\": $THRESHOLD_GB,"
echo "    \"needs_alternative\": $NEEDS_ALT,"

echo "    \"alternative_mounts\": ["
if [ "$NEEDS_ALT" = true ]; then
    FIRST=true
    df -k 2>/dev/null | awk 'NR>1' | while read -r line; do
        FS=$(echo "$line" | awk '{print $1}')
        MOUNT=$(echo "$line" | awk '{print $6}')
        FREE_KB=$(echo "$line" | awk '{print $4}')
        TOTAL_KB=$(echo "$line" | awk '{print $2}')
        FREE_GB=$((FREE_KB / 1024 / 1024))
        TOTAL_GB=$((TOTAL_KB / 1024 / 1024))

        # Skip special filesystems
        case "$FS" in
            tmpfs|devtmpfs|overlay|none|efivarfs|squashfs) continue ;;
            /dev/loop*) continue ;;
        esac

        # Skip virtual mount points
        case "$MOUNT" in
            /dev|/proc|/sys|/run|/snap|/var/lib/docker/*|/var/lib/containerd/*) continue ;;
        esac

        if [ "$FREE_GB" -gt "$THRESHOLD_GB" ]; then
            if [ "$MOUNT" != "$DOCKER_ROOT_MOUNT" ] && [ "$MOUNT" != "$VARLIB_MOUNT" ] && [ "$MOUNT" != "$TMP_MOUNT" ]; then
                [ "$FIRST" = false ] && echo ","
                FIRST=false
                echo -n "      {\"mount\": \"$MOUNT\", \"free_gb\": $FREE_GB, \"total_gb\": $TOTAL_GB, \"device\": \"$FS\"}"
            fi
        fi
    done
    echo ""
fi
echo "    ],"

# --- Summary warnings ---
echo "    \"warnings\": ["
WARNINGS=()
[ "$DOCKER_ROOT_FREE_GB" -lt "$THRESHOLD_GB" ] && WARNINGS+=("docker_data_root_low_space")
[ "$VARLIB_FREE_GB" -lt "$THRESHOLD_GB" ] && WARNINGS+=("var_lib_docker_low_space")
[ "$TMP_FREE_GB" -lt "$THRESHOLD_GB" ] && WARNINGS+=("tmp_low_space")
FIRST=true
for w in "${WARNINGS[@]}"; do
    [ "$FIRST" = false ] && echo ","
    FIRST=false
    echo -n "      \"$w\""
done
echo ""
echo "    ]"

echo "  }"

echo "}"
