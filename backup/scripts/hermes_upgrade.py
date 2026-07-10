#!/usr/bin/env python3
"""BUENOSERV Hermes Upgrade — Conecta Hermes AI a todos os departamentos."""
import os, json, sys

DOCKER_COMPOSE_PATH = "/mnt/ssd/buenoserv/docker-compose.yml"

HERMES_SERVICE = """
  # === HERMES BRIDGE ===
  hermes:
    image: python:3.12-slim
    container_name: buenoserv-hermes
    restart: always
    ports:
      - "8580:8580"
    environment:
      - DEPARTAMENTO=HERMES
      - HOME=/home/ricardobueno
      - OLLAMA_HOST=host.docker.internal
      - OLLAMA_PORT=11434
    volumes:
      - /home/ricardobueno/.config/opencode:/home/ricardobueno/.config/opencode
      - /tmp/opencode:/tmp/opencode
    working_dir: /tmp/opencode/templates
    command: bash -c "pip install flask requests -q && python3 gen_hermes_bridge.py"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - buenoserv
"""

HERMES_UPSTREAM = "    upstream hermes_up { server hermes:8580; }"

HERMES_NGINX = """
        location /hermes/ {
            proxy_pass http://hermes_up/;
            proxy_set_header Host $host;
        }

        location /hermes/perguntar {
            proxy_pass http://hermes_up/perguntar;
            proxy_set_header Host $host;
            proxy_set_header Content-Type application/json;
        }"""

def gerar():
    print("""
╔══════════════════════════════════════════════════════════╗
║         BUENOSERV — HERMES UPGRADE                      ║
║   Conectando Hermes AI a todos os departamentos         ║
╚══════════════════════════════════════════════════════════╝

Para ativar o Hermes em todos os departamentos:

1. No SERVIDOR (192.168.1.10):
   ─────────────────────────────────────
   # Instalar Ollama com Hermes 3
   bash /tmp/opencode/templates/setup_hermes.sh

   # Adicionar Hermes Bridge ao docker-compose
   # (adicione o bloco HERMES_SERVICE ao docker-compose.yml)

   # Adicionar nginx route para /hermes/
   # (adicione HERMES_NGINX ao nginx.conf)

   # Restart
   docker compose up -d

2. NO NAVEGADOR:
   ─────────────────────────────────────
   http://192.168.1.10/hermes/         → Hermes Bridge
   http://192.168.1.10/hermes/perguntar → API de perguntas

3. TESTAR:
   ─────────────────────────────────────
   curl -X POST http://localhost:8580/perguntar \\
     -H "Content-Type: application/json" \\
     -d '{"pergunta":"O que e comissionamento de SE?"}'

4. EM CADA DEPARTAMENTO:
   ─────────────────────────────────────
   Cada departamento (8501-8505) ja esta pronto para
   receber perguntas via Hermes. Apenas configure o
   departamento_service.py para chamar o Hermes Bridge
   quando receber perguntas.

5. RESULTADO:
   ─────────────────────────────────────
   Agora cada agente de engenharia responde com
   INTELIGENCIA REAL, nao apenas documentos estaticos.
   A BUENOSERV tem 81 engenheiros IA trabalhando 24/7!
""")

if __name__ == "__main__":
    gerar()
