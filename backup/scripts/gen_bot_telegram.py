#!/usr/bin/env python3
"""Bot Telegram BUENOSERV — notificações e comandos do sistema"""
import json, os, sys, datetime, asyncio
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
TOKEN_FILE = os.path.expanduser("~/.config/opencode/state/telegram_token.json")

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def carregar_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}

def salvar_token(data):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def formatar_num(v):
    return f"R$ {v:,.2f}"

async def enviar_mensagem(bot, chat_id, texto):
    try:
        from telegram import Bot
        b = Bot(token=bot)
        await b.send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

async def notificar_followup():
    """Envia notificação de propostas pendentes há 7+ dias"""
    config = carregar_token()
    bot_token = config.get("bot_token")
    chat_id = config.get("chat_id")
    if not bot_token or not chat_id:
        print("❌ Telegram não configurado. Configure com: --config <token> <chat_id>")
        return

    state = carregar_estado()
    hoje = datetime.date.today()
    alertas = []

    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial" and t["status"] != "concluido":
                ts = t.get("timestamp", "")
                if ts:
                    data = datetime.date.fromisoformat(ts[:10])
                    dias = (hoje - data).days
                    if dias >= 7:
                        alertas.append(f"⚠️ *{proj}* — {dias} dias sem retorno\n   {t.get('observacao','')}")

    if alertas:
        msg = "📬 *Follow-up Automático BUENOSERV*\n\n" + "\n\n".join(alertas)
    else:
        msg = "✅ Nenhuma proposta pendente de follow-up esta semana."

    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

async def comando_status(bot_token, chat_id):
    state = carregar_estado()
    projetos = len(state.get("projects", []))
    tasks_pendentes = sum(1 for t in state.get("tasks", {}).values() for x in t if x["status"] != "concluido")
    dre = state.get("dre", {})
    ultimo_mes = dre.get("meses", {})
    msg = f"📊 *Status BUENOSERV*\n"
    msg += f"📁 Projetos: {projetos}\n"
    msg += f"⏳ Tarefas pendentes: {tasks_pendentes}\n"
    msg += f"🤖 Agentes: {state.get('agent_count', 60)}\n"
    if ultimo_mes:
        ultimo = list(ultimo_mes.values())[-1]
        msg += f"💰 Último DRE: {formatar_num(ultimo.get('receita_bruta',0))} → Lucro {formatar_num(ultimo.get('lucro_liquido',0))}"

    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

async def comando_pipeline(bot_token, chat_id):
    state = carregar_estado()
    lines = ["📈 *Pipeline Comercial*\n"]
    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial":
                obs = t.get("observacao", "")
                status = "✅" if t["status"] == "concluido" else "⏳"
                lines.append(f"{status} *{proj}*: {obs[:80]}")
    msg = "\n".join(lines[:15]) if lines else "Nenhuma oportunidade."

    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

async def comando_dre(bot_token, chat_id):
    state = carregar_estado()
    dre = state.get("dre", {})
    meses = dre.get("meses", {})
    if not meses:
        msg = "❌ Nenhum DRE registrado."
    else:
        ultimo = list(meses.values())[-1]
        msg = f"📋 *DRE — {list(meses.keys())[-1]}/2026*\n"
        msg += f"Receita Bruta: {formatar_num(ultimo['receita_bruta'])}\n"
        msg += f"Custos: {formatar_num(ultimo['custos_servicos'])}\n"
        msg += f"Lucro Bruto: {formatar_num(ultimo['lucro_bruto'])}\n"
        msg += f"Desp. Adm: {formatar_num(ultimo['despesas_administrativas'])}\n"
        msg += f"Desp. Trib: {formatar_num(ultimo['despesas_tributarias'])}\n"
        msg += f"*Lucro Líquido: {formatar_num(ultimo['lucro_liquido'])}*"

    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

