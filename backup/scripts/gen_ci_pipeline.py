#!/usr/bin/env python3
"""gen_ci_pipeline.py — Pipeline de Integração Contínua para o ecossistema BUENOSERV."""
import json, os, sys, subprocess, datetime, py_compile, tempfile, yaml, glob

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
AGENTS_DIR = os.path.expanduser("~/.config/opencode/agents/")
TEMPLATES_DIR = "/tmp/opencode/templates/"
SITE_DIR = "/tmp/opencode/site/"
MARKET_DIR = "/tmp/opencode/market_intel/"
DASHBOARD_DIR = os.path.expanduser("~/.config/opencode/dashboard/")

EXPECTED_AGENTS = 81
EXPECTED_SCRIPTS = 42
PORT = 8080

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
RESET = "\033[0m"
NEGRITO = "\033[1m"

resultados = []

class CheckResult:
    def __init__(self, nome, status, detalhe="", sugestao=""):
        self.nome = nome
        self.status = status
        self.detalhe = detalhe
        self.sugestao = sugestao

def log(status, nome, detalhe="", sugestao=""):
    cores = {"PASS": VERDE, "FAIL": VERMELHO, "WARN": AMARELO}
    simbolos = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
    c = cores.get(status, RESET)
    s = simbolos.get(status, "?")
    print(f"  {c}{s} {nome}{RESET}")
    if detalhe:
        print(f"     {detalhe}")
    if sugestao:
        print(f"     {AMARELO}→ Sugestão: {sugestao}{RESET}")
    resultados.append(CheckResult(nome, status, detalhe, sugestao))

def check_agentes():
    nome = "AGENTES — 81 agentes .md com frontmatter YAML válido"
    if not os.path.isdir(AGENTS_DIR):
        log("FAIL", nome, f"Diretório não encontrado: {AGENTS_DIR}", "Crie ~/.config/opencode/agents/ com os agentes .md")
        return
    mds = [f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")]
    total = len(mds)
    if total < EXPECTED_AGENTS:
        log("FAIL", nome, f"Esperado {EXPECTED_AGENTS}, encontrado {total}", "Execute o script de registro de agentes para completar")
        return
    invalidos = 0
    sem_frontmatter = 0
    sem_secoes = 0
    for md in mds:
        path = os.path.join(AGENTS_DIR, md)
        with open(path) as f:
            content = f.read()
        if not content.startswith("---"):
            sem_frontmatter += 1
            continue
        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                raise ValueError("Frontmatter incompleto")
            front = yaml.safe_load(parts[1])
            if not isinstance(front, dict):
                raise ValueError("Frontmatter não é dict")
            body = parts[2]
            for secao in ["Workflow", "Competências Técnicas"]:
                if secao not in body:
                    sem_secoes += 1
                    break
        except Exception as e:
            invalidos += 1
    if invalidos:
        log("FAIL", nome, f"{invalidos} arquivo(s) com frontmatter YAML inválido", "Verifique o YAML de cada agente")
    elif sem_frontmatter:
        log("WARN", nome, f"{sem_frontmatter} arquivo(s) sem frontmatter ---", "Adicione frontmatter YAML aos agentes")
    elif sem_secoes:
        log("WARN", nome, f"{sem_secoes} arquivo(s) sem seções obrigatórias", "Adicione 'Workflow' e 'Competências Técnicas'")
    else:
        log("PASS", nome, f"{total} agentes válidos")

def check_scripts():
    nome = "SCRIPTS — 42+ scripts em /tmp/opencode/templates/"
    if not os.path.isdir(TEMPLATES_DIR):
        log("FAIL", nome, f"Diretório não encontrado: {TEMPLATES_DIR}")
        return
    pys = sorted([f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".py")])
    shs = sorted([f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".sh")])
    total = len(pys) + len(shs)
    if total < EXPECTED_SCRIPTS:
        log("WARN", nome, f"Esperado mínimo {EXPECTED_SCRIPTS}, encontrado {total} scripts", "Verifique se faltam scripts no templates/")
        return
    erros = []
    for py in pys:
        path = os.path.join(TEMPLATES_DIR, py)
        try:
            py_compile.compile(path, doraise=True)
        except py_compile.PyCompileError as e:
            erros.append(f"{py}: {e}")
    for sh in shs:
        path = os.path.join(TEMPLATES_DIR, sh)
        if not os.access(path, os.X_OK):
            erros.append(f"{sh}: não é executável")
    if erros:
        for e in erros:
            log("FAIL", nome, e)
        log("FAIL", nome, f"{len(erros)} script(s) com problemas", "Corrija os erros de syntax ou permissão")
    else:
        log("PASS", nome, f"{total} scripts OK (Python syntax + permissões)")

