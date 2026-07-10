#!/bin/bash
# BUENOSERV Server Setup Script
# Executar como root

set -e

echo "=========================================="
echo "  BUENOSERV Server Setup"
echo "  $(date)"
echo "=========================================="

# === 1. Preparar discos ===
echo "[1/8] Preparando discos..."

# Montar SSD NVMe
mkdir -p /mnt/ssd /mnt/hdd /docker

# Montar partição grande do SSD
if ! mountpoint -q /mnt/ssd; then
  mount /dev/nvme0n1p3 /mnt/ssd
  echo "/dev/nvme0n1p3 /mnt/ssd btrfs defaults 0 2" >> /etc/fstab
fi

# Montar HDD
if ! mountpoint -q /mnt/hdd; then
  # Criar partição no HDD se necessário (sda3 já existe com LVM)
  # Usar LVM para expandir
  lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv 2>/dev/null || true
  resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv 2>/dev/null || true
  echo "HDD LVM expandido"
fi

# Criar diretório Docker no SSD
mkdir -p /mnt/ssd/docker /mnt/ssd/buenoserv
ln -sf /mnt/ssd/docker /docker

# === 2. Instalar Docker ===
echo "[2/8] Instalando Docker..."
if ! command -v docker &>/dev/null; then
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl gnupg lsb-release
  mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Configurar Docker para usar SSD
cat > /etc/docker/daemon.json << 'DOCKER_EOF'
{
  "data-root": "/mnt/ssd/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
DOCKER_EOF

systemctl restart docker
systemctl enable docker
docker --version

# === 3. Instalar Portainer ===
echo "[3/8] Instalando Portainer..."
docker volume create portainer_data
docker run -d --name portainer --restart=always \
  -p 8000:8000 -p 9443:9443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  --name portainer \
  portainer/portainer-ce:latest

echo "Aguardando Portainer..."
sleep 5

# === 4. Rede Docker ===
echo "[4/8] Criando rede Docker..."
docker network create buenoserv --driver bridge 2>/dev/null || true

# === 5. Serviços Core ===
echo "[5/8] Instalando serviços core..."

# Nginx reverse proxy
mkdir -p /mnt/ssd/buenoserv/nginx
cat > /mnt/ssd/buenoserv/nginx/default.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name buenoservengenharia.com localhost;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name buenoservengenharia.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    location / {
        proxy_pass http://dashboard:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api:8090;
        proxy_set_header Host $host;
    }

    location /chat/ {
        proxy_pass http://whatsapp:8095;
        proxy_set_header Host $host;
    }
}

server {
    listen 80;
    server_name *.buenoservengenharia.com;
    return 301 https://$host$request_uri;
}
NGINX_EOF

# === 6. Docker Compose ===
echo "[6/8] Criando docker-compose.yml..."
cat > /mnt/ssd/buenoserv/docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  # === DASHBOARD ===
  dashboard:
    image: python:3.12-slim
    container_name: buenoserv-dashboard
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - /home/ricardobueno/.config/opencode:/home/ricardobueno/.config/opencode
      - /tmp/opencode:/tmp/opencode
    working_dir: /tmp/opencode/templates
    command: python3 serve_dashboard.py
    networks:
      - buenoserv

  # === API REST ===
  api:
    image: python:3.12-slim
    container_name: buenoserv-api
    restart: always
    ports:
      - "8090:8090"
    volumes:
      - /home/ricardobueno/.config/opencode:/home/ricardobueno/.config/opencode
      - /tmp/opencode:/tmp/opencode
    working_dir: /tmp/opencode/templates
    command: python3 gen_api.py 8090
    networks:
      - buenoserv

  # === WHATSAPP BOT ===
  whatsapp:
    image: python:3.12-slim
    container_name: buenoserv-whatsapp
    restart: always
    ports:
      - "8095:8095"
    volumes:
      - /home/ricardobueno/.config/opencode:/home/ricardobueno/.config/opencode
      - /tmp/opencode:/tmp/opencode
    working_dir: /tmp/opencode/templates
    command: python3 gen_bot_whatsapp.py
    networks:
      - buenoserv

  # === NGINX ===
  nginx:
    image: nginx:alpine
    container_name: buenoserv-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /mnt/ssd/buenoserv/nginx/default.conf:/etc/nginx/conf.d/default.conf
      - /mnt/ssd/buenoserv/nginx/certs:/etc/nginx/certs
      - /tmp/opencode/site:/usr/share/nginx/html:ro
    depends_on:
      - dashboard
      - api
    networks:
      - buenoserv

networks:
  buenoserv:
    external: true
COMPOSE_EOF

# === 7. Sincronizar dados ===
echo "[7/8] Configurando sincronização..."

# Criar script de sync dos dados
cat > /usr/local/bin/sync-buenoserv << 'SYNC_EOF'
#!/bin/bash
rsync -avz --delete toor@192.168.1.1:/home/ricardobueno/.config/opencode/ /home/ricardobueno/.config/opencode/
rsync -avz --delete toor@192.168.1.1:/tmp/opencode/ /tmp/opencode/
docker exec buenoserv-dashboard pkill -HUP python3 2>/dev/null || true
echo "Sincronizado em $(date)"
SYNC_EOF
chmod +x /usr/local/bin/sync-buenoserv

# === 8. Finalizar ===
echo "[8/8] Finalizando..."
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=========================================="
echo "  BUENOSERV Server Setup COMPLETE"
echo "  Portainer: https://192.168.1.10:9443"
echo "  Dashboard: http://192.168.1.10:8080"
echo "  API:       http://192.168.1.10:8090"
echo "  WhatsApp:  http://192.168.1.10:8095"
echo "=========================================="
