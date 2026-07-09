#!/usr/bin/env python3
"""gen_healer.py — Auto-healer do ecossistema BUENOSERV."""
import json, os, sys, datetime, subprocess, re, time

AGENTS_DIR = os.path.expanduser("~/.config/opencode/agents/")
TEMPLATES_DIR = "/tmp/opencode/templates/"
STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
DASHBOARD_SCRIPT = os.path.join(TEMPLATES_DIR, "serve_dashboard.py")
API_SCRIPT = os.path.join(TEMPLATES_DIR, "gen_api.py")

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
RESET = "\033[0m"
NEGRITO = "\033[1m"

correcoes = []
erros_graves = []

def corrigir(status, nome, detalhe=""):
    cores = {"CORRIGIDO": VERDE, "OK": AZUL, "PULAR": AMARELO, "ERRO": VERMELHO}
    simbolos = {"CORRIGIDO": "🔧", "OK": "✅", "PULAR": "⚠️", "ERRO": "❌"}
    c = cores.get(status, RESET)
    s = simbolos.get(status, "?")
    print(f"  {c}{s} {nome}{RESET}")
    if detalhe:
        print(f"     {detalhe}")
    if status == "CORRIGIDO":
        correcoes.append(nome)
    elif status == "ERRO":
        erros_graves.append(nome)

def healer_yaml():
    nome = "YAML — Corrigir frontmatter com dois-pontos sem aspas"
    if not os.path.isdir(AGENTS_DIR):
        corrigir("PULAR", nome, "Diretório de agentes não encontrado")
        return
    mds = [f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")]
    corrigidos = 0
    for md in mds:
        path = os.path.join(AGENTS_DIR, md)
        with open(path) as f:
            content = f.read()
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        front = parts[1]
        new_front = re.sub(
            r'^(description|title|name|subject|tema):\s*(.+?)(?:\s*#.*)?$',
            lambda m: f'{m.group(1)}: "{m.group(2).strip()}"' if ':' in m.group(2) and not m.group(2).startswith('"') else m.group(0),
            front, flags=re.MULTILINE
        )
        if new_front != front:
            content = content.replace(front, new_front, 1)
            with open(path, "w") as f:
                f.write(content)
            corrigidos += 1
    if corrigidos:
        corrigir("CORRIGIDO", nome, f"{corrigidos} arquivo(s) com YAML corrigido")
    else:
        corrigir("OK", nome, "Nenhum YAML inválido encontrado")

def healer_permissoes():
    nome = "PERMISSÕES — Scripts .py sem +x"
    if not os.path.isdir(TEMPLATES_DIR):
        corrigir("PULAR", nome, "Diretório de templates não encontrado")
        return
    pys = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".py")]
    corrigidos = 0
    for py in pys:
        path = os.path.join(TEMPLATES_DIR, py)
        if not os.access(path, os.X_OK):
            os.chmod(path, 0o755)
            corrigidos += 1
    if corrigidos:
        corrigir("CORRIGIDO", nome, f"{corrigidos} script(s) agora têm +x")
    else:
        corrigir("OK", nome, "Todos os scripts já têm permissão de execução")

def healer_secoes():
    nome = "SEÇÕES — Workflow e Competências Técnicas ausentes"
    if not os.path.isdir(AGENTS_DIR):
        corrigir("PULAR", nome, "Diretório de agentes não encontrado")
        return
    mds = [f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")]
    obrigatorias = ["## Workflow", "## Competências Técnicas"]
    corrigidos = 0
    for md in mds:
        path = os.path.join(AGENTS_DIR, md)
        with open(path) as f:
            content = f.read()
        faltando = [s for s in obrigatorias if s not in content]
        if not faltando:
            continue
        for secao in faltando:
            titulo = secao.replace("## ", "")
            if secao == "## Workflow":
                placeholder = f"\n\n## Workflow\n\n1. **Entrada:** <!-- descrever -->\n2. **Processamento:** <!-- descrever -->\n3. **Saída:** <!-- descrever -->\n"
            else:
                placeholder = f"\n\n## Competências Técnicas\n\n<!-- Listar competências técnicas do agente -->\n"
            if content.rstrip().endswith("---"):
                content = content.rstrip() + placeholder
            else:
                content = content.rstrip() + "\n" + placeholder
        with open(path, "w") as f:
            f.write(content)
        corrigidos += 1
    if corrigidos:
        corrigir("CORRIGIDO", nome, f"{corrigidos} arquivo(s) receberam seções faltantes")
    else:
        corrigir("OK", nome, "Todos os agentes têm as seções obrigatórias")

def healer_state():
    nome = "STATE — agent_state.json corrompido"
    if not os.path.isfile(STATE_FILE):
        data = {"agent_count": 81, "scripts_disponiveis": []}
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        corrigir("CORRIGIDO", nome, "State recriado com estrutura mínima")
        return
    try:
        with open(STATE_FILE) as f:
            json.load(f)
        corrigir("OK", nome, "JSON válido")
    except (json.JSONDecodeError, ValueError):
        data = {"agent_count": 81, "scripts_disponiveis": []}
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        corrigir("CORRIGIDO", nome, "JSON inválido — recriado com estrutura mínima")

def _processo_rodando(porta):
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=10)
        return f":{porta}" in r.stdout
    except Exception:
        return None

