#!/usr/bin/env python3
"""Agendador de relatórios automáticos via crontab — BUENOSERV"""
import argparse, json, os, subprocess, sys, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT_PDF = os.path.join(BASE, "gen_report_pdf.py")
MAIL = os.path.join(BASE, "gen_mail.py")
EMAIL_DEST = "ricardo.bueno@buenoservengenharia.com"
STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

CRON_JOBS = {
    "semanal": "0 8 * * 1",
    "financeiro": "0 17 * * 5",
    "mensal": "0 9 1 * *",
}

TITLES = {
    "semanal": "Relatório Semanal de Obras",
    "financeiro": "Relatório Financeiro — DRE da Semana",
    "mensal": "Relatório Mensal Consolidado",
}

def verificar_dependencias():
    for path, nome in [(REPORT_PDF, "gen_report_pdf.py"), (MAIL, "gen_mail.py")]:
        if not os.path.isfile(path):
            print(f"ERRO: {nome} não encontrado em {path}")
            sys.exit(1)

def carregar_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"relatorios_enviados": []}

def salvar_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def gerar_relatorio(tipo):
    result = subprocess.run(
        [sys.executable, REPORT_PDF, tipo],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"ERRO gen_report_pdf.py: {result.stderr.strip()}")
        return None
    for line in result.stdout.strip().splitlines():
        if line.startswith("RELATORIO|OK|"):
            return line.split("|")[3]
    print(f"ERRO: formato inesperado de gen_report_pdf.py:\n{result.stdout}")
    return None

def enviar_relatorio(tipo, caminho_html):
    now = datetime.datetime.now()
    data_envio = now.isoformat()
    titulo = TITLES.get(tipo, f"Relatório {tipo.capitalize()}")
    if not caminho_html or not os.path.isfile(caminho_html):
        print(f"AVISO: HTML não encontrado em {caminho_html}, enviando sem anexo")
        args = [sys.executable, MAIL, EMAIL_DEST, f"relatorio:{titulo}", titulo]
    else:
        with open(caminho_html) as f:
            corpo = f.read()
        args = [sys.executable, MAIL, EMAIL_DEST, titulo, corpo]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        state = carregar_state()
        state.setdefault("relatorios_enviados", []).append({
            "tipo": tipo, "data": data_envio,
            "destinatario": EMAIL_DEST, "arquivo": caminho_html, "status": "ok"
        })
        salvar_state(state)
        print(f"Relatório {tipo} enviado com sucesso para {EMAIL_DEST}")
        return True
    else:
        print(f"ERRO ao enviar {tipo}: {result.stderr.strip()}")
        return False

def executar(tipo):
    verificar_dependencias()
    print(f"Gerando relatório {tipo}...")
    caminho = gerar_relatorio(tipo)
    if not caminho:
        sys.exit(1)
    print(f"HTML gerado: {caminho}")
    print(f"Enviando e-mail para {EMAIL_DEST}...")
    enviar_relatorio(tipo, caminho)

def registrar_crontab():
    verificar_dependencias()
    python_path = sys.executable
    script_path = os.path.abspath(__file__)
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""
    for tipo, cron_expr in CRON_JOBS.items():
        tag = f"# BUENOSERV_REPORT_{tipo.upper()}"
        line = f"{cron_expr} {python_path} {script_path} {tipo} {tag}"
        lines = [l for l in existing.splitlines() if tag not in l]
        lines.append(line)
        existing = "\n".join(lines) + "\n"
    p = subprocess.run(["crontab"], input=existing, text=True, capture_output=True)
    if p.returncode == 0:
        print("Jobs registrados no crontab:")
        for tipo, expr in CRON_JOBS.items():
            print(f"  {expr} → {python_path} {script_path} {tipo}")
    else:
        print(f"ERRO: {p.stderr.strip()}")

def status_crontab():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Nenhum crontab configurado.")
        return
    lines = [l for l in result.stdout.splitlines() if "BUENOSERV_REPORT" in l]
    if not lines:
        print("Nenhum job BUENOSERV encontrado no crontab.")
        return
    print("Jobs BUENOSERV registrados no crontab:")
    for l in lines:
        print(f"  {l}")

def desregistrar_crontab():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Nenhum crontab para limpar.")
        return
    lines = [l for l in result.stdout.splitlines() if "BUENOSERV_REPORT" not in l]
    novo = "\n".join(lines) + "\n"
    subprocess.run(["crontab"], input=novo, text=True, capture_output=True)
    print("Jobs BUENOSERV removidos do crontab.")

def main():
    parser = argparse.ArgumentParser(description="Agendador de relatórios BUENOSERV")
    parser.add_argument("tipo", nargs="?", choices=["semanal", "financeiro", "mensal"],
                        help="Tipo de relatório a executar")
    parser.add_argument("--register", action="store_true", help="Registrar jobs no crontab")
    parser.add_argument("--status", action="store_true", help="Mostrar jobs registrados")
    parser.add_argument("--unregister", action="store_true", help="Remover jobs do crontab")
    args = parser.parse_args()

    if args.register:
        registrar_crontab()
    elif args.status:
        status_crontab()
    elif args.unregister:
        desregistrar_crontab()
    elif args.tipo:
        executar(args.tipo)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()