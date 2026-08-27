<div align="center">

<img src="https://img.shields.io/badge/FastAPI-2.0.0-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
<img src="https://img.shields.io/badge/Three.js-3D-black?style=for-the-badge&logo=threedotjs&logoColor=white" alt="Three.js"/>
<img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
<img src="https://img.shields.io/badge/AWS-Free_Tier-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS"/>
<img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
<img src="https://img.shields.io/badge/MQTT-AWS_IoT_Core-569A31?style=for-the-badge&logo=mqtt&logoColor=white" alt="MQTT"/>

# 🌐 IoT Cloud Shadow — Digital Twin for Real-Time Monitoring

**A production-grade IoT platform featuring a live 3D Digital Twin Dashboard, bi-directional remote actuation, AI-powered threshold alert engine, MQTT hardware ingestion, and a full AWS cloud deployment on the Free Tier.**

[🔴 Live Demo](http://13.62.228.155:5173) · [📖 API Docs](http://13.62.228.155:8000/docs) · [📊 Grafana](http://13.62.228.155:3000) · [🐛 Report Bug](https://github.com/khallaftaha-cmyk/IoT-Cloud-Shadow-A-Digital-Twin-for-Real-time-Monitoring/issues)

</div>

---

## 📖 Table of Contents

- [What Is a Digital Twin?](#-what-is-a-digital-twin)
- [System Architecture](#-system-architecture)
- [Feature Overview](#-feature-overview)
- [Project Structure](#-project-structure)
- [Local Development Setup](#-local-development-setup)
- [Environment Variables](#-environment-variables)
- [AWS Cloud Deployment (Free Tier)](#-aws-cloud-deployment-free-tier)
- [API Reference](#-api-reference)
- [Testing the System](#-testing-the-system)
- [Grafana Dashboard Setup](#-grafana-dashboard-setup)
- [Connecting Real IoT Hardware](#-connecting-real-iot-hardware)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Contributing](#-contributing)

---

## 🤖 What Is a Digital Twin?

A **Digital Twin** is a real-time virtual replica of a physical device. Every sensor reading from your hardware is mirrored to the cloud, where it can be visualized, analyzed, and acted upon — all without touching the physical device.

This project builds a complete Digital Twin system:
- A **FastAPI backend** ingests telemetry over REST or MQTT.
- An **in-memory + Redis state store** maintains the current device state.
- **WebSockets** broadcast every state change to all connected dashboards instantly.
- A **3D React dashboard** renders the twin with dynamic animations reflecting real sensor values.
- **Threshold rules** automatically detect anomalies and send back **actuation commands** to the device.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        AWS Cloud (eu-north-1)                      │
│                                                                    │
│  ┌─────────────┐    REST/MQTT     ┌───────────────────────────┐   │
│  │  IoT Device │ ──────────────► │   FastAPI Backend (EC2)   │   │
│  │ (ESP32/RPi/ │                 │   - Auth (JWT)             │   │
│  │  Simulator) │ ◄────────────── │   - Twin State (Redis)     │   │
│  └─────────────┘  Actuation Cmd  │   - Alert Engine           │   │
│                                  │   - WebSocket Broadcaster  │   │
│  ┌─────────────┐                 └───────────┬───────────────┘   │
│  │ AWS IoT Core│ ──────MQTT/TLS──────────────►│                   │
│  │  Broker     │                             │                   │
│  └─────────────┘                 ┌───────────▼───────────────┐   │
│                                  │  AWS RDS PostgreSQL 16     │   │
│  ┌─────────────┐  WebSocket      │  - Sensor Readings         │   │
│  │  3D React   │ ◄─────────────  │  - Alert Rules & Alerts    │   │
│  │  Dashboard  │                 │  - Actuation Commands      │   │
│  └─────────────┘                 │  - Users                   │   │
│                                  └───────────────────────────┘   │
│  ┌─────────────┐                                                  │
│  │   Grafana   │ ──────PostgreSQL direct────────────────────────► │
│  │  Analytics  │                                                  │
│  └─────────────┘                                                  │
└────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI (Python 3.11) | REST API, WebSocket server, business logic |
| **Database** | PostgreSQL 16 (AWS RDS) | Persistent sensor readings, alerts, commands |
| **State Cache** | Redis 7 | Fast in-memory digital twin state |
| **MQTT Broker** | AWS IoT Core / Mosquitto | Hardware telemetry ingestion over TLS |
| **Frontend** | React 18 + Three.js + Vite | 3D visualization dashboard |
| **Analytics** | Grafana 10 | Time-series dashboards and alerting |
| **Auth** | JWT (python-jose) + Argon2 | Secure API authentication |
| **Deployment** | Docker Compose + AWS EC2 | Container orchestration |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

---

## ✨ Feature Overview

### 🌐 3D Visual Digital Twin Dashboard
A live React + Three.js web application that renders a dynamic 3D device model:
- **Color-coded core**: Cyan (nominal) → Orange (warning) → Red (critical) based on live temperature
- **Rotation speed** scales with sensor values in real time
- **WebSocket live feed**: Auto-reconnects and updates instantly on every telemetry push
- **Actuation control panel**: Send remote device commands (Cooling ON, Emergency Shutdown) directly from the browser

### ⚡ Real-Time WebSocket Streaming
All connected dashboards receive pushed updates the instant any telemetry arrives — no polling required:
```
Events: twin_update | alert_triggered | actuator_command | actuator_status_update
```

### 📡 Multi-Sensor Telemetry
Each sensor reading supports:
- `temperature` (°C)
- `humidity` (%)
- `pressure` (hPa)
- `battery_level` (%)
- `extra_metadata` (arbitrary JSON for firmware version, location, etc.)

### 🚨 Threshold Rules Engine
Define custom alert rules per device and metric:
- Operators: `>`, `<`, `>=`, `<=`, `==`
- Severities: `warning`, `critical`
- Alerts are persisted to PostgreSQL and broadcast over WebSockets in real time

### 🕹️ Bi-Directional Actuation
Send remote control commands to physical or simulated devices:
- Supported commands: `COOLING_ON`, `HEATING_OFF`, `EMERGENCY_SHUTDOWN`, or any custom command
- Edge devices poll `GET /actuate/pending/{device_id}` for pending commands
- Full lifecycle: `pending` → `acknowledged` → `executed` / `failed`

### 🔐 Secure JWT Authentication
- User registration + Argon2-hashed passwords
- OAuth2 password flow returning short-lived JWT tokens
- All protected endpoints require `Authorization: Bearer <token>` header

---

## 📁 Project Structure

```
IoT monitor/
├── app/
│   ├── main.py              # FastAPI app, CORS, MQTT lifespan, router registration
│   ├── config.py            # Pydantic Settings (env var loading)
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── models.py            # ORM models: SensorReading, User, ActuatorCommand, AlertRule, Alert
│   ├── schemas.py           # Pydantic I/O schemas for all endpoints
│   ├── utils.py             # Password hashing utilities
│   ├── routers/
│   │   ├── auth.py          # POST /login
│   │   ├── user.py          # POST /users/
│   │   ├── twin.py          # POST /update-twin, GET /twin-status, GET /devices, WS /ws/twin-status
│   │   ├── actuator.py      # POST /actuate/, GET /actuate/history, PATCH /actuate/{id}/status
│   │   └── alerts.py        # POST /alerts/rules, GET /alerts, PATCH /alerts/{id}/acknowledge
│   └── services/
│       ├── alert_engine.py  # Threshold evaluation: checks rules, creates Alert records
│       ├── mqtt_bridge.py   # Paho MQTT client: connects to AWS IoT Core over TLS
│       └── virtual_sensor.py# Sensor simulator: generates multi-sensor telemetry
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Main dashboard: WS client, telemetry cards, actuation, alerts
│   │   ├── DigitalTwin3D.jsx# Three.js 3D viewport component
│   │   └── index.css        # Dark glassmorphism design system
│   ├── Dockerfile           # Multi-stage: Node build → Nginx serve
│   ├── nginx.conf           # Nginx proxy config for /api and /ws routes
│   └── vite.config.js       # Vite dev server with API proxy
├── tests/
│   ├── conf_test.py         # Pytest fixtures: test DB, test client, auth
│   ├── test_auth.py         # Authentication tests
│   ├── test_twin.py         # Telemetry and twin state tests
│   ├── test_actuator.py     # Actuation command lifecycle tests
│   └── test_alerts.py       # Alert rule creation and threshold evaluation tests
├── grafana/
│   ├── dashboards/
│   │   └── digital_twin.json# Pre-built Grafana dashboard (import directly)
│   └── provisioning/        # Grafana auto-provisioning config
├── mosquitto/
│   └── mosquitto.conf       # Local Mosquitto broker config (port 1883 + 9001 WS)
├── certs/                   # AWS IoT Core X.509 TLS certificates (gitignored)
├── Dockerfile               # Multi-stage API build: Python builder → slim runtime, non-root user
├── docker-compose.yml       # Full stack: API + Redis + MQTT + Grafana + Frontend
├── requirements.txt         # Python dependencies
└── .github/
    └── workflows/
        └── ci_cd.yml        # GitHub Actions: test → build → deploy to EC2
```

---

## 🚀 Local Development Setup

### Prerequisites
- **Python 3.11+**
- **Docker Desktop** (for running PostgreSQL, Redis, etc. locally)
- **Node.js 20+** (for frontend development)
- **Git**

### Step 1: Clone the Repository
```bash
git clone https://github.com/khallaftaha-cmyk/IoT-Cloud-Shadow-A-Digital-Twin-for-Real-time-Monitoring.git
cd "IoT-Cloud-Shadow-A-Digital-Twin-for-Real-time-Monitoring"
```

### Step 2: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your local values (see Environment Variables section below)
```

### Step 3: Start All Services with Docker Compose
```bash
docker compose up -d --build
```

This starts:
| Service | URL | Notes |
|---|---|---|
| FastAPI API | http://localhost:8000 | REST + WebSocket backend |
| API Swagger Docs | http://localhost:8000/docs | Interactive API explorer |
| 3D Digital Twin UI | http://localhost:5173 | React frontend |
| Grafana | http://localhost:3000 | Analytics dashboards |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Twin state cache |
| MQTT Broker | localhost:1883 | IoT device ingestion |

### Step 4: (Optional) Run the Virtual Sensor Simulator
In a new terminal, run the built-in multi-sensor simulator:
```bash
pip install -r requirements.txt
python -m app.services.virtual_sensor
```
This generates continuous telemetry (temperature, humidity, pressure, battery) every 2 seconds and POSTs it to your local API.

### Step 5: (Optional) Backend Development Without Docker
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔑 Environment Variables

Create a `.env` file at the project root. Copy the template below:

```env
# ── Database (PostgreSQL) ──────────────────────────────────────────
DATABASE_HOSTNAME=localhost          # Use RDS endpoint for cloud deployment
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_db_password
DATABASE_NAME=fastapi

# ── JWT Authentication ─────────────────────────────────────────────
SECRET_KEY=your_secret_key_here      # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── Optional: LLM Monitor ─────────────────────────────────────────
ANTHROPIC_API_KEY=                   # Leave empty — core API works without it

# ── Grafana ────────────────────────────────────────────────────────
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password

# ── Redis (Twin State Cache) ───────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── MQTT Broker ────────────────────────────────────────────────────
# For local Mosquitto:
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883

# For AWS IoT Core (production):
# MQTT_BROKER_HOST=your-endpoint-ats.iot.eu-north-1.amazonaws.com
# MQTT_BROKER_PORT=8883
```

> ⚠️ **Never commit your `.env` file.** It is already in `.gitignore`. Store secrets in AWS Secrets Manager or GitHub Actions secrets for production.

---

## ☁️ AWS Cloud Deployment (Free Tier)

This project is fully deployable at **$0.00/month** using the AWS 12-Month Free Tier.

### AWS Services Used

| Service | Free Tier Allowance | Cost |
|---|---|---|
| **EC2 `t3.micro`** | 750 hours/month | $0 |
| **RDS PostgreSQL `db.t3.micro`** | 750 hours + 20GB storage | $0 |
| **AWS IoT Core** | 500K messages/month | $0 |
| **ECR** | 500MB private storage | $0 |

### Phase 1: AWS RDS PostgreSQL Setup

1. Go to **AWS Console → RDS → Create database**
2. Select **PostgreSQL 15+**, template **Free tier**, instance type **`db.t3.micro`**
3. Set a strong master password
4. Enable **Public access** and open port `5432` in the Security Group
5. Note the **Endpoint URL** (e.g. `your-db.xxxx.eu-north-1.rds.amazonaws.com`)
6. Update `.env`: `DATABASE_HOSTNAME=your-db.xxxx.eu-north-1.rds.amazonaws.com`

### Phase 2: AWS IoT Core Setup

1. Go to **AWS IoT Core → All devices → Things → Create single thing**
2. Name it `sensor_01`, auto-generate certificates
3. Attach a policy with `iot:Connect`, `iot:Publish`, `iot:Subscribe`, `iot:Receive` on `Resource: "*"`
4. Download the **device certificate**, **private key**, and **Amazon Root CA 1**
5. Place them in `certs/` directory
6. Copy your **Device data endpoint** from **Settings** (e.g. `aXXXXX-ats.iot.eu-north-1.amazonaws.com`)

### Phase 3: EC2 Server Deployment

```bash
# 1. Launch Ubuntu 24.04 t3.micro with key pair saved as iot-twin-key.pem

# 2. Install Docker on EC2
ssh -i iot-twin-key.pem ubuntu@<EC2_IP>
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu

# 3. Clone and deploy (from your local machine)
ssh -i iot-twin-key.pem ubuntu@<EC2_IP> "git clone https://github.com/khallaftaha-cmyk/IoT-Cloud-Shadow-A-Digital-Twin-for-Real-time-Monitoring.git iot-monitor"

# 4. Upload credentials
scp -i iot-twin-key.pem -r ./certs ubuntu@<EC2_IP>:~/iot-monitor/
scp -i iot-twin-key.pem .env ubuntu@<EC2_IP>:~/iot-monitor/.env

# 5. Start all services
ssh -i iot-twin-key.pem ubuntu@<EC2_IP> "cd ~/iot-monitor && docker compose up -d --build"
```

### EC2 Security Group Port Rules

Open these inbound ports in your EC2 Security Group:

| Port | Protocol | Service |
|---|---|---|
| 22 | TCP | SSH |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |
| 8000 | TCP | FastAPI API |
| 3000 | TCP | Grafana |
| 5173 | TCP | 3D Frontend |
| 1883 | TCP | MQTT (local) |

---

## 📡 API Reference

### Authentication

All endpoints except `/health`, `/users/`, `/login`, and `GET /actuate/pending/{device_id}` require a JWT bearer token.

```bash
# 1. Register
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# 2. Login
curl -X POST http://localhost:8000/login \
  -d "username=you@example.com&password=yourpassword"
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Use token
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/twin-status
```

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check |
| `POST` | `/users/` | Register a new user |
| `POST` | `/login` | Authenticate and get JWT token |
| `POST` | `/update-twin` | Push sensor telemetry (updates twin + DB + triggers alert engine) |
| `GET` | `/twin-status` | Get current state of all device twins |
| `GET` | `/devices` | List all registered devices |
| `GET` | `/history` | Fetch telemetry history (query params: `limit`, `device_id`) |
| `WS` | `/ws/twin-status` | WebSocket stream for real-time twin updates and alerts |

### Alert Engine Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/alerts/rules` | Create a threshold rule |
| `GET` | `/alerts/rules` | List all active rules |
| `DELETE` | `/alerts/rules/{id}` | Delete a rule |
| `GET` | `/alerts` | Query triggered alerts (filters: `device_id`, `severity`, `acknowledged`) |
| `PATCH` | `/alerts/{id}/acknowledge` | Acknowledge an alert |

### Actuation Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/actuate/` | Issue a remote command to a device |
| `GET` | `/actuate/history` | Query command history |
| `GET` | `/actuate/pending/{device_id}` | Poll pending commands (for edge devices) |
| `PATCH` | `/actuate/{id}/status` | Update command execution status |

---

## 🧪 Testing the System

### Option 1: Swagger UI (No coding required)
1. Open **[http://localhost:8000/docs](http://localhost:8000/docs)** (or your EC2 IP)
2. Use `POST /users/` to register → `POST /login` to get a token
3. Click 🔒 **Authorize** → paste `Bearer <your_token>`
4. Try `POST /update-twin` with the sample payload below

**Sample Telemetry Payload:**
```json
{
  "device_id": "sensor_01",
  "temperature": 35.5,
  "humidity": 30.0,
  "pressure": 1010.0,
  "battery_level": 85.0,
  "status": "online",
  "timestamp": "2026-08-27T15:00:00"
}
```
> Sending temperature > 30 will trigger a `CRITICAL` alert if you created a rule for it!

### Option 2: Run the Virtual Sensor Simulator
```bash
python -m app.services.virtual_sensor
```
Streams live multi-sensor data every 2 seconds. Watch the 3D dashboard update in real time!

### Option 3: Run Automated Tests
```bash
pytest tests/ -v
```

Tests cover:
- **Auth**: Registration, login, token validation
- **Twin**: Telemetry ingestion, multi-sensor fields, device listing
- **Alerts**: Rule creation, threshold breach evaluation, acknowledgment
- **Actuation**: Command issuance, polling, status updates

---

## 📊 Grafana Dashboard Setup

### 1. Login to Grafana
Open **[http://localhost:3000](http://localhost:3000)** → Login with `admin` / `<GRAFANA_PASSWORD>`

### 2. Add PostgreSQL Data Source
1. Click **⚙️ Connections → Data sources → Add data source → PostgreSQL**
2. Configure:
   - **Host**: `localhost:5432` (or your RDS endpoint)
   - **Database**: `fastapi`
   - **User**: `postgres`
   - **Password**: your database password
   - **TLS/SSL Mode**: `disable` (for local), or configure for RDS
3. Click **Save & test** → should show ✅ `Database Connection OK`

### 3. Import the Pre-Built Dashboard
1. Click **➕ Dashboards → Import**
2. Upload `grafana/dashboards/digital_twin.json`
3. Select your PostgreSQL data source → Click **Import**

### Dashboard Panels
| Panel | Query | Description |
|---|---|---|
| **Temperature Over Time** | `SELECT timestamp, temperature FROM "Sensor_Data"` | Multi-device time-series |
| **Humidity & Pressure** | `SELECT timestamp, humidity FROM "Sensor_Data"` | Environmental metrics |
| **Battery Level Gauge** | `SELECT battery_level FROM "Sensor_Data" LIMIT 1` | Real-time gauge |
| **Latest Temperature Gauge** | Latest reading with red/orange/green thresholds | Color-coded status |
| **Recent Triggered Alerts** | `SELECT * FROM alerts ORDER BY triggered_at DESC` | Live alert table |
| **Actuation Commands Log** | `SELECT * FROM actuator_commands ORDER BY issued_at DESC` | Command history |

---

## 🔌 Connecting Real IoT Hardware

### MQTT Protocol (AWS IoT Core TLS)

Any device that can speak MQTT (ESP32, Raspberry Pi, Arduino, etc.) can publish telemetry directly to AWS IoT Core.

**Topic format:** `iot/<device_id>/telemetry`

**Payload format (JSON):**
```json
{
  "device_id": "esp32_lab_01",
  "temperature": 24.5,
  "humidity": 55.0,
  "pressure": 1013.2,
  "battery_level": 78.0,
  "status": "online",
  "timestamp": "2026-08-27T15:00:00"
}
```

**ESP32 / Arduino (using PubSubClient):**
```cpp
// Use AWS IoT Core endpoint and your X.509 certificates
// Topic: iot/esp32_lab_01/telemetry
mqttClient.publish("iot/esp32_lab_01/telemetry", payload);
```

**Python (paho-mqtt):**
```python
import paho.mqtt.client as mqtt
import ssl, json

client = mqtt.Client(client_id="my_device")
client.tls_set(
    ca_certs="certs/AmazonRootCA1.pem",
    certfile="certs/device.pem.crt",
    keyfile="certs/private.pem.key",
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.connect("your-endpoint-ats.iot.eu-north-1.amazonaws.com", 8883)
client.publish("iot/my_device/telemetry", json.dumps({
    "device_id": "my_device", "temperature": 22.0, ...
}))
```

### Polling Actuation Commands from Edge Device
Your physical device can periodically poll for pending commands (no MQTT subscription needed):
```bash
# Polling endpoint — no authentication required
curl http://your-api:8000/actuate/pending/my_device_id

# Then acknowledge execution:
curl -X PATCH http://your-api:8000/actuate/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "executed"}'
```

---

## ⚙️ CI/CD Pipeline

The project uses **GitHub Actions** for a 3-stage automated pipeline:

```
[Push to main]
      │
      ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  1. Test    │────►│  2. Build & Push │────►│  3. Deploy      │
│  pytest     │     │  docker build    │     │  ssh + docker   │
│  PostgreSQL │     │  ECR push        │     │  compose pull   │
│  (container)│     │  latest + SHA    │     │  EC2 server     │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

### Required GitHub Secrets

Go to **GitHub → Repository → Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | `eu-north-1` |
| `ECR_REPOSITORY_URI` | `<account_id>.dkr.ecr.eu-north-1.amazonaws.com/iot-digital-twin-api` |
| `EC2_HOST` | Your EC2 public IP (e.g. `13.62.228.155`) |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Contents of your `iot-twin-key.pem` file |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

All PRs must pass the automated test suite (`pytest tests/ -v`) before merging.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using FastAPI, React, Three.js, PostgreSQL, AWS, and Docker

⭐ Star this repo if you found it useful!

</div>
