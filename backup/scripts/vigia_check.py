#!/usr/bin/env python3
"""vigia_check.py — Verificador autônomo de tarefas, prazos e gatilhos"""
import json, os, datetime, sys

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
LOG_FILE = os.path.expanduser("~/.config/opencode/state/vigia.log")

def log(msg):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def check():
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    today = datetime.date.today()
    weekday = today.weekday()  # 0=Monday
    day = today.day
    alertas = []
    acoes = []
    
    # 1. Verificar fases de projeto paradas (>15 dias sem atualização)
    for p in state.get("projects", []):
        for fase, info in p.get("fases", {}).items():
            if info["status"] == "em_andamento":
                try:
                    data_fase = datetime.date.fromisoformat(info["data"][:10])
                    dias = (today - data_fase).days
                    if dias > 15:
                        alertas.append(f"🔴 {p['nome']}: '{fase}' parada há {dias} dias")
                    elif dias > 7:
                        alertas.append(f"🟡 {p['nome']}: '{fase}' sem atualização há {dias} dias")
                except:
                    pass
    
    # 2. Tarefas semanais (segunda-feira)
    if weekday == 0:
        acoes.append("🟡 Ação: Gerar status report semanal")
    
    # 3. Tarefas mensais (dia 1)
    if day == 1:
        acoes.append("🟡 Ação: Fechamento financeiro mensal (DRE)")
        acoes.append("🟡 Ação: Curva S mensal")
    if day == 5:
        acoes.append("🟡 Ação: Follow-up comercial")
    if day == 10:
        acoes.append("🟡 Ação: Auditoria qualidade")
    if day == 15:
        acoes.append("🟡 Ação: Medição de serviços")
    if day == 25:
        acoes.append("🟡 Ação: Pipeline review")
    
    # 4. Verificar lições aprendidas não registradas (exemplo)
    lessons = state.get("memory", {}).get("lessons_learned", [])
    
    # Resultado
    if not alertas and not acoes:
        log("✅ Vigia: Nada a reportar")
    else:
        for a in alertas + acoes:
            log(a)
    
    return alertas, acoes

if __name__ == "__main__":
    print(f"=== Vigia Check — {datetime.datetime.now().isoformat()[:10]} ===\n")
    alertas, acoes = check()
    print(f"\n=== Fim — {len(alertas)} alertas, {len(acoes)} ações ===")
