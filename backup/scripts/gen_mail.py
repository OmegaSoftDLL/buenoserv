#!/usr/bin/env python3
import sys, json, subprocess, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
FROM = "Ricardo Bueno <ricardo.bueno@buenoservengenharia.com>"

def carregar_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {"agent_count": 81, "emails_enviados": []}

def salvar_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f: json.dump(s, f, indent=2, ensure_ascii=False)

def corpo_padrao():
    return f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:600px;margin:0 auto">
    <div style="background:#0a1628;padding:24px;border-radius:8px 8px 0 0">
        <h1 style="color:#C9A84C;margin:0;font-size:1.2rem">BUENOSERV<small style="color:#666">.</small></h1>
    </div>
    <div style="padding:24px;background:#fff;border:1px solid #e0e0e0;border-top:none">
        {{CORPO}}
    </div>
    <div style="background:#f5f5f5;padding:16px 24px;border-radius:0 0 8px 8px;font-size:.75rem;color:#888">
        <p><b>BUENOSERV SERVIÇOS DE ENGENHARIA LTDA</b><br>
        CNPJ: 60.490.193/0001-38 · Rua Giacomo Fior, 427 — Leme-SP<br>
        BTG Pactual (208) Ag 0050 CC 2321479-4 · PIX: 60.490.193/0001-38</p>
        <p style="color:#aaa">Este e-mail é confidencial. Se recebeu por engano, favor descartar.</p>
    </div>
    </div>"""

def enviar(dest, assunto, corpo_html):
    msg = MIMEMultipart('alternative')
    msg['From'] = FROM
    msg['To'] = dest
    msg['Subject'] = assunto
    txt = corpo_html.replace('<','').replace('>','')
    msg.attach(MIMEText(txt, 'plain', 'utf-8'))
    msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))
    try:
        p = subprocess.run(['/usr/sbin/sendmail', '-t'], input=msg.as_bytes(), capture_output=True, timeout=30)
        if p.returncode == 0:
            s = carregar_state()
            s.setdefault("emails_enviados", []).append({"para": dest, "assunto": assunto, "data": datetime.now().isoformat(), "status": "ok"})
            salvar_state(s)
            print(f"✅ E-mail enviado para {dest}")
            return True
        else:
            print(f"❌ Erro sendmail: {p.stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def enviar_proposta(dest, cliente, valor):
    html = corpo_padrao().replace("{{CORPO}}", f"""
    <h2 style="color:#1A237E">Proposta Técnico-Comercial</h2>
    <p>Prezado(a) {cliente},</p>
    <p>Segue em anexo nossa proposta para o serviço de engenharia solicitado.</p>
    <p><b>Valor estimado:</b> R$ {valor:,.2f}</p>
    <p>Estamos à disposição para esclarecimentos adicionais.</p>
    <p>Atenciosamente,<br><b>Ricardo Bueno</b><br>Eng. Eletricista — BUENOSERV</p>
    """)
    return enviar(dest, f"Proposta BUENOSERV — {cliente}", html)

def enviar_follow_up(dest, nome_cliente):
    html = corpo_padrao().replace("{{CORPO}}", f"""
    <h2 style="color:#1A237E">Follow-up Comercial</h2>
    <p>Prezado(a) {nome_cliente},</p>
    <p>Espero que este e-mail o(a) encontre bem. Venho gentilmente reforçar nossa proposta anteriormente enviada.</p>
    <p>A BUENOSERV está à disposição para adequar a proposta às suas necessidades específicas.</p>
    <p>Atenciosamente,<br><b>Ricardo Bueno</b><br>+20 anos em engenharia de subestações</p>
    """)
    return enviar(dest, "Follow-up comercial — BUENOSERV", html)

def enviar_relatorio(dest, tipo):
    html = corpo_padrao().replace("{{CORPO}}", f"""
    <h2 style="color:#1A237E">Relatório {tipo}</h2>
    <p>Segue em anexo o relatório {tipo.lower()} da BUENOSERV.</p>
    <p>Qualquer dúvida, estamos à disposição.</p>
    <p>Atenciosamente,<br><b>Ricardo Bueno</b></p>
    """)
    return enviar(dest, f"Relatório {tipo} — BUENOSERV", html)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 gen_mail.py <dest> <assunto/tipo> <corpo/cliente>")
        print("Tipos: proposta:<cliente>:<valor> | followup:<cliente> | relatorio:<tipo>")
        sys.exit(1)
    dest = sys.argv[1]
    modo = sys.argv[2]
    arg3 = sys.argv[3]
    if modo.startswith("proposta:"):
        cliente = modo.split(":",1)[1]
        valor = float(arg3)
        enviar_proposta(dest, cliente, valor)
    elif modo.startswith("followup:"):
        cliente = modo.split(":",1)[1]
        enviar_follow_up(dest, cliente)
    elif modo.startswith("relatorio:"):
        tipo = modo.split(":",1)[1]
        enviar_relatorio(dest, tipo)
    else:
        enviar(dest, modo, arg3)
