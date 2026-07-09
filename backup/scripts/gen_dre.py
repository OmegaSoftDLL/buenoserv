#!/usr/bin/env python3
"""Gera DRE (Demonstração do Resultado do Exercício) da BUENOSERV"""
import json, os, sys, datetime
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def gerar_dre_estrutura():
    hoje = datetime.date.today()
    mes = hoje.month
    ano = hoje.year
    return {
        "ano": ano,
        "meses": {},
        "acumulado": {
            "receita_bruta": 0,
            "deducoes": 0,
            "receita_liquida": 0,
            "custos_servicos": 0,
            "lucro_bruto": 0,
            "despesas_administrativas": 0,
            "despesas_comerciais": 0,
            "despesas_tributarias": 0,
            "lucro_operacional": 0,
            "resultado_financeiro": 0,
            "lucro_liquido": 0
        }
    }

def calcular_simples_nacional(receita_bruta):
    """Calcula Simples Nacional para serviços de engenharia (anexo IV)"""
    if receita_bruta <= 0:
        return 0
    faixas = [
        (180000, 0.045, 0),
        (360000, 0.078, 5940),
        (720000, 0.10, 13860),
        (1800000, 0.1125, 22500),
        (3600000, 0.1355, 62100),
        (4800000, 0.147, 125640)
    ]
    for teto, aliquota, deduz in faixas:
        if receita_bruta <= teto:
            return receita_bruta * aliquota - deduz
    return receita_bruta * 0.147 - 125640

def dre_mes(state, mes, ano):
    dre = state.setdefault("dre", gerar_dre_estrutura())
    if str(mes) not in dre["meses"]:
        dre["meses"][str(mes)] = {
            "ano": ano,
            "receita_bruta": 0,
            "deducoes": 0,
            "receita_liquida": 0,
            "custos_servicos": 0,
            "lucro_bruto": 0,
            "despesas_administrativas": 0,
            "despesas_comerciais": 0,
            "despesas_tributarias": 0,
            "lucro_operacional": 0,
            "resultado_financeiro": 0,
            "lucro_liquido": 0
        }
    return dre["meses"][str(mes)]

def atualizar_dre(receita_bruta, custos=None, despesas_adm=None, despesas_com=None, resultado_fin=None):
    state = carregar_estado()
    hoje = datetime.date.today()
    mes = hoje.month
    ano = hoje.year

    dm = dre_mes(state, mes, ano)

    dm["receita_bruta"] = receita_bruta
    dm["deducoes"] = 0
    dm["receita_liquida"] = receita_bruta

    # Simples Nacional
    rb_acumulada = receita_bruta
    for m in range(1, mes):
        rb_acumulada += state.get("dre", {}).get("meses", {}).get(str(m), {}).get("receita_bruta", 0)
    simples = calcular_simples_nacional(rb_acumulada)

    dm["despesas_tributarias"] = simples
    dm["custos_servicos"] = custos if custos is not None else receita_bruta * 0.35
    dm["lucro_bruto"] = dm["receita_liquida"] - dm["custos_servicos"]
    dm["despesas_administrativas"] = despesas_adm if despesas_adm is not None else receita_bruta * 0.15
    dm["despesas_comerciais"] = despesas_com if despesas_com is not None else receita_bruta * 0.05
    dm["lucro_operacional"] = dm["lucro_bruto"] - dm["despesas_administrativas"] - dm["despesas_comerciais"] - dm["despesas_tributarias"]
    dm["resultado_financeiro"] = resultado_fin if resultado_fin is not None else -receita_bruta * 0.01
    dm["lucro_liquido"] = dm["lucro_operacional"] + dm["resultado_financeiro"]

    salvar_estado(state)
    return dm

def formatar(valor):
    return f"R$ {valor:,.2f}"

