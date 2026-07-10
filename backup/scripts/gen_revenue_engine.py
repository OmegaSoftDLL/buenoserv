#!/usr/bin/env python3
"""BUENOSERV Revenue Engine — Precificação, Propostas, Margens, Projeções"""
import json, os, sys, datetime, math
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

TABELA_PRECOS = {
    "consultoria_tecnica": {"nome": "Consultoria Técnica", "unidade": "hora", "min": 250, "max": 400, "sugerido": 320},
    "comissionamento_se": {"nome": "Comissionamento SE", "unidade": "SE", "min": 25000, "max": 150000, "sugerido": 75000},
    "projeto_telecom": {"nome": "Projeto Telecom (fibra)", "unidade": "km", "min": 1500, "max": 3000, "sugerido": 2200},
    "scada": {"nome": "SCADA", "unidade": "SE", "min": 15000, "max": 80000, "sugerido": 45000},
    "data_center": {"nome": "Data Center", "unidade": "projeto", "min": 50000, "max": 250000, "sugerido": 120000},
    "laudo_pericia": {"nome": "Laudo/Perícia", "unidade": "laudo", "min": 3000, "max": 8000, "sugerido": 5500},
    "treinamento": {"nome": "Treinamento", "unidade": "turma", "min": 5000, "max": 15000, "sugerido": 9000}
}

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def format_money(v):
    return f"R$ {v:,.2f}"

def calcular_proposta(servico, horas=0, materiais=0, quantidade=1):
    precos = TABELA_PRECOS.get(servico)
    if not precos:
        return {"erro": f"Serviço '{servico}' não encontrado"}
    valor_unitario = precos["sugerido"]
    if servico == "consultoria_tecnica":
        valor_servico = valor_unitario * horas
    else:
        valor_servico = valor_unitario * quantidade
    total = valor_servico + materiais
    margem = 0.30
    if total > 100000:
        margem = 0.35
    elif total > 500000:
        margem = 0.40
    custos_estimados = total * (1 - margem)
    return {
        "servico": precos["nome"],
        "unidade": precos["unidade"],
        "valor_unitario": valor_unitario,
        "quantidade": quantidade,
        "horas": horas,
        "valor_servico": valor_servico,
        "materiais": materiais,
        "total": total,
        "margem_estimada": f"{margem*100:.0f}%",
        "custos_estimados": custos_estimados,
        "lucro_estimado": total - custos_estimados
    }

