#!/usr/bin/env python3
"""Gerador de relatórios profissionais HTML (imprimível como PDF) — BUENOSERV"""
import json, os, sys, datetime
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
OUTPUT_DIR = "/tmp/opencode/relatorios"

CSS = """\
@page { size: A4; margin: 25mm 20mm; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 10pt; color: #1a1a1a; line-height: 1.5; }
.header { border-bottom: 3px solid #1A237E; padding-bottom: 8mm; margin-bottom: 8mm; }
.header h1 { font-size: 18pt; color: #1A237E; letter-spacing: -0.5px; }
.header .sub { font-size: 8pt; color: #666; margin-top: 2px; }
.header .meta { font-size: 8pt; color: #888; float: right; text-align: right; }
.footer { position: fixed; bottom: 0; left: 0; right: 0; text-align: center; font-size: 7pt; color: #999; border-top: 1px solid #ddd; padding-top: 3mm; }
.footer .page:after { content: counter(page); }
h2 { font-size: 13pt; color: #1A237E; margin: 6mm 0 3mm 0; padding-bottom: 2mm; border-bottom: 1px solid #e0e0e0; }
h3 { font-size: 11pt; color: #333; margin: 4mm 0 2mm 0; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0; font-size: 9pt; }
th { background: #1A237E; color: #fff; padding: 4px 6px; text-align: left; font-weight: 600; }
td { padding: 3px 6px; border-bottom: 1px solid #eee; }
tr:nth-child(even) td { background: #f8f9ff; }
.tag { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 7.5pt; font-weight: 600; }
.tag-ok { background: #e8f5e9; color: #2e7d32; }
.tag-warn { background: #fff3e0; color: #e65100; }
.tag-alert { background: #ffebee; color: #c62828; }
.tag-info { background: #e3f2fd; color: #1565c0; }
.card { border: 1px solid #e0e0e0; border-radius: 4px; padding: 4mm; margin: 3mm 0; }
.card h4 { margin-bottom: 2mm; color: #1A237E; font-size: 10pt; }
.grid-2 { display: flex; gap: 4mm; }
.grid-2 > div { flex: 1; }
.kpi { text-align: center; padding: 3mm; border: 1px solid #e0e0e0; border-radius: 4px; }
.kpi .value { font-size: 16pt; font-weight: 700; color: #1A237E; }
.kpi .label { font-size: 7pt; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-up { border-left: 3px solid #2e7d32; }
.kpi-warn { border-left: 3px solid #e65100; }
.kpi-down { border-left: 3px solid #c62828; }
.status-bar { display: inline-block; width: 60px; height: 6px; border-radius: 3px; vertical-align: middle; margin-right: 4px; }
.status-bar.ok { background: linear-gradient(90deg, #2e7d32 100%, #eee 0); }
.status-bar.warn { background: linear-gradient(90deg, #e65100 60%, #eee 60%); }
.status-bar.alert { background: linear-gradient(90deg, #c62828 30%, #eee 30%); }
.sig { margin-top: 8mm; padding-top: 3mm; border-top: 1px solid #ccc; font-size: 8pt; color: #666; }
"""

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def save_html(path, html):
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

def fmt(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}"

def pct(valor, total):
    if not total:
        return "0%"
    return f"{valor/total*100:.1f}%"

def tag_status(status):
    mapa = {
        "concluido": '<span class="tag tag-ok">Concluído</span>',
        "ok": '<span class="tag tag-ok">OK</span>',
        "em_andamento": '<span class="tag tag-warn">Em andamento</span>',
        "pendente": '<span class="tag tag-alert">Pendente</span>',
        "ativo": '<span class="tag tag-ok">Ativo</span>',
        "proposta_enviada": '<span class="tag tag-info">Proposta enviada</span>',
    }
    return mapa.get(status, f'<span class="tag tag-info">{status}</span>')

