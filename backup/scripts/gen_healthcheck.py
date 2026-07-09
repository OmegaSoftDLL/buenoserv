#!/usr/bin/env python3
"""Auto-diagnóstico do sistema BUENOSERV — verifica saúde de agentes, scripts, state, cron"""
import json, os, sys, datetime, subprocess

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
AGENTS_DIR = os.path.expanduser("~/.config/opencode/agents")
SCRIPTS_DIR = "/tmp/opencode/templates"
DASHBOARD_DIR = os.path.expanduser("~/.config/opencode/dashboard")

def verificar_agentes():
    ok = 0
    erros = []
    esperados = [
        "proposta", "planejamento", "gestao-projetos", "levantamento", "padronizador",
        "instalacao", "comissionamento", "handover", "qualidade",
        "rh", "financeiro", "juridico", "comercial", "marketing", "processos",
        "seguranca-trabalho", "almoxarifado", "manutencao",
        "arquivos", "workflow", "memoria", "vigia", "ceo", "buenoserv",
        "project-control", "suprimentos", "bom", "depara", "civil", "compliance",
        "network-architect", "template-adapter", "relatorios", "treinamento",
        "rfp", "datacenter", "structured-cabling", "physical-security",
        "telecom-dwdm", "telecom-sdh-pdh", "telecom-mplstp", "telecom-tdmop",
        "telecom-radio", "telecom-otn", "telecom-gpon", "telecom-ptn",
        "telecom-fiber", "telecom-plc", "ip-mpls", "ip-routing", "ip-multicast",
        "network-security", "firewall", "router", "switch",
        "automacao-se", "sincronismo", "wams", "scada", "scada-ems",
        "teleprotection", "cyber-power", "pmu", "tsn", "nms",
        "energia", "solar", "geracao", "gerador", "power",
        "substation-primary", "substation-secondary",
        "cftv", "acesso", "incendio", "dc-raft", "shelter",
        "seg-energia", "engenharia-aval", "processo-industrial", "pericias",
    ]
    for nome in esperados:
        path = os.path.join(AGENTS_DIR, f"{nome}.md")
        if os.path.exists(path):
            with open(path) as f:
                c = f.read()
            if "## Workflow" in c and "## Automação" in c:
                ok += 1
            else:
                erros.append(f"{nome}: sem Workflow ou Automação")
        else:
            erros.append(f"{nome}.md: ausente")
    return ok, len(esperados), erros

def verificar_scripts():
    esperados = [
        "auto_followup.py", "chain_agents.py", "enviar_email.py",
        "gen_backup.py", "gen_bom.py", "gen_bot_telegram.py", "gen_budget.py",
        "gen_calc_impostos.py", "gen_click_sign.py", "gen_conciliacao.py",
        "gen_contrato.py", "gen_crm.py", "gen_diario_obra.py",
        "gen_docx.py", "gen_dre.py", "gen_drip_campaign.py", "gen_dwg.py",
        "gen_eap.py", "gen_email_templates.py", "gen_fluxo_caixa.py",
        "gen_google_meu_negocio.py", "gen_holerite.py", "gen_nfe.py",
        "gen_orcado_realizado.py", "gen_pdf.py", "gen_portfolio.py",
        "gen_pptx.py", "gen_proposta.py", "gen_proposta_online.py",
        "gen_rfp_scraper.py", "gen_simulador_cronograma.py",
        "gen_timesheet.py", "gen_treinamento.py", "gen_xlsx.py",
        "register_agent.py", "serve_dashboard.py", "vigia_check.py",
        "gen_blog.py", "gen_biblioteca_projetos.py",
    ]
    ok = 0
    erros = []
    for nome in esperados:
        path = os.path.join(SCRIPTS_DIR, nome)
        if os.path.exists(path):
            ok += 1
        else:
            erros.append(f"{nome}: ausente")
    return ok, len(esperados), erros

