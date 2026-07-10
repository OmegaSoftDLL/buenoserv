#!/usr/bin/env python3
"""BUENOSERV Smart Router — Escolhe inteligentemente qual modelo usar para cada agente."""
import os, json, re, requests, logging, time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("router")

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")
NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")

# Cache de latência dos modelos
LATENCY_CACHE = {}

MODEL_TIERS = {
    "premium": {
        "engenharia": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "documentos": "mistralai/mistral-large-3-675b-instruct-2512",
        "analise": "meta/llama-3.1-70b-instruct",
        "rapido": "meta/llama-3.1-8b-instruct",
    },
    "local": {
        "chat": "hermes3",
        "rapido": "llama3.2:3b",
    }
}

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
        "crm": "meta/llama-3.1-8b-instruct",
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

def classificar_pergunta(pergunta: str, agente: str = "") -> dict:
    pl = pergunta.lower()
    palavras = re.findall(r'\w+', pl)
    
    # Detectar tipo de tarefa
    if any(p in pl for p in ["proposta", "contrato", "documento", "relatorio", "artigo", "especificacao"]):
        return {"tipo": "documento", "modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 10}
    if any(p in pl for p in ["calculo", "norma", "tecnico", "especificacao tecnica", "comissionamento", "subestacao"]):
        return {"tipo": "engenharia", "modelo": "nvidia/llama-3.3-nemotron-super-49b-v1", "prioridade": 9}
    if any(p in pl for p in ["email", "follow", "proposta comercial", "orcamento", "cliente"]):
        return {"tipo": "comercial", "modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 7}
    if any(p in pl for p in ["imposto", "dre", "fluxo", "financeiro", "pagar", "receber"]):
        return {"tipo": "financeiro", "modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 7}
    if any(p in pl for p in ["ola", "oi", "bom dia", "obrigado", "tudo bem"]):
        return {"tipo": "chat", "modelo": "meta/llama-3.1-8b-instruct", "prioridade": 1}

    # Verificar mapa de agente
    if agente and agente in AGENT_MODEL_MAP:
        for palavra, modelo in AGENT_MODEL_MAP[agente].items():
            if palavra in palavras:
                return {"tipo": agente, "modelo": modelo, "prioridade": 8}

    return {"tipo": "geral", "modelo": "mistralai/mistral-large-3-675b-instruct-2512", "prioridade": 5}


def consultar_ollama(modelo: str, pergunta: str, sistema: str = "", contexto: str = "") -> str:
    payload = {
        "model": modelo,
        "prompt": pergunta,
        "system": sistema[:1500],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1024}
    }
    if contexto:
        payload["system"] += f"\n\nContexto:\n{contexto[:1000]}"
    try:
        r = requests.post(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
                         json=payload, timeout=120)
        return r.json().get("response", "") if r.ok else ""
    except:
        return ""


def consultar_nvidia(modelo: str, pergunta: str, sistema: str = "", contexto: str = "") -> str:
    messages = [{"role": "system", "content": sistema[:2000]}]
    if contexto:
        messages[0]["content"] += f"\n\n{contexto[:1500]}"
    messages.append({"role": "user", "content": pergunta})
    
    try:
        r = requests.post(
            f"{NVIDIA_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"},
            json={"model": modelo, "messages": messages, "temperature": 0.3, "max_tokens": 1024},
            timeout=180
        )
        if r.ok:
            return r.json()["choices"][0]["message"]["content"]
        log.warning(f"NVIDIA {modelo}: {r.status_code} {r.text[:200]}")
    except requests.exceptions.RequestException as e:
        log.warning(f"NVIDIA offline: {e}")
    return ""


def inferir(pergunta: str, sistema: str = "", contexto: str = "", agente: str = "",
            departamento: str = "") -> dict:
    """Router principal — escolhe modelo e fallback automaticamente."""
    classificacao = classificar_pergunta(pergunta, agente or departamento)
    modelo_escolhido = classificacao["modelo"]
    modelo_usado = modelo_escolhido
    origem = "nvidia"
    inicio = time.time()

    # Tentar NVIDIA primeiro
    if classificacao["prioridade"] > 3:
        resposta = consultar_nvidia(modelo_escolhido, pergunta, sistema, contexto)
        if resposta:
            latencia = time.time() - inicio
            log.info(f"NVIDIA {modelo_escolhido}: {latencia:.1f}s")
            return {"resposta": resposta, "modelo": modelo_escolhido, "origem": "nvidia", "latencia": latencia}

    # Fallback: Hermes local
    log.info(f"Fallback NVIDIA -> Hermes local para: {pergunta[:50]}")
    resposta = consultar_ollama("hermes3", pergunta, sistema, contexto)
    if resposta:
        latencia = time.time() - inicio
        modelo_usado = "hermes3"
        origem = "local"
        return {"resposta": resposta, "modelo": modelo_usado, "origem": origem, "latencia": latencia}

    # Fallback final: Llama 3.2 3B (ultra-rápido)
    log.info(f"Fallback Hermes -> Llama 3.2 para: {pergunta[:50]}")
    resposta = consultar_ollama("llama3.2:3b", pergunta, sistema, contexto)
    latencia = time.time() - inicio
    modelo_usado = "llama3.2:3b"
    origem = "local_fallback"
    return {"resposta": resposta or "[Nenhum modelo disponivel]", "modelo": modelo_usado,
            "origem": origem, "latencia": latencia}


def testar_modelos() -> dict:
    """Testa conectividade com todos os modelos."""
    resultados = {}
    # NVIDIA
    try:
        r = requests.get(f"{NVIDIA_BASE}/models", headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"}, timeout=10)
        resultados["nvidia_api"] = "online" if r.ok else f"erro {r.status_code}"
    except:
        resultados["nvidia_api"] = "offline"
    # Ollama local
    try:
        r = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=5)
        if r.ok:
            modelos = [m["name"] for m in r.json().get("models", [])]
            resultados["ollama"] = f"online ({', '.join(modelos)})"
        else:
            resultados["ollama"] = "erro"
    except:
        resultados["ollama"] = "offline"
    return resultados


if __name__ == "__main__":
    import sys
    print("BUENOSERV Smart Router — Teste")
    print(f"NVIDIA API: {NVIDIA_BASE}")
    print(f"Ollama: {OLLAMA_HOST}:{OLLAMA_PORT}")
    print(f"\nModelos disponiveis:\n  Premium: {list(MODEL_TIERS['premium'].values())}\n  Local: {list(MODEL_TIERS['local'].values())}")
    
    pergunta = sys.argv[1] if len(sys.argv) > 1 else "O que e comissionamento de subestacao 138kV?"
    print(f"\nPergunta: {pergunta}")
    classe = classificar_pergunta(pergunta)
    print(f"Classificacao: {classe}")
    
    r = inferir(pergunta, "Voce e um engenheiro especialista.")
    print(f"\nResposta ({r['modelo']} / {r['origem']}): {r['resposta'][:200]}")
    print(f"Latencia: {r.get('latencia', 0):.1f}s")
