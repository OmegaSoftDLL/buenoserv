#!/usr/bin/env python3
"""BUENOSERV Hermes Bridge v2 — Router Inteligente com NVIDIA API + fallback local."""
import os, json, re, requests, logging, time, sys
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hermes")

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY",
    "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")
NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "host.docker.internal")
OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

AGENTS_DIR = Path(os.path.expanduser("~/.config/opencode/agents"))
DEPARTAMENTO = os.environ.get("DEPARTAMENTO", "hermes").upper()

AGENT_MODEL_MAP = {
    "engenharia": {
        "comissionamento": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "subestacao": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "protecao": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "scada": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "telecom": "mistralai/mistral-large-3-675b-instruct-2512",
        "documentacao": "mistralai/mistral-large-3-675b-instruct-2512",
        "normas": "meta/llama-3.1-70b-instruct",
        "orcamento": "mistralai/mistral-large-3-675b-instruct-2512",
    },
    "comercial": {
        "proposta": "mistralai/mistral-large-3-675b-instruct-2512",
        "contrato": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "email": "meta/llama-3.1-8b-instruct",
        "negociacao": "nvidia/llama-3.3-nemotron-super-49b-v1",
    },
    "financeiro": {
        "dre": "mistralai/mistral-large-3-675b-instruct-2512",
        "imposto": "mistralai/mistral-large-3-675b-instruct-2512",
        "fluxo": "meta/llama-3.1-8b-instruct",
        "nfe": "meta/llama-3.1-8b-instruct",
    },
    "projetos": {
        "cronograma": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "eap": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "risco": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "qualidade": "mistralai/mistral-large-3-675b-instruct-2512",
    },
    "suprimentos": {
        "compra": "meta/llama-3.1-8b-instruct",
        "contrato": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "rfp": "mistralai/mistral-large-3-675b-instruct-2512",
    },
    "tecnico": {
        "instalacao": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "teste": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "ferramenta": "meta/llama-3.1-8b-instruct",
    }
}

SYSTEM_PROMPTS = {
    "ENGENHARIA": "Voce e um engenheiro especialista em subestacoes, telecom, SCADA e protecao.",
    "COMERCIAL": "Voce e um consultor comercial de engenharia. Seja persuasivo e profissional.",
    "FINANCEIRO": "Voce e um analista financeiro especializado em DRE, fluxo de caixa e impostos.",
    "PROJETOS": "Voce e um gerente de projetos de engenharia.",
    "SUPRIMENTOS": "Voce e um especialista em compras e contratos de engenharia.",
    "TECNICO": "Voce e um tecnico especialista em comissionamento e instalacao.",
    "HERMES": "Voce e a inteligencia central da BUENOSERV."
}

def carregar_agente(nome):
    path = AGENTS_DIR / f"{nome}.md"
    if not path.exists(): return None
    with open(path) as f: return f.read()

