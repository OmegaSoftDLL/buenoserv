#!/usr/bin/env python3
"""BUENOSERV CAD/DWG Service — geração de diagramas técnicos via API."""
import os, json, subprocess, tempfile, logging
from pathlib import Path
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TEMPLATES_DIR = Path("/tmp/opencode/templates")
OUTPUT_DIR = Path("/tmp/opencode/cad_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def home():
    return jsonify({
        "servico": "BUENOSERV CAD/DWG Service",
        "versao": "1.0",
        "comandos": ["unifilar", "telecom", "rack", "fibra", "singleline"]
    })

@app.route("/gerar/<tipo>", methods=["POST"])
def gerar(tipo):
    data = request.json or {}
    projeto = data.get("projeto", "sem_nome")
    tensao = data.get("tensao", "138kV")
    barramentos = data.get("barramentos", 4)
    
    script = TEMPLATES_DIR / "gen_dwg.py"
    if not script.exists():
        return jsonify({"erro": "gen_dwg.py nao encontrado"}), 500

    outfile = OUTPUT_DIR / f"{projeto}_{tipo}.dwg"
    
    try:
        result = subprocess.run(
            ["python3", str(script), tipo, "--projeto", projeto,
             "--tensao", tensao, "--barramentos", str(barramentos),
             "--output", str(outfile)],
            capture_output=True, text=True, timeout=60
        )
        if outfile.exists():
            return send_file(str(outfile), as_attachment=True,
                           download_name=f"{projeto}_{tipo}.dwg")
        else:
            return jsonify({
                "saida": result.stdout,
                "erro": result.stderr[:500] if result.stderr else "arquivo nao gerado"
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({"erro": "timeout na geracao"}), 504
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/gerar", methods=["POST"])
def gerar_personalizado():
    data = request.json or {}
    tipo = data.get("tipo", "unifilar")
    return gerar(tipo)

@app.route("/listar")
def listar():
    arquivos = [str(f.name) for f in OUTPUT_DIR.iterdir() if f.suffix in (".dwg", ".dxf", ".pdf")]
    return jsonify({"arquivos": arquivos, "total": len(arquivos)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8510))
    print(f"⚡ BUENOSERV CAD/DWG Service")
    print(f"   Porta: {port}")
    print(f"   Output: {OUTPUT_DIR}")
    app.run(host="0.0.0.0", port=port, debug=False)
