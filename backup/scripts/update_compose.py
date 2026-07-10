import yaml

with open('/mnt/ssd/buenoserv/docker-compose.yml') as f:
    data = yaml.safe_load(f)

new_services = {
    'prometheus': {
        'image': 'prom/prometheus:latest',
        'container_name': 'buenoserv-prometheus',
        'restart': 'always',
        'ports': ['9090:9090'],
        'volumes': [
            '/mnt/ssd/buenoserv/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml',
            'prometheus_data:/prometheus'
        ],
        'command': [
            '--config.file=/etc/prometheus/prometheus.yml',
            '--storage.tsdb.path=/prometheus',
            '--web.console.libraries=/usr/share/prometheus/console_libraries',
            '--web.console.templates=/usr/share/prometheus/consoles'
        ],
        'networks': ['buenoserv']
    },
    'grafana': {
        'image': 'grafana/grafana:latest',
        'container_name': 'buenoserv-grafana',
        'restart': 'always',
        'ports': ['3000:3000'],
        'environment': {
            'GF_SECURITY_ADMIN_USER': 'buenoserv',
            'GF_SECURITY_ADMIN_PASSWORD': 'Buenoserv@2026',
            'GF_INSTALL_PLUGINS': 'grafana-piechart-panel'
        },
        'volumes': [
            'grafana_data:/var/lib/grafana',
            '/mnt/ssd/buenoserv/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards',
            '/mnt/ssd/buenoserv/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources'
        ],
        'depends_on': ['prometheus'],
        'networks': ['buenoserv']
    },
    'cadvisor': {
        'image': 'gcr.io/cadvisor/cadvisor:latest',
        'container_name': 'buenoserv-cadvisor',
        'restart': 'always',
        'ports': ['8081:8080'],
        'volumes': [
            '/:/rootfs:ro',
            '/var/run:/var/run:ro',
            '/sys:/sys:ro',
            '/var/lib/docker/:/var/lib/docker:ro',
            '/dev/disk/:/dev/disk:ro'
        ],
        'privileged': True,
        'devices': ['/dev/kmsg'],
        'networks': ['buenoserv']
    },
    'node-exporter': {
        'image': 'prom/node-exporter:latest',
        'container_name': 'buenoserv-node-exporter',
        'restart': 'always',
        'ports': ['9100:9100'],
        'volumes': [
            '/proc:/host/proc:ro',
            '/sys:/host/sys:ro',
            '/:/rootfs:ro'
        ],
        'command': [
            '--path.procfs=/host/proc',
            '--path.sysfs=/host/sys',
            '--path.rootfs=/rootfs'
        ],
        'networks': ['buenoserv']
    },
    'gpu-exporter': {
        'image': 'python:3.12-slim',
        'container_name': 'buenoserv-gpu-exporter',
        'restart': 'always',
        'ports': ['9400:9400'],
        'environment': {
            'NVIDIA_VISIBLE_DEVICES': 'all',
            'NVIDIA_DRIVER_CAPABILITIES': 'compute,utility'
        },
        'volumes': ['/tmp/opencode:/tmp/opencode'],
        'working_dir': '/tmp/opencode/templates',
        'command': 'bash -c "pip install flask -q && python3 gen_gpu_exporter.py"',
        'deploy': {
            'resources': {
                'reservations': {
                    'devices': [{'capabilities': ['gpu']}]
                }
            }
        },
        'networks': ['buenoserv']
    }
}

for name, svc in new_services.items():
    data['services'][name] = svc

if 'volumes' not in data:
    data['volumes'] = {}
data['volumes']['prometheus_data'] = {'driver': 'local'}
data['volumes']['grafana_data'] = {'driver': 'local'}

with open('/mnt/ssd/buenoserv/docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print('DOCKER_COMPOSE_UPDATED_OK')