[sudo: authenticate] Password: 
#!/usr/bin/env python3
"""gen_api.py — API REST central do ecossistema BUENOSERV."""
import http.server
import json
import os
import re
import sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
MARKET_FILE = os.path.expanduser("/tmp/opencode/market_intel/oportunidades.json")
DASHBOARD_DIR = os.path.expanduser("~/.config/opencode/dashboard")
SCRIPTS_DIR = os.path.expanduser("/tmp/opencode/templates")

CRITICAL_FILES = [
    STATE_FILE,
    os.path.expanduser("~/.config/opencode/opencode.jsonc"),
]

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def extract_pipeline(state):
    pipeline = []
    total_value = 0.0
    tasks = state.get("tasks", {})
    for project, project_tasks in tasks.items():
        for task in project_tasks:
            if task.get("agente") == "comercial" and task.get("observacao"):
                values = re.findall(r"R?\$?([\d,.]+(?:[kKMnM]?))", task["observacao"])
                parsed = 0.0
                for v in values:
                    v = v.replace(",", ".")
                    if v.lower().endswith("k"):
                        parsed += float(v[:-1]) * 1000
                    elif v.lower().endswith("m"):
                        parsed += float(v[:-1]) * 1_000_000
                    else:
                        try:
                            parsed += float(v)
                        except ValueError:
                            pass
                total_value += parsed
                pipeline.append({
                    "projeto": project,
                    "status": task.get("status"),
                    "observacao": task.get("observacao"),
                    "valor_extraido": round(parsed, 2),
                    "timestamp": task.get("timestamp"),
                })
    return {"pipeline": pipeline, "total_value": round(total_value, 2), "deals_count": len(pipeline)}


def extract_dre(state):
    dre = state.get("dre", {})
    meses = dre.get("meses", {})
    keys = ["receita_bruta", "receita_liquida", "custos_servicos", "lucro_bruto",
            "despesas_administrativas", "despesas_comerciais", "despesas_tributarias",
            "lucro_operacional", "resultado_financeiro", "lucro_liquido"]
    totals = {k: 0.0 for k in keys}
    meses_detalhados = {}
    for mes_num, mes_data in sorted(meses.items()):
        meses_detalhados[int(mes_num)] = mes_data
        for k in keys:
            totals[k] += mes_data.get(k, 0.0)
    return {
        "ano": dre.get("ano"),
        "meses": meses_detalhados,
        "totais": {k: round(v, 2) for k, v in totals.items()},
        "acumulado": dre.get("acumulado", {}),
    }


def extract_agents(state):
    tasks = state.get("tasks", {})
    agent_status = {}
    for project, project_tasks in tasks.items():
        for task in project_tasks:
            a = task.get("agente")
            if a:
                if a not in agent_status:
                    agent_status[a] = {"agente": a, "status": task.get("status"), "ultima_atividade": task.get("timestamp")}
                elif task.get("timestamp", "") > agent_status[a].get("ultima_atividade", ""):
                    agent_status[a].update({"status": task.get("status"), "ultima_atividade": task.get("timestamp")})
    return {"agent_count": state.get("agent_count", 0), "agents": list(agent_status.values())}


def extract_scripts(state):
    scripts = state.get("scripts_disponiveis", [])
    return {"scripts_count": len(scripts), "scripts": sorted(scripts)}


def extract_projects(state):
    projects = state.get("projects", [])
    return {"projects_count": len(projects), "projects": projects}


def extract_cron(state):
    schedule = state.get("schedule", {})
    cron_jobs = []
    for freq, items in schedule.items():
        for item in items:
            cron_jobs.append({"frequencia": freq, "job": item})
    return {"cron_jobs": cron_jobs}


