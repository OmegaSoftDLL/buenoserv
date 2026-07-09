#!/usr/bin/env python3
"""Fluxo de caixa projetado 90 dias"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def projetar(contas_pagar=None, contas_receber=None, saldo_inicial=0):
    state = carregar()
    hoje = datetime.date.today()
    fluxo = state.setdefault("fluxo_caixa", {"projecoes": []})
    
    pagar = contas_pagar or [
        {"desc": "Aluguel", "valor": 2500, "dia": 5},
        {"desc": "Internet/Tel", "valor": 800, "dia": 10},
        {"desc": "Pró-labore", "valor": 5000, "dia": 15},
        {"desc": "Software/Assinaturas", "valor": 600, "dia": 20},
    ]
    receber = contas_receber or [
        {"desc": "E4 ENERGIA - Consultoria", "valor": 8240, "dia": 25},
    ]
    
    proj = {"data": hoje.isoformat(), "previsoes": []}
    saldo = saldo_inicial
    print(f"\n{'='*55}")
    print(f"  FLUXO DE CAIXA PROJETADO — 90 DIAS")
    print(f"  Início: {hoje:%d/%m/%Y}")
    print(f"  Saldo inicial: R$ {saldo:,.2f}")
    print(f"{'='*55}")
    
    for d in range(90):
        data = hoje + datetime.timedelta(days=d)
        dia = data.day
        entrada = sum(r["valor"] for r in receber if r["dia"] == dia)
        saida = sum(p["valor"] for p in pagar if p["dia"] == dia)
        saldo += entrada - saida
        if entrada or saida:
            proj["previsoes"].append({
                "data": data.isoformat(),
                "entrada": entrada,
                "saida": saida,
                "saldo": saldo
            })
            print(f"  {data:%d/%m/%y}  {'+' if entrada else ' '}R$ {entrada:>8,.2f}  {'-' if saida else ' '}R$ {saida:>8,.2f}  = R$ {saldo:>8,.2f}")
    
    fluxo["projecoes"].append(proj)
    salvar(state)
    print(f"{'='*55}")
    print(f"  Saldo projetado em 90 dias: R$ {saldo:,.2f}")
    return proj

if __name__ == "__main__":
    projetar()
