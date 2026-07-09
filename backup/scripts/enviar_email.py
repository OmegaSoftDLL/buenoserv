#!/usr/bin/env python3
"""Envio de e-mails corporativos BUENOSERV via SMTP local (postfix)"""
import smtplib, json, sys, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime

EMAIL_PADRAO = "ricardo.bueno@buenoservengenharia.com"
NOME_REMETENTE = "Ricardo Bueno - BUENOSERV ENGENHARIA"
LOGO_PATH = os.path.expanduser("~/.config/opencode/agents/logo-buenoserv.jpeg")

def enviar(destinatario, assunto, corpo_html, corpo_texto="", anexos=None,
           de=EMAIL_PADRAO, nome=NOME_REMETENTE):
    # Camada externa: mixed (permite inline + anexos)
    msg_outer = MIMEMultipart('mixed')
    msg_outer['From'] = f"{nome} <{de}>"
    msg_outer['To'] = destinatario
    msg_outer['Subject'] = assunto

    # Camada interna: related (html + imagens inline)
    msg_related = MIMEMultipart('related')
    msg_html = MIMEText(corpo_html, 'html', 'utf-8')
    msg_related.attach(msg_html)

    # Anexar logo inline
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename='logo-buenoserv.jpeg')
            msg_related.attach(logo)

    msg_outer.attach(msg_related)

    # Anexos (PDF, planilhas, etc.)
    if anexos:
        for path in anexos:
            if not os.path.exists(path):
                print(f"⚠️ Anexo não encontrado: {path}")
                continue
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                    f'attachment; filename="{os.path.basename(path)}"')
                msg_outer.attach(part)

    try:
        with smtplib.SMTP('localhost', 25) as s:
            s.send_message(msg_outer)
        print(f"✅ E-mail enviado para {destinatario}: {assunto}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

HEADER_HTML = """\
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto;">
<tr><td style="padding:20px 30px 10px 30px; border-bottom:3px solid #C9A84C;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="vertical-align:middle;">
<span style="font-size:22px; font-weight:bold; color:#1A237E; letter-spacing:1px;">BUENOSERV</span><br>
<span style="font-size:11px; color:#888; letter-spacing:2px; text-transform:uppercase;">Engenharia &amp; Telecomunicações</span>
</td>
<td style="vertical-align:middle; text-align:right; width:120px;">
<img src="cid:logo" alt="Logo" style="height:55px; width:auto;">
</td>
</tr>
</table>
</td></tr></table>"""

FOOTER_HTML = """\
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto;">
<tr><td style="padding:25px 30px 20px 30px; background:#F8F9FA; border-top:1px solid #E0E0E0;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="vertical-align:top; width:50%; font-size:12px; color:#666; line-height:1.6;">
<b style="color:#1A237E;">BUENOSERV SERVIÇOS DE ENGENHARIA LTDA</b><br>
CNPJ: 60.490.193/0001-38<br>
Rua Giacomo Fior, 427 - Leme - SP
</td>
<td style="vertical-align:top; width:50%; font-size:12px; color:#666; line-height:1.6; text-align:right;">
<b style="color:#1A237E;">Ricardo Bueno</b><br>
Diretor Técnico<br>
ricardo.bueno@buenoservengenharia.com
</td>
</tr>
</table>
</td></tr>
<tr><td style="padding:10px 30px; text-align:center; color:#AAA; font-size:10px; letter-spacing:1px;">
Engenharia que conecta o futuro
</td></tr></table>"""

def template_followup_proposta(nome_cliente, contato, proposta_id, valor, data_envio):
    return f"""\
<html>
<body style="font-family:Calibri,'Segoe UI',sans-serif; color:#333; margin:0; padding:0; background:#F5F5F5;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F5F5F5; padding:20px 0;">
{HEADER_HTML}
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto; background:#FFFFFF;">
<tr><td style="padding:35px 30px 25px 30px;">
<div style="background:#1A237E; color:#FFFFFF; padding:3px 12px; display:inline-block; border-radius:3px; font-size:11px; letter-spacing:1px; font-weight:bold; margin-bottom:15px;">PROPOSTA {proposta_id}</div>
<h2 style="color:#1A237E; margin:0 0 5px 0; font-size:22px;">Follow-up</h2>
<p style="color:#666; margin:0 0 25px 0; font-size:14px;">Acompanhamento da proposta enviada em {data_envio}</p>
<p style="line-height:1.6;">Prezado(a) <b>{contato}</b>,</p>
<p style="line-height:1.6;">Esperamos que este e-mail o(a) encontre bem. Em <b>{data_envio}</b> encaminhamos nossa Proposta <b>{proposta_id}</b> para o projeto <b>{nome_cliente}</b> e gostaríamos de saber se V.S.ª teve oportunidade de analisar o material.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F4FF; border-left:4px solid #1A237E; border-radius:4px; margin:20px 0;">
<tr><td style="padding:15px 20px;">
<table width="100%" cellpadding="3" cellspacing="0">
<tr><td style="color:#666; font-size:13px; width:120px;">Valor mensal</td><td style="font-weight:bold; font-size:13px;">R$ {valor/12:,.2f}</td></tr>
<tr><td style="color:#666; font-size:13px;">Investimento anual</td><td style="font-weight:bold; font-size:13px;">R$ {valor:,.2f}</td></tr>
<tr><td style="color:#666; font-size:13px;">Validade</td><td style="font-weight:bold; font-size:13px;">30 dias</td></tr>
<tr><td style="color:#666; font-size:13px;">Escopo</td><td style="font-weight:bold; font-size:13px;">Consultoria técnica em telecomunicações</td></tr>
</table>
</td></tr>
</table>
<p style="line-height:1.6;">Estamos à disposição para uma reunião online ou presencial para esclarecermos dúvidas e detalharmos a proposta.</p>
<p style="line-height:1.6;">Aguardo seu contato.</p>
<br>
<p style="margin:0; line-height:1.4;">Atenciosamente,</p>
<p style="margin:5px 0 0 0; font-size:16px; color:#1A237E;"><b>Ricardo Bueno</b></p>
<p style="margin:0; color:#666; font-size:13px;">Diretor Técnico</p>
</td></tr>
</table>
{FOOTER_HTML}
</table>
</body>
</html>"""

def template_prospeccao(nome_empresa, contato, segmento=""):
    return f"""\
<html>
<body style="font-family:Calibri,'Segoe UI',sans-serif; color:#333; margin:0; padding:0; background:#F5F5F5;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F5F5F5; padding:20px 0;">
{HEADER_HTML}
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto; background:#FFFFFF;">
<tr><td style="padding:35px 30px 25px 30px;">
<div style="background:#C9A84C; color:#FFFFFF; padding:3px 12px; display:inline-block; border-radius:3px; font-size:11px; letter-spacing:1px; font-weight:bold; margin-bottom:15px;">APRESENTAÇÃO</div>
<h2 style="color:#1A237E; margin:0 0 5px 0; font-size:22px;">BUENOSERV Engenharia</h2>
<p style="color:#666; margin:0 0 25px 0; font-size:14px;">Soluções em telecomunicações, automação e energia para o setor elétrico</p>
<p style="line-height:1.6;">Prezado(a) <b>{contato}</b>,</p>
<p style="line-height:1.6;">A <b>BUENOSERV</b> é uma empresa de engenharia especializada em <b>telecomunicações, automação de subestações, energia e segurança</b> para concessionárias, indústrias e integradoras do setor elétrico.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
<tr>
<td style="width:50%; vertical-align:top; padding:10px 15px; background:#F0F4FF; border-radius:4px;">
<b style="color:#1A237E; font-size:13px;">🔹 Telecomunicações</b>
<p style="font-size:12px; color:#666; margin:5px 0 0 0; line-height:1.4;">Redes DWDM, MPLS-TP, SDH, rádio MW, fibra óptica, CCTV</p>
</td>
<td style="width:10px;"></td>
<td style="width:50%; vertical-align:top; padding:10px 15px; background:#F0F4FF; border-radius:4px;">
<b style="color:#1A237E; font-size:13px;">🔹 Automação de SE</b>
<p style="font-size:12px; color:#666; margin:5px 0 0 0; line-height:1.4;">IEC 61850, teleproteção, SCADA, RTU, IEDs, PMU</p>
</td>
</tr>
<tr><td height="8" colspan="3"></td></tr>
<tr>
<td style="width:50%; vertical-align:top; padding:10px 15px; background:#F0F4FF; border-radius:4px;">
<b style="color:#1A237E; font-size:13px;">🔹 Comissionamento</b>
<p style="font-size:12px; color:#666; margin:5px 0 0 0; line-height:1.4;">Testes FAT/SAT, start-up, integração de sistemas, laudos</p>
</td>
<td style="width:10px;"></td>
<td style="width:50%; vertical-align:top; padding:10px 15px; background:#F0F4FF; border-radius:4px;">
<b style="color:#1A237E; font-size:13px;">🔹 Infraestrutura</b>
<p style="font-size:12px; color:#666; margin:5px 0 0 0; line-height:1.4;">Projetos turn-key, engenharia civil/elétrica, SPDA, CFTV</p>
</td>
</tr>
</table>
<p style="line-height:1.6;">Com mais de <b>20 anos de experiência</b> em comissionamento de subestações de até 500 kV, sistemas de proteção e redes de telecomunicações críticas, entregamos soluções com excelência e segurança.</p>
<p style="line-height:1.6;">Gostaríamos de agendar uma visita técnica para apresentar nossos serviços e identificar oportunidades de parceria com a <b>{nome_empresa}</b>.</p>
<br>
<p style="margin:0; line-height:1.4;">Atenciosamente,</p>
<p style="margin:5px 0 0 0; font-size:16px; color:#1A237E;"><b>Ricardo Bueno</b></p>
<p style="margin:0; color:#666; font-size:13px;">Diretor Técnico</p>
</td></tr>
</table>
{FOOTER_HTML}
</table>
</body>
</html>"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: enviar_email.py <comando> <args_json>")
        print("Comandos: followup, prospeccao, personalizado")
        sys.exit(1)

    cmd = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    if cmd == "followup":
        html = template_followup_proposta(
            args.get("cliente","Cliente"),
            args.get("contato","Contato"),
            args.get("proposta_id","BSE-00"),
            args.get("valor",0),
            args.get("data_envio","00/00/0000"))
        enviar(args["destinatario"], args["assunto"], html)

    elif cmd == "prospeccao":
        html = template_prospeccao(
            args.get("empresa","Empresa"),
            args.get("contato","Contato"))
        enviar(args["destinatario"], args["assunto"], html)

    elif cmd == "personalizado":
        enviar(args["destinatario"], args["assunto"],
               args.get("corpo_html",""), args.get("corpo_texto",""))

    else:
        print(f"Comando desconhecido: {cmd}")
