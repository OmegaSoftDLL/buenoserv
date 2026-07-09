#!/usr/bin/env python3
"""BOM automático — gera Bill of Materials a partir de regras de engenharia"""
import json, sys

BOM_RULES = {
    "dwdm": {"mux_pond": 1, "oa": 1, "sfp_dwdm": 2, "patchcord_lc_lc": 4, "attenuator": 2},
    "sdh_stm16": {"adm_stm16": 1, "sfp_sdh": 4, "patchcord_ec_ec": 4, "cabo_e1": 4},
    "switch_48p": {"switch_48p": 1, "sfp_sx": 2, "sfp_lx": 2, "patchcord_cat6": 48},
    "fibra_km": {"cabo_sm_48f": 2, "caixa_emenda": 4, "fusion": 48, "pigtail_sc": 96, "adaptador_sc": 96},
    "radio_23ghz": {"radio_23ghz": 2, "antena_23ghz": 2, "cabo_rfd": 20, "conector_rfd": 4},
}

def gerar_bom(projeto, sistemas):
    bom = []
    for sistema, qtd in sistemas.items():
        if sistema in BOM_RULES:
            for item, qtd_por_unidade in BOM_RULES[sistema].items():
                bom.append({"item": item, "quantidade": qtd_por_unidade * qtd, "sistema": sistema})
    return bom

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_bom.py <projeto> [sistema=quantidade...]")
        print("Exemplo: gen_bom.py \"SE-Alfa\" dwdm=2 sdh_stm16=1 switch_48p=4 fibra_km=15")
        sys.exit(1)
    projeto = sys.argv[1]
    sistemas = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=")
            sistemas[k] = int(v)

    bom = gerar_bom(projeto, sistemas)
    print(f"\n📋 BOM — {projeto}")
    print(f"{'='*50}")
    for item in bom:
        print(f"  {item['quantidade']:>4}x {item['item']:<30} [{item['sistema']}]")
    print(f"{'='*50}")
    print(f"  Total de itens: {len(bom)}")