def check_state():
    nome = "STATE — agent_state.json JSON válido com chaves obrigatórias"
    if not os.path.isfile(STATE_FILE):
        log("FAIL", nome, f"Arquivo não encontrado: {STATE_FILE}", "Execute a inicialização do sistema para gerar o state")
        return
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log("FAIL", nome, f"JSON inválido: {e}", "Corrija o syntax JSON do agent_state.json")
        return
    obrigatorias = ["agent_count", "scripts_disponiveis", "tasks"]
    faltando = [k for k in obrigatorias if k not in data]
    if faltando:
        log("FAIL", nome, f"Chaves faltando: {', '.join(faltando)}", "Adicione as chaves obrigatórias ao JSON")
    else:
        ac = data.get("agent_count", 0)
        sd = len(data.get("scripts_disponiveis", []))
        log("PASS", nome, f"agent_count={ac}, scripts_disponiveis={sd}, tasks={len(data.get('tasks', {}))}")

def check_dashboard():
    nome = "DASHBOARD — serve_dashboard.py, executive.html, porta 8080"
    problemas = []
    sp = os.path.join(TEMPLATES_DIR, "serve_dashboard.py")
    if not os.path.isfile(sp):
        problemas.append("serve_dashboard.py não encontrado")
    eh = os.path.join(DASHBOARD_DIR, "executive.html")
    if not os.path.isfile(eh):
        problemas.append("executive.html não encontrado no dashboard/")
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
        if f":{PORT}" not in r.stdout:
            problemas.append(f"Porta {PORT} não está em LISTEN")
    except Exception:
        problemas.append(f"Não foi possível verificar porta {PORT}")
    if problemas:
        for p in problemas:
            log("FAIL", nome, p, "Inicie o dashboard com serve_dashboard.py")
    else:
        log("PASS", nome, "serve_dashboard.py OK, executive.html OK, porta 8080 em LISTEN")

def check_cron():
    nome = "CRON — Jobs registrados no crontab"
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if r.returncode != 0:
            log("FAIL", nome, "Nenhum crontab encontrado", "Configure os cron jobs com setup_cron.sh")
            return
        lines = [l.strip() for l in r.stdout.split("\n") if l.strip() and not l.strip().startswith("#")]
        total_jobs = len(lines)
        if total_jobs == 0:
            log("WARN", nome, "Crontab existe mas sem jobs ativos", "Adicione jobs ao crontab")
            return
        keywords = ["vigia_check", "chain_agents", "auto_followup", "gen_healthcheck"]
        found = sum(1 for k in keywords if any(k in l for l in lines))
        if found < len(keywords):
            log("WARN", nome, f"Apenas {found}/{len(keywords)} jobs esperados encontrados", "Verifique se todos os jobs foram registrados")
        else:
            log("PASS", nome, f"{total_jobs} jobs no crontab, {found} críticos OK")
    except FileNotFoundError:
        log("FAIL", nome, "crontab não disponível no sistema", "Instale cron (apt install cron)")

def check_site():
    nome = "SITE — index.html existe"
    path = os.path.join(SITE_DIR, "index.html")
    if os.path.isfile(path):
        size = os.path.getsize(path)
        log("PASS", nome, f"index.html encontrado ({size} bytes)")
    else:
        log("FAIL", nome, f"index.html não encontrado em {SITE_DIR}", "Gere o site ou crie index.html manualmente")