async def comando_alerta(bot_token, chat_id):
    state = carregar_estado()
    hoje = datetime.date.today()
    alertas = []
    for p in state.get("projects", []):
        for fase, info in p.get("fases", {}).items():
            if info["status"] == "em_andamento":
                data = datetime.date.fromisoformat(info["data"][:10])
                dias = (hoje - data).days
                if dias > 7:
                    alertas.append(f"🔴 {p['nome']}: '{fase}' parada há {dias} dias")
    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial" and t["status"] != "concluido":
                ts = t.get("timestamp", "")
                if ts:
                    data = datetime.date.fromisoformat(ts[:10])
                    dias = (hoje - data).days
                    alertas.append(f"🟡 {proj}: follow-up pendente ({dias}d)")
    msg = "🔔 *Alertas*\n\n" + "\n".join(alertas[:10]) if alertas else "✅ Nenhum alerta."

    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

async def send_notification(texto, bot_token=None, chat_id=None):
    config = carregar_token()
    bot_token = bot_token or config.get("bot_token")
    chat_id = chat_id or config.get("chat_id")
    if not bot_token or not chat_id:
        return False
    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=texto[:4000], parse_mode='Markdown')
    return True

async def comando_ajuda(bot_token, chat_id):
    msg = """🤖 *BUENOSERV Bot — Comandos*

/status — Visão geral do sistema
/pipeline — Oportunidades comerciais
/dre — Último DRE
/alerta — Alertas ativos
/ajuda — Esta mensagem"""
    from telegram import Bot
    b = Bot(token=bot_token)
    await b.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

def run_bot():
    """Inicia o bot em modo polling"""
    config = carregar_token()
    bot_token = config.get("bot_token")
    if not bot_token:
        print("❌ Configure o token primeiro: gen_bot_telegram.py --config <token> <chat_id>")
        return

    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await comando_status(bot_token, update.effective_chat.id)
    async def pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await comando_pipeline(bot_token, update.effective_chat.id)
    async def dre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await comando_dre(bot_token, update.effective_chat.id)
    async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await comando_alerta(bot_token, update.effective_chat.id)
    async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await comando_ajuda(bot_token, update.effective_chat.id)

    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("pipeline", pipeline))
    app.add_handler(CommandHandler("dre", dre))
    app.add_handler(CommandHandler("alerta", alerta))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("start", ajuda))

    print("🤖 Bot Telegram BUENOSERV rodando... Ctrl+C para parar")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

def run_health_server():
    """Run a simple health endpoint instead of bot when no token configured."""
    from flask import Flask, jsonify
    app_h = Flask(__name__)
    @app_h.route("/")
    def health():
        return jsonify({"servico": "BUENOSERV Telegram", "status": "sem_token",
                        "msg": "Configure com: gen_bot_telegram.py --config <token> <chat_id>"})
    print("🤖 Telegram sem token - rodando health server na porta 8096")
    app_h.run(host="0.0.0.0", port=8096)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        if len(sys.argv) < 4:
            print("Uso: gen_bot_telegram.py --config <bot_token> <chat_id>")
            sys.exit(1)
        salvar_token({"bot_token": sys.argv[2], "chat_id": sys.argv[3]})
        print("✅ Telegram configurado com sucesso!")
        print("   Para testar: gen_bot_telegram.py --testar")
        sys.exit(0)

    elif len(sys.argv) > 1 and sys.argv[1] == "--testar":
        asyncio.run(comando_status(None, None))
        sys.exit(0)

    elif len(sys.argv) > 1 and sys.argv[1] == "--notificar":
        asyncio.run(notificar_followup())
        sys.exit(0)

    elif len(sys.argv) > 1 and sys.argv[1] == "--enviar":
        texto = sys.argv[2] if len(sys.argv) > 2 else "🔔 Notificação automática BUENOSERV"
        asyncio.run(send_notification(texto))
        sys.exit(0)

    else:
        config = carregar_token()
        if not config.get("bot_token"):
            run_health_server()
        else:
            run_bot()
