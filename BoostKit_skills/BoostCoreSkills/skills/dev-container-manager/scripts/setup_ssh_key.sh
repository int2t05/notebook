#!/bin/bash
# setup_ssh_key.sh — One-shot SSH key-pair setup for silent agent connection.
# Generates ed25519 key if missing, copies public key to server, verifies.
# Usage: bash setup_ssh_key.sh <user>@<server>
# The user runs this ONCE and types their server password when prompted.

set -e

SERVER="${1:?用法: bash setup_ssh_key.sh <user>@<server>}"
USER="${SERVER%@*}"
HOST="${SERVER#*@}"

echo "============================================"
echo "  SSH 密钥认证配置"
echo "  目标: $SERVER"
echo "============================================"
echo ""

# ------------------------------------------------------------
# Step 1: Check if key-pair auth already works
# ------------------------------------------------------------
echo "[1/3] 检查当前 SSH 认证状态..."
if ssh -o PasswordAuthentication=no \
       -o ConnectTimeout=5 \
       -o StrictHostKeyChecking=accept-new \
       "$SERVER" 'echo ssh_ok' 2>/dev/null | grep -q ssh_ok; then
    echo "  ✓ SSH 密钥认证已正常，无需配置。"
    exit 0
fi
echo "  → 密钥认证未配置，开始设置..."

# ------------------------------------------------------------
# Step 2: Generate ed25519 key if missing
# ------------------------------------------------------------
echo ""
echo "[2/3] 检查本地密钥..."

KEY_PATH="$HOME/.ssh/id_ed25519"

if [ -f "$KEY_PATH" ]; then
    echo "  → 使用已有密钥: $KEY_PATH"
elif [ -f "$HOME/.ssh/id_rsa" ]; then
    echo "  发现 RSA 密钥，同时生成 ed25519 密钥（更安全）..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "dev-container@$HOST"
    echo "  ✓ 密钥已生成: $KEY_PATH"
else
    echo "  本地无 SSH 密钥，正在生成..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "dev-container@$HOST"
    echo "  ✓ 密钥已生成: $KEY_PATH"
fi

PUBKEY_CONTENT=$(cat "$KEY_PATH.pub")

# ------------------------------------------------------------
# Step 3: Copy public key to server
# ------------------------------------------------------------
echo ""
echo "[3/3] 复制公钥到 $SERVER ..."
echo "  提示: 需要输入一次远程服务器密码"
echo ""

if command -v ssh-copy-id &>/dev/null; then
    ssh-copy-id -o StrictHostKeyChecking=accept-new "$SERVER"
else
    cat "$KEY_PATH.pub" | ssh -o StrictHostKeyChecking=accept-new "$SERVER" \
        'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
fi

# ------------------------------------------------------------
# Step 4: Verify
# ------------------------------------------------------------
echo ""
echo "=== 验证免密登录 ==="
if ssh -o PasswordAuthentication=no -o ConnectTimeout=5 "$SERVER" 'echo ssh_ok' 2>/dev/null | grep -q ssh_ok; then
    echo ""
    echo "============================================"
    echo "  ✓ SSH 密钥认证配置成功！"
    echo "  Agent 现在可以静默连接 $SERVER"
    echo "============================================"
else
    echo ""
    echo "============================================"
    echo "  ✗ 配置后验证失败"
    echo "============================================"
    echo ""
    echo "可能原因:"
    echo "  1. 服务器禁用了公钥认证 (PubkeyAuthentication no)"
    echo "  2. 服务器 ~/.ssh 或 authorized_keys 权限不正确"
    echo ""
    echo "排查命令:"
    echo "  ssh -o PasswordAuthentication=no -v $SERVER"
    echo ""
    echo "当前公钥内容 (供管理员手动添加):"
    echo "  $PUBKEY_CONTENT"
    exit 1
fi