def projetar_receita(meses=12):
    state = carregar_estado()
    dre = state.get("dre", {})
    meses_data = dre.get("meses", {})
    receitas_passadas = []
    for m in range(1, 13):
        if str(m) in meses_data:
            receitas_passadas.append(meses_data[str(m)]["receita_bruta"])
        else:
            receitas_passadas.append(0)
    if not any(receitas_passadas):
        receitas_passadas = [0] * 12
    media = sum(receitas_passadas) / max(len([r for r in receitas_passadas if r > 0]), 1)
    if media == 0:
        media = 35000
    hoje = datetime.date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    projecao = []
    for i in range(1, meses + 1):
        mes_proj = ((mes_atual - 1) + i) % 12 + 1
        ano_proj = ano_atual + ((mes_atual - 1) + i) // 12
        fator_crescimento = 1 + (0.02 * (i // 3))
        receita = media * fator_crescimento
        projecao.append({
            "mes": mes_proj,
            "ano": ano_proj,
            "receita_projetada": round(receita, 2),
            "custo_estimado": round(receita * 0.65, 2),
            "lucro_estimado": round(receita * 0.35, 2)
        })
    return {
        "receita_media_mensal": round(media, 2),
        "total_projetado": round(sum(p["receita_projetada"] for p in projecao), 2),
        "total_lucro_estimado": round(sum(p["lucro_estimado"] for p in projecao), 2),
        "meses": projecao
    }

def analisar_margem(receita, custos):
    if receita <= 0:
        return {"erro": "Receita deve ser > 0"}
    lucro_bruto = receita - custos
    margem_bruta = (lucro_bruto / receita) * 100 if receita > 0 else 0
    despesas_adm = receita * 0.12
    despesas_com = receita * 0.05
    despesas_trib = calcular_simples(receita)
    lucro_liquido = lucro_bruto - despesas_adm - despesas_com - despesas_trib
    margem_liquida = (lucro_liquido / receita) * 100 if receita > 0 else 0
    return {
        "receita": receita,
        "custos": custos,
        "lucro_bruto": lucro_bruto,
        "margem_bruta_pct": round(margem_bruta, 2),
        "despesas_administrativas": round(despesas_adm, 2),
        "despesas_comerciais": round(despesas_com, 2),
        "despesas_tributarias": round(despesas_trib, 2),
        "lucro_liquido": round(lucro_liquido, 2),
        "margem_liquida_pct": round(margem_liquida, 2)
    }

def calcular_simples(receita_bruta):
    if receita_bruta <= 0:
        return 0
    faixas = [
        (180000, 0.045, 0),
        (360000, 0.078, 5940),
        (720000, 0.10, 13860),
        (1800000, 0.1125, 22500),
        (3600000, 0.1355, 62100),
        (4800000, 0.147, 125640)
    ]
    for teto, aliquota, deduz in faixas:
        if receita_bruta <= teto:
            return receita_bruta * aliquota - deduz
    return receita_bruta * 0.147 - 125640

def gerar_fatura(servico, valor, cliente, descricao=""):
    state = carregar_estado()
    faturas = state.setdefault("faturas", [])
    nf = {
        "id": f"BSE-NF-{len(faturas)+1:04d}",
        "data": datetime.date.today().isoformat(),
        "cliente": cliente,
        "servico": servico,
        "valor": valor,
        "descricao": descricao,
        "status": "emitida"
    }
    faturas.append(nf)
    salvar_estado(state)
    return nf

def dashboard_realtime():
    state = carregar_estado()
    dre = state.get("dre", {}).get("meses", {})
    mes_atual = str(datetime.date.today().month)
    dados_mes = dre.get(mes_atual, {})
    receita_mes = dados_mes.get("receita_bruta", 0)
    lucro_mes = dados_mes.get("lucro_liquido", 0)
    total_receita = sum(m.get("receita_bruta", 0) for m in dre.values())
    total_lucro = sum(m.get("lucro_liquido", 0) for m in dre.values())
    margem_geral = (total_lucro / total_receita * 100) if total_receita > 0 else 0
    pipeline = state.get("pipeline", 28500)
    return {
        "receita_mes_atual": receita_mes,
        "lucro_mes_atual": lucro_mes,
        "receita_acumulada": total_receita,
        "lucro_acumulado": total_lucro,
        "margem_liquida_geral": round(margem_geral, 2),
        "pipeline_value": pipeline,
        "faturas_emitidas": len(state.get("faturas", [])),
        "projetos_ativos": len([p for p in state.get("projects", []) if p.get("status") == "Ativo"])
    }

def report_mensal():
    d = dashboard_realtime()
    proj = projetar_receita(12)
    print(f"\n{'='*55}")
    print(f"  BUENOSERV — REVENUE REPORT")
    print(f"  {datetime.date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*55}")
    print(f"  Receita mês atual:    {format_money(d['receita_mes_atual'])}")
    print(f"  Lucro mês atual:      {format_money(d['lucro_mes_atual'])}")
    print(f"  Receita acumulada:    {format_money(d['receita_acumulada'])}")
    print(f"  Lucro acumulado:      {format_money(d['lucro_acumulado'])}")
    print(f"  Margem líquida:       {d['margem_liquida_geral']}%")
    print(f"  Pipeline:             {format_money(d['pipeline_value'])}")
    print(f"  Projeção 12 meses:    {format_money(proj['total_projetado'])}")
    print(f"  Lucro estimado:       {format_money(proj['total_lucro_estimado'])}")
    print(f"  Faturas emitidas:     {d['faturas_emitidas']}")
    print(f"  Projetos ativos:      {d['projetos_ativos']}")
    print(f"{'='*55}\n")
    return d

def tabela_precos_html():
    html = "<table border='1' style='border-collapse:collapse;width:100%'>"
    html += "<tr><th>Serviço</th><th>Unidade</th><th>Mínimo</th><th>Máximo</th><th>Sugerido</th></tr>"
    for k, v in TABELA_PRECOS.items():
        html += f"<tr><td>{v['nome']}</td><td>{v['unidade']}</td><td>{format_money(v['min'])}</td><td>{format_money(v['max'])}</td><td>{format_money(v['sugerido'])}</td></tr>"
    html += "</table>"
    return html

def start_flask():
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("Instale flask: pip install flask")
        return
    app = Flask(__name__)

    @app.route("/precos")
    def precos():
        return jsonify(TABELA_PRECOS)

    @app.route("/calcular")
    def calcular():
        servico = request.args.get("servico", "")
        horas = float(request.args.get("horas", 0))
        materiais = float(request.args.get("materiais", 0))
        quantidade = int(request.args.get("quantidade", 1))
        return jsonify(calcular_proposta(servico, horas, materiais, quantidade))

    @app.route("/projetar")
    def projetar():
        meses = int(request.args.get("meses", 12))
        return jsonify(projetar_receita(meses))

    @app.route("/margem")
    def margem():
        receita = float(request.args.get("receita", 0))
        custos = float(request.args.get("custos", 0))
        return jsonify(analisar_margem(receita, custos))

    @app.route("/faturar", methods=["POST"])
    def faturar():
        data = request.get_json() or {}
        nf = gerar_fatura(
            data.get("servico", ""),
            float(data.get("valor", 0)),
            data.get("cliente", ""),
            data.get("descricao", "")
        )
        return jsonify(nf)

    @app.route("/dashboard")
    def dash():
        return jsonify(dashboard_realtime())

    @app.route("/")
    def home():
        return f"""<html><head><title>BUENOSERV Revenue Engine</title>
<style>body{{font-family:sans-serif;background:#0a1628;color:#e0e0e0;padding:20px}}
h1{{color:#C9A84C}}a{{color:#C9A84C}}td,th{{padding:8px;border:1px solid #1a2d4a}}
table{{border-collapse:collapse;width:100%}}th{{background:#1a2d4a;color:#C9A84C}}
</style></head><body>
<h1>BUENOSERV Revenue Engine</h1>
<h2>Tabela de Preços</h2>
{tabela_precos_html()}
<h2>Endpoints</h2>
<ul>
<li><a href='/precos'>/precos</a> — Tabela de preços</li>
<li><a href='/calcular?servico=consultoria_tecnica&horas=160&materiais=5000'>/calcular?servico=X&horas=Y&materiais=Z</a> — Calcular proposta</li>
<li><a href='/projetar?meses=12'>/projetar?meses=N</a> — Projeção de receita</li>
<li><a href='/margem?receita=100000&custos=65000'>/margem?receita=X&custos=Y</a> — Análise de margem</li>
<li><a href='/dashboard'>/dashboard</a> — Dashboard financeiro</li>
<li>/faturar (POST) — Gerar fatura</li>
</ul></body></html>"""
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    if "--report" in sys.argv:
        report_mensal()
    elif "--projetar" in sys.argv:
        meses = int(sys.argv[sys.argv.index("--projetar") + 1]) if "--projetar" in sys.argv and len(sys.argv) > sys.argv.index("--projetar") + 1 else 12
        p = projetar_receita(meses)
        print(json.dumps(p, indent=2))
    elif "--margem" in sys.argv:
        r = float(sys.argv[sys.argv.index("--margem") + 1]) if len(sys.argv) > sys.argv.index("--margem") + 1 else 100000
        c = float(sys.argv[sys.argv.index("--custos") + 1]) if "--custos" in sys.argv and len(sys.argv) > sys.argv.index("--custos") + 1 else 65000
        print(json.dumps(analisar_margem(r, c), indent=2))
    elif "--calcular" in sys.argv:
        s = sys.argv[sys.argv.index("--calcular") + 1] if len(sys.argv) > sys.argv.index("--calcular") + 1 else "consultoria_tecnica"
        h = float(sys.argv[sys.argv.index("--horas") + 1]) if "--horas" in sys.argv else 160
        m = float(sys.argv[sys.argv.index("--materiais") + 1]) if "--materiais" in sys.argv else 0
        q = int(sys.argv[sys.argv.index("--quantidade") + 1]) if "--quantidade" in sys.argv else 1
        print(json.dumps(calcular_proposta(s, h, m, q), indent=2))
    elif "--serve" in sys.argv:
        start_flask()
    else:
        print("BUENOSERV Revenue Engine v1.0")
        print("Uso: gen_revenue_engine.py [--report|--projetar N|--margem R --custos C|--calcular S --horas H --materiais M|--serve]")
        print("\nExemplos:")
        print("  gen_revenue_engine.py --report")
        print("  gen_revenue_engine.py --projetar 12")
        print("  gen_revenue_engine.py --calcular consultoria_tecnica --horas 160 --materiais 5000")
        print("  gen_revenue_engine.py --margem 100000 --custos 65000")
        print("  gen_revenue_engine.py --serve    # Flask em :5050")
