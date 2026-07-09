#!/usr/bin/env python3
import os, json, re, logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
WHATSAPP_LOG = "/tmp/opencode/whatsapp_log.json"

# Config — trocar para Evolution API real quando disponível
EVO_API_URL = os.environ.get("EVO_API_URL", "")
EVO_API_KEY = os.environ.get("EVO_API_KEY", "")
INSTANCE = os.environ.get("EVO_INSTANCE", "buenoserv")
MODO_SIMULADO = not (EVO_API_URL and EVO_API_KEY)

def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

def log_msg(direcao, numero, mensagem):
    log = []
    if os.path.exists(WHATSAPP_LOG):
        with open(WHATSAPP_LOG) as f: log = json.load(f)
    log.append({"direcao": direcao, "numero": numero, "mensagem": mensagem, "data": datetime.now().isoformat()})
    with open(WHATSAPP_LOG, "w") as f: json.dump(log[-100:], f, indent=2, ensure_ascii=False)

def enviar_whatsapp(numero, mensagem):
    if MODO_SIMULADO:
        log_msg("envio", numero, mensagem)
        print(f"📱 [SIMULADO] WhatsApp para {numero}: {mensagem[:60]}...")
        return True
    try:
        import requests
        payload = {"number": numero, "text": mensagem, "delay": 1}
        headers = {"apikey": EVO_API_KEY}
        r = requests.post(f"{EVO_API_URL}/message/sendText/{INSTANCE}", json=payload, headers=headers, timeout=15)
        if r.ok:
            log_msg("envio", numero, mensagem)
            return True
        else:
            print(f"❌ WhatsApp API erro: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"❌ WhatsApp erro: {e}")
        return False

def processar_comando(numero, texto):
    t = texto.lower().strip()
    state = load_state()

    if t in ("/status", "status"):
        return f"""🟢 BUENOSERV — Status
🤖 Agentes: {state.get('agent_count', 81)}
📜 Scripts: {state.get('scripts_disponiveis', 0) or 0}
🏗️ Projetos: {len(state.get('projects', []))}
📊 Pipeline: ativo
✅ Sistema operacional"""

    if t in ("/pipeline", "pipeline"):
        tasks = []
        for p, ts in state.get('tasks', {}).items():
            for ta in ts:
                if 'comercial' in ta.get('agente',''):
                    tasks.append(ta)
        if not tasks:
            return "📋 Pipeline vazio"
        res = "📋 *Pipeline Comercial*\n"
        for i, ta in enumerate(tasks[:5], 1):
            res += f"{i}. {ta.get('observacao','')[:50]} — {ta.get('status','')}\n"
        res += f"\nTotal: {len(tasks)} oportunidades"
        return res

    if t in ("/dre", "dre"):
        dre = state.get('dre', {})
        meses = dre.get('meses', {})
        if not meses:
            return "💰 DRE não disponível"
        ultimo = list(meses.values())[-1]
        return f"""💰 *DRE Financeiro*
Receita: R$ {ultimo.get('receita_bruta',0):,.2f}
Custos: R$ {ultimo.get('custos_operacionais',0):,.2f}
Lucro: R$ {ultimo.get('lucro_liquido',0):,.2f}"""

    if t in ("/contato", "contato", "contato humano"):
        return """📞 *Falar com Ricardo Bueno*
📧 ricardo.bueno@buenoservengenharia.com
📱 (19) — consultar
💬 Disponivel para reuniao online"""

    if t in ("/ajuda", "ajuda", "/help", "help", "menu", "/menu"):
        return """🤖 *BUENOSERV Bot — Comandos*
/status — Status do sistema
/pipeline — Pipeline comercial
/dre — Resumo financeiro
/proposta — Solicitar proposta
/contato — Falar com engenheiro
/ajuda — Este menu"""

    if any(p in t for p in ("proposta", "orcamento", "orçamento")):
        enviar_whatsapp(numero, "Ótimo! Um engenheiro entrará em contato em até 24h para elaborar sua proposta.")
        return "✅ Solicitação de proposta registrada"

    return f"""Olá! 👋
Eu sou o assistente virtual da *BUENOSERV*.
Comandos disponíveis: /status, /pipeline, /dre, /proposta, /contato, /ajuda
Ou me pergunte sobre nossos serviços de engenharia!"""

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"erro": "sem dados"}), 400
    numero = data.get("from", data.get("sender", "unknown"))
    mensagem = data.get("text", data.get("message", ""))
    log_msg("recebido", numero, mensagem)
    resposta = processar_comando(numero, mensagem)
    if resposta:
        enviar_whatsapp(numero, resposta)
    return jsonify({"status": "ok"}), 200

@app.route("/enviar", methods=["POST"])
def enviar():
    data = request.json
    numero = data.get("numero", "")
    mensagem = data.get("mensagem", "")
    if not numero or not mensagem:
        return jsonify({"erro": "numero e mensagem obrigatorios"}), 400
    ok = enviar_whatsapp(numero, mensagem)
    return jsonify({"status": "enviado" if ok else "erro"}), 200 if ok else 500

@app.route("/log", methods=["GET"])
def log():
    if os.path.exists(WHATSAPP_LOG):
        with open(WHATSAPP_LOG) as f: return jsonify(json.load(f))
    return jsonify([])

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "modo": "simulado" if MODO_SIMULADO else "real",
        "instancia": INSTANCE,
        "evo_api_url": EVO_API_URL or "não configurado"
    })

if __name__ == "__main__":
    print(f"📱 BUENOSERV WhatsApp Bot")
    print(f"   Modo: {'SIMULADO' if MODO_SIMULADO else 'REAL com Evolution API'}")
    if MODO_SIMULADO:
        print(f"   Para modo real: export EVO_API_URL=... EVO_API_KEY=... EVO_INSTANCE=buenoserv")
    print(f"   Webhook: POST /webhook")
    print(f"   Enviar:  POST /enviar")
    print(f"   Log:     GET /log")
    app.run(host="0.0.0.0", port=8095, debug=True)