def relatorio_semanal(state):
    hoje = datetime.date.today()
    projetos = state.get("projects", [])
    tasks = state.get("tasks", {})
    evol = state.get("evolucao_progresso", {})
    dre = state.get("dre", {}).get("meses", {}).get(str(hoje.month), {})

    ativos = [p for p in projetos if p.get("status") == "Ativo"]
    frentes_total = evol.get("total_frentes", 0)
    frentes_conc = len(evol.get("concluidas", []))
    pendentes = len(evol.get("pendentes_implementacao", []))

    prospeccoes = [k for k in tasks if k.startswith("Prospeccao")]
    novas_prosp = len(prospeccoes)
    tasks_em_andamento = sum(1 for k, v in tasks.items() for t in v if t.get("status") == "em_andamento")

    receita_mes = dre.get("receita_bruta", 0)
    lucro_mes = dre.get("lucro_liquido", 0)

    data_fim = hoje.strftime("%d/%m/%Y")
    data_ini = (hoje - datetime.timedelta(days=7)).strftime("%d/%m/%Y")

    rows = []
    for p in ativos:
        fases_ok = sum(1 for f in p.get("fases", {}).values() if f.get("status") in ("ok", "concluido"))
        total_fases = len(p.get("fases", {}))
        rows.append(f"""<tr><td>{p['id']}</td><td>{p['nome']}</td><td>{p.get('cliente','')}</td><td>{tag_status(p['status'])}</td><td>{fases_ok}/{total_fases}</td></tr>""")

    prospec_rows = []
    for k in sorted(prospeccoes):
        tlist = tasks[k]
        ult = tlist[-1] if tlist else {}
        prospec_rows.append(f"""<tr><td>{k.replace('Prospeccao ','')}</td><td>{tag_status(ult.get('status',''))}</td><td style="font-size:8pt">{ult.get('observacao','')[:60]}</td></tr>""")

    pend_rows = []
    for item in evol.get("pendentes_implementacao", [])[:10]:
        pend_rows.append(f"<li>{item}</li>")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Relatório Semanal — BUENOSERV</title><style>{CSS}</style></head><body>
<div class="header">
  <div class="meta">Relatório Semanal<br>{data_ini} a {data_fim}</div>
  <h1>📊 Relatório Semanal Executivo</h1>
  <div class="sub">BUENOSERV SERVIÇOS DE ENGENHARIA LTDA — CNPJ 60.490.193/0001-38</div>
</div>

<div class="grid-2">
  <div class="kpi kpi-up"><div class="value">{len(ativos)}</div><div class="label">Projetos ativos</div></div>
  <div class="kpi kpi-up"><div class="value">{frentes_conc}/{frentes_total}</div><div class="label">Frentes concluídas</div></div>
  <div class="kpi kpi-warn"><div class="value">{pendentes}</div><div class="label">Pendências</div></div>
  <div class="kpi kpi-up"><div class="value">{novas_prosp}</div><div class="label">Novas oportunidades</div></div>
  <div class="kpi kpi-up"><div class="value">{fmt(receita_mes)}</div><div class="label">Receita do mês</div></div>
  <div class="kpi {('kpi-up' if lucro_mes>=0 else 'kpi-down')}"><div class="value">{fmt(lucro_mes)}</div><div class="label">Lucro líquido</div></div>
</div>

<h2>📋 Pipeline — Projetos Ativos</h2>
<table><thead><tr><th>ID</th><th>Projeto</th><th>Cliente</th><th>Status</th><th>Fases</th></tr></thead><tbody>
{"".join(rows)}
</tbody></table>

<h2>🆕 Novas Oportunidades</h2>
<table><thead><tr><th>Empresa</th><th>Status</th><th>Última ação</th></tr></thead><tbody>
{"".join(prospec_rows)}
</tbody></table>

<h2>⚠️ Alertas e Pendências</h2>
<ul style="margin-left:5mm;font-size:9pt">
{"".join(pend_rows)}
</ul>

<h2>📈 Indicadores da Semana</h2>
<table>
<tr><td>Tasks em andamento</td><td><strong>{tasks_em_andamento}</strong></td></tr>
<tr><td>Total de prospecções ativas</td><td><strong>{novas_prosp}</strong></td></tr>
<tr><td>Frentes de desenvolvimento</td><td><strong>{frentes_total}</strong></td></tr>
<tr><td>Frentes concluídas</td><td><strong>{frentes_conc} ({pct(frentes_conc,frentes_total)})</strong></td></tr>
</table>

