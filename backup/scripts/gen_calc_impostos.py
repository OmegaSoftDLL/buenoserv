#!/usr/bin/env python3
"""Calculadora de impostos — Simples Nacional + ISS"""
import sys

def calc_simples_nacional(receita_bruta_12m, receita_mes):
    """Anexo IV - Serviços de engenharia"""
    faixas = [
        (180000, 0.045, 0),
        (360000, 0.078, 5940),
        (720000, 0.10, 13860),
        (1800000, 0.1125, 22500),
        (3600000, 0.1355, 62100),
        (4800000, 0.147, 125640)
    ]
    for teto, aliquota, deduz in faixas:
        if receita_bruta_12m <= teto:
            aliquota_efetiva = (receita_bruta_12m * aliquota - deduz) / receita_bruta_12m
            valor_das = receita_mes * aliquota_efetiva
            return {
                "aliquota_nominal": aliquota,
                "aliquota_efetiva": aliquota_efetiva,
                "valor_das": valor_das,
                "faixa": f"Até R$ {teto:,.0f}"
            }
    return {"erro": "Acima do teto do Simples Nacional"}

def calc_iss(receita_mes, aliquota_iss=0.05):
    try:
        aliquota_municipio = float(aliquota_iss)
    except:
        aliquota_municipio = 0.05
    return {
        "base_calculo": receita_mes,
        "aliquota": aliquota_municipio,
        "valor_iss": receita_mes * aliquota_municipio
    }

if __name__ == "__main__":
    rb_12m = float(sys.argv[1]) if len(sys.argv) > 1 else 98880
    rb_mes = float(sys.argv[2]) if len(sys.argv) > 2 else 8240
    
    simples = calc_simples_nacional(rb_12m, rb_mes)
    iss = calc_iss(rb_mes)
    
    print(f"\n{'='*50}")
    print(f"  CALCULADORA DE IMPOSTOS — BUENOSERV")
    print(f"  Regime: Simples Nacional (Anexo IV)")
    print(f"{'='*50}")
    print(f"\n  Dados:")
    print(f"    Receita bruta 12 meses: R$ {rb_12m:,.2f}")
    print(f"    Receita do mês:          R$ {rb_mes:,.2f}")
    print(f"\n  Simples Nacional (DAS):")
    print(f"    Faixa:      {simples.get('faixa', 'N/A')}")
    print(f"    Alíquota nominal: {simples.get('aliquota_nominal', 0)*100:.2f}%")
    print(f"    Alíquota efetiva:  {simples.get('aliquota_efetiva', 0)*100:.2f}%")
    print(f"    Valor DAS:         R$ {simples.get('valor_das', 0):,.2f}")
    print(f"\n  ISS (Leme-SP):")
    print(f"    Base:       R$ {iss['base_calculo']:,.2f}")
    print(f"    Alíquota:   {iss['aliquota']*100:.1f}%")
    print(f"    Valor ISS:  R$ {iss['valor_iss']:,.2f}")
    print(f"\n  Total de impostos no mês: R$ {simples.get('valor_das', 0) + iss['valor_iss']:,.2f}")
    print(f"  Carga tributária efetiva: {(simples.get('valor_das', 0) + iss['valor_iss']) / rb_mes * 100:.1f}%")
