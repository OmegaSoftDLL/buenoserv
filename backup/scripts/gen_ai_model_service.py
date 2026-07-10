import sys, subprocess, os, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

REQUIRED = ["torch", "transformers", "sentence_transformers", "flask"]

for pkg in REQUIRED:
    try:
        __import__(pkg.replace("-", "_").replace(".", "_"))
        log.info(f"{pkg} já instalado")
    except ImportError:
        log.warning(f"Instalando {pkg}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

import torch, flask, json, numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from transformers import pipeline

app = Flask(__name__)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
log.info(f"Dispositivo: {DEVICE}")
if DEVICE == "cuda":
    log.info(f"GPU: {torch.cuda.get_device_name(0)}")
    log.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

log.info("Carregando modelo sentence-transformers/all-MiniLM-L6-v2...")
modelo_embed = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=DEVICE)
log.info("Modelo de embedding carregado com sucesso")

log.info("Carregando modelo de completação (pequeno)...")
try:
    modelo_completar = pipeline(
        "text-generation",
        model="distilgpt2",
        device=0 if DEVICE == "cuda" else -1,
    )
    log.info("Modelo de completação carregado")
except Exception as e:
    log.warning(f"Falha ao carregar modelo de completação: {e}")
    modelo_completar = None

AGENTES = [
    {"nome": "Dashboard Financeiro", "descricao": "Relatórios financeiros, contas a pagar/receber, fluxo de caixa, DRE"},
    {"nome": "Comissionamento Elétrico", "descricao": "Comissionamento de subestações, painéis elétricos, transformadores, proteção"},
    {"nome": "Orçamento de Obras", "descricao": "Orçamentação, BIM, Cronograma, EAP,BOM, medição de obras"},
    {"nome": "Documentação Técnica", "descricao": "Documentos, DWG, PDF, relatórios, memoriais descritivos"},
    {"nome": "Assistente Administrativo", "descricao": "Emails, holerites, contratos, propostas, conciliação bancária"},
]


@app.route("/modelo", methods=["GET"])
def modelo_info():
    return jsonify({
        "modelo_embedding": "sentence-transformers/all-MiniLM-L6-v2",
        "modelo_completacao": "distilgpt2" if modelo_completar else None,
        "dispositivo": DEVICE,
        "gpu": torch.cuda.get_device_name(0) if DEVICE == "cuda" else None,
        "dimensao_embedding": modelo_embed.get_sentence_embedding_dimension(),
        "agentes_indexados": len(AGENTES),
    })


@app.route("/embed", methods=["POST"])
def embed():
    dados = request.get_json()
    if not dados or "texto" not in dados:
        return jsonify({"erro": "Campo 'texto' é obrigatório"}), 400
    texto = dados["texto"]
    emb = modelo_embed.encode(texto, convert_to_numpy=True)
    return jsonify({
        "texto": texto,
        "dimensao": emb.shape[0],
        "embedding": emb.tolist(),
        "dispositivo": DEVICE,
    })


@app.route("/search", methods=["POST"])
def search():
    dados = request.get_json()
    if not dados or "texto" not in dados:
        return jsonify({"erro": "Campo 'texto' é obrigatório"}), 400
    texto = dados["texto"]
    top_k = dados.get("top_k", 5)

    emb_query = modelo_embed.encode(texto, normalize_embeddings=True)
    emb_agentes = modelo_embed.encode(
        [a["nome"] + " - " + a["descricao"] for a in AGENTES],
        normalize_embeddings=True,
    )
    scores = np.dot(emb_agentes, emb_query)
    indices = np.argsort(scores)[::-1][:top_k]

    resultados = []
    for i in indices:
        resultados.append({
            "agente": AGENTES[i]["nome"],
            "descricao": AGENTES[i]["descricao"],
            "score": float(scores[i]),
        })
    return jsonify({"consulta": texto, "resultados": resultados})


@app.route("/completar", methods=["POST"])
def completar():
    dados = request.get_json()
    if not dados or "texto" not in dados:
        return jsonify({"error": "Campo 'texto' é obrigatório"}), 400
    if modelo_completar is None:
        return jsonify({"error": "Modelo de completação não disponível"}), 503
    texto = dados["texto"]
    max_len = dados.get("max_length", 100)
    out = modelo_completar(texto, max_length=max_len, num_return_sequences=1)[0]
    return jsonify({"input": texto, "completacao": out["generated_text"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8560, debug=False)