<div class="sig">
<p>Relatório gerado automaticamente em {hoje.strftime("%d/%m/%Y às %H:%M")} · BUENOSERV Autopilot</p>
</div>
<div class="footer"><span class="page">Página </span></div>
</body></html>"""
    return html

def relatorio_projeto(state):
    hoje = datetime.date.today()
    projetos = state.get("projects", [])
    tasks = state.get("tasks", {})
    licoes = state.get("memory", {}).get("lessons_learned", [])

    card_projetos = []
    for p in projetos:
        fases = p.get("fases", {})
        rows_fases = []
        for nome_fase, dados in fases.items():
            rows_fases.append(f"""<tr><td>{nome_fase.capitalize()}</td><td>{tag_status(dados.get('status',''))}</td><td style="font-size:8pt">{dados.get('data','')[:10]}</td></tr>""")

        p_tasks = tasks.get(p["nome"], [])
        pend = [t for t in p_tasks if t.get("status") == "pendente"]
        em_and = [t for t in p_tasks if t.get("status") == "em_andamento"]
        concl = [t for t in p_tasks if t.get("status") == "concluido"]

        li_c = ""
        for item in licoes:
            if item.get("projeto") == p["nome"]:
                li_c += f"<li>{item.get('licao','')}</li>"

        card_projetos.append(f"""
<div class="card">
<h4>{p['id']} — {p['nome']}</h4>
<table>
<tr><td style="width:140px"><strong>Cliente</strong></td><td>{p.get('cliente','')}</td></tr>
<tr><td><strong>Escopo</strong></td><td>{p.get('escopo','')}</td></tr>
<tr><td><strong>Status</strong></td><td>{tag_status(p.get('status',''))}</td></tr>
<tr><td><strong>Início</strong></td><td>{p.get('data_inicio','')[:10]}</td></tr>
<tr><td><strong>Fases</strong></td><td>{len(fases)} fases ({sum(1 for f in fases.values() if f.get('status') in ('ok','concluido'))} concluídas)</td></tr>
</table>

<h4>Fases / Cronograma</h4>
<table><thead><tr><th>Fase</th><th>Status</th><th>Data</th></tr></thead><tbody>
{"".join(rows_fases)}
</tbody></table>

<h4>Entregas / Tasks</h4>
<table>
<tr><td>Concluídas</td><td><strong>{len(concl)}</strong></td></tr>
<tr><td>Em andamento</td><td><strong>{len(em_and)}</strong></td></tr>
<tr><td>Pendentes</td><td><strong>{len(pend)}</strong></td></tr>
</table>

{"".join((f"<h4>Lições aprendidas</h4><ul>{li_c}</ul>") if li_c else "")}

<h4>Últimas atividades</h4>
<table><thead><tr><th>Agente</th><th>Status</th><th>Observação</th></tr></thead><tbody>
{"".join(f"<tr><td>{t.get('agente','')}</td><td>{tag_status(t.get('status',''))}</td><td style='font-size:8pt'>{t.get('observacao','')}</td></tr>" for t in p_tasks[-5:])}
</tbody></table>
</div>""")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Relatório de Projetos — BUENOSERV</title><style>{CSS}</style></head><body>
<div class="header">
  <div class="meta">Gerado em {hoje.strftime("%d/%m/%Y")}</div>
  <h1>📋 Relatório de Projetos</h1>
  <div class="sub">BUENOSERV SERVIÇOS DE ENGENHARIA LTDA — Status detalhado de projetos</div>
</div>

<h2>📌 Projetos Ativos ({len(projetos)})</h2>
{"".join(card_projetos) if card_projetos else "<p>Nenhum projeto ativo no momento.</p>"}

<div class="sig">
<p>Relatório gerado automaticamente em {hoje.strftime("%d/%m/%Y às %H:%M")} · BUENOSERV Autopilot</p>
</div>
<div class="footer"><span class="page">Página </span></div>
</body></html>"""
    return html

