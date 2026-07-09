#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  gen_site_deploy.sh — Deploy script para BUENOSERV
#  Gera backup, valida HTML, cria relatorio e prepara deploy
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR)"
SITE_DIR="${PROJECT_ROOT}/site"
BACKUP_DIR="${PROJECT_ROOT}/backups/$(date +%Y%m%d_%H%M%S)"
DEPLOY_REPORT="${PROJECT_ROOT}/deploy_report_$(date +%Y%m%d_%H%M%S).txt"
ERRORS=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; ERRORS=$((ERRORS + 1)); }

# ------------------------------------------------------------------
# 1. Backup do site atual
# ------------------------------------------------------------------
backup_site() {
  info "Criando backup em ${BACKUP_DIR} ..."
  mkdir -p "${BACKUP_DIR}"
  if [ -d "${SITE_DIR}" ]; then
    cp -r "${SITE_DIR}" "${BACKUP_DIR}/"
    info "Backup concluido."
  else
    warn "Diretorio ${SITE_DIR} nao encontrado. Backup ignorado."
  fi
}

# ------------------------------------------------------------------
# 2. Validacao HTML (verifica se arquivos existem)
# ------------------------------------------------------------------
validate_html() {
  info "Validando arquivos do site..."

  FILES=(
    "${SITE_DIR}/index.html"
    "${SITE_DIR}/portal_cliente.html"
    "${SITE_DIR}/dashboard/executive.html"
    "${SITE_DIR}/dashboard/ceo_dashboard.html"
    "${SITE_DIR}/robots.txt"
    "${SITE_DIR}/sitemap.xml"
    "${SITE_DIR}/.htaccess"
  )

  for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
      info "  OK  ${f}"
    else
      error "  MISSING  ${f}"
    fi
  done
}

# ------------------------------------------------------------------
# 3. Gera deploy report
# ------------------------------------------------------------------
generate_report() {
  info "Gerando relatorio de deploy..."
  {
    echo "============================================"
    echo "  BUENOSERV - Deploy Report"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================"
    echo ""
    echo "Arquivos do site:"
    find "${SITE_DIR}" -type f | sort
    echo ""
    echo "Status: $([ "$ERRORS" -eq 0 ] && echo "OK - Pronto para deploy" || echo "COM ERROS - corrija antes de deploy")"
    echo "Erros encontrados: ${ERRORS}"
    echo ""
    echo "Tamanho total do site:"
    du -sh "${SITE_DIR}" 2>/dev/null || echo "N/A"
  } > "${DEPLOY_REPORT}"

  info "Relatorio salvo em: ${DEPLOY_REPORT}"
  cat "${DEPLOY_REPORT}"
}

# ------------------------------------------------------------------
# 4. Permissoes corretas
# ------------------------------------------------------------------
set_permissions() {
  info "Ajustando permissoes..."
  find "${SITE_DIR}" -type d -exec chmod 755 {} \;
  find "${SITE_DIR}" -type f -exec chmod 644 {} \;
  chmod 755 "${SCRIPT_DIR}/gen_site_deploy.sh"
  info "Permissoes ajustadas (dir:755, file:644)."
}

# ------------------------------------------------------------------
# 5. Instrucoes de deploy
# ------------------------------------------------------------------
deploy_instructions() {
  echo ""
  echo "============================================"
  echo "  INSTRUCOES DE DEPLOY"
  echo "============================================"
  echo ""
  echo "--- GitHub Pages ---"
  echo "  1. Crie um repositorio: git init && git add . && git commit -m 'site'"
  echo "  2. Crie um repo no GitHub e siga as instrucoes para push"
  echo "  3. No GitHub, va em Settings > Pages > source: main /root"
  echo "  4. Pronto! URL: https://<user>.github.io/<repo>/"
  echo ""
  echo "--- VPS (Apache/Nginx) ---"
  echo "  1. Envie os arquivos via SCP/RSYNC:"
  echo "     rsync -avz --delete ${SITE_DIR}/ user@seuvps:/var/www/buenoserv/"
  echo ""
  echo "  2. Configure o VirtualHost (Apache):"
  echo '     <VirtualHost *:80>'
  echo "       ServerName buenoserv.com"
  echo "       DocumentRoot /var/www/buenoserv"
  echo '       <Directory /var/www/buenoserv>'
  echo "         AllowOverride All"
  echo "         Require all granted"
  echo "       </Directory>"
  echo "     </VirtualHost>"
  echo ""
  echo "  3. Habilite SSL (Certbot):"
  echo "     sudo certbot --apache -d buenoserv.com"
  echo ""
  echo "  4. Recarregue o Apache: sudo systemctl reload apache2"
  echo ""
  echo "============================================"
}

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
main() {
  echo ""
  echo "  BUENOSERV - Script de Deploy"
  echo "  ============================="
  echo ""

  backup_site
  validate_html
  generate_report
  set_permissions
  deploy_instructions

  echo ""
  if [ "$ERRORS" -eq 0 ]; then
    info "Tudo OK! Site pronto para deploy."
  else
    error "${ERRORS} erro(s) encontrado(s). Corrija antes de fazer deploy."
  fi
  echo ""
}

main "$@"
