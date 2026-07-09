#!/usr/bin/env python3
"""Auto-treinamento — lê documentos técnicos e gera quizzes de aprendizado"""
import os, sys, json, random, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
QUIZ_DIR = os.path.expanduser("~/.config/opencode/treinamento")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)
def salvar(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

BANCO_QUESTOES = {
    "telecom": [
        {"q": "Qual a taxa do STM-1?", "a": "155 Mbps", "opcoes": ["155 Mbps", "622 Mbps", "2.5 Gbps", "10 Gbps"]},
        {"q": "O que significa DWDM?", "a": "Dense Wavelength Division Multiplexing", "opcoes": ["Digital Wavelength Division Multiplexing", "Dense Wavelength Division Multiplexing", "Double Wavelength Division Mode", "Dynamic Wavelength Data Multiplex"]},
        {"q": "Qual fibra é mais usada em longa distância?", "a": "G.652.D (SMF)", "opcoes": ["G.652.D (SMF)", "G.655 (NZ-DSF)", "G.657 (Bend-insensitive)", "MMF OM4"]},
        {"q": "O que é OSNR?", "a": "Optical Signal-to-Noise Ratio", "opcoes": ["Optical Signal-to-Noise Ratio", "Optical System Network Rate", "Output Signal Null Reference", "Optical Spectrum Normalized Reading"]},
        {"q": "Qual protocolo de proteção em anéis SDH?", "a": "MSP (Multiplex Section Protection)", "opcoes": ["MSP", "STP", "RSTP", "OSPF"]},
    ],
    "subestacao": [
        {"q": "Qual norma para proteção em subestações?", "a": "IEC 61850", "opcoes": ["IEC 61850", "IEEE C37.118", "NBR 5410", "ANSI C12.18"]},
        {"q": "O que significa RTU?", "a": "Remote Terminal Unit", "opcoes": ["Remote Terminal Unit", "Real-Time Unit", "Regional Transmission Utility", "Rotary Transformer Unit"]},
        {"q": "Qual função ANSI para relé de distância?", "a": "21", "opcoes": ["21", "50", "51", "87"]},
        {"q": "O que é malha de terra?", "a": "Sistema de aterramento da subestação", "opcoes": ["Sistema de aterramento da subestação", "Rede de fibra óptica subterrânea", "Sistema de drenagem de cabos", "Estrutura de suporte de barramentos"]},
        {"q": "Qual a tensão típica de serviços auxiliares AC em SE?", "a": "220V CA", "opcoes": ["127V CA", "220V CA", "380V CA", "480V CA"]},
    ],
    "seguranca": [
        {"q": "O que significa NR-10?", "a": "Segurança em instalações e serviços em eletricidade", "opcoes": ["Segurança em instalações e serviços em eletricidade", "Trabalho em altura", "Equipamentos de proteção individual", "Sinalização de segurança"]},
        {"q": "Qual o limite de tensão para NR-10?", "a": "Acima de 50V", "opcoes": ["Acima de 50V", "Acima de 220V", "Acima de 1000V", "Qualquer tensão"]},
        {"q": "O que significa LOTO?", "a": "Lockout/Tagout — bloqueio e etiquetagem", "opcoes": ["Lockout/Tagout", "Low Torque Operation", "Linear Output Test Object", "Load Overload Transfer Option"]},
        {"q": "Qual EPI obrigatório para trabalho em SEP?", "a": "Capacete, luvas isolantes, óculos, vestimenta ATPV", "opcoes": ["Capacete + bota", "Luvas de borracha", "Capacete, luvas isolantes, óculos, vestimenta ATPV", "Apenas uniforme"]},
    ],
    "gestao": [
        {"q": "O que significa EAP?", "a": "Estrutura Analítica do Projeto (WBS)", "opcoes": ["Estrutura Analítica do Projeto", "Etapa de Avaliação de Performance", "Especificação de Aquisição de Produto", "Estudo de Aplicação Prática"]},
        {"q": "Qual a diferença entre PERT e CPM?", "a": "PERT usa 3 estimativas (otimista, provável, pessimista); CPM usa 1", "opcoes": ["PERT é para tempo, CPM para custo", "PERT usa 3 estimativas; CPM usa 1", "São a mesma coisa", "PERT é determinístico, CPM é probabilístico"]},
        {"q": "O que significa EVM?", "a": "Earned Value Management — gerenciamento de valor agregado", "opcoes": ["Earned Value Management", "Estimated Value Method", "Enterprise Vendor Management", "Electronic Verification Module"]},
    ]
}

def gerar_quiz(temas=None, n=5):
    temas = temas or list(BANCO_QUESTOES.keys())
    questoes = []
    for t in temas:
        questoes.extend(BANCO_QUESTOES.get(t, []))
    random.shuffle(questoes)
    questoes = questoes[:n]
    return questoes

def aplicar_quiz(interativo=True, temas=None, n=5):
    questoes = gerar_quiz(temas, n)
    acertos = 0
    print(f"\n{'='*50}")
    print(f"  📝 QUIZ DE TREINAMENTO — BUENOSERV")
    print(f"  Tema: {', '.join(temas) if temas else 'Geral'}")
    print(f"{'='*50}\n")
    for i, q in enumerate(questoes, 1):
        print(f"{i}. {q['q']}")
        if interativo:
            for j, op in enumerate(q['opcoes'], 1):
                print(f"   {j}) {op}")
            try:
                resp = int(input("\nResposta: "))
                if 1 <= resp <= len(q['opcoes']):
                    if q['opcoes'][resp-1] == q['a']:
                        print("  ✅ Correto!\n")
                        acertos += 1
                    else:
                        print(f"  ❌ Incorreto. Resposta: {q['a']}\n")
                else:
                    print(f"  Resposta: {q['a']}\n")
            except:
                print(f"  Resposta: {q['a']}\n")
        else:
            print(f"   Resposta: {q['a']}\n")
    
    if interativo:
        pct = acertos / len(questoes) * 100
        print(f"{'='*50}")
        print(f"  Resultado: {acertos}/{len(questoes)} ({pct:.0f}%)")
        print(f"{'='*50}")
        # Salvar progresso
        state = carregar()
        if "treinamento" not in state:
            state["treinamento"] = {"historico": []}
        state["treinamento"]["historico"].append({
            "data": datetime.datetime.now().isoformat(),
            "temas": temas,
            "acertos": acertos,
            "total": len(questoes),
            "pct": pct
        })
        salvar(state)
    return acertos, len(questoes)

if __name__ == "__main__":
    import sys
    tema = sys.argv[1] if len(sys.argv) > 1 else None
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    temas = [tema] if tema and tema != "geral" else None
    aplicar_quiz(temas=temas, n=n)
