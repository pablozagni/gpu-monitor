from flask import Flask, jsonify, send_from_directory
import subprocess, urllib.request, json

app = Flask(__name__)

# GPU index -> puerto Ollama (segun CUDA_VISIBLE_DEVICES configurado)
OLLAMA_PORTS = {
    0: 11435,  # RTX 3090
    1: 11434,  # RTX 5070
}

def run(cmd):
    return subprocess.check_output(cmd, shell=True).decode().strip()

def ollama_model(port):
    try:
        url = f"http://host.docker.internal:{port}/api/ps"
        req = urllib.request.urlopen(url, timeout=2)
        data = json.loads(req.read())
        models = data.get("models", [])
        if models:
            return models[0].get("name", "")
        return ""
    except:
        return ""

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
            "processes": [],
            "ollama_model": "",
        })

    procs_raw = run("nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory --format=csv,noheader,nounits 2>/dev/null || echo ''")
    uuid_raw = run("nvidia-smi --query-gpu=index,gpu_uuid --format=csv,noheader")
    uuid_map = {}
    for line in uuid_raw.splitlines():
        parts = [x.strip() for x in line.split(',')]
        uuid_map[parts[1]] = int(parts[0])

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

    for gpu in gpus:
        port = OLLAMA_PORTS.get(gpu['index'])
        if port:
            gpu['ollama_model'] = ollama_model(port)

    return jsonify(gpus)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
