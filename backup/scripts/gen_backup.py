#!/usr/bin/env python3
"""Backup automático — zip agentes + state + site e salva localmente"""
import os, sys, datetime, zipfile, shutil

BASE = os.path.expanduser("~/.config/opencode")
BACKUP_DIR = os.path.expanduser("~/Backups_Buenoserv")
AGENTS = os.path.join(BASE, "agents")
STATE = os.path.join(BASE, "state")
DASHBOARD = os.path.join(BASE, "dashboard")
SITE = "/tmp/opencode/site"
TEMPLATES = "/tmp/opencode/templates"

def gerar_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    data = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = f"buenoserv_backup_{data}.zip"
    path = os.path.join(BACKUP_DIR, nome)

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for diretorio in [AGENTS, STATE, DASHBOARD]:
            if os.path.exists(diretorio):
                for root, dirs, files in os.walk(diretorio):
                    for f in files:
                        fp = os.path.join(root, f)
                        arcname = os.path.relpath(fp, BASE)
                        z.write(fp, arcname)
        if os.path.exists(SITE):
            for root, dirs, files in os.walk(SITE):
                for f in files:
                    fp = os.path.join(root, f)
                    arcname = os.path.join("site", os.path.relpath(fp, SITE))
                    z.write(fp, arcname)
        if os.path.exists(TEMPLATES):
            for root, dirs, files in os.walk(TEMPLATES):
                for f in files:
                    if f.endswith('.py'):
                        fp = os.path.join(root, f)
                        arcname = os.path.join("templates", f)
                        z.write(fp, arcname)

    tamanho = os.path.getsize(path)
    print(f"✅ Backup criado: {path}")
    print(f"   Tamanho: {tamanho/1024:.1f} KB")
    # Manter últimos 10 backups
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')])
    while len(backups) > 10:
        remover = os.path.join(BACKUP_DIR, backups.pop(0))
        os.remove(remover)
        print(f"   🗑️ Backup antigo removido: {remover}")
    return path

if __name__ == "__main__":
    gerar_backup()
