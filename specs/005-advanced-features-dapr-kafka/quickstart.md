# Quickstart: Advanced Task Management with Distributed Architecture

**Feature**: 005-advanced-features-dapr-kafka
**Date**: 2026-03-31

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker + Docker Compose | Latest | Kafka + Zookeeper |
| Dapr CLI | 1.13+ | Distributed runtime |
| kubectl | 1.28+ | Kubernetes (production only) |
| Helm | 3.14+ | Kubernetes deployment |

---

## 1. Install Dapr CLI (local dev)

```bash
# macOS / Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr (self-hosted mode)
dapr init
```

---

## 2. Start Kafka (Docker Compose)

```yaml
# docker-compose.kafka.yml (place in project root)
version: "3.9"
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    depends_on: [zookeeper]
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
```

```bash
docker compose -f docker-compose.kafka.yml up -d
```

---

## 3. Configure Dapr Components (Local)

Create `dapr/components/` directory in the project root:

```bash
mkdir -p dapr/components
```

**`dapr/components/pubsub-kafka.yaml`**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "todo-chatbot"
  - name: authType
    value: "none"
```

**`dapr/components/secretstore-local.yaml`**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: localsecrets
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: "./dapr/secrets.json"
  - name: nestedSeparator
    value: ":"
```

**`dapr/secrets.json`** (gitignored):
```json
{
  "jwt-secret": "your-jwt-secret-here",
  "database-url": "postgresql+asyncpg://...",
  "kafka-brokers": "localhost:9092"
}
```

> Add `dapr/secrets.json` to `.gitignore`

---

## 4. Run Database Migrations

```bash
cd backend

# Run all new migrations
python scripts/run_migrations.py

# Migrations to run (in order):
# 003_extend_tasks_table.sql     — adds priority, due_date, recurrence fields
# 004_create_reminders_table.sql — reminders
# 005_create_tags_table.sql      — tags (user-scoped)
# 006_create_task_tags_table.sql — task_tags junction
# 007_create_recurrence_series_table.sql — recurrence_series
```

---

## 5. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt

# New packages added:
# python-dateutil   — RRULE parsing
# apscheduler       — Background reminder scheduler
# dapr              — Dapr Python SDK
```

---

## 6. Run Backend with Dapr Sidecar

```bash
cd backend

# Run with Dapr sidecar (self-hosted)
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. Run Frontend

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

---

## 8. Verify Dapr + Kafka Integration

```bash
# Check Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Publish a test event manually
curl -X POST http://localhost:3500/v1.0/publish/taskpubsub/tasks \
  -H "Content-Type: application/json" \
  -d '{"event_type": "task.created", "task_id": "test-123", "user_id": "user-456"}'

# List Kafka topics
docker exec -it $(docker ps -q --filter ancestor=confluentinc/cp-kafka) \
  kafka-topics --bootstrap-server localhost:9092 --list
```

---

## 9. Kubernetes Production Deployment

```bash
# Install Dapr on cluster
dapr init --kubernetes --wait

# Apply Dapr components
kubectl apply -f todo-chatbot/dapr/components/

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=jwt-secret="$(openssl rand -hex 32)" \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=kafka-brokers="$KAFKA_BROKERS"

# Deploy with Helm
helm upgrade --install todo-chatbot ./todo-chatbot \
  --set dapr.enabled=true \
  --set kafka.enabled=true \
  --namespace default
```

---

## Environment Variables Reference

### Backend `.env` (local dev, no Dapr)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET=your-secret-here
CORS_ORIGINS=http://localhost:3000
DAPR_ENABLED=false          # Set true when running with Dapr sidecar
DAPR_HTTP_PORT=3500
DAPR_PUBSUB_NAME=taskpubsub
REMINDER_POLL_INTERVAL=300  # Seconds between reminder checks (default: 300)
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `dapr: command not found` | Install Dapr CLI (step 1) |
| Kafka connection refused | Start Docker Compose (step 2) |
| RRULE parse error | Validate RRULE string at [rrule.js](https://jakubroztocil.github.io/rrule/) |
| Reminder not firing | Check APScheduler logs; verify `trigger_at` is in UTC |
| Dapr sidecar 500 on publish | Check `dapr/components/pubsub-kafka.yaml` broker address |