def exibir_dre(mes=None, ano=None):
    state = carregar_estado()
    dre = state.get("dre")
    if not dre:
        print("❌ Nenhum DRE encontrado. Execute com receita para criar.")
        return

    hoje = datetime.date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    dm = dre.get("meses", {}).get(str(mes), {})
    if not dm:
        print(f"❌ Nenhum DRE para {mes}/{ano}")
        return

    print(f"\n{'='*50}")
    print(f"  DRE — BUENOSERV SERVIÇOS DE ENGENHARIA LTDA")
    print(f"  Período: {mes:02d}/{ano}")
    print(f"{'='*50}")
    print(f"  1. Receita Bruta de Serviços    {formatar(dm['receita_bruta'])}")
    print(f"  2. Deduções                     {formatar(dm['deducoes'])}")
    print(f"  {'─'*40}")
    print(f"  3. Receita Líquida              {formatar(dm['receita_liquida'])}")
    print(f"  4. Custos dos Serviços          {formatar(dm['custos_servicos'])}")
    print(f"  {'─'*40}")
    print(f"  5. Lucro Bruto                  {formatar(dm['lucro_bruto'])}")
    print(f"  6. Despesas Administrativas     {formatar(dm['despesas_administrativas'])}")
    print(f"  7. Despesas Comerciais          {formatar(dm['despesas_comerciais'])}")
    print(f"  8. Despesas Tributárias         {formatar(dm['despesas_tributarias'])}")
    print(f"  {'─'*40}")
    print(f"  9. Lucro Operacional            {formatar(dm['lucro_operacional'])}")
    print(f"  10. Resultado Financeiro        {formatar(dm['resultado_financeiro'])}")
    print(f"  {'─'*40}")
    print(f"  11. Lucro Líquido               {formatar(dm['lucro_liquido'])}")
    print(f"{'='*50}\n")

    # Margens
    if dm['receita_liquida'] > 0:
        margem_bruta = dm['lucro_bruto'] / dm['receita_liquida'] * 100
        margem_liquida = dm['lucro_liquido'] / dm['receita_liquida'] * 100
        print(f"  Margem Bruta: {margem_bruta:.1f}%")
        print(f"  Margem Líquida: {margem_liquida:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Modo interativo
        try:
            rb = float(input("Receita Bruta do mês: R$ "))
            custos = input("Custos dos serviços (Enter=35%): R$ ").strip()
            custos = float(custos) if custos else None
            adm = input("Despesas adm (Enter=15%): R$ ").strip()
            adm = float(adm) if adm else None
            com = input("Despesas comerciais (Enter=5%): R$ ").strip()
            com = float(com) if com else None
            resfin = input("Resultado financeiro (Enter=-1%): R$ ").strip()
            resfin = float(resfin) if resfin else None
            dm = atualizar_dre(rb, custos, adm, com, resfin)
            exibir_dre()
            # Tentar gerar XLSX
            try:
                sys.path.insert(0, '/tmp/opencode/templates')
                from gen_xlsx import gerar_dre_xlsx
                path = os.path.expanduser(f"~/Desktop/DRE_{datetime.date.today().month:02d}_{datetime.date.today().year}.xlsx")
                gerar_dre_xlsx(path, dm, datetime.date.today().month, datetime.date.today().year)
            except ImportError:
                print("💡 Dica: instale openpyxl (pip install openpyxl) para gerar XLSX")
            except Exception as e:
                print(f"⚠️ Erro ao gerar XLSX: {e}")
        except ValueError:
            print("❌ Valor inválido")
        except KeyboardInterrupt:
            print("\n🛑 Cancelado")
    elif sys.argv[1] == "ver":
        mes = int(sys.argv[2]) if len(sys.argv) > 2 else None
        ano = int(sys.argv[3]) if len(sys.argv) > 3 else None
        exibir_dre(mes, ano)
    elif sys.argv[1] == "atualizar":
        rb = float(sys.argv[2])
        custos = float(sys.argv[3]) if len(sys.argv) > 3 else None
        dm = atualizar_dre(rb, custos)
        exibir_dre()
    else:
        print("Uso: gen_dre.py [ver <mes> <ano> | atualizar <receita> <custos>]")
