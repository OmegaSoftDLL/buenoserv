#!/usr/bin/env python3
"""Conciliação bancária — importa extrato × contas a pagar/receber"""
import json, sys, datetime

def reconciliar(extrato_entradas, extrato_saidas, contas_sistema):
    print(f"\n{'='*55}")
    print(f"  CONCILIAÇÃO BANCÁRIA — {datetime.date.today():%d/%m/%Y}")
    print(f"{'='*55}")
    print(f"\n📥 Entradas no extrato: R$ {sum(extrato_entradas):,.2f}")
    print(f"📤 Saídas no extrato:   R$ {sum(extrato_saidas):,.2f}")
    print(f"\n📋 Contas no sistema:   R$ {sum(contas_sistema):,.2f}")
    
    conciliadas_e = sum(min(extrato_entradas.count(v), contas_sistema.count(v)) * v for v in set(extrato_entradas + contas_sistema))
    pendentes_e = sum(extrato_entradas) - conciliadas_e
    faltantes_e = sum(contas_sistema) - conciliadas_e
    
    print(f"\n  Entradas conciliadas:  R$ {conciliadas_e:,.2f}")
    print(f"  Entradas pendentes:    R$ {pendentes_e:,.2f}")
    print(f"  Faturas não pagas:     R$ {faltantes_e:,.2f}")

if __name__ == "__main__":
    reconciliar([8500, 5000], [1500, 800, 500], [8500, 5000, 2500])
