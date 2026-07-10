#!/usr/bin/env python3
"""BUENOSERV — Emissão Automática de NF-e (simulada)"""
import json, os, sys, datetime, hashlib
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

DADOS_EMPRESA = {
    "razao_social": "BUENOSERV SERVIÇOS DE ENGENHARIA LTDA",
    "cnpj": "60.490.193/0001-38",
    "ie": "Isento (Simples Nacional)",
    "regime": "Simples Nacional (LC 123/2006)",
    "endereco": "Rua Giacomo Fior, 427, Leme - SP, 13610-000",
    "telefone": "(11) 99999-8888",
    "pix": "60.490.193/0001-38"
}

ANEXO_IV_ALIQUOTAS = [
    (180000, 0.045, 0),
    (360000, 0.078, 5940),
    (720000, 0.10, 13860),
    (1800000, 0.1125, 22500),
    (3600000, 0.1355, 62100),
    (4800000, 0.147, 125640)
]

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def format_money(v):
    return f"R$ {v:,.2f}"

def calcular_aliquota_simples(receita_bruta_12m):
    for teto, aliquota, deduzir in ANEXO_IV_ALIQUOTAS:
        if receita_bruta_12m <= teto:
            return aliquota, deduzir
    return 0.147, 125640

def calcular_impostos_nf(valor, receita_bruta_12m=0):
    aliquota, deduzir = calcular_aliquota_simples(receita_bruta_12m or valor * 12)
    pis = valor * 0.0065
    cofins = valor * 0.03
    iss = valor * 0.02
    simples = valor * aliquota - (deduzir / 12) if receita_bruta_12m > 0 else 0
    total_impostos = pis + cofins + iss + simples
    return {
        "pis": round(pis, 2),
        "cofins": round(cofins, 2),
        "iss": round(iss, 2),
        "simples_nacional": round(max(simples, 0), 2),
        "total_impostos": round(total_impostos, 2),
        "aliquota_efetiva": round(aliquota * 100, 2),
        "valor_liquido": round(valor - total_impostos, 2)
    }

def gerar_chave_acesso(nf_numero, serie="1", emissao=None):
    emissao = emissao or datetime.date.today()
    cnpj = DADOS_EMPRESA["cnpj"].replace(".", "").replace("/", "").replace("-", "")
    uf = "35"
    data = emissao.strftime("%y%m")
    modelo = "55"
    serie = serie.zfill(3)
    numero = str(nf_numero).zfill(9)
    tp_emis = "1"
    codigo = f"{uf}{data}{cnpj}{modelo}{serie}{numero}{tp_emis}"
    dv = 0
    soma = 0
    pesos = [4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2]
    for i, c in enumerate(codigo):
        if i < len(pesos):
            soma += int(c) * pesos[i]
    resto = soma % 11
    dv = 0 if resto < 2 else 11 - resto
    return codigo + str(dv)

def gerar_nfe(cliente, cpf_cnpj, descricao, valor, quantidade=1, receita_bruta_12m=0):
    state = carregar_estado()
    nfes = state.setdefault("nfes", [])
    nf_numero = len(nfes) + 1
    hoje = datetime.date.today()
    chave = gerar_chave_acesso(nf_numero)
    impostos = calcular_impostos_nf(valor, receita_bruta_12m)
    nfe = {
        "id": f"BSE-NFE-{nf_numero:04d}",
        "numero": nf_numero,
        "serie": "1",
        "chave_acesso": chave,
        "data_emissao": hoje.isoformat(),
        "data_saida": hoje.isoformat(),
        "emitente": DADOS_EMPRESA,
        "destinatario": {
            "nome": cliente,
            "cpf_cnpj": cpf_cnpj,
            "endereco": ""
        },
        "produtos": [{
            "codigo": f"SRV-{nf_numero:04d}",
            "descricao": descricao,
            "ncm": "99999999",
            "cfop": "5902",
            "unidade": "UN",
            "quantidade": quantidade,
            "valor_unitario": round(valor / quantidade, 2),
            "valor_total": valor
        }],
        "valor_total": valor,
        "impostos": impostos,
        "valor_liquido": impostos["valor_liquido"],
        "status": "autorizada",
        "protocolo": f"SP{hoje.strftime('%d%m%Y')}{nf_numero:08d}"
    }
    nfes.append(nfe)
    salvar_estado(state)
    return nfe

