#!/usr/bin/env python3
"""gen_search.py — Buscador full-text do ecossistema BUENOSERV"""
import os, json, sys, re, time
from pathlib import Path

HOME = os.path.expanduser("~")
AGENTS_DIR = os.path.join(HOME, ".config/opencode/agents")
MANUALS_DIR = os.path.join(HOME, ".config/opencode/manuals")
TEMPLATES_DIR = "/tmp/opencode/templates"
STATE_FILE = os.path.join(HOME, ".config/opencode/state/agent_state.json")
INDEX_FILE = "/tmp/opencode/search_index.json"

STOPWORDS = {
    "a","ao","aos","aquele","aquela","aquilo","as","ate","com","como","da","das",
    "de","dela","dele","deles","depois","do","dos","e","ela","ele","eles","em",
    "entre","era","eram","essa","essas","esse","esses","esta","estamos","estas",
    "estava","estavam","este","esteja","estejam","estes","estou","eu","foi",
    "fomos","for","foram","foi","fui","ha","isso","isto","ja","la","lhe","lhes",
    "lo","mas","mais","me","mesma","mesmo","meu","meus","minha","minhas","muito",
    "muita","muitos","muitas","na","nao","nas","nem","no","nos","nossa","nossas",
    "nosso","nossos","num","numa","nunca","o","os","ou","para","pela","pelas",
    "pelo","pelos","por","qual","quando","que","quem","sao","se","seja","sejam",
    "sem","sempre","sendo","ser","seu","seus","sou","sua","suas","sao","tambem",
    "tem","temos","tenho","teu","teus","to","tua","tuas","tudo","um","uma","umas",
    "uns","voce","voces","the","and","are","at","be","but","by","for","if","in",
    "into","is","it","no","not","of","on","or","such","that","the","their","then",
    "there","these","they","this","to","was","will","with","from","its","can",
    "all","has","had","been","were","do","does","done","have","which","who",
    "whom","those","some","any","each","every","also","both","just","more",
    "most","only","other","same","than","too","very","well","like","into",
    "over","still","while",
}

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "magenta": "\033[95m",
    "blue": "\033[94m",
}

def tokenize(text):
    text = text.lower()
    tokens = re.findall(r'[a-záéíóúâêôãçà]+(?:\d*[a-z]*)*|\d+', text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def classify_file(path):
    if AGENTS_DIR in path or path.replace(HOME, "~").startswith("~/.config/opencode/agents"):
        return "AGENTE"
    if MANUALS_DIR in path or "manuals" in path:
        return "MANUAL"
    if "templates" in path or TEMPLATES_DIR in path:
        return "SCRIPT"
    if "state" in path or "agent_state" in path:
        return "STATE"
    return "OUTRO"

def extract_docstrings(filepath):
    content = open(filepath, encoding="utf-8", errors="replace").read()
    parts = []
    docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)
    parts.extend(docstrings)
    comments = re.findall(r'#\s*(.*)$', content, re.MULTILINE)
    parts.extend(comments)
    return "\n".join(parts)

def index_file(filepath):
    path_str = str(filepath)
    tipo = classify_file(path_str)
    ext = os.path.splitext(path_str)[1].lower()

    if ext == ".py" and tipo == "SCRIPT":
        content = extract_docstrings(path_str)
    elif ext == ".md":
        content = open(path_str, encoding="utf-8", errors="replace").read()
    elif ext == ".json":
        content = open(path_str, encoding="utf-8", errors="replace").read()
    else:
        return None

    lines = content.split("\n")
    tokens = tokenize(content)

    positions = {}
    for i, token in enumerate(tokens):
        if token not in positions:
            positions[token] = []
        positions[token].append(i)

    return {
        "path": path_str,
        "path_short": path_str.replace(HOME, "~"),
        "tipo": tipo,
        "tokens": positions,
        "token_count": len(tokens),
        "lines": len(lines),
        "content": content,
        "lines_raw": lines,
    }

