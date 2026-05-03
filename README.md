# GPU Monitor

Dashboard web para monitorear GPUs NVIDIA en tiempo real.  
Muestra temperatura, utilización, VRAM y procesos activos. Soporta múltiples GPUs.

## Stack

- Python 3.11 + Flask (API)
- Chart.js (gráficos)
- nvidia-smi (datos)
- Docker

## Requisitos

- Docker con NVIDIA Container Toolkit instalado
- GPU NVIDIA con driver >= 520

### Instalar nvidia-container-toolkit (si no está)

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Uso

```bash
git clone https://github.com/TU_USUARIO/gpu-monitor
cd gpu-monitor
docker compose up -d
```

Abrir en el browser: `http://localhost:5001`

## Multi-GPU

Detecta automáticamente todas las GPUs del sistema.  
Al agregar una nueva GPU, aparece en el dashboard sin cambios.

## API

`GET /api/gpu` — devuelve array JSON con datos de cada GPU:

```json
[
  {
    "index": 0,
    "name": "NVIDIA GeForce RTX 5070",
    "temp": 34,
    "util_gpu": 0,
    "mem_total": 12227,
    "mem_used": 2,
    "mem_free": 11772,
    "power_draw": 1.2,
    "power_limit": 250.0,
    "processes": []
  }
]
```

## Capturas

> _agregar screenshots aquí_

## Licencia

MIT
