#!/usr/bin/env python3
"""Timesheet integrado — registra horas por projeto + aprovação"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar_estado(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def registrar_horas(projeto, engenheiro, horas, descricao, data=None):
    state = carregar_estado()
    if "timesheet" not in state:
        state["timesheet"] = {"registros": [], "aprovacoes": {}}
    data = data or datetime.date.today().isoformat()
    reg = {
        "projeto": projeto,
        "engenheiro": engenheiro,
        "horas": horas,
        "descricao": descricao,
        "data": data,
        "timestamp": datetime.datetime.now().isoformat(),
        "aprovado": False
    }
    state["timesheet"]["registros"].append(reg)
    salvar_estado(state)
    print(f"✅ {horas}h registradas: {engenheiro} → {projeto} ({descricao})")
    return reg

def aprovar_horas(engenheiro=None, projeto=None):
    state = carregar_estado()
    aprovadas = 0
    for r in state.get("timesheet", {}).get("registros", []):
        if not r["aprovado"]:
            if (engenheiro is None or r["engenheiro"] == engenheiro) and \
               (projeto is None or r["projeto"] == projeto):
                r["aprovado"] = True
                aprovadas += 1
    salvar_estado(state)
    print(f"✅ {aprovadas} registros aprovados")
    return aprovadas

def horas_por_projeto(projeto=None):
    state = carregar_estado()
    resumo = {}
    for r in state.get("timesheet", {}).get("registros", []):
        if projeto and r["projeto"] != projeto:
            continue
        p = r["projeto"]
        if p not in resumo:
            resumo[p] = {"total_h": 0, "aprovadas": 0, "engenheiros": set()}
        resumo[p]["total_h"] += r["horas"]
        resumo[p]["engenheiros"].add(r["engenheiro"])
        if r["aprovado"]:
            resumo[p]["aprovadas"] += r["horas"]
    return resumo

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_timesheet.py registrar|aprovar|resumo [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "registrar":
        if len(sys.argv) < 5:
            print("Uso: gen_timesheet.py registrar <projeto> <engenheiro> <horas> <descricao>")
            sys.exit(1)
        registrar_horas(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])
    elif cmd == "aprovar":
        eng = sys.argv[2] if len(sys.argv) > 2 else None
        proj = sys.argv[3] if len(sys.argv) > 3 else None
        aprovar_horas(eng, proj)
    elif cmd == "resumo":
        proj = sys.argv[2] if len(sys.argv) > 2 else None
        resumo = horas_por_projeto(proj)
        for p, info in resumo.items():
            print(f"{p}: {info['total_h']}h ({info['aprovadas']}h aprovadas) - {', '.join(info['engenheiros'])}")
