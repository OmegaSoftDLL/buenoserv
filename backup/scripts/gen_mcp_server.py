#!/usr/bin/env python3
"""BUENOSERV MCP Server — Model Context Protocol para IAs de engenharia."""
import os, json, subprocess, sys, logging
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

STATE_FILE = Path(os.path.expanduser("~/.config/opencode/state/agent_state.json"))
SCRIPTS_DIR = Path("/tmp/opencode/templates")
AGENTS_DIR = Path(os.path.expanduser("~/.config/opencode/agents"))

TOOLS = {
    "consultar_state": {
        "descricao": "Consulta o estado atual do ecossistema BUENOSERV",
        "parametros": {"chave": "(opcional) chave especifica para filtrar"}
    },
    "executar_script": {
        "descricao": "Executa um script do ecossistema e retorna o resultado",
        "parametros": {"script": "nome do script (ex: gen_oracle.py)", "args": "argumentos (opcional)"}
    },
    "buscar_agente": {
        "descricao": "Busca conhecimento em um agente de engenharia",
        "parametros": {"agente": "nome do agente", "query": "consulta"}
    },
    "gerar_diagrama": {
        "descricao": "Gera diagrama tecnico DWG",
        "parametros": {"tipo": "unifilar|telecom|rack|fibra", "projeto": "nome do projeto"}
    },
    "consultar_pipeline": {
        "descricao": "Retorna o pipeline comercial atual",
        "parametros": {}
    },
    "consultar_dre": {
        "descricao": "Retorna o DRE financeiro",
        "parametros": {}
    },
    "recomendar_acoes": {
        "descricao": "Oraculo: recomenda proximas acoes baseado no estado",
        "parametros": {}
    },
    "status_sistema": {
        "descricao": "Status completo de saude do sistema",
        "parametros": {}
    }
}

def carregar_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

def executar(script, args=""):
    path = SCRIPTS_DIR / script
    if not path.exists():
        return {"erro": f"script {script} nao encontrado"}
    cmd = ["python3", str(path)] + (args.split() if args else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {"stdout": r.stdout[:2000], "stderr": r.stderr[:500], "codigo": r.returncode}
    except subprocess.TimeoutExpired:
        return {"erro": "timeout"}
    except Exception as e:
        return {"erro": str(e)}

@app.route("/mcp")
def mcp_info():
    return jsonify({
        "nome": "BUENOSERV MCP Server",
        "versao": "1.0",
        "protocolo": "Model Context Protocol",
        "tools": list(TOOLS.keys()),
        "total_tools": len(TOOLS)
    })

@app.route("/mcp/tools")
def mcp_tools():
    return jsonify(TOOLS)

@app.route("/mcp/call", methods=["POST"])
def mcp_call():
    data = request.json or {}
    tool = data.get("tool", "")
    params = data.get("params", {})

    if tool == "consultar_state":
        state = carregar_state()
        chave = params.get("chave")
        if chave:
            v = state
            for k in chave.split("."):
                v = v.get(k, {}) if isinstance(v, dict) else {}
            return jsonify({"resultado": v})
        return jsonify({"resultado": state})

    if tool == "executar_script":
        script = params.get("script", "")
        args = params.get("args", "")
        return jsonify(executar(script, args))

    if tool == "buscar_agente":
        agente = params.get("agente", "")
        query = params.get("query", "").lower()
        path = AGENTS_DIR / f"{agente}.md"
        if not path.exists():
            return jsonify({"erro": f"agente {agente} nao encontrado"})
        with open(path) as f:
            content = f.read()
        if query:
            lines = [l.strip() for l in content.split("\n") if query in l.lower()]
            return jsonify({"agente": agente, "resultados": lines[:10], "total": len(lines)})
        return jsonify({"agente": agente, "conteudo": content[:2000]})

    if tool == "gerar_diagrama":
        tipo = params.get("tipo", "unifilar")
        projeto = params.get("projeto", "mcp_gerado")
        return jsonify(executar("gen_dwg.py", f"{tipo} --projeto {projeto}"))

    if tool == "consultar_pipeline":
        state = carregar_state()
        pipeline = []
        for proj, tasks in state.get("tasks", {}).items():
            for t in tasks:
                if "comercial" in t.get("agente", ""):
                    pipeline.append(t)
        return jsonify({"pipeline": pipeline[:20], "total": len(pipeline)})

    if tool == "consultar_dre":
        state = carregar_state()
        return jsonify({"dre": state.get("dre", {})})

    if tool == "recomendar_acoes":
        return jsonify(executar("gen_oracle.py", "--json"))

    if tool == "status_sistema":
        return jsonify(executar("gen_ci_pipeline.py"))

    return jsonify({"erro": f"tool '{tool}' nao encontrada"}), 404

@app.route("/mcp/agents")
def mcp_agents():
    agentes = sorted([f.stem for f in AGENTS_DIR.glob("*.md")])
    return jsonify({"total": len(agentes), "agentes": agentes})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "tools": len(TOOLS)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8520))
    print(f"🔌 BUENOSERV MCP Server")
    print(f"   Tools: {len(TOOLS)}")
    print(f"   Porta: {port}")
    print(f"   Endpoints: /mcp, /mcp/tools, /mcp/call, /mcp/agents, /health")
    app.run(host="0.0.0.0", port=port, debug=False)
