#!/bin/zsh
# install.sh — Install the Draw.io MCP and Skill from this bundle.
#
# What it does:
#   1. Runs `npm install` inside mcp/drawio/ to fetch the MCP server runtime
#      (@next-ai-drawio/mcp-server) and all of its npm dependencies.
#   2. Prints the exact mcp.json snippet the user should paste into their
#      Trae / Cursor / Claude Desktop / Codex MCP config (with the absolute
#      path to THIS bundle already filled in).
#   3. Prints where to copy the Skill (skill/drawio-diagrams) so the host
#      editor can load it as a Skill.
#
# Re-run safely: it skips the npm install step when node_modules already
# contains the expected entry file.

set -eu

BUNDLE_DIR="${0:A:h}"
MCP_DIR="${BUNDLE_DIR}/mcp/drawio"
ENTRY="${MCP_DIR}/node_modules/@next-ai-drawio/mcp-server/dist/index.js"
LAUNCHER="${BUNDLE_DIR}/mcp/run-drawio-mcp.sh"
SKILL_SRC="${BUNDLE_DIR}/skill/drawio-diagrams"

print -n -- "==> Installing Draw.io MCP runtime ... "
if [[ -f "${ENTRY}" ]]; then
    print "already installed, skipping."
else
    if ! command -v npm >/dev/null 2>&1; then
        print "\n[!] npm was not found on PATH. Install Node.js 18+ (https://nodejs.org) and re-run."
        exit 1
    fi
    ( cd "${MCP_DIR}" && npm install --no-audit --no-fund --loglevel=error )
    print "done."
fi

chmod +x "${LAUNCHER}"

cat <<EOF

==> Install complete.

----------------------------------------------------------------
1) Register the MCP server
----------------------------------------------------------------
Add the following to your MCP config (Trae: .trae/mcp.json,
Cursor: ~/.cursor/mcp.json, Claude Desktop: claude_desktop_config.json,
Codex: .codex/config.toml or similar):

${BUNDLE_DIR}/mcp/mcp.json  is already pre-written. Open it and replace
the placeholder <DRAWIO_BUNDLE> with the absolute path to THIS folder:

    /Users/<you>/Desktop/Drawio

Then merge the "mcpServers" object into your editor's MCP config, or
symlink the file:

    ln -s "${BUNDLE_DIR}/mcp/mcp.json" /path/to/your/editor/mcp.json

----------------------------------------------------------------
2) Install the Skill
----------------------------------------------------------------
Copy the entire skill/drawio-diagrams directory into your editor's
skill folder so it is auto-discovered:

    cp -R "${SKILL_SRC}" ~/.trae/skills/                # Trae
    cp -R "${SKILL_SRC}" ~/.claude/skills/              # Claude Code
    cp -R "${SKILL_SRC}" ~/.codex/skills/               # Codex

(Adjust the destination to match your editor's skill root.)

----------------------------------------------------------------
3) Verify
----------------------------------------------------------------
Restart your editor. The Draw.io MCP should appear with these tools:
  - start_session
  - create_new_diagram
  - get_diagram
  - edit_diagram
  - export_diagram

The Draw.io Skill (drawio-diagrams) should be visible in the editor's
Skill list and auto-activated when you mention "draw.io", "drawio",
"flow chart", "architecture diagram", etc.

----------------------------------------------------------------
Notes
----------------------------------------------------------------
- The MCP runtime needs Node.js 18+ or Trae/Codex's bundled Electron.
- The launcher prefers Trae's Electron binary, then Homebrew/system
  Node, then PATH. See mcp/run-drawio-mcp.sh for details.
- Default HTTP port is 6002 (set in mcp/mcp.json under "env.PORT").
  Change it if 6002 is already taken on your machine.

EOF
