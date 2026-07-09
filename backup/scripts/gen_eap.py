#!/usr/bin/env python3
"""EAP automática — gera Estrutura Analítica do Projeto a partir do escopo"""
import sys, json, os

def gerar_eap(projeto, fases, saida=None):
    saida = saida or f"/tmp/opencode/EAP_{projeto.replace(' ','_')}.txt"
    saida_txt = saida
    
    lines = [f"EAP — {projeto}", "=" * (len(projeto) + 8), ""]
    
    def add_nivel(texto, nivel):
        prefixo = "  " * nivel + ("└── " if nivel > 0 else "")
        lines.append(f"{prefixo}{texto}")
    
    nivel = 0
    for fase, subitens in fases.items():
        add_nivel(fase, nivel)
        for sub in subitens:
            if isinstance(sub, dict):
                for k, v in sub.items():
                    add_nivel(f"{k}: {v}", nivel + 1)
            else:
                add_nivel(sub, nivel + 1)
    
    with open(saida_txt, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"\n📋 EAP — {projeto}")
    print("\n".join(lines))
    print(f"\n✅ EAP salva: {saida_txt}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_eap.py <projeto> [fases_json]")
        print("Exemplo: gen_eap.py \"SE-Alfa\" '{\"Projeto\":[\"Básico\",\"Executivo\"],\"Instalação\":[\"Civil\",\"Montagem\"],\"Testes\":[\"FAT\",\"SAT\"]}'")
        sys.exit(1)
    projeto = sys.argv[1]
    fases = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {
        "1. Proposta": ["Análise de escopo", "Dimensionamento", "Elaboração", "Apresentação"],
        "2. Projeto": ["Levantamento de campo", "Projeto básico", "Projeto executivo", "Aprovação"],
        "3. Suprimentos": ["BOM", "Cotação", "Compra", "Recebimento"],
        "4. Instalação": ["Civil", "Montagem eletromecânica", "Cabeamento", "Energização"],
        "5. Comissionamento": ["Testes unitários", "FAT", "SAT", "Treinamento"],
        "6. Handover": ["Documentação as-built", "Manual do sistema", "Termo de entrega", "Garantia"]
    }
    gerar_eap(projeto, fases)
