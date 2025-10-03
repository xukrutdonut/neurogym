# 🚀 Inicio Rápido - NeuroGym en Raspberry Pi 5 con Docker

Esta guía te ayudará a instalar y ejecutar NeuroGym en tu Raspberry Pi 5 usando Docker con acceso web en **menos de 10 minutos**.

## 📋 Requisitos Previos

- **Hardware**: Raspberry Pi 5 (4GB RAM mínimo recomendado)
- **Sistema**: Raspberry Pi OS 64-bit (Bookworm o posterior)
- **Almacenamiento**: Tarjeta microSD de 32GB o más
- **Red**: Conexión a Internet

## ⚡ Instalación Rápida (Método Automático)

### Opción 1: Script de Instalación Automática (Recomendado)

Este script instalará Docker, clonará el repositorio, construirá la imagen y lanzará el servicio automáticamente.

```bash
# Descarga y ejecuta el script de instalación
curl -fsSL https://raw.githubusercontent.com/neurogym/neurogym/main/deployment/setup-raspberry-pi.sh | bash
```

¡Eso es todo! El servicio estará disponible en:
- **Local**: http://localhost:8000
- **En tu red**: http://[IP-de-tu-raspberry]:8000

### Opción 2: Instalación Manual Paso a Paso

Si prefieres instalar manualmente, sigue estos pasos:

#### Paso 1: Instalar Docker

```bash
# Actualizar el sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin -y

# Reiniciar para aplicar cambios (necesario)
sudo reboot
```

#### Paso 2: Clonar el Repositorio

```bash
git clone https://github.com/neurogym/neurogym.git
cd neurogym
```

#### Paso 3: Construir e Iniciar el Servicio

```bash
# Construir la imagen Docker (puede tardar varios minutos)
docker compose build

# Iniciar el servicio
docker compose up -d

# Verificar que funciona
curl http://localhost:8000/health
```

## ✅ Verificar la Instalación

Una vez instalado, verifica que todo funciona correctamente:

```bash
# Verificar el estado del servicio
docker compose ps

# Ver los logs
docker compose logs -f

# Probar la API
curl http://localhost:8000/health
```

Deberías ver una respuesta como:
```json
{"status": "healthy"}
```

## 🌐 Acceder al Servicio Web

### Desde la Raspberry Pi

Abre un navegador y visita:
- **API**: http://localhost:8000
- **Documentación Interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación Alternativa (ReDoc)**: http://localhost:8000/redoc

### Desde Otro Dispositivo en tu Red

1. Obtén la dirección IP de tu Raspberry Pi:
   ```bash
   hostname -I
   ```

2. Desde otro dispositivo en la misma red, accede a:
   - **API**: http://[IP-de-tu-raspberry]:8000
   - **Documentación**: http://[IP-de-tu-raspberry]:8000/docs

   Ejemplo: `http://192.168.1.100:8000`

## 🎯 Primeros Pasos con la API

### Listar Tareas Disponibles

```bash
curl http://localhost:8000/tasks
```

### Crear un Entorno

```bash
curl -X POST http://localhost:8000/environments \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "PerceptualDecisionMaking-v0",
    "kwargs": {"dt": 100}
  }'
```

### Ejemplo Completo en Python

```python
import requests

# Conectar a la API
base_url = "http://localhost:8000"

# Crear entorno
response = requests.post(
    f"{base_url}/environments",
    json={"task_name": "PerceptualDecisionMaking-v0", "kwargs": {"dt": 100}}
)
session_id = response.json()["session_id"]
print(f"Entorno creado con ID: {session_id}")

# Resetear entorno
response = requests.post(f"{base_url}/environments/{session_id}/reset")
observation = response.json()["observation"]
print(f"Observación inicial: {observation}")

# Ejecutar 10 pasos
for i in range(10):
    response = requests.post(
        f"{base_url}/environments/{session_id}/step",
        json={"session_id": session_id, "action": 1}
    )
    data = response.json()
    print(f"Paso {i+1}: Recompensa={data['reward']}, Terminado={data['terminated']}")

# Limpiar
requests.delete(f"{base_url}/environments/{session_id}")
print("Entorno eliminado")
```

