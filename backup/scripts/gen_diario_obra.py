#!/usr/bin/env python3
"""Gerador de diário de obra DOCX + registro fotográfico"""
import os, sys, datetime

def gerar_diario_obra(projeto, data, atividades, equipe="", observacoes="", saida=None):
    saida = saida or os.path.expanduser(f"~/Desktop/Diario_Obra_{projeto.replace(' ','_')}_{data}.txt")
    cab = f"""DIÁRIO DE OBRA
Projeto: {projeto}
Data: {data}
Equipe: {equipe}
_________________________________________

ATIVIDADES DO DIA:
"""
    corpo = "\n".join(f"  {i}. {a}" for i, a in enumerate(atividades, 1))
    obs = f"\n\nOBSERVAÇÕES:\n{observacoes}" if observacoes else ""
    ass = f"""

__________________________________
Responsável: ____________________

__________________________________
Fiscal: _________________________
"""
    with open(saida, 'w') as f:
        f.write(cab + corpo + obs + ass)
    print(f"✅ Diário de obra gerado: {saida}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: gen_diario_obra.py <projeto> <data> [atividades...]")
        sys.exit(1)
    gerar_diario_obra(sys.argv[1], sys.argv[2], sys.argv[3:])
