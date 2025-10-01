# Guía de Despliegue de NeuroGym / NeuroGym Deployment Guide

[English version below](#english-version)

## 🇪🇸 Versión en Español

### Resumen

Esta guía describe cómo desplegar NeuroGym como un servicio web en Raspberry Pi 5 utilizando Docker. El proyecto ha sido adaptado para proporcionar una API REST que permite interactuar con los entornos de NeuroGym de forma remota.

### Características Principales

- ✅ **Optimizado para ARM64**: Dockerfile específico para Raspberry Pi 5
- ✅ **API REST completa**: Basada en FastAPI con documentación interactiva
- ✅ **Docker y Docker Compose**: Despliegue fácil y reproducible
- ✅ **Servicio systemd**: Configuración para inicio automático
- ✅ **Eficiente en recursos**: Configurado para hardware limitado
- ✅ **Health checks**: Monitoreo automático del servicio

### Requisitos

- Raspberry Pi 5 (4GB RAM mínimo recomendado)
- Raspberry Pi OS 64-bit (Bookworm o posterior)
- Docker Engine 20.10+
- Docker Compose v2.0+

### Instalación Rápida

#### Opción 1: Script Automático

```bash
git clone https://github.com/neurogym/neurogym.git
cd neurogym
bash deployment/setup-raspberry-pi.sh
```

Este script:
1. Actualiza el sistema
2. Instala Docker y Docker Compose
3. Construye la imagen Docker
4. Inicia el servicio
5. Verifica que funcione correctamente

#### Opción 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/neurogym/neurogym.git
cd neurogym

# 2. Construir imagen Docker
docker compose build

# 3. Iniciar servicio
docker compose up -d

# 4. Verificar estado
docker compose ps
curl http://localhost:8000/health
```

### Uso del Servicio Web

#### Acceso a la Documentación

Una vez iniciado, la API está disponible en:
- **URL local**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

#### Ejemplos de Uso

##### 1. Verificar Estado del Servicio

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{"status": "healthy"}
```

##### 2. Listar Tareas Disponibles

```bash
curl http://localhost:8000/tasks
```

##### 3. Crear un Entorno

```bash
curl -X POST http://localhost:8000/environments \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "PerceptualDecisionMaking-v0",
    "kwargs": {"dt": 100}
  }'
```

##### 4. Usar Cliente Python

```python
import requests

# Configurar URL base
BASE_URL = "http://localhost:8000"

# Crear entorno
response = requests.post(
    f"{BASE_URL}/environments",
    json={
        "task_name": "PerceptualDecisionMaking-v0",
        "kwargs": {"dt": 100}
    }
)
session_id = response.json()["session_id"]

# Resetear entorno
response = requests.post(f"{BASE_URL}/environments/{session_id}/reset")
observation = response.json()["observation"]

# Ejecutar acciones
for _ in range(10):
    response = requests.post(
        f"{BASE_URL}/environments/{session_id}/step",
        json={"session_id": session_id, "action": 1}
    )
    result = response.json()
    print(f"Recompensa: {result['reward']}")

# Limpiar
requests.delete(f"{BASE_URL}/environments/{session_id}")
```

Ver ejemplo completo en: [examples/api_client_example.py](examples/api_client_example.py)

### Configuración como Servicio del Sistema

Para que NeuroGym se inicie automáticamente al arrancar el Raspberry Pi:

```bash
# Copiar archivo de servicio
sudo cp deployment/neurogym.service /etc/systemd/system/

# Editar WorkingDirectory si es necesario
sudo nano /etc/systemd/system/neurogym.service

# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable neurogym.service
sudo systemctl start neurogym.service

# Verificar estado
sudo systemctl status neurogym.service
```

### Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Reiniciar servicio
docker compose restart

# Detener servicio
docker compose down

# Ver estado de recursos
docker stats

# Ver sesiones activas
curl http://localhost:8000/environments
```

### Configuración de Recursos

El archivo `docker-compose.yml` incluye límites apropiados para Raspberry Pi 5:

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

Ajusta estos valores según tu configuración específica.

### Seguridad

#### Recomendaciones

1. **Firewall**: Limitar acceso al puerto 8000
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

2. **Red Local**: Por defecto, el servicio es accesible en la red local
   - Para acceso público, considera usar un proxy reverso (nginx) con HTTPS
   - Implementa autenticación para entornos de producción

3. **Actualizaciones**: Mantén el sistema actualizado
   ```bash
   sudo apt update && sudo apt upgrade
   docker compose pull && docker compose up -d
   ```

### Solución de Problemas

#### El servicio no inicia

```bash
# Ver logs detallados
docker compose logs

# Verificar si el puerto está en uso
sudo netstat -tulpn | grep 8000

# Reiniciar Docker
sudo systemctl restart docker
```

#### Problemas de memoria

```bash
# Reducir límites en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

#### Problemas de red

```bash
# Verificar conectividad
curl http://localhost:8000/health

# Reiniciar red Docker
docker network prune
docker compose up -d
```

---

## 🇬🇧 English Version

### Overview

This guide describes how to deploy NeuroGym as a web service on Raspberry Pi 5 using Docker. The project has been adapted to provide a REST API that allows remote interaction with NeuroGym environments.

### Key Features

- ✅ **ARM64 Optimized**: Specific Dockerfile for Raspberry Pi 5
- ✅ **Complete REST API**: Based on FastAPI with interactive documentation
- ✅ **Docker & Docker Compose**: Easy and reproducible deployment
- ✅ **Systemd Service**: Configuration for automatic startup
- ✅ **Resource Efficient**: Configured for limited hardware
- ✅ **Health Checks**: Automatic service monitoring

### Requirements

- Raspberry Pi 5 (4GB RAM minimum recommended)
- Raspberry Pi OS 64-bit (Bookworm or later)
- Docker Engine 20.10+
- Docker Compose v2.0+

### Quick Installation

#### Option 1: Automated Script

```bash
git clone https://github.com/neurogym/neurogym.git
cd neurogym
bash deployment/setup-raspberry-pi.sh
```

This script:
1. Updates the system
2. Installs Docker and Docker Compose
3. Builds the Docker image
4. Starts the service
5. Verifies it works correctly

#### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/neurogym/neurogym.git
cd neurogym

# 2. Build Docker image
docker compose build

# 3. Start service
docker compose up -d

# 4. Check status
docker compose ps
curl http://localhost:8000/health
```

### Using the Web Service

#### Accessing Documentation

Once started, the API is available at:
- **Local URL**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

#### Usage Examples

See the Spanish section above for detailed examples, or refer to:
- [README.docker.md](README.docker.md) - Detailed Docker deployment guide
- [examples/api_client_example.py](examples/api_client_example.py) - Complete Python client example

### System Service Configuration

To make NeuroGym start automatically on Raspberry Pi boot:

```bash
# Copy service file
sudo cp deployment/neurogym.service /etc/systemd/system/

# Edit WorkingDirectory if needed
sudo nano /etc/systemd/system/neurogym.service

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable neurogym.service
sudo systemctl start neurogym.service

# Check status
sudo systemctl status neurogym.service
```

### Useful Commands

```bash
# View logs in real-time
docker compose logs -f

# Restart service
docker compose restart

# Stop service
docker compose down

# View resource usage
docker stats

# View active sessions
curl http://localhost:8000/environments
```

### Additional Resources

- **Main README**: [README.md](README.md) - General NeuroGym documentation
- **Docker README**: [README.docker.md](README.docker.md) - Detailed Docker instructions
- **API Tests**: [tests/test_api.py](tests/test_api.py) - API endpoint tests
- **Example Client**: [examples/api_client_example.py](examples/api_client_example.py)

### Contributing

This deployment configuration is part of the NeuroGym project. For contributions:
1. Follow the main [CONTRIBUTING.md](CONTRIBUTING.md) guidelines
2. Test your changes on Raspberry Pi 5 if possible
3. Update documentation as needed

### Support

For issues or questions:
- GitHub Issues: https://github.com/neurogym/neurogym/issues
- Documentation: https://neurogym.github.io/neurogym/latest/

### License

Apache-2.0 License - See [LICENSE](LICENSE) for details.
