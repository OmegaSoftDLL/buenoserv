#!/usr/bin/env python3
"""Gerador de contrato DOCX a partir de template + dados"""
import os, sys, json, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)

def gerar_contrato(cliente, objeto, valor, prazo_meses, saida=None):
    saida = saida or os.path.expanduser(f"~/Desktop/Contrato_{cliente.replace(' ','_')}.txt")
    hoje = datetime.date.today()
    fim = hoje.replace(year=hoje.year + (prazo_meses // 12), month=hoje.month + (prazo_meses % 12) if hoje.month + (prazo_meses % 12) <= 12 else (hoje.month + prazo_meses % 12) - 12)
    if fim.month != (hoje.month + prazo_meses % 12) % 12 or fim.month == 0:
        fim = fim.replace(year=fim.year + 1, month=fim.month % 12 or 12)

    contrato = f"""CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE ENGENHARIA

CONTRATANTE: {cliente}
CONTRATADA: BUENOSERV SERVIÇOS DE ENGENHARIA LTDA - CNPJ: 60.490.193/0001-38
Endereço: Rua Giacomo Fior, nº 427 - Leme - SP
Data: {hoje:%d/%m/%Y}

CLÁUSULA PRIMEIRA - OBJETO
{objeto}

CLÁUSULA SEGUNDA - VALOR E CONDIÇÕES DE PAGAMENTO
Valor total: R$ {valor:,.2f}
Prazo: {prazo_meses} meses
Pagamento: 30 dias após medição

CLÁUSULA TERCEIRA - PRAZO
Início: {hoje:%d/%m/%Y}
Término: {fim:%d/%m/%Y}

CLÁUSULA QUARTA - OBRIGAÇÕES DA CONTRATADA
- Executar os serviços conforme escopo e cronograma aprovados
- Alocar equipe técnica qualificada
- Fornecer relatórios mensais de acompanhamento
- Cumprir normas NR-10, NR-35 e demais aplicáveis

CLÁUSULA QUINTA - OBRIGAÇÕES DA CONTRATANTE
- Disponibilizar acesso ao local dos serviços
- Fornecer informações técnicas necessárias
- Efetuar os pagamentos nas datas acordadas

CLÁUSULA SEXTA - RESCISÃO
O contrato poderá ser rescindido por qualquer parte mediante aviso prévio de 30 dias.

CLÁUSULA SÉTIMA - FORO
Fica eleito o foro da Comarca de Leme - SP para dirimir dúvidas.

__________________________________        __________________________________
BUENOSERV ENGENHARIA                       {cliente}
"""
    with open(saida, 'w') as f:
        f.write(contrato)
    print(f"✅ Contrato gerado: {saida}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: gen_contrato.py <cliente> <objeto> <valor> [prazo_meses]")
        sys.exit(1)
    gerar_contrato(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 12)
