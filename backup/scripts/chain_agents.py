#!/usr/bin/env python3
"""Orquestrador de cadeia de agentes — executa agentes em sequência com passagem de contexto"""
import json, os, sys, subprocess, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
PROJETOS_DIR = "/tmp/opencode/projetos"

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def localizar_projeto(ref):
    state = carregar_estado()
    for p in state["projects"]:
        if p["id"] == ref or p["nome"] == ref:
            return p
    return None

def registrar_tarefa(projeto, agente, status, observacao=""):
    state = carregar_estado()
    nome = projeto
    for p in state["projects"]:
        if p["id"] == projeto or p["nome"] == projeto:
            nome = p["nome"]
            break
    if nome not in state["tasks"]:
        state["tasks"][nome] = []
    state["tasks"][nome].append({
        "agente": agente,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(),
        "observacao": observacao
    })
    salvar_estado(state)
    print(f"📝 Tarefa registrada: {agente} → {status}")

def iniciar_projeto(nome, cliente, escopo):
    state = carregar_estado()
    projeto = {
        "id": f"P-{len(state['projects'])+1:03d}",
        "nome": nome,
        "cliente": cliente,
        "escopo": escopo,
        "status": "Ativo",
        "data_inicio": datetime.datetime.now().isoformat(),
        "fases": {}
    }
    state["projects"].append(projeto)
    os.makedirs(f"{PROJETOS_DIR}/{projeto['id']}", exist_ok=True)
    salvar_estado(state)
    print(f"✅ Projeto {projeto['id']} criado: {nome}")
    return projeto

def avancar_fase(projeto_ref, fase, status="concluido"):
    state = carregar_estado()
    p = None
    for proj in state["projects"]:
        if proj["id"] == projeto_ref or proj["nome"] == projeto_ref:
            p = proj
            break
    if p:
        p["fases"][fase] = {
            "status": status,
            "data": datetime.datetime.now().isoformat()
        }
        if status == "concluido":
            print(f"✅ Fase '{fase}' concluída para {p['id']} ({p['nome']})")
        salvar_estado(state)
        return
    print(f"❌ Projeto {projeto_ref} não encontrado")

def listar_tarefas_pendentes():
    state = carregar_estado()
    pendentes = []
    for proj, tasks in state["tasks"].items():
        for t in tasks:
            if t["status"] != "concluido":
                pendentes.append((proj, t))
    return pendentes

def status_geral():
    state = carregar_estado()
    print(f"\n=== STATUS GERAL — {len(state['projects'])} projetos ===")
    for p in state["projects"]:
        fases = p.get("fases", {})
        concluidas = sum(1 for f in fases.values() if f["status"] == "concluido")
        total = len(fases) or 1
        print(f"  {p['id']}: {p['nome']} ({p['cliente']}) — {concluidas}/{len(fases)} fases")
    print(f"=== Tasks pendentes: {len(listar_tarefas_pendentes())} ===\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: chain_agents.py <comando> [args]")
        print("Comandos: iniciar, avancar, status, pendentes")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "iniciar":
        iniciar_projeto(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else "")
    elif cmd == "avancar":
        avancar_fase(sys.argv[2], sys.argv[3])
    elif cmd == "status":
        status_geral()
    elif cmd == "pendentes":
        for p, t in listar_tarefas_pendentes():
            print(f"  {p} → {t['agente']}: {t['status']}")
    elif cmd == "registrar":
        registrar_tarefa(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv)>5 else "")
    else:
        print(f"Comando desconhecido: {cmd}")
