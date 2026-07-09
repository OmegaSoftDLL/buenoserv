#!/usr/bin/env python3
"""Inteligência de Mercado BUENOSERV — varredura simulada de oportunidades no setor elétrico"""
import json, os, sys, datetime, random, hashlib

KEYWORDS = [
    "licitação subestação", "comissionamento elétrico", "proteção SE",
    "telecom energia", "SCADA", "leilão ANEEL", "transmissão energia"
]

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
DATA_DIR = "/tmp/opencode/market_intel"
OPORTUNIDADES_FILE = os.path.join(DATA_DIR, "oportunidades.json")
TENDENCIAS_FILE = os.path.join(DATA_DIR, "tendencias.json")
RELATORIO_FILE = os.path.join(DATA_DIR, "relatorio.md")

_FONTES_SIMULADAS = {
    "ANEEL": [
        "Leilão de Transmissão nº 02/2026 — lotes BA/MG (138kV e 230kV)",
        "Consulta Pública CP 015/2026 — procedural para integração de parques eólicos",
        "Leilão de Transmissão nº 03/2026 — LT 500kV Norte-Nordeste",
        "Audiência Pública AP 023/2026 — revisão dos procedimentos de rede",
        "Edital de chamamento para projetos de P&D estratégico — transmissão",
        "Leilão A-5 reserva de capacidade — subestações 345kV",
    ],
    "ComprasNet": [
        "Pregão 89/2026 — serviços de comissionamento elétrico SE Sudeste",
        "Concorrência 42/2026 — ampliação de subestação 230kV em SP",
        "Pregão 103/2026 — modernização de sistemas SCADA e telecom",
        "Concorrência 57/2026 — obras de proteção e controle SE 138kV",
        "Pregão 67/2026 — contratação de engenharia para proteção SE",
        "Concorrência 31/2026 — implantação de fibra óptica em LT 230kV",
    ],
    "DOE": [
        "Portaria MME 456/2026 — diretrizes para licitação de transmissão",
        "Despacho ANEEL 1.234/2026 — aprova ED de subestação 500kV",
        "Portaria MME 478/2026 — cronograma de leilões A-5 e A-6 2027",
        "Resolução Normativa 1.056/2026 — requisitos de telecom em SE",
        "Portaria MMA 89/2026 — licenciamento ambiental de LT e SE",
        "Despacho ONS 789/2026 — requisitos de proteção e teleproteção",
    ],
    "Tendências": [
        "Crescimento de 23% em investimentos em transmissão previsto para 2027",
        "Demanda aquecida por sistemas de proteção digital IEC 61850",
        "Expansão do mercado de SCADA/ADMS no Brasil pós-privatizações",
        "Nova regulação ANEEL exige telemonitoramento em todas as SE acima de 138kV",
        "Escassez de mão de obra especializada em comissionamento elétrico",
        "Abertura de novas frentes em energia offshore e hidrogênio verde",
    ]
}

def _id_oportunidade(op):
    raw = f"{op['fonte']}||{op['titulo']}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def _carregar_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def _salvar_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _carregar_estado():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _salvar_estado(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def _gerar_oportunidade(fonte, titulo):
    now = datetime.datetime.now()
    dias_uteis = random.randint(5, 60)
    prazo = (now + datetime.timedelta(days=dias_uteis)).isoformat()
    return {
        "id": None,
        "fonte": fonte,
        "titulo": titulo,
        "data_identificacao": now.isoformat(),
        "prazo": prazo,
        "keywords_match": [kw for kw in KEYWORDS if any(
            t.lower() in kw for t in titulo.lower().split()
        )],
        "status": "identificada",
        "probabilidade": random.choice(["alta", "média", "baixa"]),
        "estimativa_receita": random.choice([
            "R$ 500k-2M", "R$ 2M-5M", "R$ 5M-15M", "R$ 15M-50M", None
        ]),
    }

def _gerar_tendencia(titulo):
    now = datetime.datetime.now()
    return {
        "titulo": titulo,
        "data_identificacao": now.isoformat(),
        "categoria": random.choice(["regulatória", "tecnológica", "mercado", "macroeconômica"]),
        "impacto": random.choice(["alto", "médio", "baixo"]),
        "detalhes": f"Identificado em {now.strftime('%d/%m/%Y')} — monitoramento contínuo.",
    }

def scan_oportunidades():
    state = _carregar_estado()
    seen = set(state.get("market_intel", {}).get("seen_ids", []))

    oportunidades = _carregar_json(OPORTUNIDADES_FILE, [])
    conhecidos = {(op["fonte"], op["titulo"]) for op in oportunidades}
    novas = []

    for fonte, itens in _FONTES_SIMULADAS.items():
        if fonte == "Tendências":
            continue
        for item in random.sample(itens, min(2, len(itens))):
            if (fonte, item) in conhecidos:
                continue
            op = _gerar_oportunidade(fonte, item)
            op["id"] = _id_oportunidade(op)
            if op["id"] not in seen:
                seen.add(op["id"])
                op["status"] = "nova"
                novas.append(op)
                oportunidades.append(op)

    state.setdefault("market_intel", {})["seen_ids"] = list(seen)
    _salvar_estado(state)
    _salvar_json(OPORTUNIDADES_FILE, oportunidades)

    return novas

