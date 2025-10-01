# NeuroGym API - Quick Reference Card

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/neurogym/neurogym.git
cd neurogym
bash deployment/setup-raspberry-pi.sh
```

## 📍 Endpoints

### Base URL
```
http://localhost:8000
```

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root/welcome message |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/tasks` | GET | List all available tasks |
| `/environments` | GET | List active sessions |
| `/environments` | POST | Create new environment |
| `/environments/{id}` | GET | Get environment info |
| `/environments/{id}` | DELETE | Delete environment |
| `/environments/{id}/reset` | POST | Reset environment |
| `/environments/{id}/step` | POST | Take action in environment |

## 💻 Usage Examples

### Python

```python
import requests

base = "http://localhost:8000"

# Create environment
r = requests.post(f"{base}/environments", 
    json={"task_name": "PerceptualDecisionMaking-v0", "kwargs": {"dt": 100}})
sid = r.json()["session_id"]

# Reset
r = requests.post(f"{base}/environments/{sid}/reset")
obs = r.json()["observation"]

# Step
r = requests.post(f"{base}/environments/{sid}/step",
    json={"session_id": sid, "action": 1})
result = r.json()

# Cleanup
requests.delete(f"{base}/environments/{sid}")
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# List tasks
curl http://localhost:8000/tasks

# Create environment
curl -X POST http://localhost:8000/environments \
  -H "Content-Type: application/json" \
  -d '{"task_name": "PerceptualDecisionMaking-v0", "kwargs": {"dt": 100}}'

# Reset (replace SESSION_ID)
curl -X POST http://localhost:8000/environments/SESSION_ID/reset

# Step (replace SESSION_ID)
curl -X POST http://localhost:8000/environments/SESSION_ID/step \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "action": 1}'

# Delete (replace SESSION_ID)
curl -X DELETE http://localhost:8000/environments/SESSION_ID
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const base = 'http://localhost:8000';

async function run() {
    // Create environment
    const createResp = await axios.post(`${base}/environments`, {
        task_name: 'PerceptualDecisionMaking-v0',
        kwargs: {dt: 100}
    });
    const sid = createResp.data.session_id;
    
    // Reset
    const resetResp = await axios.post(`${base}/environments/${sid}/reset`);
    const obs = resetResp.data.observation;
    
    // Step
    const stepResp = await axios.post(`${base}/environments/${sid}/step`, {
        session_id: sid,
        action: 1
    });
    const result = stepResp.data;
    
    // Cleanup
    await axios.delete(`${base}/environments/${sid}`);
}

run();
```

## 🐳 Docker Commands

```bash
# Build
docker compose build

# Start (detached)
docker compose up -d

# Start (foreground)
docker compose up

# Stop
docker compose down

# View logs
docker compose logs -f

# Restart
docker compose restart

# Check status
docker compose ps

# View resource usage
docker stats
```

## 🔧 Service Management (systemd)

```bash
# Start service
sudo systemctl start neurogym.service

# Stop service
sudo systemctl stop neurogym.service

# Restart service
sudo systemctl restart neurogym.service

# Check status
sudo systemctl status neurogym.service

# Enable auto-start on boot
sudo systemctl enable neurogym.service

# Disable auto-start
sudo systemctl disable neurogym.service

# View logs
sudo journalctl -u neurogym.service -f
```

## 📊 Response Examples

### Create Environment Response
```json
{
  "session_id": "d9e889f4-1234-5678-9abc-def012345678",
  "task_name": "PerceptualDecisionMaking-v0",
  "observation_space": {
    "shape": [3],
    "dtype": "float32"
  },
  "action_space": {
    "n": 2,
    "shape": []
  }
}
```

### Reset Response
```json
{
  "observation": [1.0, 0.5, 0.5],
  "info": {}
}
```

### Step Response
```json
{
  "observation": [1.0, 0.6, 0.4],
  "reward": 0.0,
  "terminated": false,
  "truncated": false,
  "info": {
    "gt": 0,
    "new_trial": false
  }
}
```

## 🔍 Available Tasks (Sample)

- `PerceptualDecisionMaking-v0`
- `ContextDecisionMaking-v0`
- `DelayedMatchToSample-v0`
- `GoNogo-v0`
- `ReadySetGo-v0`
- `AntiReach-v0`
- `Bandit-v0`
- ... and 20+ more!

Full list: `curl http://localhost:8000/tasks`

## 🛠️ Troubleshooting

### Service not starting
```bash
docker compose logs
sudo systemctl status neurogym.service
```

### Port already in use
```bash
# Check what's using port 8000
sudo netstat -tulpn | grep 8000

# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Check health
```bash
curl http://localhost:8000/health
```

### View active sessions
```bash
curl http://localhost:8000/environments
```

## 📚 Resources

- **Full Documentation**: [README.docker.md](../README.docker.md)
- **Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Example Client**: [examples/api_client_example.py](../examples/api_client_example.py)
- **API Tests**: [tests/test_api.py](../tests/test_api.py)

## 🌐 Network Access

### Local Access
```
http://localhost:8000
```

### Network Access (from other devices)
```
http://[RASPBERRY_PI_IP]:8000
```

Find Raspberry Pi IP:
```bash
hostname -I
```

## 🔒 Security Notes

1. **Firewall**: Limit port 8000 access
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

2. **Production**: Use HTTPS with nginx reverse proxy

3. **Authentication**: Implement auth for production use

## 💡 Tips

- Use interactive docs: http://localhost:8000/docs
- Monitor with: `docker stats`
- Save logs: `docker compose logs > logs.txt`
- Backup config: Copy `docker-compose.yml` and `Dockerfile`

## 📞 Support

- Issues: https://github.com/neurogym/neurogym/issues
- Docs: https://neurogym.github.io/neurogym/latest/
