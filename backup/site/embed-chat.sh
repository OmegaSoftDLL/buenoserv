#!/bin/bash
# Adiciona o chat widget BUENOSERV aos HTMLs do site
# Uso: ./embed-chat.sh [index.html] [portal_cliente.html]

SCRIPT='<script src="chat-widget.js"></script>'
FILES=("$@")

if [ ${#FILES[@]} -eq 0 ]; then
  FILES=("index.html" "portal_cliente.html")
fi

for file in "${FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "[SKIP] $file — não encontrado"
    continue
  fi

  if grep -q 'chat-widget.js' "$file"; then
    echo "[OK]   $file — já possui o widget"
    continue
  fi

  # insere antes de </body>
  sed -i "s|</body>|  $SCRIPT\n</body>|" "$file"
  echo "[ADD]  $file — widget inserido"
done