def _restart_script(script_path, porta):
    nome_script = os.path.basename(script_path)
    try:
        r = subprocess.run(["pkill", "-f", nome_script], capture_output=True, timeout=10)
        time.sleep(1)
    except Exception:
        pass
    try:
        subprocess.Popen(
            ["python3", script_path, str(porta)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(2)
        return _processo_rodando(porta)
    except Exception:
        return False

def healer_dashboard():
    nome = "DASHBOARD — serve_dashboard.py na porta 8080"
    rodando = _processo_rodando(8080)
    if rodando is None:
        corrigir("PULAR", nome, "Não foi possível verificar porta 8080")
        return
    if rodando:
        corrigir("OK", nome, "Dashboard está ouvindo na porta 8080")
        return
    if not os.path.isfile(DASHBOARD_SCRIPT):
        corrigir("ERRO", nome, "serve_dashboard.py não encontrado")
        return
    ok = _restart_script(DASHBOARD_SCRIPT, 8080)
    if ok:
        corrigir("CORRIGIDO", nome, "Dashboard reiniciado na porta 8080")
    else:
        corrigir("ERRO", nome, "Falha ao reiniciar dashboard")

def healer_api():
    nome = "API — gen_api.py na porta 8090"
    rodando = _processo_rodando(8090)
    if rodando is None:
        corrigir("PULAR", nome, "Não foi possível verificar porta 8090")
        return
    if rodando:
        corrigir("OK", nome, "API está ouvindo na porta 8090")
        return
    if not os.path.isfile(API_SCRIPT):
        corrigir("ERRO", nome, "gen_api.py não encontrado")
        return
    ok = _restart_script(API_SCRIPT, 8090)
    if ok:
        corrigir("CORRIGIDO", nome, "API reiniciada na porta 8090")
    else:
        corrigir("ERRO", nome, "Falha ao reiniciar API")

def healer_orfanos():
    nome = "ÓRFÃOS — Scripts sem entrada no state"
    if not os.path.isfile(STATE_FILE):
        corrigir("PULAR", nome, "State não encontrado")
        return
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (json.JSONDecodeError, ValueError):
        corrigir("PULAR", nome, "State inválido — execute healer_state primeiro")
        return
    scripts_state = set(state.get("scripts_disponiveis", []))
    scripts_dir = set()
    if os.path.isdir(TEMPLATES_DIR):
        for f in os.listdir(TEMPLATES_DIR):
            if f.endswith(".py") or f.endswith(".sh"):
                scripts_dir.add(f)
    orfaos = sorted(scripts_dir - scripts_state)
    if not orfaos:
        corrigir("OK", nome, "Nenhum script órfão encontrado")
        return
    state["scripts_disponiveis"] = sorted(list(scripts_state | set(orfaos)))
    if "agent_count" not in state:
        state["agent_count"] = len(scripts_dir)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    corrigir("CORRIGIDO", nome, f"{len(orfaos)} script(s) adicionados ao state: {', '.join(orfaos)}")

def gerar_relatorio(path):
    resumo = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H%M"),
        "iso": datetime.datetime.now().isoformat(),
        "correcoes": len(correcoes),
        "erros_graves": len(erros_graves),
        "detalhes_correcoes": correcoes,
        "detalhes_erros": erros_graves,
    }
    with open(path, "w") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)
    return resumo

def main():
    print(f"\n{NEGRITO}═══ BUENOSERV AUTO-HEALER ═══{RESET}\n")
    start = time.time()

    healer_yaml()
    healer_permissoes()
    healer_secoes()
    healer_state()
    healer_dashboard()
    healer_api()
    healer_orfanos()

    elapsed = time.time() - start
    data_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    rel_path = f"/tmp/opencode/healer_log_{data_str}.json"
    resumo = gerar_relatorio(rel_path)

    print(f"\n{NEGRITO}═══ RESUMO DO HEALER ═══{RESET}")
    print(f"  {VERDE}🔧 Correções: {resumo['correcoes']}{RESET}")
    print(f"  {VERMELHO}❌ Erros: {resumo['erros_graves']}{RESET}")
    print(f"  ⏱  Tempo: {elapsed:.1f}s")
    print(f"\n  Log salvo: {rel_path}")

    if erros_graves:
        print(f"\n{VERMELHO}⚠️  Erros que não puderam ser corrigidos:{RESET}")
        for e in erros_graves:
            print(f"  ❌ {e}")
        exit_code = 2
    elif correcoes:
        exit_code = 1
    else:
        exit_code = 0

    print(f"\n{NEGRITO}Exit code: {exit_code}{RESET}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
