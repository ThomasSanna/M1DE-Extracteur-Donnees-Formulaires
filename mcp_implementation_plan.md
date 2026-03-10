# Plan d'implémentation — Serveur MCP Standalone FormAI

FormAI expose déjà une API REST. L'objectif est d'ajouter un **serveur MCP standalone** (Plan A) qui wrappe les fonctions métier existantes sans toucher au code REST. Un client MCP (Antigravity, Claude Desktop, Cursor...) pourra alors appeler les tools FormAI directement.

---

## Proposed Changes

### Dépendance

#### [MODIFY] [requirements.txt](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/requirements.txt)

Ajouter `mcp` (SDK Python officiel du Model Context Protocol) :

```diff
 openai
 pydantic
 python-dotenv
 fastapi
 uvicorn[standard]
 python-multipart
 pypdf
+mcp
```

---

### Nouveau module MCP

#### [NEW] [src/mcp_server/\_\_init\_\_.py](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/mcp_server/__init__.py)
Fichier vide pour faire de `mcp_server` un package Python.

---

#### [NEW] [src/mcp_server/tools.py](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/mcp_server/tools.py)

Contient la **définition des 2 tools MCP MVP** :

**Tool 1 — `extract_from_text`**
- Paramètres : `document_text: str`, `schema: dict`
- Logique : valide le schéma via `ExtractionSchema.model_validate(schema)`, appelle [extract()](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/core/extractor.py#90-158) depuis `src.core.extractor`, sérialise le résultat [ExtractionResult](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/core/models.py#66-73) en dict propre via `.model_dump()`
- Gestion d'erreur : retourne un dict `{"status": "error", "message": "..."}` si exception (pas de crash, le LLM reçoit toujours quelque chose d'exploitable)
- Sécurité : troncature du texte à 50 000 chars (même limite que l'API REST)

**Tool 2 — `list_schemas`**
- Paramètres : aucun
- Logique : lit `data/schemas/*.json`, retourne une liste `[{"name": ..., "description": ..., "fields": [...]}]`
- Gestion d'erreur : retourne liste vide si le dossier n'existe pas

> [!NOTE]
> **Choix de sérialisation** : [ExtractionResult](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/core/models.py#66-73) est un objet Pydantic. MCP attend un retour JSON-sérialisable. On utilise `.model_dump(mode="json")` qui gère les `datetime` et les types custom automatiquement.

---

#### [NEW] [src/mcp_server/server.py](file:///c:/Users/thoma/Desktop/programmes/M1DENG/Semestre%202/M1DE-ai-gateway/Projet/src/mcp_server/server.py)

Point d'entrée principal. Crée l'objet `FastMCP`, importe et enregistre les tools, et expose le `mcp` en STDIO.

```python
# Squelette simplifié
from mcp.server.fastmcp import FastMCP
from src.mcp_server.tools import extract_from_text, list_schemas

mcp = FastMCP("FormAI Extractor")
mcp.tool()(extract_from_text)
mcp.tool()(list_schemas)

if __name__ == "__main__":
    mcp.run()  # transport STDIO par défaut
```

**Transport choisi : STDIO**
- Compatible nativement avec Claude Desktop, Cursor et Antigravity
- Plus simple qu'un serveur SSE (pas de port à ouvrir, pas de CORS)
- Lancé directement via `python -m src.mcp_server.server`

---

## Verification Plan

### Test 1 — MCP Inspector (sans client IA)

```bash
# Depuis la racine du projet, venv activé
npx @modelcontextprotocol/inspector python -m src.mcp_server.server
```

→ Ouvre une interface web sur `http://localhost:5173`  
→ Vérifie que **2 tools** apparaissent : `extract_from_text` et `list_schemas`  
→ Appelle `list_schemas` → doit retourner la liste des schemas de `data/schemas/`  
→ Appelle `extract_from_text` avec :
  - `document_text`: `"Thomas Sanna, infirmier diplômé d'État, 5 ans d'expérience"`
  - `schema`: `{"schema_name": "cv", "fields": [{"name": "nom", "type": "string", "required": true, "description": "Nom complet"}]}`

### Test 2 — Tests pytest existants (non-régression)

```bash
# Depuis la racine du projet, venv activé
pytest tests/ -v
```

→ Les 5 tests existants doivent toujours passer (le serveur MCP est un module additionnel, il ne modifie pas `src/core/`)

### Test 3 — Connexion depuis Antigravity (optionnel, après impl.)

Depuis Antigravity, demander d'appeler le tool FormAI sur un texte fourni.
