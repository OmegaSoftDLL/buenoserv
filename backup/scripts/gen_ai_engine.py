#!/usr/bin/env python3
"""BUENOSERV AI Inference Engine — Motor de IA para os departamentos usando GPU."""
import os, json, logging, subprocess, threading, time
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DEPARTAMENTO = os.environ.get("DEPARTAMENTO", "IA").upper()
STATE_FILE = Path(os.path.expanduser("~/.config/opencode/state/agent_state.json"))

# Verificar GPU disponivel
try:
    result = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free", "--format=csv,noheader"],
                          capture_output=True, text=True, timeout=10)
    GPUS = [g.strip() for g in result.stdout.strip().split("\n") if g.strip()]
except:
    GPUS = []

MODELS_DIR = Path("/mnt/ssd/buenoserv/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def carregar_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

@app.route("/")
def home():
    return jsonify({
        "servico": f"BUENOSERV AI Engine - {DEPARTAMENTO}",
        "gpus_disponiveis": len(GPUS),
        "gpus": GPUS,
        "modelos": [f.name for f in MODELS_DIR.iterdir() if f.is_dir()]
    })

@app.route("/gpu")
def gpu_status():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total",
                           "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
        gpus = [dict(zip(["index","name","temp","util","mem_used","mem_total"], g.strip().split(", "))) for g in r.stdout.strip().split("\n") if g.strip()]
        return jsonify({"gpus": gpus, "total": len(gpus)})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/inferir/<modelo>", methods=["POST"])
def inferir(modelo):
    """Simula inferencia de IA usando GPU (placeholder para modelos reais)."""
    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"erro": "prompt obrigatorio"}), 400
    
    start = time.time()
    # Simulacao de inferencia GPU (placeholder)
    time.sleep(0.5)
    elapsed = time.time() - start
    
    return jsonify({
        "modelo": modelo,
        "prompt": prompt[:100],
        "resposta": f"[{modelo}] Processado via GPU: {prompt[:50]}...",
        "tempo_segundos": round(elapsed, 2),
        "gpu_utilizada": GPUS[0] if GPUS else "nenhuma"
    })

@app.route("/treinar", methods=["POST"])
def treinar():
    """Simula fine-tuning de modelo (placeholder)."""
    data = request.json or {}
    dataset = data.get("dataset", "engenharia")
    epocas = data.get("epocas", 3)
    
    return jsonify({
        "status": "simulado",
        "dataset": dataset,
        "epocas": epocas,
        "observacao": "Implementar com PyTorch/TensorFlow quando modelos reais disponiveis"
    })

@app.route("/modelos")
def listar_modelos():
    modelos = []
    for f in MODELS_DIR.iterdir():
        if f.is_dir():
            size = sum(f.stat().st_size for f in f.rglob("*")) if any(f.rglob("*")) else 0
            modelos.append({"nome": f.name, "tamanho_mb": round(size/1024/1024, 1)})
    return jsonify({"modelos": modelos})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8550))
    print(f"🧠 BUENOSERV AI Engine - {DEPARTAMENTO}")
    print(f"   GPUs: {len(GPUS)}")
    for g in GPUS:
        print(f"     - {g}")
    print(f"   Porta: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
