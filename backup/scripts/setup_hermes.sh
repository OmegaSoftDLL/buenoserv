#!/bin/bash
# BUENOSERV — Ativar Hermes AI em todos os departamentos
# Execute no servidor quando estiver online

set -e

echo "=========================================="
echo "  ATIVANDO HERMES AI — BUENOSERV"
echo "=========================================="

# 1. Instalar Ollama
echo "[1/5] Instalando Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
echo "Ollama $(ollama --version)"

# 2. Configurar GPU para Ollama
echo "[2/5] Configurando GPU..."
export OLLAMA_HOST=0.0.0.0
export OLLAMA_PORT=11434
cat > /etc/systemd/system/ollama.service.d/override.conf << 'OLLAMA'
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_KEEP_ALIVE=-1"
Environment="OLLAMA_NUM_PARALLEL=2"
OLLAMA
systemctl daemon-reload
systemctl restart ollama

# 3. Pull Hermes 3 (8B) — modelo de IA para engenharia
echo "[3/5] Baixando Hermes 3 (8B)..."
ollama pull hermes3
echo "Hermes 3 pronto!"

# 4. Testar inferencia
echo "[4/5] Testando..."
ollama run hermes3 "Explique o comissionamento de subestacao 138kV em 3 frases." 2>/dev/null

# 5. Verificar GPU
echo "[5/5] GPU status..."
curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null | head -10 || true

echo ""
echo "=========================================="
echo "  HERMES AI ATIVADO!"
echo "  API: http://localhost:11434"
echo "  Modelo: hermes3"
echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "=========================================="