def relatorio_financeiro(state):
    hoje = datetime.date.today()
    mes = str(hoje.month)
    dre_data = state.get("dre", {})
    meses = dre_data.get("meses", {})

    dm = meses.get(mes, {})
    mes_ant = str(hoje.month - 1) if hoje.month > 1 else "12"
    dm_ant = meses.get(mes_ant, {})

    rb = dm.get("receita_bruta", 0)
    rl = dm.get("receita_liquida", 0)
    lb = dm.get("lucro_bruto", 0)
    lo = dm.get("lucro_operacional", 0)
    ll = dm.get("lucro_liquido", 0)
    cs = dm.get("custos_servicos", 0)
    da = dm.get("despesas_administrativas", 0)
    dc = dm.get("despesas_comerciais", 0)
    dt = dm.get("despesas_tributarias", 0)
    rf = dm.get("resultado_financeiro", 0)

    rb_a = dm_ant.get("receita_bruta", 0)
    ll_a = dm_ant.get("lucro_liquido", 0)

    var_rec = ((rb - rb_a) / rb_a * 100) if rb_a else 0
    var_ll = ((ll - ll_a) / ll_a * 100) if ll_a else 0

    margem_bruta = (lb / rl * 100) if rl else 0
    margem_liquida = (ll / rl * 100) if rl else 0

    info = state.get("buenoserv_real", {})
    pix = info.get("pix", "")

    dre_rows = f"""<tr><td>1. Receita Bruta de Serviços</td><td style="text-align:right">{fmt(rb)}</td><td style="text-align:right">{fmt(rb_a)}</td><td style="text-align:right;color={'#2e7d32' if var_rec>=0 else '#c62828'}">{var_rec:+.1f}%</td></tr>
<tr><td>2. Deduções</td><td style="text-align:right">{fmt(dm.get('deducoes',0))}</td><td style="text-align:right">{fmt(dm_ant.get('deducoes',0))}</td><td style="text-align:right">—</td></tr>
<tr style="font-weight:600;background:#f0f0f0"><td>3. Receita Líquida</td><td style="text-align:right">{fmt(rl)}</td><td style="text-align:right">{fmt(dm_ant.get('receita_liquida',0))}</td><td style="text-align:right">—</td></tr>
<tr><td>4. Custos dos Serviços</td><td style="text-align:right">{fmt(cs)}</td><td style="text-align:right">{fmt(dm_ant.get('custos_servicos',0))}</td><td style="text-align:right">—</td></tr>
<tr style="font-weight:600;background:#f0f0f0"><td>5. Lucro Bruto</td><td style="text-align:right">{fmt(lb)}</td><td style="text-align:right">{fmt(dm_ant.get('lucro_bruto',0))}</td><td style="text-align:right">—</td></tr>
<tr><td>6. Despesas Administrativas</td><td style="text-align:right">{fmt(da)}</td><td style="text-align:right">{fmt(dm_ant.get('despesas_administrativas',0))}</td><td style="text-align:right">—</td></tr>
<tr><td>7. Despesas Comerciais</td><td style="text-align:right">{fmt(dc)}</td><td style="text-align:right">{fmt(dm_ant.get('despesas_comerciais',0))}</td><td style="text-align:right">—</td></tr>
<tr><td>8. Despesas Tributárias</td><td style="text-align:right">{fmt(dt)}</td><td style="text-align:right">{fmt(dm_ant.get('despesas_tributarias',0))}</td><td style="text-align:right">—</td></tr>
<tr style="font-weight:600;background:#f0f0f0"><td>9. Lucro Operacional</td><td style="text-align:right">{fmt(lo)}</td><td style="text-align:right">{fmt(dm_ant.get('lucro_operacional',0))}</td><td style="text-align:right">—</td></tr>
<tr><td>10. Resultado Financeiro</td><td style="text-align:right">{fmt(rf)}</td><td style="text-align:right">{fmt(dm_ant.get('resultado_financeiro',0))}</td><td style="text-align:right">—</td></tr>
<tr style="font-weight:700;background:#e8eaf6"><td>11. Lucro Líquido</td><td style="text-align:right">{fmt(ll)}</td><td style="text-align:right">{fmt(ll_a)}</td><td style="text-align:right;color={'#2e7d32' if var_ll>=0 else '#c62828'}">{var_ll:+.1f}%</td></tr>"""

    fluxo_rows = f"""<tr><td>Saldo inicial (estimado)</td><td style="text-align:right">R$ 5.000,00</td></tr>
<tr><td>+ Recebimentos (previsão)</td><td style="text-align:right">{fmt(rb)}</td></tr>
<tr><td>− Pagamentos (custos + despesas)</td><td style="text-align:right">{fmt(cs + da + dc + dt)}</td></tr>
<tr style="font-weight:700;background:#e8eaf6"><td>= Saldo projetado</td><td style="text-align:right">{fmt(rb - cs - da - dc - dt)}</td></tr>"""

    prev_rows = ""
    if ll:
        proj_12 = ll * 12
        prev_rows += f"<tr><td>Projeção anual (linear)</td><td style='text-align:right'>{fmt(proj_12)}</td></tr>"
    if rb:
        prev_rows += f"<tr><td>Margem bruta</td><td style='text-align:right'>{margem_bruta:.1f}%</td></tr>"
        prev_rows += f"<tr><td>Margem líquida</td><td style='text-align:right'>{margem_liquida:.1f}%</td></tr>"

    projetos = state.get("projects", [])
    receita_contratos = sum(8000 for p in projetos if p.get("status") == "Ativo")
    prev_rows += f"<tr><td>Receita recorrente (contratos ativos)</td><td style='text-align:right'>{fmt(receita_contratos)}/mês</td></tr>"
    proposta = state.get("memory", {}).get("completed_projects", [])
    for cp in proposta:
        if cp.get("tipo") == "proposta_enviada":
            prev_rows += f"<tr><td>Proposta: {cp.get('cliente','')}</td><td style='text-align:right'>{fmt(cp.get('valor',0))}</td></tr>"

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Relatório Financeiro — BUENOSERV</title><style>{CSS}</style></head><body>
<div class="header">
  <div class="meta">Período: {hoje.strftime("%m/%Y")}</div>
  <h1>💰 Relatório Financeiro</h1>
  <div class="sub">BUENOSERV SERVIÇOS DE ENGENHARIA LTDA — DRE, Fluxo de Caixa & Previsão</div>
