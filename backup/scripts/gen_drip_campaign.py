#!/usr/bin/env python3
"""Drip campaign — sequência automática de e-mails D+3, D+7, D+14, D+30"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

SEQUENCIA = {
    3:  "Assunto: Ainda está avaliando nossa proposta?\n\nOlá {cliente}, gostaria de saber se já teve oportunidade de analisar nossa proposta. Estou à disposição para esclarecer dúvidas.",
    7:  "Assunto: Case de sucesso relacionado\n\n{cliente}, seguem abaixo alguns cases de sucesso da BUENOSERV em projetos similares ao seu...",
    14: "Assunto: Últimos dias para condições especiais\n\n{cliente}, estamos com uma agenda comercial se fechando para este mês. Se houver interesse, podemos conversar sobre condições especiais.",
    30: "Assunto: Mantendo contato\n\n{cliente}, mesmo que agora não seja o momento ideal, gostaria de manter contato para futuras oportunidades na área de engenharia."
}

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def verificar_disparos():
    state = carregar()
    if "drip_campaign" not in state:
        state["drip_campaign"] = {"campanhas": []}
    hoje = datetime.date.today()
    disparos = []

    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            if t["agente"] == "comercial" and t["status"] == "concluido":
                ts = t.get("timestamp", "")
                if ts:
                    data_envio = datetime.date.fromisoformat(ts[:10])
                    dias = (hoje - data_envio).days
                    # Verificar se já tem campanha para este projeto
                    camp_existente = any(
                        c["projeto"] == proj for c in state["drip_campaign"]["campanhas"]
                    )
                    if not camp_existente and dias >= 3:
                        # Iniciar campanha
                        state["drip_campaign"]["campanhas"].append({
                            "projeto": proj,
                            "inicio": data_envio.isoformat(),
                            "proximo_dia": 3,
                            "disparos": []
                        })
                        disparos.append((proj, 3))
                    elif camp_existente:
                        for c in state["drip_campaign"]["campanhas"]:
                            if c["projeto"] == proj:
                                for dia, msg in SEQUENCIA.items():
                                    if dias >= dia and dia not in [d["dia"] for d in c["disparos"]]:
                                        if dia > c.get("proximo_dia", 0) or c.get("proximo_dia", 0) == dia:
                                            c["disparos"].append({"dia": dia, "data": hoje.isoformat()})
                                            c["proximo_dia"] = dia
                                            disparos.append((proj, dia))

    salvar(state)
    return disparos

if __name__ == "__main__":
    disparos = verificar_disparos()
    if disparos:
        print(f"📧 Disparos pendentes para hoje:")
        for proj, dia in disparos:
            print(f"  • {proj}: D+{dia}")
            if dia in SEQUENCIA:
                print(f"    Modelo: {SEQUENCIA[dia][:60]}...")
    else:
        print("✅ Nenhum disparo pendente hoje.")