def check_market():
    nome = "MERCADO — market_intel/ com arquivos esperados"
    if not os.path.isdir(MARKET_DIR):
        log("FAIL", nome, f"Diretório não encontrado: {MARKET_DIR}", "Crie /tmp/opencode/market_intel/")
        return
    arquivos = os.listdir(MARKET_DIR)
    esperados = ["oportunidades.json", "relatorio.md", "tendencias.json"]
    faltando = [e for e in esperados if e not in arquivos]
    if faltando:
        log("WARN", nome, f"Arquivos faltando: {', '.join(faltando)}", "Execute gen_market_intel.py para gerar os arquivos de mercado")
    else:
        detalhes = "; ".join(f"{a} ({os.path.getsize(os.path.join(MARKET_DIR, a))}b)" for a in esperados)
        log("PASS", nome, f"{len(arquivos)} arquivos: {detalhes}")

def check_deps():
    nome = "DEPENDÊNCIAS — openpyxl e python3"
    ok = True
    # python3
    try:
        r = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        pyver = r.stdout.strip() or r.stderr.strip()
    except FileNotFoundError:
        log("FAIL", nome, "python3 não encontrado no PATH", "Instale python3")
        ok = False
        pyver = "ausente"
    # openpyxl
    try:
        import openpyxl
        oxl_ver = openpyxl.__version__
    except ImportError:
        log("FAIL", nome, "openpyxl não instalado", "pip install openpyxl")
        ok = False
        oxl_ver = "ausente"
    # yaml (PyYAML)
    try:
        import yaml
        yml_ver = yaml.__version__
    except ImportError:
        log("FAIL", nome, "PyYAML não instalado", "pip install pyyaml")
        ok = False
        yml_ver = "ausente"
    if ok:
        log("PASS", nome, f"python3 ({pyver}), openpyxl ({oxl_ver}), pyyaml ({yml_ver})")

def gerar_relatorio(path):
    total = len(resultados)
    passed = sum(1 for r in resultados if r.status == "PASS")
    failed = sum(1 for r in resultados if r.status == "FAIL")
    warned = sum(1 for r in resultados if r.status == "WARN")
    rel = {
        "timestamp": datetime.datetime.now().isoformat(),
        "resumo": {"total": total, "passed": passed, "failed": failed, "warned": warned},
        "checks": [{"nome": r.nome, "status": r.status, "detalhe": r.detalhe, "sugestao": r.sugestao} for r in resultados]
    }
    with open(path, "w") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    return rel["resumo"]

def main():
    print(f"\n{NEGRITO}═══ BUENOSERV CI Pipeline ═══{RESET}\n")
    check_agentes()
    check_scripts()
    check_state()
    check_dashboard()
    check_cron()
    check_site()
    check_market()
    check_deps()
    data_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    rel_path = f"/tmp/opencode/ci_relatorio_{data_str}.json"
    resumo = gerar_relatorio(rel_path)
    print(f"\n{NEGRITO}═══ RESUMO ═══{RESET}")
    print(f"  {VERDE}{resumo['passed']} PASS ✅{RESET}")
    print(f"  {VERMELHO}{resumo['failed']} FAIL ❌{RESET}")
    print(f"  {AMARELO}{resumo['warned']} WARN ⚠️{RESET}")
    print(f"  Total: {resumo['total']} verificações")
    print(f"\n  Relatório salvo: {rel_path}")
    if resumo["failed"]:
        print(f"\n{VERMELHO}Ações corretivas sugeridas:{RESET}")
        for r in resultados:
            if r.status == "FAIL" and r.sugestao:
                print(f"  ❌ {r.nome}: {r.sugestao}")
    exit_code = 0
    if resumo["failed"] > 0:
        exit_code = 1
    elif resumo["warned"] > 0:
        exit_code = 2
    print(f"\n{NEGRITO}Exit code: {exit_code}{RESET}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
