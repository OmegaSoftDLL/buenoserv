#!/usr/bin/env python3
"""Auto Follow-up — verifica propostas pendentes e dispara e-mail automático"""
import json, os, sys, subprocess
from datetime import datetime, date

STATE_PATH = os.path.expanduser("~/.config/opencode/state/agent_state.json")
EMAIL_SCRIPT = "/tmp/opencode/templates/enviar_email.py"
LOG_PATH = os.path.expanduser("~/.config/opencode/state/followup.log")

def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def should_followup(task_history):
    """Verifica se já passaram 7+ dias desde o último envio e não houve retorno"""
    last_send = None
    has_response = False
    for t in task_history:
        if t["agente"] == "comercial" and t["status"] == "concluido":
            if "enviado" in t.get("observacao", "").lower() or "email" in t.get("observacao", "").lower():
                try:
                    ts = datetime.fromisoformat(t["timestamp"])
                    if last_send is None or ts > last_send:
                        last_send = ts
                except:
                    pass
            if "retorno" in t.get("observacao", "").lower() or "resposta" in t.get("observacao", "").lower():
                has_response = True
    if not last_send:
        return False, None
    days_since = (datetime.now() - last_send).days
    return (days_since >= 7 and not has_response), days_since

def main():
    if not os.path.exists(STATE_PATH):
        log("State nao encontrado")
        return

    with open(STATE_PATH) as f:
        state = json.load(f)

    log("=== Auto Follow-up Scan ===")
    triggered = 0

    for task_name, task_history in state.get("tasks", {}).items():
        # Só processa tarefas comerciais de prospeccao
        is_commercial = any(t["agente"] == "comercial" for t in task_history)
        if not is_commercial:
            continue

        should, days = should_followup(task_history)
        if not should:
            continue

        # Extrair email do destinatario das observacoes
        destinatario = None
        assunto = f"Follow-up - BUENOSERV Engenharia"
        empresa = task_name
        for t in task_history:
            obs = t.get("observacao", "")
            if "@" in obs:
                for word in obs.split():
                    if "@" in word:
                        destinatario = word.strip(".,;!?")
            if "iosienergia" in obs.lower():
                empresa = "IOSI Energia"
            elif "sistem.eng" in obs.lower():
                empresa = "Sistem Engenharia"
            elif "omexom" in obs.lower():
                empresa = "Omexom Brasil"
            elif "mpeengenharia" in obs.lower():
                empresa = "MPE Engenharia"
            elif "engesist" in obs.lower():
                empresa = "Engesist"
            elif "montelbras" in obs.lower():
                empresa = "Montelbras"
            elif "construtorabrasilreal" in obs.lower():
                empresa = "Brasil Real Energia"
            elif "engie" in obs.lower():
                empresa = "Engie Brasil"
            elif "aplicaengenharia" in obs.lower():
                empresa = "Aplica Engenharia"
            elif "proteonengenharia" in obs.lower():
                empresa = "Proteon Engenharia"

        if not destinatario:
            log(f"  ⚠️ {task_name}: sem email encontrado, pulando")
            continue

        args = json.dumps({
            "destinatario": destinatario,
            "assunto": f"Follow-up - Prospeccao - {empresa}",
            "cliente": empresa,
            "contato": "Diretor Tecnico",
            "proposta_id": "-",
            "valor": 0,
            "data_envio": datetime.now().strftime("%d/%m/%Y")
        })

        result = subprocess.run(
            ["python3", EMAIL_SCRIPT, "followup", args],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            log(f"  ✅ Follow-up enviado para {destinatario} ({empresa}) - {days}d apos ultimo contato")
            triggered += 1
        else:
            log(f"  ❌ Erro ao enviar para {destinatario}: {result.stderr}")

    log(f"Total: {triggered} follow-ups disparados")
    print(f"\n📧 {triggered} follow-ups enviados")

if __name__ == "__main__":
    main()