## 🔧 Comandos Útiles

### Gestión del Servicio

```bash
# Iniciar el servicio
docker compose up -d

# Detener el servicio
docker compose down

# Reiniciar el servicio
docker compose restart

# Ver logs en tiempo real
docker compose logs -f

# Ver estado
docker compose ps

# Ver uso de recursos
docker stats
```

### Actualizar NeuroGym

```bash
# Detener el servicio
docker compose down

# Actualizar el código
git pull

# Reconstruir la imagen
docker compose build

# Reiniciar el servicio
docker compose up -d
```

## 🔄 Configurar Inicio Automático

Para que NeuroGym se inicie automáticamente al arrancar tu Raspberry Pi:

```bash
# Copiar el archivo de servicio systemd
sudo cp deployment/neurogym.service /etc/systemd/system/

# Editar la ruta de trabajo (cambiar /home/pi/neurogym por tu ruta)
sudo nano /etc/systemd/system/neurogym.service

# Habilitar el servicio
sudo systemctl daemon-reload
sudo systemctl enable neurogym.service
sudo systemctl start neurogym.service

# Verificar el estado
sudo systemctl status neurogym.service
```

## 🔥 Solución de Problemas

### El servicio no inicia

```bash
# Ver logs detallados
docker compose logs

# Verificar el estado de Docker
sudo systemctl status docker

# Reiniciar Docker
sudo systemctl restart docker
docker compose up -d
```

### Puerto 8000 en uso

Si el puerto 8000 ya está en uso, edita `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Usar puerto 8080 en lugar de 8000
```

### Problemas de memoria

Si tu Raspberry Pi tiene poca memoria, reduce los límites en `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2G  # Reducir de 4G a 2G
```

### Verificar que Docker está instalado correctamente

```bash
docker --version
docker compose version
docker ps
```

## 📚 Documentación Adicional

- **Guía Completa en Español**: [README.docker.md](README.docker.md)
- **Guía de Despliegue**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Referencia Rápida API**: [deployment/QUICK_REFERENCE.md](deployment/QUICK_REFERENCE.md)
- **Ejemplo de Cliente**: [examples/api_client_example.py](examples/api_client_example.py)
- **Documentación Completa**: https://neurogym.github.io/neurogym/latest/

## 🎓 Tareas Disponibles

NeuroGym incluye más de 20 tareas de neurociencia:

- **PerceptualDecisionMaking-v0**: Toma de decisiones perceptuales
- **ContextDecisionMaking-v0**: Decisiones dependientes del contexto
- **DelayMatchSample-v0**: Memoria de trabajo con retraso
- **GoNogo-v0**: Tarea Go/NoGo
- **ReadySetGo-v0**: Temporización motora
- Y muchas más...

Lista completa en: http://localhost:8000/tasks

## ⚡ Rendimiento en Raspberry Pi 5

- **Inicio**: ~30-60 segundos para construir la imagen
- **Uso de CPU**: 5-15% en reposo
- **Uso de RAM**: ~500MB-1GB
- **Red**: Baja latencia, accesible desde toda la red local

## 💡 Consejos

1. **Usa un SSD**: Para mejor rendimiento, usa un SSD externo en lugar de tarjeta SD
2. **Refrigeración**: Usa un disipador o ventilador para evitar throttling
3. **Red estable**: Conecta tu Raspberry Pi por Ethernet para mejor estabilidad
4. **Backup**: Guarda una copia de tu configuración `docker-compose.yml`

## 🤝 Soporte

Si tienes problemas:
1. Revisa la sección de **Solución de Problemas** arriba
2. Consulta la [documentación completa](https://neurogym.github.io/neurogym/latest/)
3. Abre un issue en: https://github.com/neurogym/neurogym/issues

## 📄 Licencia

NeuroGym está licenciado bajo Apache-2.0. Ver [LICENSE](LICENSE) para más detalles.

---

**¡Listo!** 🎉 Ahora tienes NeuroGym funcionando en tu Raspberry Pi 5 con acceso web.

Para más información, visita: https://neurogym.github.io/neurogym/latest/