</div>

<div class="grid-2">
  <div class="kpi kpi-up"><div class="value">{fmt(rb)}</div><div class="label">Receita do mês</div></div>
  <div class="kpi {('kpi-up' if ll>=0 else 'kpi-down')}"><div class="value">{fmt(ll)}</div><div class="label">Lucro líquido</div></div>
  <div class="kpi {('kpi-up' if var_rec>=0 else 'kpi-down')}"><div class="value">{var_rec:+.1f}%</div><div class="label">Var. receita vs mês ant.</div></div>
  <div class="kpi kpi-up"><div class="value">{margem_liquida:.1f}%</div><div class="label">Margem líquida</div></div>
</div>

<h2>📄 DRE — Demonstração do Resultado</h2>
<table><thead><tr><th>Conta</th><th style="text-align:right">Mês Atual</th><th style="text-align:right">Mês Anterior</th><th style="text-align:right">Variação</th></tr></thead><tbody>
{dre_rows}
</tbody></table>

<h2>💵 Fluxo de Caixa (Previsão)</h2>
<table><thead><tr><th>Item</th><th style="text-align:right">Valor</th></tr></thead><tbody>
{fluxo_rows}
</tbody></table>

<h2>🔮 Previsão & Projeções</h2>
<table><thead><tr><th>Indicador</th><th style="text-align:right">Valor</th></tr></thead><tbody>
{prev_rows}
</tbody></table>

<h2>🏦 Dados da Empresa</h2>
<table>
<tr><td style="width:160px"><strong>Razão Social</strong></td><td>{info.get('nome','')}</td></tr>
<tr><td><strong>CNPJ</strong></td><td>{info.get('cnpj','')}</td></tr>
<tr><td><strong>Regime</strong></td><td>{info.get('regime','')}</td></tr>
<tr><td><strong>PIX</strong></td><td>{pix}</td></tr>
<tr><td><strong>Banco</strong></td><td>{info.get('banco','')}</td></tr>
</table>

<div class="sig">
<p>Relatório gerado automaticamente em {hoje.strftime("%d/%m/%Y às %H:%M")} · BUENOSERV Autopilot</p>
<p>Este documento é uma projeção gerencial. Valores podem diferir do resultado real.</p>
</div>
<div class="footer"><span class="page">Página </span></div>
</body></html>"""
    return html

def main():
    if len(sys.argv) < 2:
        print("Uso: gen_report_pdf.py <semanal|projeto|financeiro>")
        sys.exit(1)

    tipo = sys.argv[1].strip().lower()
    state = carregar_estado()

    hoje = datetime.date.today()
    nome_arquivo = f"{hoje.strftime('%Y-%m-%d')}_{tipo}_buenoserv.html"
    path = os.path.join(OUTPUT_DIR, nome_arquivo)

    geradores = {
        "semanal": relatorio_semanal,
        "projeto": relatorio_projeto,
        "financeiro": relatorio_financeiro,
    }

    if tipo not in geradores:
        print(f"Tipo inválido: {tipo}. Use: semanal, projeto, financeiro")
        sys.exit(1)

    html = geradores[tipo](state)
    save_html(path, html)
    print(f"RELATORIO|OK|{tipo}|{path}")

if __name__ == "__main__":
    main()
