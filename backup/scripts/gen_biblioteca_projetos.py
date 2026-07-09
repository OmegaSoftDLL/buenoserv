#!/usr/bin/env python3
"""Biblioteca de projetos — repositório de documentação de projetos anteriores"""
import json, os, sys, datetime, shutil

BASE_DIR = "/tmp/opencode/projetos"
STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)

def listar_projetos():
    state = carregar()
    print(f"\n{'='*55}")
    print(f"  BIBLIOTECA DE PROJETOS — BUENOSERV")
    print(f"{'='*55}")
    for p in state.get("projects", []):
        fases = p.get("fases", {})
        n_fases = len(fases)
        n_concluidas = sum(1 for f in fases.values() if f["status"] == "concluido")
        print(f"\n  📁 {p['id']}: {p['nome']}")
        print(f"     Cliente: {p['cliente']}")
        print(f"     Fases: {n_concluidas}/{n_fases} concluídas")
        print(f"     Início: {p.get('data_inicio','')[:10]}")
        # Check for docs
        dir_path = os.path.join(BASE_DIR, p['id'])
        if os.path.exists(dir_path):
            docs = os.listdir(dir_path)
            if docs:
                print(f"     Documentos: {', '.join(docs[:3])}")
    print(f"\n{'='*55}")

def arquivar_projeto(projeto_id):
    state = carregar()
    for p in state.get("projects", []):
        if p["id"] == projeto_id:
            p["status"] = "Arquivado"
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print(f"✅ Projeto {projeto_id} arquivado")
            return
    print(f"❌ Projeto {projeto_id} não encontrado")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "arquivar":
        arquivar_projeto(sys.argv[2])
    else:
        listar_projetos()
