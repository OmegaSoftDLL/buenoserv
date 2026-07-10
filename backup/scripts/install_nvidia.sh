#!/bin/bash
set -e

echo "=== 1. Removendo drivers antigos ==="
apt-get purge -y nvidia* cuda* cudnn* libnvidia* 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true

echo "=== 2. Blacklist nouveau ==="
cat > /etc/modprobe.d/blacklist-nvidia-nouveau.conf << 'BLACKLIST'
blacklist nouveau
options nouveau modeset=0
BLACKLIST
update-initramfs -u 2>&1 | tail -1

echo "=== 3. Instalando drivers NVIDIA ==="
apt-get update -qq
apt-get install -y -qq nvidia-driver-570 nvidia-utils-570 2>&1 | tail -5

echo "=== 4. Instalando CUDA 12.8 ==="
wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2604/x86_64/cuda-keyring_1.1-1_all.deb -O /tmp/cuda-keyring.deb 2>/dev/null || echo "wget falhou, tentando alternativa"
if [ -f /tmp/cuda-keyring.deb ]; then
  dpkg -i /tmp/cuda-keyring.deb
  apt-get update -qq
  apt-get install -y -qq cuda-toolkit-12.8 2>&1 | tail -5
else
  echo "CUDA keyring nao disponivel para 26.04 — instalando driver-only"
fi

echo "=== 5. NVIDIA Container Toolkit ==="
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg 2>/dev/null
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' > /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update -qq
apt-get install -y -qq nvidia-container-toolkit 2>&1 | tail -3

echo "=== 6. Configurar Docker NVIDIA ==="
nvidia-ctk runtime configure --runtime=docker 2>&1 | tail -3
systemctl restart docker

echo "=== 7. PATH CUDA ==="
echo 'export PATH=/usr/local/cuda/bin:$PATH' > /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> /etc/profile.d/cuda.sh
chmod +x /etc/profile.d/cuda.sh

echo "=== INSTALACAO CONCLUIDA ==="
echo "REINICIALIZE O SERVIDOR para ativar drivers NVIDIA"
echo "Apos reboot: nvidia-smi para verificar"
