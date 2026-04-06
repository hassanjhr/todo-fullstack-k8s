# API Contracts: Dapr Building Block Endpoints

**Feature**: `006-full-dapr-oracle-deploy`  
**Date**: 2026-04-06

> These are the Dapr sidecar API calls and binding handler endpoints added or used by this feature.
> Existing REST API (`/api/tasks`, `/api/auth`, etc.) is unchanged.

---

## 1. Dapr Pub/Sub — Publish Task Event

**Direction**: Backend → Dapr sidecar → Kafka

```
POST http://localhost:3500/v1.0/publish/taskpubsub/tasks
Content-Type: application/json

{
  "event_type": "task.created" | "task.updated" | "task.completed",
  "task_id": "string (UUID)",
  "user_id": "string (UUID)",
  "timestamp": "ISO 8601 UTC string"
}

Response: 204 No Content (success)
Response: 403 (component not found / unauthorized)
Response: 500 (Kafka broker unreachable)
```

---

## 2. Dapr State Store — Save/Read Task State

**Direction**: Backend → Dapr sidecar → Redis

```
# Save state
POST http://localhost:3500/v1.0/state/statestore
Content-Type: application/json

[
  {
    "key": "task-{task_id}",
    "value": { "status": "string", "updated_at": "ISO 8601" }
  }
]

Response: 204 No Content

# Read state
GET http://localhost:3500/v1.0/state/statestore/task-{task_id}

Response 200: { "status": "string", "updated_at": "ISO 8601" }
Response 204: (key not found)
```

---

## 3. Dapr Cron Binding — Reminder Handler

**Direction**: Dapr sidecar → Backend (incoming binding trigger)

```
POST /reminder-cron
Content-Type: application/json

{}  (empty body — cron binding sends empty payload)

Response: 200 OK   (binding handled, reminders processed)
Response: 500      (handler error — Dapr will retry)
```

**Backend handler location**: `backend/src/api/routes/dapr_bindings.py`  
**Route registered as**: `POST /reminder-cron` on the FastAPI app

---

## 4. Dapr Secrets — Read Secret

**Direction**: Backend (on startup) → Dapr sidecar → K8s Secret

```
GET http://localhost:3500/v1.0/secrets/k8ssecrets/{secret-name}

# Examples:
GET http://localhost:3500/v1.0/secrets/k8ssecrets/JWT_SECRET_KEY
GET http://localhost:3500/v1.0/secrets/k8ssecrets/DATABASE_URL

Response 200:
{
  "JWT_SECRET_KEY": "the-secret-value"
}

Response 403: (app not authorized for this secret)
Response 404: (secret not found)
```

> **Note**: `k8ssecrets` reads from the K8s Secret that shares the same name as the key requested, within the same namespace as the Dapr sidecar.

---

## 5. Dapr Service Invocation — Frontend → Backend

**Direction**: Frontend (via its Dapr sidecar) → Backend Dapr sidecar → Backend

```
# Instead of:
GET http://todo-backend-svc:8000/api/tasks

# Frontend calls its local Dapr sidecar:
GET http://localhost:3500/v1.0/invoke/todo-backend/method/api/tasks
Authorization: Bearer {jwt_token}

# Dapr handles: service discovery, mTLS, retries, load balancing
# Backend receives the request on its normal route: GET /api/tasks
```

**All existing frontend API calls are remapped** from `http://localhost:8000/...` to `http://localhost:3500/v1.0/invoke/todo-backend/method/...` when running on K8s with Dapr.

**Configuration**: `NEXT_PUBLIC_DAPR_ENABLED=true` env var switches the API base URL in the frontend.

---

## 6. CI/CD — GitHub Actions Inputs/Outputs

**Workflow trigger**:
```yaml
on:
  push:
    branches: [main]
```

**Required GitHub Secrets**:

| Secret | Used In | Description |
|--------|---------|-------------|
| `OKE_KUBECONFIG` | deploy job | Base64-encoded OKE kubeconfig |
| `DATABASE_URL` | deploy job | Neon PostgreSQL URL |
| `JWT_SECRET_KEY` | deploy job | JWT signing key |
| `OPENAI_API_KEY` | deploy job | OpenAI key |
| `GHCR_TOKEN` | build job | GitHub PAT with `write:packages` (or use `GITHUB_TOKEN`) |

**Workflow outputs** (passed between jobs):
```
backend_image: ghcr.io/hassanjhr/todo-backend:sha-{commit}
frontend_image: ghcr.io/hassanjhr/todo-frontend:sha-{commit}
```
