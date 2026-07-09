#!/usr/bin/env python3
"""Orçamento x Realizado — dashboard comparativo por projeto"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def registrar_orcamento(projeto, valor_orcado, descricao=""):
    state = carregar()
    if "orcamentos" not in state:
        state["orcamentos"] = []
    state["orcamentos"].append({
        "projeto": projeto,
        "valor_orcado": valor_orcado,
        "descricao": descricao,
        "data": datetime.date.today().isoformat(),
        "realizados": []
    })
    salvar(state)
    print(f"✅ Orçamento registrado: {projeto} — R${valor_orcado:,.2f}")

def registrar_realizado(projeto, valor, descricao=""):
    state = carregar()
    for o in state.get("orcamentos", []):
        if o["projeto"] == projeto:
            o["realizados"].append({
                "valor": valor,
                "descricao": descricao or "Despesa",
                "data": datetime.date.today().isoformat()
            })
            salvar(state)
            total_real = sum(r["valor"] for r in o["realizados"])
            diff = o["valor_orcado"] - total_real
            pct = total_real / o["valor_orcado"] * 100 if o["valor_orcado"] else 0
            print(f"✅ Realizado registrado: {projeto} — R${valor:,.2f}")
            print(f"   Total: R${total_real:,.2f} / R${o['valor_orcado']:,.2f} ({pct:.1f}%)")
            print(f"   Saldo: R${diff:,.2f}")
            return
    print(f"❌ Projeto '{projeto}' não encontrado. Registre o orçamento primeiro.")

def exibir_comparativo(projeto=None):
    state = carregar()
    for o in state.get("orcamentos", []):
        if projeto and o["projeto"] != projeto:
            continue
        total_real = sum(r["valor"] for r in o["realizados"])
        diff = o["valor_orcado"] - total_real
        pct = total_real / o["valor_orcado"] * 100 if o["valor_orcado"] else 0
        print(f"\n{'='*50}")
        print(f"  {o['projeto']}")
        print(f"{'='*50}")
        print(f"  Orçado:   R$ {o['valor_orcado']:>10,.2f}")
        print(f"  Realizado: R$ {total_real:>10,.2f} ({pct:.1f}%)")
        print(f"  Diferença: R$ {diff:>10,.2f}")
        if total_real > o["valor_orcado"]:
            print(f"  ⚠️  ACIMA DO ORÇAMENTO em R$ {abs(diff):,.2f}")
        for r in o["realizados"]:
            print(f"    - {r['data']}: R${r['valor']:,.2f} ({r['descricao']})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_orcado_realizado.py orcar <projeto> <valor> [desc]")
        print("      gen_orcado_realizado.py realizar <projeto> <valor> [desc]")
        print("      gen_orcado_realizado.py ver [projeto]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "orcar":
        registrar_orcamento(sys.argv[2], float(sys.argv[3]), " ".join(sys.argv[4:]))
    elif cmd == "realizar":
        registrar_realizado(sys.argv[2], float(sys.argv[3]), " ".join(sys.argv[4:]))
    elif cmd == "ver":
        exibir_comparativo(sys.argv[2] if len(sys.argv) > 2 else None)