def cmd_index():
    print("Indexando...\n")
    file_list = []

    if os.path.isdir(AGENTS_DIR):
        for f in sorted(os.listdir(AGENTS_DIR)):
            if f.endswith(".md"):
                file_list.append(os.path.join(AGENTS_DIR, f))

    if os.path.isdir(MANUALS_DIR):
        for f in sorted(os.listdir(MANUALS_DIR)):
            if f.endswith(".md"):
                file_list.append(os.path.join(MANUALS_DIR, f))

    if os.path.isdir(TEMPLATES_DIR):
        for f in sorted(os.listdir(TEMPLATES_DIR)):
            if f.endswith(".py") and f != "gen_search.py":
                file_list.append(os.path.join(TEMPLATES_DIR, f))

    if os.path.isfile(STATE_FILE):
        file_list.append(STATE_FILE)

    total = len(file_list)
    indexed = {}
    for i, fp in enumerate(file_list, 1):
        sys.stdout.write(f"\r  [{i}/{total}] {os.path.basename(fp)}     ")
        sys.stdout.flush()
        result = index_file(fp)
        if result:
            indexed[fp] = result
    print()

    data = {
        "timestamp": time.time(),
        "indexed_files": len(indexed),
        "files": indexed,
    }
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nIndice salvo em {INDEX_FILE} com {len(indexed)} arquivos")
    return data

def build_index():
    return cmd_index()

def load_index():
    if not os.path.isfile(INDEX_FILE):
        print("Indice nao encontrado. Execute 'python gen_search.py index' primeiro")
        return None
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)

def search_term(term, data, filter_tipo=None):
    term_lower = term.lower()
    term_words = term_lower.split()

    results = []

    for fpath, finfo in data.get("files", {}).items():
        if filter_tipo and finfo.get("tipo") != filter_tipo:
            continue

        content = finfo.get("content", "")
        lines = finfo.get("lines_raw", [])
        content_lower = content.lower()
        tipo = finfo.get("tipo", "OUTRO")
        short_path = finfo.get("path_short", fpath)

        if term_lower not in content_lower:
            continue

        score = 0
        matching_lines = []

        for li, line in enumerate(lines):
            line_lower = line.lower()
            lc = line_lower.count(term_lower)
            if lc > 0:
                ctx_start = max(0, li - 3)
                ctx_end = min(len(lines), li + 4)
                context = lines[ctx_start:ctx_end]

                if tipo == "AGENTE" and li < 2 and term_lower in line_lower:
                    score += 10 * lc
                elif li == 0 and line.startswith("#"):
                    score += 10 * lc
                elif line.startswith("##") or line.startswith("###"):
                    score += 5 * lc
                else:
                    score += 1 * lc

                matching_lines.append({
                    "linha": li + 1,
                    "contexto": context[:],
                    "ctx_start": ctx_start,
                })

        if not matching_lines and term_lower in content_lower:
            score = 1
            matching_lines.append({
                "linha": 1,
                "contexto": lines[:3],
                "ctx_start": 0,
            })

        results.append({
            "path": short_path,
            "path_full": fpath,
            "tipo": tipo,
            "score": score,
            "matches": matching_lines,
            "total_lines": finfo.get("lines", 0),
        })

    results.sort(key=lambda r: (-r["score"], r["path"]))
    return results

