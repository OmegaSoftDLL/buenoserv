#!/usr/bin/env python3
"""Calculadora de budget — estima custo de projeto por parâmetros de engenharia"""
import json, os, sys

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

# Tabelas de custo paramétrico (valores de referência mercado)
CUSTOS = {
    "fibra_km": {"instalacao_aerea": 35000, "instalacao_subterranea": 85000, "projeto_km": 5000},
    "equipamentos": {
        "switch_gerenciado_24p": 8500, "switch_gerenciado_48p": 15000,
        "roteador_core": 45000, "roteador_edge": 22000,
        "firewall_corp": 18000, "firewall_carrier": 65000,
        "sdh_adm_stm1": 15000, "sdh_adm_stm16": 55000,
        "dwdm_mux": 85000, "dwdm_oa": 45000,
        "mpls_pe": 35000, "mpls_p": 65000,
        "radio_5ghz": 8500, "radio_23ghz": 25000,
        "scada_rtu": 12000, "scada_master": 95000,
    },
    "servicos": {
        "h_eng_pleno": 120, "h_eng_senior": 200, "h_tecnico": 80,
        "comissionamento_eq": 0.15, "instalacao_eq": 0.08,
        "viagem_diaria": 450, "quilometragem": 2.50
    },
    "subestacao": {
        "iat_138kV": 450000, "iat_230kV": 680000, "iat_500kV": 1200000,
        "ampliacao_138kV": 180000, "ampliacao_230kV": 280000,
        "projeto_basico": 85000, "projeto_executivo": 120000
    }
}

def estimar_fibra(km, tipo="instalacao_aerea"):
    c = CUSTOS["fibra_km"]
    return km * (c.get(tipo, c["instalacao_aerea"]) + c["projeto_km"])

def estimar_equipamentos(itens):
    total = 0
    det = []
    for eq, qtd in itens:
        custo = CUSTOS["equipamentos"].get(eq, 0)
        subtotal = custo * qtd
        total += subtotal
        det.append(f"  {eq} x{qtd} = R${subtotal:,.2f}")
    return total, det

def estimar_servicos(eng_pleno_h=0, eng_senior_h=0, tecnico_h=0, viagens=0, km=0):
    s = CUSTOS["servicos"]
    total = (eng_pleno_h * s["h_eng_pleno"] +
             eng_senior_h * s["h_eng_senior"] +
             tecnico_h * s["h_tecnico"] +
             viagens * s["viagem_diaria"] +
             km * s["quilometragem"])
    return total

def estimar_se(tensao="138kV", tipo="iat"):
    c = CUSTOS["subestacao"]
    chave = f"{tipo}_{tensao}"
    return c.get(chave, 0)

def gerar_budget(km_fibra=0, tipo_fibra="instalacao_aerea", equipamentos=None,
                 eng_pleno_h=0, eng_senior_h=0, tecnico_h=0, viagens=0, km=0,
                 se_tensao=None, se_tipo="iat", margem=0.25):
    itens = []
    total = 0

    if km_fibra > 0:
        v = estimar_fibra(km_fibra, tipo_fibra)
        itens.append(("Rede Fibra Óptica", v))
        total += v

    if equipamentos:
        v, det = estimar_equipamentos(equipamentos)
        itens.append(("Equipamentos", v))
        total += v

    v_serv = estimar_servicos(eng_pleno_h, eng_senior_h, tecnico_h, viagens, km)
    if v_serv > 0:
        itens.append(("Serviços Técnicos", v_serv))
        total += v_serv

    if se_tensao:
        v = estimar_se(se_tensao, se_tipo)
        if v > 0:
            itens.append(f"Subestação {se_tipo.upper()} {se_tensao}", v)
            total += v

    # BDI / Margem
    bdi = total * margem
    itens.append(("BDI/Margem", bdi))
    total_geral = total + bdi

    return {
        "itens": itens,
        "total_sem_bdi": total,
        "total_com_bdi": total_geral,
        "margem": margem
    }

def exibir_budget(b):
    print(f"\n{'='*55}")
    print("  ORÇAMENTO ESTIMADO")
    print(f"{'='*55}")
    for nome, valor in b["itens"]:
        print(f"  {nome:<40} R$ {valor:>10,.2f}")
    print(f"  {'─'*55}")
    print(f"  {'Total s/ BDI':<40} R$ {b['total_sem_bdi']:>10,.2f}")
    print(f"  {'Total c/ BDI':<40} R$ {b['total_com_bdi']:>10,.2f}")
    print(f"{'='*55}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "tabela":
        print("\nCustos de Referência para Orçamentação:\n")
        for cat, itens in CUSTOS.items():
            print(f"  📂 {cat.upper()}:")
            for k, v in itens.items():
                if isinstance(v, dict):
                    for sk, sv in v.items():
                        print(f"    {k} > {sk}: R${sv:,.2f}")
                else:
                    print(f"    {k}: R${v:,.2f}")
            print()
    else:
        # Exemplo com valores típicos
        b = gerar_budget(
            km_fibra=15,
            tipo_fibra="instalacao_aerea",
            equipamentos=[
                ("switch_gerenciado_48p", 4),
                ("roteador_core", 2),
                ("firewall_corp", 2),
                ("sdh_adm_stm16", 2),
                ("scada_rtu", 3),
            ],
            eng_pleno_h=160,
            eng_senior_h=80,
            tecnico_h=240,
            viagens=30,
            km=1200
        )
        exibir_budget(b)
