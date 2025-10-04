# NeuroGym Docker & Web Service Deployment

Este documento describe cómo instalar y ejecutar NeuroGym en Raspberry Pi 5 utilizando Docker y cómo usar el servicio web.

This document describes how to install and run NeuroGym on Raspberry Pi 5 using Docker and how to use the web service.

---

**🇪🇸 ¿Prefieres una guía rápida en español?** → [INICIO_RAPIDO_RPI5.md](INICIO_RAPIDO_RPI5.md)

**🇬🇧 Looking for a quick English guide?** → Continue reading below or see [QUICK_REFERENCE.md](deployment/QUICK_REFERENCE.md)

---

## Requisitos / Requirements

### Hardware
- Raspberry Pi 5 (4GB RAM mínimo / minimum recommended)
- Tarjeta microSD de 32GB o más / microSD card 32GB or larger
- Conexión a Internet / Internet connection

### Software
- Raspberry Pi OS (64-bit) - Bookworm or later
- Docker Engine 20.10 o superior / or higher
- Docker Compose v2.0 o superior / or higher

## Instalación / Installation

### 1. Instalar Docker en Raspberry Pi 5 / Install Docker on Raspberry Pi 5

```bash
# Actualizar el sistema / Update system
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker / Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker / Add user to docker group
sudo usermod -aG docker $USER

# Instalar Docker Compose / Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# Reiniciar para aplicar cambios / Restart to apply changes
sudo reboot
```

### 2. Clonar el Repositorio / Clone Repository

```bash
git clone https://github.com/neurogym/neurogym.git
cd neurogym
```

### 3. Construir la Imagen Docker / Build Docker Image

```bash
# Construcción básica / Basic build
docker build -t neurogym:latest .

# O usando docker-compose / Or using docker-compose
docker compose build
```

## Uso / Usage

### Opción 1: Docker Compose (Recomendado / Recommended)

```bash
# Iniciar el servicio / Start service
docker compose up -d

# Ver logs / View logs
docker compose logs -f

# Detener el servicio / Stop service
docker compose down
```

### Opción 2: Docker Run

```bash
# Ejecutar el contenedor / Run container
docker run -d \
  --name neurogym-service \
  -p 8000:8000 \
  --restart unless-stopped \
  neurogym:latest

# Ver logs / View logs
docker logs -f neurogym-service

# Detener / Stop
docker stop neurogym-service
```

## API Web / Web API

El servicio web estará disponible en / The web service will be available at:
- **Local**: http://localhost:8000
- **Red Local / Local Network**: http://[raspberry-pi-ip]:8000

### Documentación Interactiva / Interactive Documentation

Una vez iniciado el servicio, accede a / Once the service is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ejemplos de Uso / Usage Examples

#### 1. Verificar Salud del Servicio / Check Service Health

```bash
curl http://localhost:8000/health
```

#### 2. Listar Tareas Disponibles / List Available Tasks

```bash
curl http://localhost:8000/tasks
```

#### 3. Crear un Entorno / Create an Environment

```bash
curl -X POST http://localhost:8000/environments \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "PerceptualDecisionMaking-v0",
    "kwargs": {
      "dt": 100
    }
  }'
```

Respuesta / Response:
```json
{
  "session_id": "uuid-here",
  "task_name": "PerceptualDecisionMaking-v0",
  "observation_space": {...},
  "action_space": {...}
}
```

#### 4. Resetear Entorno / Reset Environment

```bash
curl -X POST http://localhost:8000/environments/{session_id}/reset
```

#### 5. Ejecutar Acción / Execute Action

```bash
curl -X POST http://localhost:8000/environments/{session_id}/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "action": 1
  }'
```

#### 6. Eliminar Entorno / Delete Environment

```bash
curl -X DELETE http://localhost:8000/environments/{session_id}
```

## Cliente Python / Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Crear entorno / Create environment
response = requests.post(
    f"{BASE_URL}/environments",
    json={
        "task_name": "PerceptualDecisionMaking-v0",
        "kwargs": {"dt": 100}
    }
)
session_id = response.json()["session_id"]

# Resetear / Reset
response = requests.post(f"{BASE_URL}/environments/{session_id}/reset")
observation = response.json()["observation"]

# Ejecutar acciones / Execute actions
for _ in range(10):
    response = requests.post(
        f"{BASE_URL}/environments/{session_id}/step",
        json={"session_id": session_id, "action": 1}
    )
    data = response.json()
    print(f"Reward: {data['reward']}, Done: {data['terminated']}")

# Limpiar / Cleanup
requests.delete(f"{BASE_URL}/environments/{session_id}")
```

## Configuración / Configuration

### Variables de Entorno / Environment Variables

Puedes configurar el servicio usando variables de entorno / You can configure the service using environment variables:

```bash
# En docker-compose.yml / In docker-compose.yml
environment:
  - NEUROGYM_ENV=production
  - LOG_LEVEL=info
  - MAX_SESSIONS=100
```

### Límites de Recursos / Resource Limits

Para Raspberry Pi 5, se recomiendan estos límites / For Raspberry Pi 5, these limits are recommended:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 512M
```

## Solución de Problemas / Troubleshooting

### El servicio no inicia / Service won't start

```bash
# Verificar logs / Check logs
docker compose logs

# Verificar recursos / Check resources
docker stats
```

### Puerto en uso / Port in use

```bash
# Cambiar puerto en docker-compose.yml / Change port in docker-compose.yml
ports:
  - "8080:8000"  # Usar 8080 en lugar de 8000 / Use 8080 instead of 8000
```

### Problemas de memoria / Memory issues

```bash
# Reducir límites en docker-compose.yml / Reduce limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

## Seguridad / Security

### Recomendaciones / Recommendations

1. **Firewall**: Configurar firewall para limitar acceso / Configure firewall to limit access
   ```bash
   sudo ufw allow 8000/tcp
   ```

2. **Red Local**: Por defecto, el servicio es accesible en la red local. Para producción, considera usar un proxy reverso con HTTPS.
   / By default, the service is accessible on the local network. For production, consider using a reverse proxy with HTTPS.

3. **Autenticación**: Implementar autenticación para acceso seguro / Implement authentication for secure access

## Monitoreo / Monitoring

### Health Check

El contenedor incluye un health check automático / The container includes automatic health check:

```bash
# Ver estado / Check status
docker inspect --format='{{json .State.Health}}' neurogym-service
```

### Logs

```bash
# Logs en tiempo real / Real-time logs
docker compose logs -f

# Últimas 100 líneas / Last 100 lines
docker compose logs --tail=100
```

## Actualización / Update

```bash
# Detener servicio / Stop service
docker compose down

# Actualizar código / Update code
git pull

# Reconstruir imagen / Rebuild image
docker compose build

# Reiniciar / Restart
docker compose up -d
```

## Rendimiento en Raspberry Pi 5 / Performance on Raspberry Pi 5

- **CPU**: Se recomienda usar 2-4 cores / Recommended to use 2-4 cores
- **RAM**: Mínimo 2GB, recomendado 4GB / Minimum 2GB, recommended 4GB
- **Almacenamiento / Storage**: SSD recomendado para mejor rendimiento / SSD recommended for better performance

## Soporte / Support

Para problemas o preguntas / For issues or questions:
- GitHub Issues: https://github.com/neurogym/neurogym/issues
- Documentación / Documentation: https://neurogym.github.io/neurogym/latest/

## Licencia / License

Apache-2.0 License - Ver / See [LICENSE](LICENSE) para más detalles / for details.
