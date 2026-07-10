from flask import Flask, Response
import subprocess
import re
import time

app = Flask(__name__)

def parse_nvidia_smi():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,temperature.gpu,memory.used,memory.total,utilization.gpu,power.draw',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        metrics = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 7:
                continue
            idx, name, temp, mem_used, mem_total, util, power = parts
            name_clean = name.replace('"', '').replace(' ', '_')
            mem_used_bytes = float(mem_used) * 1024 * 1024 if mem_used else 0
            mem_total_bytes = float(mem_total) * 1024 * 1024 if mem_total else 0
            metrics.append(f'nvidia_gpu_temperature_celsius{{gpu="{idx}",name="{name_clean}"}} {temp}')
            metrics.append(f'nvidia_gpu_memory_used_bytes{{gpu="{idx}",name="{name_clean}"}} {mem_used_bytes}')
            metrics.append(f'nvidia_gpu_memory_total_bytes{{gpu="{idx}",name="{name_clean}"}} {mem_total_bytes}')
            metrics.append(f'nvidia_gpu_utilization_percent{{gpu="{idx}",name="{name_clean}"}} {util}')
            metrics.append(f'nvidia_gpu_power_watts{{gpu="{idx}",name="{name_clean}"}} {power}')
        return metrics
    except Exception as e:
        return [f'nvidia_gpu_up 0']

@app.route('/metrics')
def metrics():
    gpu_metrics = parse_nvidia_smi()
    prom_metrics = '# HELP nvidia_gpu_temperature_celsius GPU temperature in Celsius\n'
    prom_metrics += '# TYPE nvidia_gpu_temperature_celsius gauge\n'
    prom_metrics += '# HELP nvidia_gpu_memory_used_bytes GPU memory used in bytes\n'
    prom_metrics += '# TYPE nvidia_gpu_memory_used_bytes gauge\n'
    prom_metrics += '# HELP nvidia_gpu_memory_total_bytes GPU memory total in bytes\n'
    prom_metrics += '# TYPE nvidia_gpu_memory_total_bytes gauge\n'
    prom_metrics += '# HELP nvidia_gpu_utilization_percent GPU utilization percent\n'
    prom_metrics += '# TYPE nvidia_gpu_utilization_percent gauge\n'
    prom_metrics += '# HELP nvidia_gpu_power_watts GPU power draw in watts\n'
    prom_metrics += '# TYPE nvidia_gpu_power_watts gauge\n'
    prom_metrics += '\n'.join(gpu_metrics) + '\n'
    return Response(prom_metrics, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9400)