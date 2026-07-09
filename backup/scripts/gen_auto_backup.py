#!/usr/bin/env python3
"""gen_auto_backup.py — Backup automático do ecossistema BUENOSERV para GitHub."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

REPO_URL = "https://github.com/OmegaSoftDLL/buenoserv.git"
REPO_DIR = "/tmp/opencode/backup_repo"
STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

HOME = os.path.expanduser("~")
CONFIG_OPENCODE = os.path.join(HOME, ".config", "opencode")
TMP_OPENCODE = "/tmp/opencode"

BACKUP_MAP = {
    "state":     (os.path.join(CONFIG_OPENCODE, "state", "agent_state.json"), "backup/state/"),
    "agentes":   (os.path.join(CONFIG_OPENCODE, "agents"), "backup/agentes/"),
    "scripts":   (os.path.join(TMP_OPENCODE, "templates"), "backup/scripts/"),
    "manuais":   (os.path.join(CONFIG_OPENCODE, "manuals"), "backup/manuais/"),
    "dashboard": (os.path.join(CONFIG_OPENCODE, "dashboard"), "backup/dashboard/"),
    "site":      (os.path.join(TMP_OPENCODE, "site"), "backup/site/"),
    "logs":      (TMP_OPENCODE, "backup/logs/"),
    "relatorios":(os.path.join(TMP_OPENCODE, "relatorios"), "backup/relatorios/"),
    "market":    (os.path.join(TMP_OPENCODE, "market_intel"), "backup/market/"),
}

RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"


def log_info(msg): print(f"{GREEN}[INFO]{RESET} {msg}")
def log_warn(msg): print(f"{YELLOW}[WARN]{RESET} {msg}")
def log_ok(msg):   print(f"{GREEN}[OK]{RESET} {msg}")
def log_err(msg):  print(f"{RED}[ERRO]{RESET} {msg}")


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def ensure_repo():
    if not os.path.isdir(REPO_DIR):
        log_info("Clonando repositório...")
        run(["git", "clone", REPO_URL, REPO_DIR])
        log_ok("Repositório clonado")
    else:
        run(["git", "fetch", "origin"], cwd=REPO_DIR)
        run(["git", "reset", "--hard", "origin/master"], cwd=REPO_DIR)


def copy_to_backup(src, dest_subdir, is_file=False):
    dest_dir = os.path.join(REPO_DIR, dest_subdir)
    os.makedirs(dest_dir, exist_ok=True)
    if is_file:
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dest_dir, os.path.basename(src)))
    else:
        if os.path.isdir(src):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dest_dir, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)
                elif os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)


def backup_state_only():
    ensure_repo()
    log_info("Copiando state...")
    s, d = BACKUP_MAP["state"]
    copy_to_backup(s, d, is_file=True)
    commit_and_push()


def backup_all():
    ensure_repo()
    for name, (src, dest) in BACKUP_MAP.items():
        is_file = name == "state"
        if name == "logs":
            dest_dir = os.path.join(REPO_DIR, dest)
            os.makedirs(dest_dir, exist_ok=True)
            for f in os.listdir(src):
                if f.endswith(".json"):
                    shutil.copy2(os.path.join(src, f), os.path.join(dest_dir, f))
            log_ok(f"{name} copiado")
            continue
        copy_to_backup(src, dest, is_file=is_file)
        log_ok(f"{name} copiado")
    commit_and_push()


def commit_and_push():
    os.chdir(REPO_DIR)
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        log_info("Nenhuma mudança detectada. Nada a commitar.")
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"Backup automático {now}"
    run(["git", "add", "."], cwd=REPO_DIR)
    run(["git", "commit", "-m", msg], cwd=REPO_DIR)
    run(["git", "push", "origin", "master"], cwd=REPO_DIR)
    log_ok(f"Commit e push realizados: {msg}")
    update_state_timestamp(now)


def update_state_timestamp(now_str):
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
        data["ultimo_backup"] = now_str
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_ok(f"Estado salvo em agent_state.json -> ultimo_backup: {now_str}")


def show_status():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
        ultimo = data.get("ultimo_backup", "Nunca")
        print(f"{CYAN}Último backup:{RESET} {ultimo}")
    else:
        log_warn("agent_state.json não encontrado")


def register_cron():
    cron_job = "0 23 * * * cd /tmp/opencode/templates && python3 gen_auto_backup.py >> /tmp/opencode/backup_cron.log 2>&1"
    existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if "gen_auto_backup.py" in existing.stdout:
        log_info("Cron já registrado")
        return
    new_cron = existing.stdout.strip() + "\n" + cron_job + "\n"
    p = subprocess.run(["crontab", "-"], input=new_cron, capture_output=True, text=True)
    if p.returncode == 0:
        log_ok("Cron registrado: diário às 23h")
    else:
        log_err(f"Falha ao registrar cron: {p.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Backup BUENOSERV para GitHub")
    parser.add_argument("--state-only", action="store_true", help="Apenas state")
    parser.add_argument("--status", action="store_true", help="Verificar último backup")
    parser.add_argument("--register-cron", action="store_true", help="Registrar cron diário 23h")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.register_cron:
        register_cron()
    elif args.state_only:
        backup_state_only()
    else:
        backup_all()


if __name__ == "__main__":
    main()