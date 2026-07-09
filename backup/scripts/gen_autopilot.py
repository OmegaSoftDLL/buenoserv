#!/usr/bin/env python3
"""Autopilot BUENOSERV — orquestrador inteligente que analisa estado e toma decisões"""
import json, os, sys, datetime, subprocess

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
LOG_FILE = os.path.expanduser("~/.config/opencode/state/autopilot.log")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"  {msg}")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def analisar_pipeline():
    """Analisa pipeline e sugere próximas ações"""
    state = carregar()
    acoes = []
    hoje = datetime.date.today()
    
    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial":
                ts = t.get("timestamp", "")
                if ts and t["status"] != "concluido":
                    data = datetime.date.fromisoformat(ts[:10])
                    dias = (hoje - data).days
                    if dias >= 7 and "follow" not in str(acoes).lower():
                        acoes.append(("followup", proj, dias, "Enviar follow-up automático"))
    return acoes

def analisar_projetos():
    """Analisa projetos parados"""
    state = carregar()
    alertas = []
    hoje = datetime.date.today()
    for p in state.get("projects", []):
        for fase, info in p.get("fases", {}).items():
            if info["status"] == "em_andamento":
                data = datetime.date.fromisoformat(info["data"][:10])
                dias = (hoje - data).days
                if dias > 15:
                    alertas.append(("projeto_parado", p["nome"], dias, f"Fase {fase} parada há {dias} dias"))
    return alertas

def analisar_dashboard():
    """Verifica se dashboard está rodando"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", 8080))
        s.close()
        return True
    except:
        return False

def executar_acao(tipo, alvo, dados):
    """Executa uma ação automaticamente"""
    log(f"⚡ Ação: {tipo} → {alvo} ({dados})")
    
    if tipo == "followup":
        log(f"  📧 Follow-up necessário para {alvo} (D+{dados})")
        # Tentar disparar via Telegram se configurado
        try:
            subprocess.run([sys.executable, "/tmp/opencode/templates/gen_bot_telegram.py", "--enviar",
                          f"⚠️ Follow-up: {alvo} — {dados} dias sem retorno"], timeout=10)
            log(f"  ✅ Notificação Telegram enviada")
        except:
            log(f"  ℹ️ Telegram não configurado")
    
    elif tipo == "projeto_parado":
        log(f"  🔴 Alerta: {alvo} — {dados}")
        try:
            subprocess.run([sys.executable, "/tmp/opencode/templates/gen_bot_telegram.py", "--enviar",
                          f"🔴 Projeto parado: {alvo}"], timeout=10)
        except:
            pass

def ciclo_autopilot():
    log(f"\n{'='*50}")
    log(f"🤖 AUTOPILOT — {datetime.datetime.now():%d/%m/%Y %H:%M}")
    
    state = carregar()
    
    # 1. Pipeline
    acoes = analisar_pipeline()
    if acoes:
        log(f"📊 Pipeline: {len(acoes)} ações recomendadas")
        for tipo, alvo, dias, desc in acoes:
            executar_acao(tipo, alvo, dias)
    else:
        log(f"📊 Pipeline: OK")
    
    # 2. Projetos
    alertas = analisar_projetos()
    if alertas:
        log(f"🏗️ Projetos: {len(alertas)} alertas")
        for tipo, alvo, dias, desc in alertas:
            executar_acao(tipo, alvo, desc)
    else:
        log(f"🏗️ Projetos: OK")
    
    # 3. Dashboard
    if not analisar_dashboard():
        log(f"📊 Dashboard: PARADO — iniciando...")
        try:
            subprocess.Popen([sys.executable, "/tmp/opencode/templates/serve_dashboard.py"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log(f"  ✅ Dashboard reiniciado")
        except Exception as e:
            log(f"  ❌ Erro ao iniciar: {e}")
    else:
        log(f"📊 Dashboard: ONLINE (porta 8080)")
    
    # 4. Backup automático (se sexta-feira)
    if datetime.date.today().weekday() == 4:
        log(f"💾 Backup semanal: iniciando...")
        try:
            subprocess.run([sys.executable, "/tmp/opencode/templates/gen_backup.py"], timeout=30)
            log(f"  ✅ Backup concluído")
        except Exception as e:
            log(f"  ❌ Erro backup: {e}")
    
    # 5. DRE mensal (se dia 25+)
    if datetime.date.today().day >= 25:
        log(f"💰 Fechamento mensal: lembrar de atualizar DRE")
    
    # 6. Atualizar state
    ultima_execucao = datetime.datetime.now().isoformat()
    state.setdefault("autopilot", {"historico": []})
    state["autopilot"]["ultima_execucao"] = ultima_execucao
    state["autopilot"]["historico"].append({
        "timestamp": ultima_execucao,
        "acoes": len(acoes) + len(alertas)
    })
    salvar(state)
    
    log(f"✅ Ciclo concluído — {len(acoes)+len(alertas)} ações processadas")

if __name__ == "__main__":
    ciclo_autopilot()
