#!/usr/bin/env python3
"""Oráculo BUENOSERV — engine de recomendação inteligente"""
import json, os, sys, datetime, subprocess, socket

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
AGENTS_DIR = os.path.expanduser("~/.config/opencode/agents")
SCRIPTS_DIR = "/tmp/opencode/templates"
MARKET_FILE = "/tmp/opencode/market_intel/oportunidades.json"

C_RESET = "\033[0m"
C_VERDE = "\033[92m"
C_AMARELO = "\033[93m"
C_VERMELHO = "\033[91m"
C_AZUL = "\033[94m"
C_MAGENTA = "\033[95m"
C_CIANO = "\033[96m"
C_NEGRITO = "\033[1m"

HOJE = datetime.date.today()
SEMANA = HOJE.weekday()
DIAS_SEMANA = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

def cor_prioridade(p):
    return {"ALTA": C_VERMELHO, "MEDIA": C_AMARELO, "BAIXA": C_AZUL}.get(p, C_RESET)

def carregar_estado():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def carregar_oportunidades():
    try:
        with open(MARKET_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def contar_agentes():
    return len([f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")]) if os.path.isdir(AGENTS_DIR) else 0

def contar_scripts():
    if not os.path.isdir(SCRIPTS_DIR):
        return 0
    return len([f for f in os.listdir(SCRIPTS_DIR)
                if f.endswith((".py", ".sh")) and not f.startswith("__")])

def verificar_dashboard():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(("localhost", 8000))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    try:
        r = subprocess.run(["curl", "-sf", "http://localhost:8000/api/state"],
                          capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        pass
    try:
        path = os.path.expanduser("~/.config/opencode/dashboard/index.html")
        return os.path.exists(path)
    except:
        return False

def analisar():
    state = carregar_estado()
    oport = carregar_oportunidades()
    hoje_str = HOJE.isoformat()
    recomendacoes = []
    score = 100

    # 1. Pipeline: follow-up >7 dias sem retorno
    tasks = state.get("tasks", {})
    for proj, tlist in tasks.items():
        for t in tlist:
            if t.get("agente") == "comercial" and t.get("status") in ("em_andamento", None, ""):
                ts = t.get("timestamp", "")
                if ts:
                    try:
                        d = datetime.date.fromisoformat(ts[:10])
                        dias = (HOJE - d).days
                        if dias > 7:
                            recomendacoes.append({
                                "prioridade": "ALTA", "origem": "pipeline",
                                "titulo": f"Follow-up em '{proj}'",
                                "descricao": f"Sem retorno há {dias} dias (último: {ts[:10]})",
                                "acao": f"python3 /tmp/opencode/templates/auto_followup.py --projeto \"{proj}\"",
                                "impacto": "Recuperar oportunidade comercial"
                            })
                            score -= 5
                    except ValueError:
                        pass

    # 2. DRE: lucro líquido < 20% da receita líquida
    dre_meses = state.get("dre", {}).get("meses", {})
    for mes, dm in dre_meses.items():
        rl = dm.get("receita_liquida", 0)
        ll = dm.get("lucro_liquido", 0)
        if rl > 0 and (ll / rl) < 0.20:
            pct = ll / rl * 100
            recomendacoes.append({
                "prioridade": "ALTA", "origem": "dre",
                "titulo": f"Margem líquida baixa ({pct:.1f}%) — mês {mes}",
                "descricao": f"Lucro líquido R${ll:,.2f} é apenas {pct:.1f}% da receita R${rl:,.2f}",
                "acao": "python3 /tmp/opencode/templates/gen_dre.py ver",
                "impacto": "Revisar custos e despesas para aumentar margem"
            })
            score -= 10

    # 3. Agentes: count < 81
    qtd_agentes = contar_agentes()
    meta_agentes = 81
    if qtd_agentes < meta_agentes:
        falta = meta_agentes - qtd_agentes
        recomendacoes.append({
            "prioridade": "ALTA", "origem": "agentes",
            "titulo": f"Apenas {qtd_agentes}/{meta_agentes} agentes",
            "descricao": f"Faltam {falta} agentes para completar o ecossistema",
            "acao": "python3 /tmp/opencode/templates/chain_agents.py",
            "impacto": "Expandir capacidade de automação do sistema"
        })
        score -= 15
    else:
        score += 5

    # 4. Scripts: count < 45
    qtd_scripts = contar_scripts()
    meta_scripts = 45
    if qtd_scripts < meta_scripts:
        falta = meta_scripts - qtd_scripts
        recomendacoes.append({
            "prioridade": "MEDIA", "origem": "scripts",
            "titulo": f"Apenas {qtd_scripts}/{meta_scripts} scripts",
            "descricao": f"Faltam {falta} scripts no template engine",
            "acao": "# Identificar scripts ausentes e gerar",
            "impacto": "Completar biblioteca de automação"
        })
        score -= 10
    else:
        score += 5

    # 5. Projetos: sem atualização >14 dias
    for p in state.get("projects", []):
        ultima = ""
        for fase, info in p.get("fases", {}).items():
            d = info.get("data", "")
            if d and d > ultima:
                ultima = d
        if ultima:
            try:
                d = datetime.date.fromisoformat(ultima[:10])
                dias = (HOJE - d).days
                if dias > 14:
                    recomendacoes.append({
                        "prioridade": "MEDIA", "origem": "projetos",
                        "titulo": f"Projeto '{p['nome']}' parado há {dias} dias",
                        "descricao": f"Cliente: {p.get('cliente', 'N/A')} | Última atualização: {ultima[:10]}",
                        "acao": f"# Contatar cliente e atualizar cronograma do projeto {p['id']}",
                        "impacto": "Manter relacionamento e evitar atrasos"
                    })
                    score -= 8
            except ValueError:
                pass

    # 6. Cron/Autopilot: não executou hoje
    autopilot = state.get("autopilot", {})
    ultima_exec = autopilot.get("ultima_execucao", "")
    if ultima_exec:
        try:
            d = datetime.date.fromisoformat(ultima_exec[:10])
            if d < HOJE:
                recomendacoes.append({
                    "prioridade": "MEDIA", "origem": "cron",
                    "titulo": "Autopilot não executou hoje",
                    "descricao": f"Última execução: {ultima_exec[:10]}",
                    "acao": "python3 /tmp/opencode/templates/gen_autopilot.py",
                    "impacto": "Automação do ecossistema pode estar parada"
                })
                score -= 8
        except ValueError:
            pass
    else:
        recomendacoes.append({
            "prioridade": "MEDIA", "origem": "cron",
            "titulo": "Autopilot sem histórico de execução",
            "descricao": "Nenhuma execução registrada",
            "acao": "python3 /tmp/opencode/templates/gen_autopilot.py",
            "impacto": "Iniciar ciclo de automação"
        })
        score -= 5

    # 7. Market: novas oportunidades
    novas = [o for o in oport if o.get("status") == "nova"]
    if novas:
        recomendacoes.append({
            "prioridade": "MEDIA", "origem": "market",
            "titulo": f"{len(novas)} nova(s) oportunidade(s) de mercado",
            "descricao": "fontes: " + ", ".join(set(o.get("fonte", "") for o in novas)),
            "acao": "python3 /tmp/opencode/templates/gen_market_intel.py",
            "impacto": f"Potencial de R$ {sum(int(o.get('estimativa_receita','0').replace('R$ ','').replace('M','000000').replace('k','000').split('-')[0]) for o in novas):,} em negócios"
        })
        score += 5

    # 8. Dashboard: servidor respondendo
    dash_ok = verificar_dashboard()
    if not dash_ok:
        recomendacoes.append({
            "prioridade": "ALTA", "origem": "dashboard",
            "titulo": "Dashboard não está respondendo",
            "descricao": "Servidor HTTP em localhost:8000 inacessível",
            "acao": "python3 /tmp/opencode/templates/serve_dashboard.py &",
            "impacto": "Monitoramento visual do ecossistema indisponível"
        })
        score -= 12

    # 9. Data: ações específicas do dia da semana
    dia_nome = DIAS_SEMANA[SEMANA]
    if dia_nome == "segunda":
        recomendacoes.append({
            "prioridade": "BAIXA", "origem": "data",
            "titulo": "Segunda-feira — dia de follow-up",
            "descricao": "Iniciar semana com follow-ups pendentes",
            "acao": "python3 /tmp/opencode/templates/auto_followup.py --todos",
            "impacto": "Manter pipeline aquecido"
        })
    elif dia_nome == "sexta":
        recomendacoes.append({
            "prioridade": "BAIXA", "origem": "data",
            "titulo": "Sexta-feira — gerar relatório semanal",
            "descricao": "Fechar a semana com relatório de atividades",
            "acao": "python3 /tmp/opencode/templates/gen_report_pdf.py",
            "impacto": "Registro semanal para tomada de decisão"
        })

    recomendacoes.sort(key=lambda r: {"ALTA": 0, "MEDIA": 1, "BAIXA": 2}[r["prioridade"]])

    score = max(0, min(100, score))

    return recomendacoes, score

def linha():
    return f"{C_CIANO}{'═' * 40}{C_RESET}"

def formatar_resumo(recs, score):
    top3 = recs[:3]
    saida = f"\n{linha()}\n"
    saida += f"  {C_NEGRITO}ORÁCULO BUENOSERV{C_RESET}\n"
    saida += f"  {HOJE:%d/%m/%Y} ({DIAS_SEMANA[SEMANA].capitalize()})\n"
    saida += f"  Saúde do Sistema: {formatar_score(score)}\n"
    saida += f"{linha()}\n"
    saida += f"\n{C_NEGRITO}As 3 principais ações hoje:{C_RESET}\n"
    for i, r in enumerate(top3, 1):
        pc = cor_prioridade(r["prioridade"])
        saida += f"\n  {i}. {pc}[{r['prioridade']}]{C_RESET} {C_NEGRITO}{r['titulo']}{C_RESET}"
        saida += f"\n     {r['descricao']}"
        saida += f"\n     {C_AMARELO}→{C_RESET} {r['acao']}"
    total = len(recs)
    if total > 3:
        saida += f"\n\n  ... +{total - 3} recomendação(ões) — use {C_CIANO}--detalhado{C_RESET} para ver todas"
    saida += f"\n{linha()}\n"
    return saida

def formatar_detalhado(recs, score):
    saida = f"\n{linha()}\n"
    saida += f"  {C_NEGRITO}ORÁCULO BUENOSERV — ANÁLISE DETALHADA{C_RESET}\n"
    saida += f"  {HOJE:%d/%m/%Y} ({DIAS_SEMANA[SEMANA].capitalize()})\n"
    saida += f"  Saúde do Sistema: {formatar_score(score)}\n"
    saida += f"{linha()}\n"
    for i, r in enumerate(recs, 1):
        pc = cor_prioridade(r["prioridade"])
        saida += f"\n{'─' * 50}"
        saida += f"\n  {C_NEGRITO}#{i}{C_RESET} {pc}[{r['prioridade']}]{C_RESET} {C_NEGRITO}{r['titulo']}{C_RESET}"
        saida += f"\n  {' ' * 4}{C_AZUL}Fonte:{C_RESET} {r['origem']}"
        saida += f"\n  {' ' * 4}{C_AZUL}Descrição:{C_RESET} {r['descricao']}"
        saida += f"\n  {' ' * 4}{C_AZUL}Ação:{C_RESET} {r['acao']}"
        saida += f"\n  {' ' * 4}{C_AZUL}Impacto:{C_RESET} {r['impacto']}"
    saida += f"\n{'─' * 50}"
    saida += f"\n  {C_NEGRITO}Resumo:{C_RESET} {len(recs)} recomendação(ões) | Score: {formatar_score(score)}"
    saida += f"\n{linha()}\n"
    return saida

def formatar_score(score):
    if score >= 80:
        return f"{C_VERDE}{C_NEGRITO}{score}/100 (BOA){C_RESET}"
    elif score >= 60:
        return f"{C_AMARELO}{C_NEGRITO}{score}/100 (ATENÇÃO){C_RESET}"
    else:
        return f"{C_VERMELHO}{C_NEGRITO}{score}/100 (CRÍTICA){C_RESET}"

def json_output(recs, score):
    return json.dumps({
        "data": HOJE.isoformat(),
        "dia_semana": DIAS_SEMANA[SEMANA],
        "score_saude": score,
        "total_recomendacoes": len(recs),
        "recomendacoes": [{
            "prioridade": r["prioridade"],
            "origem": r["origem"],
            "titulo": r["titulo"],
            "descricao": r["descricao"],
            "acao": r["acao"],
            "impacto": r["impacto"]
        } for r in recs]
    }, indent=2, ensure_ascii=False)

def mostrar_saude(resumo=False):
    state = carregar_estado()
    qtd_agentes = contar_agentes()
    qtd_scripts = contar_scripts()
    dash_ok = verificar_dashboard()

    print(f"\n{C_NEGRITO}{C_CIANO}{'═' * 40}{C_RESET}")
    print(f"  {C_NEGRITO}RELATÓRIO DE SAÚDE DO SISTEMA{C_RESET}")
    print(f"  {HOJE:%d/%m/%Y %H:%M}")
    print(f"{C_CIANO}{'═' * 40}{C_RESET}")

    checks = [
        ("Agentes completos", qtd_agentes >= 81,
         f"{qtd_agentes}/81 agentes"),
        ("Scripts presentes", qtd_scripts >= 45,
         f"{qtd_scripts}/45 scripts"),
        ("Dashboard ativo", dash_ok,
         "Servidor respondendo" if dash_ok else "Inacessível"),
    ]

    # DRE
    dre = state.get("dre", {})
    total_ll = 0
    total_rl = 0
    for dm in dre.get("meses", {}).values():
        total_rl += dm.get("receita_liquida", 0)
        total_ll += dm.get("lucro_liquido", 0)
    margem = (total_ll / total_rl * 100) if total_rl > 0 else 0
    checks.append(("Margem líquida", margem >= 20, f"{margem:.1f}%"))

    # Pipeline
    tasks = state.get("tasks", {})
    pendentes = sum(1 for tl in tasks.values() for t in tl
                    if t.get("agente") == "comercial" and t.get("status") in ("em_andamento", None, ""))
    checks.append(("Pipeline ativo", pendentes == 0, f"{pendentes} pendente(s)"))

    # Autopilot
    ultima = state.get("autopilot", {}).get("ultima_execucao", "")
    autopilot_ok = bool(ultima) and datetime.date.fromisoformat(ultima[:10]) >= HOJE
    checks.append(("Autopilot OK", autopilot_ok,
                   "Executou hoje" if autopilot_ok else "Parado"))

    for nome, ok, status in checks:
        ico = f"{C_VERDE}✓{C_RESET}" if ok else f"{C_VERMELHO}✗{C_RESET}"
        print(f"  {ico} {nome}: {status}")

    _, score = analisar()
    print(f"{C_CIANO}{'─' * 40}{C_RESET}")
    print(f"  Score de Saúde: {formatar_score(score)}")
    print(f"{C_CIANO}{'═' * 40}{C_RESET}\n")

if __name__ == "__main__":
    recs, score = analisar()

    if "--json" in sys.argv:
        print(json_output(recs, score))
    elif "--detalhado" in sys.argv:
        print(formatar_detalhado(recs, score))
    elif "--saude" in sys.argv:
        mostrar_saude()
    else:
        print(formatar_resumo(recs, score))

    path = os.path.abspath(__file__)
    print(f"\n  📍 {C_AZUL}{path}{C_RESET}")
    print(f"  📊 {len(recs)} recomendações | Score: {score}/100")
