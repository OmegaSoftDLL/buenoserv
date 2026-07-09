#!/usr/bin/env python3
"""RFP Scraper — varre sites de licitação por palavras-chave do setor de energia/telecom"""
import json, os, sys, datetime, re, time
from urllib.request import urlopen, Request
from urllib.error import URLError

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
TERMOS = [
    "subestação", "subestacao", "telecomunicações", "telecomunicacoes",
    "fibra óptica", "fibra optica", "SDH", "DWDM", "MPLS",
    "comissionamento", "proteção", "protecao", "SCADA",
    "IEC 61850", "sistema de energia", "linha de transmissão", "linha transmissao",
    "SE 138kV", "SE 230kV", "SE 500kV", "SE 69kV",
    "teleproteção", "teleprotecao", "PCM", "piloto"
]

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

def salvar_estado(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def buscar_comprasnet():
    """Busca licitações no ComprasNet (Governo Federal)"""
    resultados = []
    url = "https://www.gov.br/compras/pt-br/acesso-a-informacao/consultas/licitacoes"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        for termo in TERMOS:
            if termo.lower() in html.lower():
                resultados.append(f"ComprasNet: termo '{termo}' encontrado")
        return resultados
    except Exception as e:
        return [f"ComprasNet: erro ao acessar ({e})"]

def buscar_diario_oficial():
    """Simula busca no Diário Oficial da União"""
    resultados = []
    try:
        url = "https://www.in.gov.br/leitura?secao=do3"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        for termo in TERMOS:
            if termo.lower() in html.lower():
                resultados.append(f"DOU: termo '{termo}' encontrado")
        return resultados or ["DOU: Nenhum termo encontrado hoje"]
    except Exception as e:
        return [f"DOU: erro ao acessar ({e})"]

def buscar_aneel():
    """Busca consultas públicas e licitações ANEEL"""
    resultados = []
    try:
        url = "https://www.aneel.gov.br/consultas-publicas"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        for termo in TERMOS:
            if termo.lower() in html.lower():
                resultados.append(f"ANEEL: termo '{termo}' encontrado em consultas públicas")
        # Leilão out/26
        if "2026" in html and ("leilão" in html.lower() or "leilao" in html.lower()):
            resultados.append("ANEEL: Possível menção a leilão 2026")
        return resultados or ["ANEEL: Nenhum termo encontrado"]
    except Exception as e:
        return [f"ANEEL: erro ao acessar ({e})"]

def buscar_tce():
    """Busca licitações nos Tribunais de Contas estaduais"""
    resultados = []
    estados = ["sp", "rj", "mg", "rs", "pr", "ba", "df", "go", "es", "sc"]
    for estado in estados[:3]:  # Limitar a 3 para não sobrecarregar
        try:
            url = f"https://www.tce.{estado}.gov.br/licitacoes"
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=10) as r:
                html = r.read().decode('utf-8', errors='ignore')
            for termo in TERMOS[:3]:
                if termo.lower() in html.lower():
                    resultados.append(f"TCE-{estado.upper()}: '{termo}' encontrado")
        except:
            pass
    return resultados or ["TCE: Nenhum resultado (timeout/não acessível)"]

def salvar_resultados(resultados):
    state = carregar_estado()
    if "rfp_scraper" not in state:
        state["rfp_scraper"] = {"historico": [], "ultima_busca": None}
    state["rfp_scraper"]["ultima_busca"] = datetime.datetime.now().isoformat()
    state["rfp_scraper"]["historico"].append({
        "data": datetime.datetime.now().isoformat(),
        "resultados": resultados
    })
    # Manter últimas 50 buscas
    if len(state["rfp_scraper"]["historico"]) > 50:
        state["rfp_scraper"]["historico"] = state["rfp_scraper"]["historico"][-50:]
    salvar_estado(state)

def exibir_resultados(resultados, fontes):
    print(f"\n{'='*55}")
    print(f"  RFP Scraper — {datetime.date.today():%d/%m/%Y}")
    print(f"{'='*55}")
    for fonte, res in zip(fontes, resultados):
        print(f"\n  📡 {fonte}:")
        for r in res[:5]:
            print(f"    {'•' if 'erro' not in r.lower() else '⚠️'} {r}")
    print(f"\n{'='*55}")

if __name__ == "__main__":
    print("🔍 RFP Scraper — Buscando licitações...")
    fontes = ["ComprasNet", "Diário Oficial", "ANEEL", "TCE"]
    resultados = [
        buscar_comprasnet(),
        buscar_diario_oficial(),
        buscar_aneel(),
        buscar_tce()
    ]
    salvar_resultados(resultados)
    exibir_resultados(resultados, fontes)

    # Contar matches
    total = sum(1 for r in resultados for item in r if "encontrado" in item.lower())
    print(f"\n  Total de matches: {total}")
    if total > 0:
        print("  ✅ Novas oportunidades potenciais encontradas!")
    else:
        print("  ℹ️  Nenhum match novo. Tente ampliar os termos de busca.")