def healthcheck():
    results = {}
    all_ok = True
    for f in CRITICAL_FILES:
        exists = os.path.isfile(f)
        results[os.path.basename(f)] = "pass" if exists else "fail"
        if not exists:
            all_ok = True
    state = load_json(STATE_FILE)
    if state:
        results["agent_count"] = "pass" if state.get("agent_count", 0) > 0 else "fail"
        results["scripts_available"] = "pass" if state.get("scripts_disponiveis") else "fail"
    else:
        results["state_file"] = "fail"
        all_ok = False
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": results,
        "timestamp": datetime.now().isoformat(),
    }


def extract_market():
    data = load_json(MARKET_FILE)
    if data is None:
        state = load_json(STATE_FILE)
        if state and state.get("market_intel"):
            return {"fonte": "state_cache", "oportunidades": list(state["market_intel"].values())}
        return None
    return {"fonte": "oportunidades.json", "oportunidades": data if isinstance(data, list) else []}


def summary(state):
    pipeline_data = extract_pipeline(state)
    scripts = state.get("scripts_disponiveis", [])
    dre_data = state.get("dre", {})
    meses = dre_data.get("meses", {})
    ultimo_mes = max(meses.keys()) if meses else None
    dre_receita = meses[ultimo_mes].get("receita_bruta", 0) if ultimo_mes else 0
    health = healthcheck()
    return {
        "agent_count": state.get("agent_count", 0),
        "total_pipeline_value": pipeline_data["total_value"],
        "pipeline_deals": pipeline_data["deals_count"],
        "scripts_count": len(scripts),
        "dre_receita_ultimo_mes": dre_receita,
        "dre_meses_disponiveis": len(meses),
        "projects_count": len(state.get("projects", [])),
        "status": health["status"],
        "ultima_atualizacao": state.get("last_update", ""),
    }


class APIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s - %s\n" % (datetime.now().isoformat(), self.client_address[0], format % args))

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _error(self, msg, status=404):
        self._send_json({"erro": msg}, status)

    def _load_state_or_error(self):
        state = load_json(STATE_FILE)
        if state is None:
            self._error("agent_state.json nao encontrado ou invalido")
            return None
        return state

    def do_OPTIONS(self):
        self._send_json({})

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/api/state":
            state = self._load_state_or_error()
            if state:
                self._send_json(state)
        elif path == "/api/pipeline":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_pipeline(state))
        elif path == "/api/dre":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_dre(state))
        elif path == "/api/agents":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_agents(state))
        elif path == "/api/scripts":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_scripts(state))
        elif path == "/api/projects":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_projects(state))
        elif path == "/api/cron":
            state = self._load_state_or_error()
            if state:
                self._send_json(extract_cron(state))
        elif path == "/api/health":
            self._send_json(healthcheck())
        elif path == "/api/market":
            market = extract_market()
            if market is None:
                self._error("oportunidades.json nao encontrado")
            else:
                self._send_json(market)
        elif path == "/api/summary":
            state = self._load_state_or_error()
            if state:
                self._send_json(summary(state))
        elif path == "" or path == "/":
            state = self._load_state_or_error()
            info = {
                "servico": "BUENOSERV API Central",
                "versao": "2.0",
                "endpoints": [
                    "/api/state", "/api/pipeline", "/api/dre", "/api/agents",
                    "/api/scripts", "/api/projects", "/api/cron", "/api/health",
                    "/api/market", "/api/summary"
                ]
            }
            if state:
                info["agentes"] = state.get("agent_count", 0)
                info["projetos"] = len(state.get("projects", []))
                info["scripts"] = len(state.get("scripts_disponiveis", []))
            self._send_json(info)
        else:
            self._error("Endpoint nao encontrado: " + self.path, 404)


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), APIHandler)
    print("BUENOSERV API rodando em http://localhost:%d" % PORT)
    print("Endpoints: /api/state /api/pipeline /api/dre /api/agents /api/scripts /api/projects /api/cron /api/health /api/market /api/summary")
    print("Pressione Ctrl+C para parar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado.")
        server.server_close()
