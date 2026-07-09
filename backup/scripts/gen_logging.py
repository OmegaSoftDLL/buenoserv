#!/usr/bin/env python3
"""Sistema de logging centralizado — registra todas as ações do sistema"""
import json, os, sys, datetime, glob

LOG_DIR = os.path.expanduser("~/.config/opencode/state/")
STATE_FILE = os.path.join(LOG_DIR, "agent_state.json")
MASTER_LOG = os.path.join(LOG_DIR, "system.log")

def registrar(origem, tipo, mensagem, detalhe=""):
    ts = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": ts,
        "origem": origem,
        "tipo": tipo,
        "mensagem": mensagem,
        "detalhe": str(detalhe)[:200]
    }
    # Escreve no master log
    with open(MASTER_LOG, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # Também salva no state
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        state.setdefault("system_log", [])
        state["system_log"].append(entry)
        if len(state["system_log"]) > 500:
            state["system_log"] = state["system_log"][-500:]
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except:
        pass
    return entry

def consolidar_logs():
    """Consolida logs dispersos em um relatório unificado"""
    logs = {}
    for logfile in glob.glob(os.path.join(LOG_DIR, "*.log")):
        nome = os.path.basename(logfile)
        if nome == "system.log":
            continue
        try:
            with open(logfile) as f:
                lines = f.readlines()[-50:]  # Últimas 50 linhas
            if lines:
                logs[nome] = {"caminho": logfile, "linhas": len(lines), "ultimas": lines[-5:]}
        except:
            pass
    return logs

def relatorio(saida=None):
    saida = saida or os.path.expanduser("~/Desktop/Relatorio_Sistema_BUENOSERV.txt")
    logs = consolidar_logs()
    
    with open(saida, 'w') as f:
        f.write(f"RELATÓRIO DE LOGS — BUENOSERV\n")
        f.write(f"{datetime.datetime.now():%d/%m/%Y %H:%M}\n")
        f.write("=" * 55 + "\n\n")
        
        # Logs de cada fonte
        for nome, info in sorted(logs.items()):
            f.write(f"📄 {nome} ({info['linhas']} linhas)\n")
            f.write(f"   {info['caminho']}\n")
            for line in info['ultimas']:
                f.write(f"   {line.strip()[:100]}\n")
            f.write("\n")
        
        # Master log
        if os.path.exists(MASTER_LOG):
            with open(MASTER_LOG) as ml:
                entries = ml.readlines()[-20:]
            f.write("📋 SYSTEM LOG (últimos 20 eventos)\n")
            for e in entries:
                try:
                    entry = json.loads(e)
                    f.write(f"   [{entry['timestamp'][:19]}] {entry['origem']}: {entry['mensagem'][:80]}\n")
                except:
                    f.write(f"   {e.strip()[:100]}\n")
    
    print(f"✅ Relatório de logs: {saida}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "consolidar":
        logs = consolidar_logs()
        for nome, info in logs.items():
            print(f"  {nome}: {info['linhas']} linhas")
    elif len(sys.argv) > 1 and sys.argv[1] == "relatorio":
        relatorio()
    else:
        # Modo interativo
        import sys
        if len(sys.argv) >= 4:
            registrar(sys.argv[1], sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
        else:
            print("Uso: gen_logging.py <origem> <tipo> <mensagem> [detalhe]")
