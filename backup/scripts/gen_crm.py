#!/usr/bin/env python3
"""CRM evoluído — pipeline com forecast de receita ponderada"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)

def calcular_forecast():
    state = carregar()
    pipeline = []
    
    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial":
                obs = t.get("observacao", "")
                valor = 0
                import re
                match = re.search(r'R[\$]?\s*([\d.]+)', obs)
                if match:
                    valor = float(match.group(1).replace('.', ''))
                prob = 0.5 if t["status"] == "concluido" else 0.1
                pipeline.append({
                    "projeto": proj,
                    "valor": valor,
                    "probabilidade": prob,
                    "valor_ponderado": valor * prob,
                    "status": t["status"],
                    "data": t.get("timestamp", "")[:10]
                })
    
    total_pipeline = sum(p["valor"] for p in pipeline)
    total_ponderado = sum(p["valor_ponderado"] for p in pipeline)
    
    print(f"\n{'='*55}")
    print(f"  CRM — FORECAST DE RECEITA")
    print(f"{'='*55}")
    print(f"  {'Projeto':<30} {'Valor':>10} {'Prob':>6} {'Ponderado':>10}")
    print(f"  {'─'*56}")
    for p in sorted(pipeline, key=lambda x: -x["valor_ponderado"]):
        status = "✅" if p["status"] == "concluido" else "🔄"
        print(f"  {status} {p['projeto'][:28]:<28} R${p['valor']:>7,.0f} {p['probabilidade']*100:>5.0f}% R${p['valor_ponderado']:>7,.0f}")
    print(f"  {'─'*56}")
    print(f"  {'TOTAL':<30} R${total_pipeline:>7,.0f}       R${total_ponderado:>7,.0f}")
    print(f"{'='*55}")
    
    return pipeline

if __name__ == "__main__":
    calcular_forecast()