def analisar_tendencias():
    tendencias = _carregar_json(TENDENCIAS_FILE, [])
    novos = []

    for titulo in _FONTES_SIMULADAS["Tendências"]:
        if not any(t["titulo"] == titulo for t in tendencias):
            t = _gerar_tendencia(titulo)
            novos.append(t)
            tendencias.append(t)

    if novos:
        _salvar_json(TENDENCIAS_FILE, tendencias)

    return novos

def filtrar_por_escopo(termo):
    oportunidades = _carregar_json(OPORTUNIDADES_FILE, [])
    termo_lower = termo.lower()
    return [
        op for op in oportunidades
        if termo_lower in op["titulo"].lower()
        or any(termo_lower in kw for kw in op.get("keywords_match", []))
    ]

def gerar_relatorio_semanal():
    oportunidades = _carregar_json(OPORTUNIDADES_FILE, [])
    tendencias = _carregar_json(TENDENCIAS_FILE, [])
    now = datetime.datetime.now()

    novas = [op for op in oportunidades if op.get("status") == "nova"]
    por_fonte = {}
    for op in oportunidades:
        por_fonte.setdefault(op["fonte"], []).append(op)

    linhas = []
    linhas.append(f"# Relatório Semanal de Inteligência de Mercado — BUENOSERV")
    linhas.append(f"**Gerado em:** {now.strftime('%d/%m/%Y %H:%M')}")
    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 1. Resumo Executivo")
    linhas.append("")
    linhas.append(f"- Total de oportunidades monitoradas: **{len(oportunidades)}**")
    linhas.append(f"- Novas oportunidades na semana: **{len(novas)}**")
    linhas.append(f"- Tendências ativas: **{len(tendencias)}**")
    linhas.append(f"- Fontes monitoradas: ANEEL, ComprasNet, DOE")
    linhas.append("")

    if novas:
        linhas.append("## 2. Novas Oportunidades")
        linhas.append("")
        for op in novas:
            kw = ", ".join(op["keywords_match"]) if op["keywords_match"] else "-"
            linhas.append(f"- **[{op['fonte']}]** {op['titulo']}")
            linhas.append(f"  - Prazo: {op['prazo'][:10]} | Prob.: {op['probabilidade']} | Receita: {op.get('estimativa_receita', 'N/I')}")
            linhas.append(f"  - Keywords: {kw}")
            linhas.append("")

    linhas.append("## 3. Oportunidades por Fonte")
    linhas.append("")
    for fonte, itens in sorted(por_fonte.items()):
        linhas.append(f"- **{fonte}:** {len(itens)} oportunidade(s)")
    linhas.append("")

    linhas.append("## 4. Tendências de Mercado")
    linhas.append("")
    for t in tendencias:
        linhas.append(f"- **{t['titulo']}** (impacto: {t['impacto']}, categoria: {t['categoria']})")
    linhas.append("")

    linhas.append("## 5. Filtro Rápido")
    linhas.append("")
    linhas.append("Use `filtrar_por_escopo(\"subestação\")` para refinar por tema.")
    linhas.append("")

    linhas.append("---")
    linhas.append(f"*BUENOSERV Engenharia — Inteligência de Mercado*")

    relatorio = "\n".join(linhas)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RELATORIO_FILE, "w") as f:
        f.write(relatorio)

    return relatorio

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"  BUENOSERV — Inteligência de Mercado")
    print(f"  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")

    print("\n🔍 Escaneando oportunidades...")
    novas = scan_oportunidades()
    if novas:
        for op in novas:
            print(f"  🆕 [{op['fonte']}] {op['titulo']}")
    else:
        print("  ℹ️  Nenhuma oportunidade nova (já identificadas anteriormente)")

    print("\n📊 Analisando tendências...")
    novas_tend = analisar_tendencias()
    for t in novas_tend:
        print(f"  📈 {t['titulo']}")
    if not novas_tend:
        print("  ℹ️  Nenhuma nova tendência identificada")

    print("\n📄 Gerando relatório semanal...")
    gerar_relatorio_semanal()
    print(f"  ✅ Relatório salvo em {RELATORIO_FILE}")

    op_escopo = filtrar_por_escopo("subestação")
    print(f"\n🔎 Filtro por 'subestação': {len(op_escopo)} oportunidade(s)")

    print(f"\n{'='*60}")
    print(f"  Fontes: {len(_FONTES_SIMULADAS)-1} | Oportunidades totais: {len(_carregar_json(OPORTUNIDADES_FILE, []))} | Tendências: {len(_carregar_json(TENDENCIAS_FILE, []))}")
    print(f"{'='*60}")
