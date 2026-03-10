"""Point d'entrée du serveur MCP standalone FormAI.

Lance un serveur MCP en transport STDIO. Compatible avec :
  - Antigravity (MCP Store ou config custom)
  - Claude Desktop (~/.claude/claude_desktop_config.json)
  - Cursor (~/.cursor/mcp.json)
  - MCP Inspector (npx @modelcontextprotocol/inspector)

Usage :
    # Depuis la racine du projet, venv activé :
    python -m src.mcp_server.server

Transport choisi : STDIO
    Raison : standard universel MCP, ne nécessite pas d'ouvrir un port HTTP.
    Le client lance le serveur comme sous-processus et communique via stdin/stdout.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.mcp_server.tools import extract_from_file, extract_from_text, list_schemas

# ---------------------------------------------------------------------------
# Création du serveur MCP
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="FormAI Extractor",
    instructions=(
        "Tu es connecté à FormAI, un extracteur de données structurées depuis des documents. "
        "Utilise `extract_from_text` pour analyser un texte et en extraire des champs définis "
        "par un schéma JSON. Utilise `list_schemas` pour découvrir les schémas disponibles. "
        "Utilise `extract_from_file` pour analyser directement un fichier local (PDF, TXT, JSON)."
    ),
)

# ---------------------------------------------------------------------------
# Enregistrement des tools
# ---------------------------------------------------------------------------

mcp.tool()(extract_from_text)
mcp.tool()(list_schemas)
mcp.tool()(extract_from_file)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # mcp.run() démarre le serveur en STDIO (comportement par défaut de FastMCP)
    mcp.run()