def verificar_state():
    if not os.path.exists(STATE_FILE):
        return False, "agent_state.json não existe"
    try:
        with open(STATE_FILE) as f:
            s = json.load(f)
        checks = []
        if "agent_count" not in s: checks.append("agent_count ausente")
        if "projects" not in s: checks.append("projects ausente")
        if "tasks" not in s: checks.append("tasks ausente")
        if "dre" not in s: checks.append("dre ausente")
        if "evolucao_progresso" not in s: checks.append("evolucao_progresso ausente")
        return len(checks) == 0, checks if checks else "OK"
    except json.JSONDecodeError:
        return False, "agent_state.json inválido"

def verificar_cron():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            lines = [l for l in result.stdout.split("\n") if l.strip() and not l.startswith("#")]
            buenoserv_jobs = [l for l in lines if "buenoserv" in l.lower() or "opencode" in l.lower() or "gen_" in l.lower()]
            return len(buenoserv_jobs), len(lines), buenoserv_jobs
        return 0, 0, []
    except:
        return -1, -1, []

def verificar_dashboard():
    path = os.path.join(DASHBOARD_DIR, "index.html")
    if not os.path.exists(path):
        return False, "index.html ausente"
    with open(path) as f:
        c = f.read()
    if "fetch('/api/state')" in c:
        return True, "OK (dinâmico)"
    return True, "OK (estático)"

def executar():
    print(f"\n{'='*55}")
    print(f"  🩺 AUTO-DIAGNÓSTICO BUENOSERV")
    print(f"  {datetime.datetime.now():%d/%m/%Y %H:%M}")
    print(f"{'='*55}")

    # 1. Agentes
    a_ok, a_total, a_erros = verificar_agentes()
    print(f"\n📋 Agentes: {a_ok}/{a_total} completos (Workflow+Automação)")
    if a_erros:
        for e in a_erros[:3]:
            print(f"   ⚠️  {e}")
        if len(a_erros) > 3:
            print(f"   ... +{len(a_erros)-3} erros")

    # 2. Scripts
    s_ok, s_total, s_erros = verificar_scripts()
    print(f"📜 Scripts: {s_ok}/{s_total} presentes")
    for e in s_erros:
        print(f"   ❌ {e}")

    # 3. State
    state_ok, state_msg = verificar_state()
    state_status = "✅" if state_ok else "❌"
    print(f"💾 State: {state_status} {state_msg if isinstance(state_msg, str) else ', '.join(state_msg[:3])}")

    # 4. Cron
    c_buenoserv, c_total, c_jobs = verificar_cron()
    if c_buenoserv >= 0:
        print(f"⏰ Cron: {c_buenoserv} jobs BUENOSERV ativos")
        for j in c_jobs:
            print(f"   {j.strip()[:70]}...")
    else:
        print(f"⏰ Cron: não acessível")

    # 5. Dashboard
    d_ok, d_msg = verificar_dashboard()
    d_status = "✅" if d_ok else "❌"
    print(f"📊 Dashboard: {d_status} {d_msg}")

    # 6. Prospecções Pendentes
    try:
        with open(STATE_FILE) as f:
            s = json.load(f)
        pendentes = 0
        for proj, tasks in s.get("tasks", {}).items():
            for t in tasks:
                if t["agente"] == "comercial" and t["status"] != "concluido":
                    pendentes += 1
        print(f"📧 Prospecções pendentes: {pendentes}")
    except:
        pass

    # Score geral
    if a_ok == a_total and s_ok == s_total and state_ok:
        print(f"\n{'='*55}")
        print(f"  ✅ SAÚDE GERAL: OK — Sistema operacional")
    else:
        print(f"\n{'='*55}")
        print(f"  ⚠️  SAÚDE GERAL: ATENÇÃO — {a_total-a_ok} agentes, {s_total-s_ok} scripts")
    print(f"{'='*55}")

if __name__ == "__main__":
    executar()
