#!/usr/bin/env python3
"""Blog técnico BUENOSERV — gera posts técnicos em HTML"""
import os, sys, datetime

ARTIGOS = {
    "iec61850-comissionamento": {
        "titulo": "IEC 61850 no Comissionamento de Subestações: Guia Prático",
        "resumo": "Protocolo IEC 61850 e sua aplicação no comissionamento de IEDs, GOOSE, Sampled Values e engenharia de sistema.",
        "tags": ["IEC 61850", "Comissionamento", "Subestação", "GOOSE", "SV"],
        "secoes": [
            ("Introdução", "A IEC 61850 revolucionou a automação de subestações, substituindo a fiação por comunicação digital."),
            ("Arquitetura", "Station bus, process bus, IEDs, HMI, Gateway. Rede redundante PRP/HSR conforme IEC 62439."),
            ("GOOSE", "Generic Object Oriented Substation Event — mensagens multicast para proteção e controle."),
            ("Sampled Values", "Amostras digitalizadas de tensão e corrente (IEC 61850-9-2LE)."),
            ("Ferramentas", "Configuração SCL, ICD, CID. Testes com Omicron, ISA, DOLE."),
            ("Comissionamento", "Teste de latência GOOSE, assinaturas SV, verificação de esquemas lógicos.")
        ]
    },
    "teleprotecao-pott-dcb": {
        "titulo": "Teleproteção: POTT vs DCB — Quando Usar Cada Um",
        "resumo": "Comparativo entre esquemas de teleproteção POTT (Permissive Overreaching Transfer Trip) e DCB (Directional Comparison Blocking).",
        "tags": ["Teleproteção", "POTT", "DCB", "Proteção de Linhas", "ANSI 85"],
        "secoes": [
            ("Conceitos", "Teleproteção permite disparo rápido de relés em ambas as extremidades da linha."),
            ("POTT", "Permissive Overreaching Transfer Trip — sinal de permissão enviado quando falta é detectada."),
            ("DCB", "Directional Comparison Blocking — sinal de bloqueio enviado quando falta é externa."),
            ("Comparação", "POTT: mais seguro (requer permissão). DCB: mais rápido (ausência de bloqueio = trip)."),
            ("Recomendação", "POTT para linhas curtas (<50km). DCB para linhas longas (>50km).")
        ]
    },
    "comissionamento-sdh-dwdm": {
        "titulo": "Comissionamento de Redes SDH/DWDM: Roteiro Técnico",
        "resumo": "Passo a passo para comissionamento de anéis SDH e sistemas DWDM, incluindo testes ópticos, proteção e handover.",
        "tags": ["SDH", "DWDM", "Comissionamento", "Fibra Óptica", "OSNR"],
        "secoes": [
            ("Planejamento", "Análise de rota, cálculo de atenuação, OSNR budget."),
            ("Instalação", "ODF, cabos pigtail, fusão. Certificação OTDR."),
            ("SDH", "Loopback, BERT, proteção MSP, K1/K2 bytes."),
            ("DWDM", "OSA, curva de ganho O.A., canal loading, FEC."),
            ("Aceitação", "FAT, SAT, relatório de testes, as-built.")
        ]
    },
    "nr10-seguranca-se": {
        "titulo": "NR-10 Aplicada a Subestações: O que o Engenheiro Precisa Saber",
        "resumo": "A NR-10 determina requisitos de segurança em instalações elétricas. Veja como aplicar em SE de alta tensão.",
        "tags": ["NR-10", "Segurança", "Subestação", "SEP", "LOTO"],
        "secoes": [
            ("Escopo", "NR-10 aplica a todas as fases de geração, transmissão e distribuição de energia."),
            ("SEP", "Sistema Elétrico de Potência: tensão acima de 50V."),
            ("LOTO", "Lockout/Tagout — procedimento de bloqueio para trabalho seguro."),
            ("ATPV", "Vestimenta para arco elétrico. Categoria 2 mínimo em SE."),
            ("Treinamento", "NR-10 básico (40h) + complementar (SEP) obrigatório.")
        ]
    }
}

def gerar_blog_html(artigo_id, saida=None):
    artigo = ARTIGOS.get(artigo_id)
    if not artigo:
        print(f"❌ Artigo '{artigo_id}' não encontrado. Opções: {', '.join(ARTIGOS.keys())}")
        return
    saida = saida or os.path.expanduser(f"~/Desktop/blog_{artigo_id}.html")
    
    secoes = "\n".join(f'<div class="secao"><h2>{t}</h2><p>{c}</p></div>' for t, c in artigo["secoes"])
    tags = " ".join(f'<span class="tag">{t}</span>' for t in artigo["tags"])
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>{artigo['titulo']} — BUENOSERV</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Calibri,sans-serif;background:#F0F2F5;padding:40px;color:#333}}
.paper{{max-width:800px;margin:0 auto;background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
h1{{color:#1A237E;font-size:1.6rem;border-bottom:3px solid #C9A84C;padding-bottom:12px;margin-bottom:20px}}
.resumo{{font-size:1.05rem;color:#555;margin-bottom:20px;line-height:1.5}}
.tags{{margin-bottom:24px}}
.tag{{display:inline-block;background:#E8EAF6;color:#1A237E;padding:3px 10px;border-radius:12px;font-size:.8rem;margin:2px}}
.secao{{margin-bottom:20px}}
.secao h2{{color:#1A237E;font-size:1.1rem;margin-bottom:6px}}
.secao p{{line-height:1.6;color:#444}}
.footer{{border-top:1px solid #ddd;margin-top:30px;padding-top:15px;font-size:.8rem;color:#888}}
</style>
</head>
<body>
<div class="paper">
<h1>{artigo['titulo']}</h1>
<div class="tags">{tags}</div>
<p class="resumo">{artigo['resumo']}</p>
{secoes}
<div class="footer">
<p>BUENOSERV ENGENHARIA — {datetime.date.today():%d/%m/%Y}</p>
<p>Por Ricardo Bueno, Diretor Técnico</p>
</div>
</div>
</body>
</html>"""
    with open(saida, 'w') as f:
        f.write(html)
    print(f"✅ Blog post: {saida}")

def listar_artigos():
    print("Artigos disponíveis:")
    for k, v in ARTIGOS.items():
        print(f"  • {k}: {v['titulo']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        listar_artigos()
        sys.exit(0)
    gerar_blog_html(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
