from flask import Flask, jsonify, send_from_directory
import subprocess

app = Flask(__name__)

def run(cmd):
    return subprocess.check_output(cmd, shell=True).decode().strip()

@app.route('/api/gpu')
def gpu():
    q = "index,name,temperature.gpu,utilization.gpu,utilization.memory,power.draw,power.limit,memory.total,memory.used,memory.free"
    raw = run(f"nvidia-smi --query-gpu={q} --format=csv,noheader,nounits")

    gpus = []
    for line in raw.splitlines():
        v = [x.strip() for x in line.split(',')]
        gpus.append({
            "index": int(v[0]), "name": v[1],
            "temp": int(v[2]), "util_gpu": int(v[3]), "util_mem": int(v[4]),
            "power_draw": float(v[5]), "power_limit": float(v[6]),
            "mem_total": int(v[7]), "mem_used": int(v[8]), "mem_free": int(v[9]),
        })

    # procesos — nvidia-smi agrega columna gpu_uuid para identificar a cuál pertenece
    procs_raw = run("nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory --format=csv,noheader,nounits 2>/dev/null || echo ''")

    # mapa uuid -> index
    uuid_raw = run("nvidia-smi --query-gpu=index,gpu_uuid --format=csv,noheader")
    uuid_map = {}
    for line in uuid_raw.splitlines():
        parts = [x.strip() for x in line.split(',')]
        uuid_map[parts[1]] = int(parts[0])

    for gpu in gpus:
        gpu['processes'] = []

    for line in procs_raw.splitlines():
        if not line.strip():
            continue
        p = [x.strip() for x in line.split(',')]
        idx = uuid_map.get(p[0], 0)
        if idx < len(gpus):
            gpus[idx]['processes'].append({
                "pid": p[1], "name": p[2],
                "mem_mb": int(p[3]) if p[3].isdigit() else 0
            })

    return jsonify(gpus)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
