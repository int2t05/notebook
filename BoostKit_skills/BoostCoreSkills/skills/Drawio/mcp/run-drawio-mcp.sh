#!/bin/zsh
# Draw.io MCP runtime launcher.
# Resolves the MCP server entry relative to this script so the bundle is portable.
set -eu

SCRIPT_DIR="${0:A:h}"
ENTRY="${SCRIPT_DIR}/drawio/node_modules/@next-ai-drawio/mcp-server/dist/index.js"

if [[ ! -f "${ENTRY}" ]]; then
    print -u2 "Draw.io MCP runtime is missing: ${ENTRY}"
    print -u2 "Run \`npm install\` inside ${SCRIPT_DIR}/drawio first, or use install.sh in the bundle root."
    exit 1
fi

# Prefer Trae's bundled Node runtime (Electron binary acting as Node).
for trae_electron in \
    "/Applications/Trae CN.app/Contents/MacOS/Electron" \
    "/Applications/Trae.app/Contents/MacOS/Electron"; do
    if [[ -x "${trae_electron}" ]]; then
        export ELECTRON_RUN_AS_NODE=1
        exec "${trae_electron}" "${ENTRY}"
    fi
done

# Then check common Homebrew / system Node locations.
for node_bin in \
    "/opt/homebrew/bin/node" \
    "/usr/local/bin/node" \
    "/Applications/Codex.app/Contents/Resources/node"; do
    if [[ -x "${node_bin}" ]]; then
        exec "${node_bin}" "${ENTRY}"
    fi
done

# Fall back to whatever `node` is on PATH.
if command -v node >/dev/null 2>&1; then
    exec node "${ENTRY}"
fi

print -u2 "Node.js 18 or newer was not found. Install Node.js or use the Trae / Codex bundled runtime."
exit 1
