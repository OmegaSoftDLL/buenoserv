#!/bin/bash
# init_projeto.sh — Inicializa um novo projeto completo
# Uso: ./init_projeto.sh "Nome do Projeto" "Cliente" "Escopo"

set -e

PROJETO="$1"
CLIENTE="$2"
ESCOPO="$3"

if [ -z "$PROJETO" ] || [ -z "$CLIENTE" ]; then
    echo "Uso: init_projeto.sh \"Nome\" \"Cliente\" [\"Escopo\"]"
    exit 1
fi

# Normalizar nome do projeto para ID
ID=$(echo "$PROJETO" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]')
DATA=$(date +%Y-%m-%d)

echo "🚀 Inicializando projeto: $PROJETO ($CLIENTE)"

# 1. Registrar no state
source /tmp/opencode-env/bin/activate
python3 /tmp/opencode/templates/chain_agents.py iniciar "$PROJETO" "$CLIENTE" "$ESCOPO"

# 2. Criar estrutura de diretórios
BASE_DIR="/tmp/opencode/projetos/$PROJETO"
mkdir -p "$BASE_DIR"/{00-DOCS,01-PROPOSTA,02-ENGENHARIA/{levantamento,projetos,bom-depara},03-SUPRIMENTOS,04-CIVIL,05-INSTALACAO/{fotos,checklists},06-COMISSIONAMENTO/{sat,testes},07-HANDOVER/{asbuilt,manuais},08-QUALIDADE,09-FINANCEIRO,10-RH}

echo "✅ Estrutura criada em $BASE_DIR"
echo "📋 Projeto $PROJETO inicializado com sucesso!"