def print_results(term, results):
    if not results:
        print(f'{ANSI["yellow"]}Nenhum resultado para "{term}"{ANSI["reset"]}')
        return

    n = len(results)
    print(f'\n{ANSI["bold"]}{ANSI["cyan"]}Resultados para "{term}" ({n} resultado{"s" if n != 1 else ""}):{ANSI["reset"]}\n')

    for idx, r in enumerate(results[:30], 1):
        tag = {
            "AGENTE": f'{ANSI["green"]}[AGENTE]{ANSI["reset"]}',
            "MANUAL": f'{ANSI["blue"]}[MANUAL]{ANSI["reset"]}',
            "SCRIPT": f'{ANSI["magenta"]}[SCRIPT]{ANSI["reset"]}',
            "STATE": f'{ANSI["yellow"]}[STATE]{ANSI["reset"]}',
        }.get(r["tipo"], f'[{r["tipo"]}]')

        first = r["matches"][0] if r["matches"] else None
        loc = f':{first["linha"]}' if first else ""

        print(f'{ANSI["bold"]}{idx}. {tag} {r["path"]}{loc}{ANSI["reset"]}')

        if first:
            for ctx_line in first["contexto"]:
                stripped = ctx_line.strip()
                if stripped:
                    highlighted = re.sub(
                        re.escape(term),
                        f'{ANSI["red"]}{ANSI["bold"]}\\g<0>{ANSI["reset"]}',
                        stripped,
                        flags=re.IGNORECASE
                    )
                    print(f'   {highlighted}')
                else:
                    print()

        print(f'   {ANSI["bold"]}Score: {r["score"]}{ANSI["reset"]}\n')

    if len(results) > 30:
        print(f'  ... e mais {len(results) - 30} resultados nao exibidos')

def print_results_json(results):
    clean = []
    for r in results:
        entry = {
            "arquivo": r["path"],
            "tipo": r["tipo"],
            "score": r["score"],
            "linhas": r["total_lines"],
        }
        if r["matches"]:
            m = r["matches"][0]
            entry["linha"] = m["linha"]
            entry["contexto"] = "\n".join(l.strip() for l in m["contexto"])
        clean.append(entry)
    print(json.dumps(clean, indent=2, ensure_ascii=False))

def cmd_stats(data):
    if not data:
        return
    files = data.get("files", {})
    tipocount = {}
    total_tokens = 0
    for finfo in files.values():
        t = finfo.get("tipo", "OUTRO")
        tipocount[t] = tipocount.get(t, 0) + 1
        total_tokens += finfo.get("token_count", 0)

    ts = data.get("timestamp", 0)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "desconhecido"

    print(f'{ANSI["bold"]}Estatisticas do Indice BUENOSERV{ANSI["reset"]}\n')
    print(f'  Ultima indexacao: {dt}')
    print(f'  Total arquivos:   {len(files)}')
    print(f'  Total palavras:   {total_tokens}')
    print()
    for t in ["AGENTE", "MANUAL", "SCRIPT", "STATE"]:
        cnt = tipocount.get(t, 0)
        if cnt:
            print(f'  {t}: {cnt} arquivo{"s" if cnt != 1 else ""}')
    print()
    if os.path.isfile(INDEX_FILE):
        print(f'  Tamanho do indice: {os.path.getsize(INDEX_FILE) / 1024:.1f} KB')
    else:
        print("  (arquivo de indice nao encontrado)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python gen_search.py [index|busca|stats]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "index":
        data = build_index()
    elif cmd == "busca":
        if len(sys.argv) < 3:
            print('Uso: python gen_search.py busca "termo" [--json] [--agentes|--manuais|--scripts|--state]')
            sys.exit(1)
        term = sys.argv[2]
        filter_tipo = None
        for arg in sys.argv[3:]:
            if arg == "--agentes":
                filter_tipo = "AGENTE"
            elif arg == "--manuais":
                filter_tipo = "MANUAL"
            elif arg == "--scripts":
                filter_tipo = "SCRIPT"
            elif arg == "--state":
                filter_tipo = "STATE"
        as_json = "--json" in sys.argv

        data = load_index()
        if not data:
            sys.exit(1)
        results = search_term(term, data, filter_tipo)
        if as_json:
            print_results_json(results)
        else:
            print_results(term, results)
    elif cmd == "stats":
        data = load_index()
        if data:
            cmd_stats(data)
    else:
        print(f"Comando desconhecido: {cmd}")
        print("Use: index, busca, stats")
        sys.exit(1)