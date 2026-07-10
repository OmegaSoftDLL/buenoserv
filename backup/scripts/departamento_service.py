#!/usr/bin/env python3
"""BUENOSERV Department Service — container departamental com IAs de engenharia."""
import os, json, glob, re, logging
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DEPARTAMENTO = os.environ.get("DEPARTAMENTO", "core").upper()
AGENTS_DIR = Path("/home/ricardobueno/.config/opencode/agents")
STATE_FILE = Path("/home/ricardobueno/.config/opencode/state/agent_state.json")

DEPT_PATTERNS = {
    "ENGENHARIA": [
        "telecom", "scada", "ems", "nms", "pmu", "wams", "sincronismo",
        "substation", "power", "energia", "geracao", "solar", "shelter",
        "automacao", "civil", "instalacao", "manutencao", "comissionamento", "handover",
        "ip-", "router", "switch", "network", "tsn",
        "firewall", "physical-security", "cftv", "seguranca", "incendio",
        "qualidade", "memoria", "levantamento", "processo-industrial",
        "dwg", "bom", "mcp", "dcl", "fibra", "teleprotection",
        "protecao", "controle", "instrumentacao",
        "normas", "documentacao", "ensaio", "medicao", "qualidade_energia",
        "gerador", "dc-raft", "datacenter", "cyber",
        "acesso", "arquivos", "depara", "padronizador", "template",
        "project-control", "gestao-projetos", "planejamento",
        "pericias", "engenharia-aval", "curriculo",
        "workflow", "vigia", "rfp", "ceo", "buenoserv",
    ],
    "COMERCIAL": [
        "comercial", "crm", "proposta", "click_sign", "drip_campaign",
        "followup", "email_templates", "portfolio", "google_meu_negocio",
        "marketing", "rfp", "juridico",
    ],
    "FINANCEIRO": [
        "financeiro", "contabilidade", "dre", "fluxo_caixa", "conciliacao",
        "calc_impostos", "nfe", "orcado_realizado", "budget", "contas",
        "rh",
    ],
    "PROJETOS": [
        "gestao-projetos", "project-control", "planejamento", "cronograma",
        "eap", "diario_obra", "timesheet", "biblioteca_projetos",
        "simulador_cronograma", "monte_carlo", "memoria", "handover",
        "qualidade", "documentacao", "arquivos", "treinamento",
    ],
    "SUPRIMENTOS": [
        "suprimentos", "compras", "rfp", "contrato", "almoxarifado",
        "rfp_scraper", "depara",
    ],
    "TECNICO": [
        "instalacao", "manutencao", "comissionamento", "automacao",
        "telecom-", "ip-", "router", "switch", "scada",
        "cftv", "firewall", "gerador", "dc-raft", "datacenter",
        "shelter", "bom", "depara", "padronizador", "template",
        "ensaio", "medicao", "qualidade", "teste",
        "fibra", "radio", "gpon", "dwdm", "sdh", "otn", "ptn",
        "teleprotection", "tsn", "nms", "ems", "pmu", "wams",
        "sincronismo", "substation", "power", "cyber",
        "structured-cabling", "seguranca-trabalho", "seg-energia",
        "incendio", "relatorios", "processos", "compliance",
    ],
    "RH": [
        "rh", "holerite", "treinamento", "recursos_humanos", "curriculo",
    ],
    "SISTEMA": [
        "ceo", "autopilot", "healthcheck", "healer", "oracle",
        "ci_pipeline", "logging", "backup", "buenoserv",
        "vigia", "workflow", "template-adapter",
    ],
}

def carregar_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

def listar_agentes():
    padroes = DEPT_PATTERNS.get(DEPARTAMENTO, [])
    agentes = []
    for f in sorted(AGENTS_DIR.glob("*.md")):
        nome = f.stem.lower()
        if padroes and not any(p.lower() in nome for p in padroes):
            continue
        with open(f) as fh:
            content = fh.read()
        meta = {}
        m = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
        agentes.append({
            "nome": f.stem,
            "descricao": meta.get("description", ""),
            "modo": meta.get("mode", ""),
            "tamanho": len(content)
        })
    return agentes

@app.route("/")
def home():
    return jsonify({
        "servico": f"BUENOSERV - Departamento {DEPARTAMENTO}",
        "agentes": len(listar_agentes()),
        "status": "operacional"
    })

@app.route("/agentes")
def agentes():
    return jsonify(listar_agentes())

@app.route("/agentes/<nome>")
def agente(nome):
    path = AGENTS_DIR / f"{nome}.md"
    if not path.exists():
        return jsonify({"erro": "agente nao encontrado"}), 404
    with open(path) as f:
        content = f.read()
    return jsonify({"nome": nome, "conteudo": content})

@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.json
    termo = data.get("q", "").lower()
    if not termo:
        return jsonify({"erro": "parametro 'q' obrigatorio"}), 400
    resultados = []
    for a in listar_agentes():
        path = AGENTS_DIR / f"{a['nome']}.md"
        with open(path) as f:
            content = f.read()
        for i, line in enumerate(content.split("\n"), 1):
            if termo in line.lower():
                resultados.append({"agente": a["nome"], "linha": i, "texto": line.strip()[:120], "descricao": a["descricao"]})
                break
    return jsonify({"resultados": resultados, "total": len(resultados)})

@app.route("/state")
def state():
    return jsonify(carregar_state())

@app.route("/saude")
def saude():
    agentes = listar_agentes()
    try:
        import resource
        memoria = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    except:
        memoria = 0
    return jsonify({
        "departamento": DEPARTAMENTO,
        "agentes_carregados": len(agentes),
        "memoria_mb": memoria
    })

@app.route("/perguntar", methods=["POST"])
def perguntar_router():
    data = request.json or {}
    pergunta = data.get("pergunta", "")
    if not pergunta:
        return jsonify({"erro": "pergunta obrigatoria"}), 400
    agentes = listar_agentes()[:5]
    contexto = "\n".join([f"- {a['nome']}: {a['descricao']}" for a in agentes if a.get("descricao")])
    conteudo = "\n".join([
        open(AGENTS_DIR / f"{a['nome']}.md").read()[:500]
        for a in agentes[:3]
        if (AGENTS_DIR / f"{a['nome']}.md").exists()
    ])
    try:
        import urllib.request
        payload = json.dumps({
            "pergunta": pergunta,
            "contexto": f"Departamento {DEPARTAMENTO}\nAgentes: {contexto}\n\n{conteudo}",
            "departamento": DEPARTAMENTO.lower()
        }).encode()
        req = urllib.request.Request(
            "http://hermes:8580/perguntar", data=payload,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=120)
        d = json.loads(resp.read())
        return jsonify({
            "pergunta": pergunta,
            "resposta": d.get("resposta", ""),
            "modelo": d.get("modelo", "hermes3"),
            "origem": d.get("origem", "local"),
            "departamento": DEPARTAMENTO,
            "agentes_consultados": [a["nome"] for a in agentes[:3]]
        })
    except Exception as e:
        return jsonify({
            "pergunta": pergunta,
            "resposta": f"[Router offline: {e}]",
            "departamento": DEPARTAMENTO,
            "fallback": True
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8500))
    agentes = listar_agentes()
    print(f"🏢 BUENOSERV - Departamento {DEPARTAMENTO}")
    print(f"   Agentes: {len(agentes)}")
    for a in agentes[:5]:
        print(f"     - {a['nome']}: {a['descricao'][:60]}")
    if len(agentes) > 5:
        print(f"     ... e mais {len(agentes)-5}")
    print(f"   Porta: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
