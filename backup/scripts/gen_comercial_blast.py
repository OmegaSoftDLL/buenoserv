#!/usr/bin/env python3
"""BUENOSERV Commercial Blast — disparo automatizado de propostas e follow-ups."""
import json, os, subprocess, sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
SCRIPTS_DIR = "/tmp/opencode/templates"
LOG_FILE = "/tmp/opencode/comercial_blast.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def carregar_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {}

def salvar_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f: json.dump(s, f, indent=2, ensure_ascii=False)

def executar(script, args, timeout=60):
    path = os.path.join(SCRIPTS_DIR, script)
    if not os.path.exists(path):
        return {"erro": f"{script} nao encontrado"}
    try:
        r = subprocess.run(["python3", path] + args, capture_output=True, text=True, timeout=timeout)
        return {"ok": r.returncode == 0, "stdout": r.stdout[:500], "stderr": r.stderr[:200]}
    except Exception as e:
        return {"erro": str(e)}

def listar_oportunidades():
    state = carregar_state()
    opps = []
    for proj, tasks in state.get("tasks", {}).items():
        for t in tasks:
            agente = t.get("agente", "").lower()
            if "comercial" not in agente and "rfp" not in agente:
                continue
            # Extrair valor da observacao
            obs = t.get("observacao", "")
            import re
            match = re.search(r"R[$]?\s*([\d.,]+)", obs)
            valor = 0
            if match:
                try: valor = float(match.group(1).replace(".", "").replace(",", "."))
                except: pass
            opps.append({
                "projeto": proj,
                "cliente": proj.replace("Prospeccao ", "").strip(),
                "status": t.get("status", ""),
                "valor": valor,
                "observacao": obs,
                "data": t.get("timestamp", "")[:10]
            })
    return opps

def enviar_proposta(cliente, email, valor):
    log(f"Enviando proposta para {cliente} ({email}) — R$ {valor:,.2f}")
    return executar("gen_mail.py", [email, f"proposta:{cliente}", str(valor)])

def enviar_followup(cliente, email):
    log(f"Enviando follow-up para {cliente} ({email})")
    return executar("gen_mail.py", [email, f"followup:{cliente}", ""])

def dry_run():
    opps = listar_oportunidades()
    print(f"\n{'='*60}")
    print(f"  BUENOSERV COMMERCIAL BLAST — DRY RUN")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")
    
    ativas = [o for o in opps if o["status"] == "em_andamento"]
    concluidas = [o for o in opps if o["status"] == "concluido"]
    
    print(f"Total: {len(opps)} oportunidades")
    print(f"Ativas: {len(ativas)}")
    print(f"Concluídas: {len(concluidas)}")
    print(f"Valor total: R$ {sum(o['valor'] for o in opps):,.2f}\n")
    
    if ativas:
        print("Ações recomendadas:")
        for o in ativas:
            print(f"  → Proposta para {o['cliente']} — R$ {o['valor']:,.2f}")
    
    print(f"\nComandos que seriam executados:")
    for o in ativas[:3]:
        print(f"  gen_mail.py ricardo.bueno@buenoservengenharia.com proposta:{o['cliente']} {o['valor']}")
    
    return ativas

def disparar():
    opps = listar_oportunidades()
    ativas = [o for o in opps if o["status"] == "em_andamento"]
    
    if not ativas:
        log("Nenhuma oportunidade ativa para disparo")
        return
    
    log(f"Iniciando blast comercial — {len(ativas)} oportunidades ativas")
    
    for o in ativas:
        email = "ricardo.bueno@buenoservengenharia.com"
        if o["valor"] > 0:
            r = enviar_proposta(o["cliente"], email, o["valor"])
        else:
            r = enviar_followup(o["cliente"], email)
        
        status = "✅" if r.get("ok") else "❌"
        log(f"  {status} {o['cliente']}: {r.get('stdout','')[:60]}")
        
        # Atualizar state
        state = carregar_state()
        for proj, tasks in state.get("tasks", {}).items():
            for t in tasks:
                if t.get("observacao","") == o["observacao"]:
                    t["ultimo_contato"] = datetime.now().isoformat()
        salvar_state(state)
    
    log("Blast comercial concluido")

if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run()
    elif "--enviar" in sys.argv:
        disparar()
    else:
        print("Uso: python3 gen_comercial_blast.py [--dry-run | --enviar]")
        print("  --dry-run  : Mostra o que seria feito")
        print("  --enviar   : Executa o disparo real")
