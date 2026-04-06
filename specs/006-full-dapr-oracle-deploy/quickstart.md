# Quickstart: Full Dapr Deployment

**Feature**: `006-full-dapr-oracle-deploy`

---

## Part B — Minikube (Local)

### Prerequisites
- Minikube installed and running: `minikube start`
- Dapr CLI 1.17.x installed
- Helm 3.x installed
- kubectl configured for Minikube

### Step 1: Install Dapr on Minikube
```bash
dapr init --kubernetes --wait
# Verify: dapr status -k
```

### Step 2: Build images inside Minikube
```bash
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

### Step 3: Create K8s Secret
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=jwt-secret=YOUR_JWT_SECRET \
  --from-literal=database-url="postgresql+asyncpg://..." \
  --from-literal=kafka-brokers="kafka:9092"
```

### Step 4: Deploy with Helm
```bash
helm upgrade --install todo-chatbot ./todo-chatbot \
  --set dapr.enabled=true \
  --set env.DATABASE_URL="postgresql+asyncpg://..." \
  --set env.JWT_SECRET_KEY="your-secret" \
  --set env.OPENAI_API_KEY="sk-..."
```

### Step 5: Verify all Dapr components
```bash
kubectl get components          # Should show: taskpubsub, statestore, reminder-cron, k8ssecrets
dapr dashboard -k               # Open Dapr dashboard
kubectl get pods                # All pods Running with 2/2 (app + dapr sidecar)
```

### Step 6: Test
```bash
# Get Minikube IP
minikube service todo-chatbot-frontend --url

# Verify Kafka topic after creating a task
kubectl exec deploy/todo-chatbot-kafka -- \
  kafka-topics --bootstrap-server localhost:9092 --list
# Expected output: tasks
```

---

## Part C — Oracle OKE (Cloud)

### Prerequisites
- Oracle Cloud account (Always Free tier)
- OCI CLI installed and configured (`oci setup config`)
- kubectl, Helm, Dapr CLI installed

### Step 1: Provision OKE Cluster (one-time)
```bash
# Via OCI Console (recommended for first time):
# OCI → Developer Services → Kubernetes Clusters (OKE)
# → Create Cluster → Quick Create
# → Shape: VM.Standard.A1.Flex (ARM), 2 OCPU, 12GB per node, 2 nodes
# → Download kubeconfig

# Configure kubectl
export KUBECONFIG=~/.kube/oke-config
kubectl get nodes   # Should show 2 ARM nodes
```

### Step 2: Install Dapr on OKE
```bash
dapr init --kubernetes --wait
dapr status -k   # All Dapr system services should be Running
```

### Step 3: Create K8s Secrets on OKE
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=jwt-secret=YOUR_JWT_SECRET \
  --from-literal=database-url="postgresql+asyncpg://..." \
  --from-literal=kafka-brokers="kafka:9092"
```

### Step 4: Deploy via Helm
```bash
helm upgrade --install todo-chatbot ./todo-chatbot \
  --set dapr.enabled=true \
  --set backend.image.repository=ghcr.io/hassanjhr/todo-backend \
  --set backend.image.tag=latest \
  --set backend.image.pullPolicy=Always \
  --set frontend.image.repository=ghcr.io/hassanjhr/todo-frontend \
  --set frontend.image.tag=latest \
  --set frontend.image.pullPolicy=Always \
  --set env.DATABASE_URL="postgresql+asyncpg://..." \
  --set env.JWT_SECRET_KEY="your-secret" \
  --set env.OPENAI_API_KEY="sk-..."
```

### Step 5: Get public URL
```bash
kubectl get svc todo-chatbot-frontend
# EXTERNAL-IP column shows OKE Load Balancer IP
# Open http://<EXTERNAL-IP>:3000 in browser
```

---

## CI/CD — Automated Deployment

### Step 1: Add GitHub Secrets
Go to your repo → Settings → Secrets → Actions:
```
OKE_KUBECONFIG   = $(cat ~/.kube/oke-config | base64 -w 0)
DATABASE_URL     = postgresql+asyncpg://...
JWT_SECRET_KEY   = your-jwt-secret
OPENAI_API_KEY   = sk-...
```

### Step 2: Push to main
```bash
git push origin main
# GitHub Actions automatically:
# 1. Builds backend + frontend Docker images
# 2. Pushes to ghcr.io/hassanjhr/...
# 3. Runs helm upgrade on OKE
# 4. Verifies rollout status
```

### Step 3: Monitor deployment
```
GitHub → Actions → deploy.yml run → View logs
```

---

## Monitoring

### Install kube-prometheus-stack (one-time on OKE)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f k8s/monitoring/prometheus-values.yaml
```

### Access Grafana
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Open http://localhost:3000 (admin / prom-operator)
# Import Dapr dashboard: ID 14746
```

---

## Verification Checklist

- [ ] `kubectl get components` shows 4 Dapr components (taskpubsub, statestore, reminder-cron, k8ssecrets)
- [ ] `kubectl get pods` shows all pods `2/2 Running` (app + sidecar)
- [ ] Task creation → Kafka topic `tasks` receives event within 5 seconds
- [ ] Cron binding fires every 5 minutes → `/reminder-cron` handler called
- [ ] Backend secrets loaded via Dapr (no plaintext in pod env: `kubectl exec ... env`)
- [ ] Frontend → Backend calls routed via Dapr service invocation (check Dapr dashboard traces)
- [ ] Public URL accessible on OKE Load Balancer IP
- [ ] CI/CD push to main → deployment completes in < 15 minutes
- [ ] Grafana dashboard shows pod metrics and Dapr sidecar metrics
