#!/usr/bin/env python3
"""BUENOSERV — Sistema de Cobrança: Boletos, Lembretes, Contas a Receber, Conciliação"""
import json, os, sys, datetime, smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
EMAIL_PADRAO = "ricardo.bueno@buenoservengenharia.com"
NOME_REMETENTE = "Ricardo Bueno - BUENOSERV ENGENHARIA"

DADOS_BOLETO = {
    "banco": "Banco BTG Pactual (208)",
    "agencia": "0050",
    "conta": "2321479-4",
    "cedente": "BUENOSERV SERVIÇOS DE ENGENHARIA LTDA",
    "cnpj": "60.490.193/0001-38",
    "pix": "60.490.193/0001-38"
}

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def format_money(v):
    return f"R$ {v:,.2f}"

def gerar_boleto_html(cliente, valor, vencimento, descricao, nosso_numero):
    hoje = datetime.date.today()
    dias_restantes = (vencimento - hoje).days
    status = "VENCIDO" if dias_restantes < 0 else f"Vence em {dias_restantes} dias" if dias_restantes > 0 else "VENCE HOJE"
    status_cor = "#f44336" if dias_restantes < 0 else "#4caf50" if dias_restantes > 5 else "#ff9800"

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Boleto {nosso_numero}</title>
<style>
@page{{size:210mm 297mm;margin:10mm}}
body{{font-family:monospace,sans-serif;font-size:11px;color:#222;padding:0;margin:0}}
.boletobox{{max-width:700px;margin:auto;border:2px solid #333;padding:20px}}
.header{{border-bottom:3px solid #C9A84C;padding-bottom:10px;margin-bottom:15px;text-align:center}}
.header h1{{font-size:20px;color:#1A237E;margin:0}}
.header h2{{font-size:14px;color:#666;margin:2px 0 0 0;font-weight:normal}}
.logo-bar{{background:#1A237E;color:white;padding:8px 15px;font-size:13px;font-weight:bold;margin-bottom:15px}}
.logo-bar span{{color:#C9A84C}}
.linha{{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed #ccc}}
.linha .label{{color:#666;width:180px}}
.linha .valor{{font-weight:bold;flex:1}}
.status-badge{{display:inline-block;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:13px}}
.dados-banco{{background:#f5f5f5;padding:10px;margin:10px 0;border-radius:4px}}
.codigo-barras{{text-align:center;font-size:18px;letter-spacing:3px;font-family:monospace;padding:12px;background:#eee;margin:12px 0;border-radius:4px}}
.total{{font-size:22px;font-weight:bold;text-align:right;color:#1A237E;padding:8px 0;border-top:2px solid #C9A84C;margin-top:10px}}
.pix-section{{background:#e8f5e9;padding:10px;border-radius:4px;margin:10px 0;text-align:center;font-size:14px}}
.pix-section .pix-key{{font-size:18px;font-weight:bold;letter-spacing:1px;color:#1A237E}}
.footer{{text-align:center;padding:12px;color:#999;font-size:9px;border-top:1px solid #ddd;margin-top:15px}}
.recibo{{border:2px dashed #999;padding:12px;margin-top:15px;font-size:10px}}
</style></head><body>
<div class="boletobox">
<div class="header">
<h1>BOLETO BANCÁRIO</h1>
<h2>{DADOS_BOLETO["cedente"]}</h2>
</div>
<div class="logo-bar">BUENOSERV <span>ENGENHARIA</span> — CNPJ: {DADOS_BOLETO["cnpj"]}</div>

<div class="status-badge" style="background:{status_cor}22;color:{status_cor};border:1px solid {status_cor}66">{status}</div>

<div class="dados-banco">
<div class="linha"><span class="label">Banco</span><span class="valor">{DADOS_BOLETO["banco"]}</span></div>
<div class="linha"><span class="label">Agência / Conta</span><span class="valor">{DADOS_BOLETO["agencia"]} / {DADOS_BOLETO["conta"]}</span></div>
<div class="linha"><span class="label">Nosso Número</span><span class="valor">{nosso_numero}</span></div>
</div>

<div class="linha"><span class="label">Cliente</span><span class="valor">{cliente}</span></div>
<div class="linha"><span class="label">Descrição</span><span class="valor">{descricao}</span></div>
<div class="linha"><span class="label">Data Emissão</span><span class="valor">{hoje.strftime('%d/%m/%Y')}</span></div>
<div class="linha"><span class="label">Data Vencimento</span><span class="valor" style="color:{status_cor};font-weight:bold">{vencimento.strftime('%d/%m/%Y')}</span></div>

<div class="total">Valor: {format_money(valor)}</div>

<div class="codigo-barras">{nosso_numero[:4]}.{nosso_numero[4:8]} {nosso_numero[8:12]}.{nosso_numero[12:16]} {nosso_numero[16:20]}.{nosso_numero[20:24]} {nosso_numero[24:28]}.{nosso_numero[28:32]} {nosso_numero[32:38]}</div>

<div class="pix-section">
<p>PIX — Pagamento Instantâneo</p>
<div class="pix-key">{DADOS_BOLETO["pix"]}</div>
<p style="font-size:10px;color:#666;margin-top:4px">Chave: CNPJ</p>
</div>

<div class="recibo">
<p><b>RECIBO DO PAGADOR</b></p>
<p>Declaro ter recebido o boleto acima e me comprometo a efetuar o pagamento até a data de vencimento.</p>
<p style="margin-top:8px">Assinatura: ______________________________ &nbsp; Data: ___/___/___</p>
</div>

<div class="footer">
{DADOS_BOLETO["cedente"]} — CNPJ: {DADOS_BOLETO["cnpj"]}<br>
Rua Giacomo Fior, 427 - Leme - SP — E-mail: {EMAIL_PADRAO}
</div>
</div></body></html>"""

def gerar_boleto(cliente, valor, vencimento_dias=30, descricao=""):
    state = carregar_estado()
    boletos = state.setdefault("boletos", [])
    hoje = datetime.date.today()
    vencimento = hoje + datetime.timedelta(days=vencimento_dias)
    nosso_numero = f"{hoje.year}{hoje.month:02d}{hoje.day:02d}{(len(boletos)+1):04d}{hash(cliente+str(valor))%10000:04d}"
    boleto = {
        "id": f"BSE-BOL-{len(boletos)+1:04d}",
        "cliente": cliente,
        "valor": valor,
        "descricao": descricao or f"Serviços de engenharia — {hoje.strftime('%B/%Y')}",
        "emissao": hoje.isoformat(),
        "vencimento": vencimento.isoformat(),
        "nosso_numero": nosso_numero,
        "status": "emitido",
        "pago_em": None,
        "valor_pago": 0
    }
    boletos.append(boleto)
    salvar_estado(state)
    html = gerar_boleto_html(cliente, valor, vencimento, boleto["descricao"], nosso_numero)
    saida = f"/tmp/boleto_{boleto['id']}.html"
    with open(saida, "w") as f:
        f.write(html)
    print(f"✅ Boleto gerado: {saida}")
    return boleto

def enviar_lembrete(cliente, email, dias_vencimento=5):
    state = carregar_estado()
    boletos_cliente = [b for b in state.get("boletos", [])
                       if b["cliente"].lower() == cliente.lower() and b["status"] == "emitido"]
    if not boletos_cliente:
        print(f"❌ Nenhum boleto pendente para {cliente}")
        return False
    hoje = datetime.date.today()
    vencidos = [b for b in boletos_cliente if datetime.date.fromisoformat(b["vencimento"]) < hoje]
    a_vencer = [b for b in boletos_cliente if (datetime.date.fromisoformat(b["vencimento"]) - hoje).days <= dias_vencimento]
    selecionados = vencidos + a_vencer
    if not selecionados:
        print(f"✅ Nenhum boleto próximo do vencimento para {cliente}")
        return True
    corpo = f"""<html><body style="font-family:sans-serif;background:#f5f5f5;padding:20px">
<div style="max-width:600px;margin:auto;background:white;border-radius:8px;padding:30px;border:1px solid #ddd">
<div style="border-bottom:3px solid #C9A84C;padding-bottom:10px;margin-bottom:20px">
<span style="font-size:22px;font-weight:bold;color:#1A237E">BUENOSERV</span>
<span style="font-size:11px;color:#888;margin-left:10px">Engenharia & Telecomunicações</span>
</div>
<h2 style="color:#1A237E">Lembrete de Pagamento</h2>
<p>Prezado(a) <b>{cliente}</b>,</p>
<p>Identificamos o(s) seguinte(s) boleto(s) próximo(s) do vencimento ou em atraso:</p>
<table style="width:100%;border-collapse:collapse;margin:15px 0">
<tr style="background:#1A237E;color:white"><th style="padding:8px;text-align:left">Vencimento</th><th style="padding:8px;text-align:left">Valor</th><th style="padding:8px;text-align:left">Status</th></tr>"""
    for b in selecionados:
        venc = datetime.date.fromisoformat(b["vencimento"])
        dias = (venc - hoje).days
        if dias < 0:
            status = f'<span style="color:#f44336;font-weight:bold">VENCIDO ({abs(dias)} dias)</span>'
        elif dias == 0:
            status = '<span style="color:#ff9800;font-weight:bold">VENCE HOJE</span>'
        else:
            status = f'<span style="color:#4caf50">Vence em {dias} dias</span>'
        corpo += f'<tr><td style="padding:8px;border-bottom:1px solid #ddd">{venc.strftime("%d/%m/%Y")}</td><td style="padding:8px;border-bottom:1px solid #ddd;font-weight:bold">{format_money(b["valor"])}</td><td style="padding:8px;border-bottom:1px solid #ddd">{status}</td></tr>'
    corpo += f"""</table>
<p style="background:#fff3e0;padding:12px;border-radius:4px;font-size:13px">
<b>PIX:</b> {DADOS_BOLETO["pix"]} (CNPJ) — Banco BTG Pactual</p>
<p>Solicitamos a regularização o quanto antes para evitar encargos.</p>
<br><p>Atenciosamente,<br><b>Ricardo Bueno</b><br>Diretor Técnico — BUENOSERV</p>
<div style="border-top:1px solid #ddd;padding-top:10px;margin-top:15px;font-size:11px;color:#888;text-align:center">
{DADOS_BOLETO["cedente"]} — CNPJ: {DADOS_BOLETO["cnpj"]}<br>
Rua Giacomo Fior, 427 - Leme - SP
</div></div></body></html>"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{NOME_REMETENTE} <{EMAIL_PADRAO}>"
        msg['To'] = email
        msg['Subject'] = f"BUENOSERV — Lembrete de Pagamento ({len(selecionados)} boleto(s))"
        msg.attach(MIMEText(corpo, 'html', 'utf-8'))
        with smtplib.SMTP('localhost', 25) as s:
            s.send_message(msg)
        print(f"✅ Lembrete enviado para {email} ({len(selecionados)} boleto(s))")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

def contas_a_receber():
    state = carregar_estado()
    boletos = state.get("boletos", [])
    hoje = datetime.date.today()
    resumo = {
        "total_emitido": len(boletos),
        "total_pago": len([b for b in boletos if b["status"] == "pago"]),
        "total_pendente": len([b for b in boletos if b["status"] == "emitido"]),
        "total_vencido": len([b for b in boletos if b["status"] == "emitido" and datetime.date.fromisoformat(b["vencimento"]) < hoje]),
        "valor_total_pendente": sum(b["valor"] for b in boletos if b["status"] == "emitido"),
        "valor_total_vencido": sum(b["valor"] for b in boletos if b["status"] == "emitido" and datetime.date.fromisoformat(b["vencimento"]) < hoje),
        "valor_total_recebido": sum(b["valor_pago"] for b in boletos if b["status"] == "pago"),
        "boletos": boletos
    }
    return resumo

def notificar_vencimento():
    state = carregar_estado()
    hoje = datetime.date.today()
    for b in state.get("boletos", []):
        if b["status"] != "emitido":
            continue
        venc = datetime.date.fromisoformat(b["vencimento"])
        dias = (venc - hoje).days
        if -1 <= dias <= 3:  # Vence hoje, ontem ou nos próximos 3 dias
            print(f"⚠️ Boleto {b['id']} — {b['cliente']} — {format_money(b['valor'])} — Vence {venc.strftime('%d/%m/%Y')} ({'venceu' if dias < 0 else f'em {dias} dias'})")
    return True

def conciliar(extrato_path=None):
    state = carregar_estado()
    boletos = state.setdefault("boletos", [])
    lancamentos = state.setdefault("conciliacao", [])

    if extrato_path:
        try:
            with open(extrato_path) as f:
                ext = json.load(f)
        except:
            print(f"❌ Erro ao ler extrato: {extrato_path}")
            return
        conciliados = 0
        for item in ext:
            valor = float(item.get("valor", 0))
            desc = item.get("descricao", "").lower()
            data = item.get("data", "")
            for b in boletos:
                if b["status"] != "emitido":
                    continue
                if abs(b["valor"] - valor) < 0.01:
                    b["status"] = "pago"
                    b["pago_em"] = data
                    b["valor_pago"] = valor
                    lancamentos.append({
                        "boleto_id": b["id"],
                        "cliente": b["cliente"],
                        "valor": valor,
                        "data_pagamento": data,
                        "origem": extrato_path
                    })
                    conciliados += 1
                    print(f"✅ Conciliado: {b['id']} — {b['cliente']} — {format_money(valor)}")
                    break
        salvar_estado(state)
        print(f"\n📊 Conciliação: {conciliados}/{len(ext)} lançamentos conciliados")
    else:
        pendentes = [b for b in boletos if b["status"] == "emitido"]
        print(f"\n{'='*50}")
        print(f"  CONCILIAÇÃO BANCÁRIA")
        print(f"{'='*50}")
        print(f"  Boletos emitidos:     {len(boletos)}")
        print(f"  Conciliados (pagos):  {len(lancamentos)}")
        print(f"  Pendentes:            {len(pendentes)}")
        print(f"  Total pendente:       {format_money(sum(b['valor'] for b in pendentes))}")
        print(f"{'='*50}\n")
        if pendentes:
            print("  Pendentes de conciliação:")
            for b in pendentes:
                print(f"    {b['id']:15s} {b['cliente']:25s} {format_money(b['valor']):>10s} — Vence {b['vencimento']}")

def exibir_contas_receber():
    resumo = contas_a_receber()
    print(f"\n{'='*55}")
    print(f"  CONTAS A RECEBER — BUENOSERV")
    print(f"{'='*55}")
    print(f"  Total emitido:          {resumo['total_emitido']}")
    print(f"  Total pago:             {resumo['total_pago']}")
    print(f"  Total pendente:         {resumo['total_pendente']}")
    print(f"  Total vencido:          {resumo['total_vencido']}")
    print(f"  Valor pendente:         {format_money(resumo['valor_total_pendente'])}")
    print(f"  Valor vencido:          {format_money(resumo['valor_total_vencido'])}")
    print(f"  Valor recebido:         {format_money(resumo['valor_total_recebido'])}")
    print(f"{'='*55}\n")
    if resumo["boletos"]:
        print(f"  {'ID':15s} {'Cliente':25s} {'Valor':>10s} {'Vencimento':12s} {'Status':10s}")
        print(f"  {'-'*72}")
        for b in resumo["boletos"]:
            print(f"  {b['id']:15s} {b['cliente']:25s} {format_money(b['valor']):>10s} {b['vencimento']:12s} {b['status']:10s}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("BUENOSERV — Sistema de Cobrança")
        print(f"Uso: gen_cobranca.py <comando> [args]")
        print(f"\nComandos:")
        print(f"  gerar <cliente> <valor> [dias_venc=30] [descricao]")
        print(f"  lembrete <cliente> <email> [dias=5]")
        print(f"  contas")
        print(f"  notificar")
        print(f"  conciliar [extrato.json]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "gerar":
        if len(sys.argv) < 4:
            print("Uso: gen_cobranca.py gerar <cliente> <valor> [dias_venc=30] [descricao]")
            sys.exit(1)
        cliente = sys.argv[2]
        valor = float(sys.argv[3])
        dias = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        desc = sys.argv[5] if len(sys.argv) > 5 else ""
        boleto = gerar_boleto(cliente, valor, dias, desc)
        print(f"  ID:       {boleto['id']}")
        print(f"  Cliente:  {boleto['cliente']}")
        print(f"  Valor:    {format_money(boleto['valor'])}")
        print(f"  Venc:     {boleto['vencimento']}")

    elif cmd == "lembrete":
        if len(sys.argv) < 4:
            print("Uso: gen_cobranca.py lembrete <cliente> <email> [dias=5]")
            sys.exit(1)
        cliente = sys.argv[2]
        email = sys.argv[3]
        dias = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        enviar_lembrete(cliente, email, dias)

    elif cmd == "contas":
        exibir_contas_receber()

    elif cmd == "notificar":
        notificar_vencimento()

    elif cmd == "conciliar":
        extrato = sys.argv[2] if len(sys.argv) > 2 else None
        conciliar(extrato)

    else:
        print(f"Comando desconhecido: {cmd}")