def classificar(pergunta: str, departamento: str = "") -> dict:
    pl = pergunta.lower()
    palavras = re.findall(r'\w+', pl)
    if any(p in pl for p in ["proposta", "contrato", "documento", "relatorio", "especificacao"]):
        return {"modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 10}
    if any(p in pl for p in ["calculo", "norma", "tecnico", "comissionamento", "subestacao", "138kv", "500kv"]):
        return {"modelo": "nvidia/llama-3.3-nemotron-super-49b-v1", "prioridade": 9}
    if any(p in pl for p in ["email", "follow", "proposta comercial", "orcamento", "cliente", "venda"]):
        return {"modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 7}
    if any(p in pl for p in ["imposto", "dre", "fluxo", "financeiro", "pagar", "receber", "nfe"]):
        return {"modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 7}
    if any(p in pl for p in ["ola", "oi", "bom dia", "obrigado", "tudo bem", "teste"]):
        return {"modelo": "meta/llama-3.1-8b-instruct", "prioridade": 1}
    if departamento and departamento in AGENT_MODEL_MAP:
        for palavra, modelo in AGENT_MODEL_MAP[departamento].items():
            if palavra in palavras:
                return {"modelo": modelo, "prioridade": 8}
    return {"modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 5}

def consultar_nvidia(modelo: str, messages: list) -> str:
    try:
        r = requests.post(f"{NVIDIA_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"},
            json={"model": modelo, "messages": messages, "temperature": 0.3, "max_tokens": 1500},
            timeout=180)
        if r.ok: return r.json()["choices"][0]["message"]["content"]
        log.warning(f"NVIDIA {modelo}: {r.status_code}")
    except Exception as e:
        log.warning(f"NVIDIA erro: {e}")
    return ""

def consultar_ollama(modelo: str, pergunta: str, system: str) -> str:
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate",
            json={"model": modelo, "prompt": pergunta, "system": system[:2000],
                  "stream": False, "options": {"temperature": 0.3, "num_predict": 1024}},
            timeout=120)
        if r.ok: return r.json().get("response", "")
    except: pass
    return ""

def inferir(pergunta: str, contexto: str = "", departamento: str = "") -> dict:
    system = SYSTEM_PROMPTS.get(departamento.upper(), SYSTEM_PROMPTS["HERMES"])
    if contexto: system += f"\n\nContexto:\n{contexto[:1500]}"
    
    classe = classificar(pergunta, departamento)
    modelo = classe["modelo"]
    inicio = time.time()
    
    # Tentar NVIDIA (para tudo que nao for chat)
    if classe["prioridade"] > 2:
        messages = [{"role": "system", "content": system[:2000]},
                     {"role": "user", "content": pergunta}]
        resp = consultar_nvidia(modelo, messages)
        if resp:
            lat = time.time() - inicio
            log.info(f"NVIDIA {modelo} OK em {lat:.1f}s")
            return {"resposta": resp, "modelo": modelo, "origem": "nvidia", "latencia_s": round(lat, 1)}
        log.info(f"NVIDIA {modelo} falhou, fallback local")
    
    # Fallback: Hermes 3 local (GPU)
    resp = consultar_ollama("hermes3", pergunta, system)
    if resp:
        lat = time.time() - inicio
        return {"resposta": resp, "modelo": "hermes3", "origem": "local", "latencia_s": round(lat, 1)}
    
    # Fallback final: Llama 3.2 3B
    resp = consultar_ollama("llama3.2:3b", pergunta, system)
    lat = time.time() - inicio
    return {"resposta": resp or "[Nenhum modelo disponivel]", "modelo": "llama3.2:3b",
            "origem": "local_fallback", "latencia_s": round(lat, 1)}

def buscar_agente_relevante(pergunta):
    pl = pergunta.lower()
    keywords = {
        "telecom": ["telecom", "fibra", "dwdm", "sdh", "radio", "gpon", "mpls", "otn"],
        "subestacao": ["subestacao", "se", "138kv", "500kv", "alta tensao"],
        "protecao": ["protecao", "rele", "curva", "iec 61850"],
        "scada": ["scada", "ems", "rtu", "supervisao", "controle"],
        "comissionamento": ["comissionamento", "fat", "sat", "teste", "startup"],
        "data_center": ["data center", "datacenter", "tier", "ups", "climatizacao"],
        "cyber": ["cyber", "seguranca", "firewall", "iec 62351"],
        "dwg": ["dwg", "cad", "desenho", "diagrama", "unifilar"],
        "orcamento": ["orcamento", "proposta", "preco", "valor", "custo"],
        "cronograma": ["cronograma", "prazo", "eap", "project"],
        "contrato": ["contrato", "juridico", "legal"],
    }
    for agente, palavras in keywords.items():
        if any(p in pl for p in palavras): return agente
    return ""

@app.route("/")
def home():
    nvidia = "online"
    gpu = "ativada"
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if not r.ok: gpu = "offline"
    except: gpu = "offline"
    try:
        r = requests.get(f"{NVIDIA_BASE}/models", headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"}, timeout=5)
        if not r.ok: nvidia = f"erro {r.status_code}"
    except: nvidia = "offline"
    return jsonify({
        "servico": "BUENOSERV Smart Router",
        "nvidia_api": nvidia,
        "gpu_local": gpu,
        "modelos": {
            "premium": ["nemotron-super-49b", "mistral-large-3-675b", "llama-3.1-70b", "llama-3.1-8b"],
            "local": ["hermes3", "llama3.2:3b"]
        }
    })

@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.json or {}
    pergunta = data.get("pergunta", "")
    contexto = data.get("contexto", "")
    departamento = data.get("departamento", buscar_agente_relevante(pergunta))
    if not pergunta:
        return jsonify({"erro": "pergunta obrigatoria"}), 400
    resultado = inferir(pergunta, contexto, departamento)
    return jsonify({"pergunta": pergunta, "resposta": resultado["resposta"],
        "modelo": resultado["modelo"], "origem": resultado["origem"],
        "latencia_s": resultado["latencia_s"]})

@app.route("/router/testar")
def testar_router():
    resultados = {"nvidia": {}, "local": {}}
    try:
        r = requests.get(f"{NVIDIA_BASE}/models",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"}, timeout=10)
        resultados["nvidia"]["api"] = "online" if r.ok else f"erro {r.status_code}"
    except: resultados["nvidia"]["api"] = "offline"
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.ok:
            modelos = [m["name"] for m in r.json().get("models", [])]
            resultados["local"]["ollama"] = modelos
    except: resultados["local"]["ollama"] = []
    return jsonify(resultados)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8580))
    print(f"BUENOSERV Smart Router")
    print(f"  NVIDIA: {NVIDIA_BASE}")
    print(f"  Ollama: {OLLAMA_URL}")
    print(f"  Porta: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
