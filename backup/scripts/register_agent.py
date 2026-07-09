#!/usr/bin/env python3
"""Registra um novo agente no sistema — atualiza CEO, workflow, buenoserv e estado"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
CEO_FILE = os.path.expanduser("~/.config/opencode/agents/ceo.md")

def atualizar_estado(nome, descricao, categoria):
    with open(STATE_FILE) as f:
        state = json.load(f)
    state["agent_count"] += 1
    state["last_update"] = datetime.datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"✅ Estado atualizado: {state['agent_count']} agentes")

def adicionar_ao_ceo(nome, descricao, categoria):
    """Adiciona entrada no catálogo do CEO"""
    if not os.path.exists(CEO_FILE):
        print(f"❌ CEO file not found: {CEO_FILE}")
        return
    
    with open(CEO_FILE) as f:
        content = f.read()
    
    # Procurar a categoria certa e adicionar
    marker = f"### {categoria}"
    if marker in content:
        # Encontrar o final da seção e adicionar
        lines = content.split('\n')
        new_lines = []
        added = False
        in_section = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == marker:
                in_section = True
            elif in_section and line.startswith('|'):
                continue
            elif in_section and not added:
                # Adicionar nova linha na tabela
                last_id = 0
                for l in lines:
                    if l.startswith('|') and '|' in l:
                        parts = l.split('|')
                        if len(parts) > 1 and parts[1].strip().startswith('@'):
                            name = parts[1].strip()
                            if name != nome:
                                continue
                new_lines.append(f"| {nome} | {descricao} |")
                added = True
                in_section = False
        content = '\n'.join(new_lines)
        with open(CEO_FILE, 'w') as f:
            f.write(content)
        print(f"✅ Agente {nome} registrado no @ceo")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: register_agent.py <nome> <descricao> [categoria]")
        print("Exemplo: register_agent.py @novo-agente \"Faz alguma coisa\" \"CORPORATIVO\"")
        sys.exit(1)
    
    nome = sys.argv[1]
    descricao = sys.argv[2]
    categoria = sys.argv[3] if len(sys.argv) > 3 else "TÉCNICOS"
    
    atualizar_estado(nome, descricao, categoria)
    adicionar_ao_ceo(nome, descricao, categoria)
    print(f"\n🎉 Agente {nome} registrado com sucesso!")
    print(f"\nAções manuais necessárias:")
    print(f"  1. Criar ~/.config/opencode/agents/{nome.replace('@','')}.md")
    print(f"  2. Adicionar cross-references nos agentes relacionados")
    print(f"  3. Atualizar @workflow (matriz de chamada)")
    print(f"  4. Atualizar @buenoserv (escopo)")
    print(f"  5. Copiar para vaults Obsidian")
