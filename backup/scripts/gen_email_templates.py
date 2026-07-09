#!/usr/bin/env python3
"""Templates adicionais de e-mail — cobrança, contrato assinado, SAT aprovado"""
import json, os, sys, datetime

MODELOS = {
    "cobranca": {
        "assunto": "Boleto - {projeto} - Vencimento {vencimento}",
        "corpo": """Prezado {cliente},

Segue boleto referente à medição do período de {periodo}.

Valor: R$ {valor:,.2f}
Vencimento: {vencimento}
Banco: BTG Pactual (208) | Ag: 0050 | CC: 2321479-4
PIX: 60.490.193/0001-38 (CNPJ)

Atenciosamente,
BUENOSERV SERVIÇOS DE ENGENHARIA LTDA"""
    },
    "contrato_assinado": {
        "assunto": "Contrato assinado - {projeto}",
        "corpo": """Prezado {cliente},

Segue em anexo o contrato devidamente assinado pela BUENOSERV.

Dados do contrato:
- Projeto: {projeto}
- Valor: R$ {valor:,.2f}
- Prazo: {prazo}
- Início: {inicio}

Estamos à disposição para quaisquer esclarecimentos.

Atenciosamente,
Ricardo Bueno - Diretor Técnico
BUENOSERV ENGENHARIA"""
    },
    "sat_aprovado": {
        "assunto": "SAT aprovado - {projeto} - {cliente}",
        "corpo": """Prezado {cliente},

Comunicamos que o Teste de Aceitação em Site (SAT) do projeto {projeto} foi APROVADO em {data}.

Itens verificados:
{itens}

A partir desta data, inicia-se o período de garantia de 12 meses.

Atenciosamente,
BUENOSERV ENGENHARIA"""
    },
    "followup_proposta": {
        "assunto": "Follow-up - Proposta {projeto}",
        "corpo": """Prezado {cliente},

Gostaria de saber se já teve oportunidade de avaliar nossa proposta para {projeto}.

Estou à disposição para esclarecer quaisquer dúvidas técnicas ou comerciais.

Atenciosamente,
Ricardo Bueno
(19) {telefone}"""
    }
}

def gerar_email(tipo, **kwargs):
    modelo = MODELOS.get(tipo)
    if not modelo:
        print(f"❌ Tipo '{tipo}' não encontrado. Opções: {', '.join(MODELOS.keys())}")
        return
    assunto = modelo["assunto"].format(**kwargs)
    corpo = modelo["corpo"].format(**kwargs)
    print(f"📧 {assunto}")
    print(f"{'─'*50}")
    print(corpo)
    print(f"{'─'*50}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gen_email_templates.py <tipo> [param=valor...]")
        print(f"Tipos: {', '.join(MODELOS.keys())}")
        sys.exit(1)
    tipo = sys.argv[1]
    params = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            params[k] = v
    gerar_email(tipo, **params)