def gerar_pdf_nfe(nfe):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>NF-e {nfe['id']}</title>
<style>
body{{font-family:monospace;font-size:12px;padding:20px}}
.header{{text-align:center;border-bottom:2px solid #000;padding-bottom:10px;margin-bottom:10px}}
.header h1{{font-size:18px;margin:0}}
.chave{{font-size:14px;font-weight:bold;letter-spacing:2px;text-align:center;margin:10px 0;padding:8px;background:#eee}}
table{{width:100%;border-collapse:collapse;margin:8px 0}}
td,th{{border:1px solid #333;padding:6px;text-align:left}}
th{{background:#ddd}}
.total{{font-size:16px;font-weight:bold;text-align:right;margin:10px 0}}
.footer{{border-top:2px solid #000;margin-top:20px;padding-top:10px;font-size:10px;text-align:center}}
</style></head><body>
<div class="header">
<h1>NOTA FISCAL ELETRÔNICA</h1>
<p>{DADOS_EMPRESA['razao_social']} — CNPJ: {DADOS_EMPRESA['cnpj']}</p>
<p>{DADOS_EMPRESA['endereco']}</p>
</div>
<div class="chave">Chave de Acesso: {nfe['chave_acesso']}</div>
<p><b>Número:</b> {nfe['numero']:04d} &nbsp; <b>Série:</b> {nfe['serie']} &nbsp; <b>Emissão:</b> {nfe['data_emissao']}</p>
<p><b>Destinatário:</b> {nfe['destinatario']['nome']} — {nfe['destinatario']['cpf_cnpj']}</p>
<table>
<tr><th>Código</th><th>Descrição</th><th>NCM</th><th>CFOP</th><th>Qtd</th><th>V.Unit</th><th>V.Total</th></tr>
<tr><td>{nfe['produtos'][0]['codigo']}</td><td>{nfe['produtos'][0]['descricao']}</td>
<td>{nfe['produtos'][0]['ncm']}</td><td>{nfe['produtos'][0]['cfop']}</td>
<td>{nfe['produtos'][0]['quantidade']}</td>
<td>{format_money(nfe['produtos'][0]['valor_unitario'])}</td>
<td>{format_money(nfe['produtos'][0]['valor_total'])}</td></tr>
</table>
<div class="total">Valor Total: {format_money(nfe['valor_total'])}</div>
<table>
<tr><th>PIS</th><td>{format_money(nfe['impostos']['pis'])}</td></tr>
<tr><th>COFINS</th><td>{format_money(nfe['impostos']['cofins'])}</td></tr>
<tr><th>ISS</th><td>{format_money(nfe['impostos']['iss'])}</td></tr>
<tr><th>Simples Nacional</th><td>{format_money(nfe['impostos']['simples_nacional'])}</td></tr>
<tr><th>Total Impostos</th><td>{format_money(nfe['impostos']['total_impostos'])}</td></tr>
<tr><th>Valor Líquido</th><td>{format_money(nfe['impostos']['valor_liquido'])}</td></tr>
</table>
<p><b>Protocolo:</b> {nfe['protocolo']}</p>
<div class="footer">
<p>BUENOSERV SERVIÇOS DE ENGENHARIA LTDA — CNPJ: 60.490.193/0001-38</p>
<p>Regime: Simples Nacional — Consulte pela Chave de Acesso em www.nfe.fazenda.gov.br</p>
</div>
</body></html>"""
    try:
        from weasyprint import HTML
        saida = f"/tmp/nfe_{nfe['id']}.pdf"
        HTML(string=html).write_pdf(saida)
        print(f"✅ PDF gerado: {saida}")
        return saida
    except ImportError:
        saida = f"/tmp/nfe_{nfe['id']}.html"
        with open(saida, "w") as f:
            f.write(html)
        print(f"⚠️ weasyprint não instalado. HTML salvo: {saida}")
        print("  Instale: pip install weasyprint")
        return saida

def enviar_nfe_email(nfe, email_cliente):
    try:
        sys.path.insert(0, '/tmp/opencode/templates')
        from enviar_email import enviar
        html = f"""<html><body style="font-family:sans-serif">
<h2>NF-e {nfe['id']} — BUENOSERV</h2>
<p><b>Cliente:</b> {nfe['destinatario']['nome']}</p>
<p><b>Valor:</b> {format_money(nfe['valor_total'])}</p>
<p><b>Chave de Acesso:</b> {nfe['chave_acesso']}</p>
<p><b>Protocolo:</b> {nfe['protocolo']}</p>
<p>Segue em anexo a Nota Fiscal Eletrônica.</p>
<p>Atenciosamente,<br>Ricardo Bueno — BUENOSERV</p>
</body></html>"""
        enviar(email_cliente, f"NF-e {nfe['id']} — BUENOSERV", html,
               anexos=[f"/tmp/nfe_{nfe['id']}.pdf"])
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

def registrar_dre(nfe):
    state = carregar_estado()
    dre = state.setdefault("dre", {"ano": datetime.date.today().year, "meses": {}})
    mes = str(datetime.date.today().month)
    if mes not in dre["meses"]:
        dre["meses"][mes] = {
            "ano": datetime.date.today().year,
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
    dm = dre["meses"][mes]
    dm["receita_bruta"] += nfe["valor_total"]
    dm["deducoes"] += nfe["impostos"]["total_impostos"]
    dm["receita_liquida"] = dm["receita_bruta"] - dm["deducoes"]
    dm["despesas_tributarias"] += nfe["impostos"]["total_impostos"]
    dm["custos_servicos"] = dm["receita_bruta"] * 0.35
    dm["lucro_bruto"] = dm["receita_liquida"] - dm["custos_servicos"]
    dm["despesas_administrativas"] = dm["receita_bruta"] * 0.12
    dm["despesas_comerciais"] = dm["receita_bruta"] * 0.05
    dm["lucro_operacional"] = dm["lucro_bruto"] - dm["despesas_administrativas"] - dm["despesas_comerciais"] - dm["despesas_tributarias"]
    dm["resultado_financeiro"] = dm["receita_bruta"] * 0.005
    dm["lucro_liquido"] = dm["lucro_operacional"] + dm["resultado_financeiro"]
    salvar_estado(state)
    print(f"✅ DRE atualizado para mês {mes}")

def exibir_nfe(nfe):
    print(f"\n{'='*55}")
    print(f"  NOTA FISCAL ELETRÔNICA")
    print(f"  {nfe['id']}")
    print(f"{'='*55}")
    print(f"  Emitente:          {nfe['emitente']['razao_social']}")
    print(f"  CNPJ:              {nfe['emitente']['cnpj']}")
    print(f"  Destinatário:      {nfe['destinatario']['nome']}")
    print(f"  CPF/CNPJ:          {nfe['destinatario']['cpf_cnpj']}")
    print(f"  Descrição:         {nfe['produtos'][0]['descricao']}")
    print(f"  Valor:             {format_money(nfe['valor_total'])}")
    print(f"  Impostos:          {format_money(nfe['impostos']['total_impostos'])}")
    print(f"  Valor Líquido:     {format_money(nfe['impostos']['valor_liquido'])}")
    print(f"  Chave Acesso:      {nfe['chave_acesso']}")
    print(f"  Protocolo:         {nfe['protocolo']}")
    print(f"  Status:            {nfe['status']}")
    print(f"{'='*55}\n")

def listar_nfes():
    state = carregar_estado()
    nfes = state.get("nfes", [])
    if not nfes:
        print("Nenhuma NF-e emitida.")
        return
    print(f"\n{'='*70}")
    print(f"  NF-es emitidas: {len(nfes)}")
    print(f"{'='*70}")
    for nfe in nfes:
        print(f"  {nfe['id']:15s} | {nfe['data_emissao']:10s} | {nfe['destinatario']['nome']:25s} | {format_money(nfe['valor_total']):>12s} | {nfe['status']:10s}")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("BUENOSERV — Emissão de NF-e")
        print(f"Uso: gen_nfe_auto.py <comando> [args]")
        print(f"\nComandos:")
        print(f"  emitir <cliente> <cpf_cnpj> <valor> <descricao>")
        print(f"  listar")
        print(f"  pdf <id_nfe>")
        print(f"  enviar <id_nfe> <email>")
        print(f"  help")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "emitir":
        if len(sys.argv) < 6:
            print("Uso: gen_nfe_auto.py emitir <cliente> <cpf_cnpj> <valor> <descricao> [qtd]")
            sys.exit(1)
        cliente = sys.argv[2]
        cpf_cnpj = sys.argv[3]
        valor = float(sys.argv[4])
        descricao = sys.argv[5]
        qtd = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        nfe = gerar_nfe(cliente, cpf_cnpj, descricao, valor, qtd)
        exibir_nfe(nfe)
        pdf = gerar_pdf_nfe(nfe)
        registrar_dre(nfe)

    elif cmd == "listar":
        listar_nfes()

    elif cmd == "pdf":
        if len(sys.argv) < 3:
            print("Uso: gen_nfe_auto.py pdf <id_nfe>")
            sys.exit(1)
        state = carregar_estado()
        for nfe in state.get("nfes", []):
            if nfe["id"] == sys.argv[2]:
                gerar_pdf_nfe(nfe)
                break
        else:
            print(f"NF-e {sys.argv[2]} não encontrada.")

    elif cmd == "enviar":
        if len(sys.argv) < 4:
            print("Uso: gen_nfe_auto.py enviar <id_nfe> <email>")
            sys.exit(1)
        state = carregar_estado()
        for nfe in state.get("nfes", []):
            if nfe["id"] == sys.argv[2]:
                pdf = gerar_pdf_nfe(nfe)
                enviar_nfe_email(nfe, sys.argv[3])
                break
        else:
            print(f"NF-e {sys.argv[2]} não encontrada.")

    elif cmd == "help":
        print("Comandos disponíveis:")
        print("  emitir <cliente> <cpf_cnpj> <valor> <descricao> [qtd]")
        print("  listar")
        print("  pdf <id_nfe>")
        print("  enviar <id_nfe> <email>")
    else:
        print(f"Comando desconhecido: {cmd}")
