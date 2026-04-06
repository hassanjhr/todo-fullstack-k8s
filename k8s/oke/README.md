# Oracle OKE Cluster Setup (Always Free)

## Step 1: Create OKE Cluster (OCI Console)

1. Login → **Oracle Cloud Console** → Developer Services → **Kubernetes Clusters (OKE)**
2. Click **Create Cluster** → **Quick Create**
3. Configure:
   - **Name**: `todo-app-cluster`
   - **Kubernetes version**: Latest stable
   - **Node shape**: `VM.Standard.A1.Flex` (ARM Ampere — Always Free)
   - **OCPUs per node**: 2
   - **Memory per node**: 12 GB
   - **Node count**: 2
   - **Node pool name**: `pool1`
4. Click **Next** → **Create Cluster**
5. Wait ~10 minutes for cluster to be Active

## Step 2: Download kubeconfig

```bash
# Install OCI CLI if not installed
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
oci setup config

# Get cluster OCID from OCI Console → OKE → Cluster Details
OKE_CLUSTER_OCID="ocid1.cluster.oc1...."
OCI_REGION="your-region"   # e.g. ap-mumbai-1

oci ce cluster create-kubeconfig \
  --cluster-id $OKE_CLUSTER_OCID \
  --file ~/.kube/oke-config \
  --region $OCI_REGION \
  --token-version 2.0.0

export KUBECONFIG=~/.kube/oke-config
kubectl get nodes   # Should show 2 ARM nodes
```

## Step 3: Store kubeconfig as GitHub Secret

```bash
# Base64-encode the kubeconfig
cat ~/.kube/oke-config | base64 -w 0

# Go to GitHub → repo → Settings → Secrets → Actions → New secret
# Name: OKE_KUBECONFIG
# Value: (paste base64 output)
```

## Step 4: Add all required GitHub Secrets

| Secret | Value |
|--------|-------|
| `OKE_KUBECONFIG` | Base64-encoded `~/.kube/oke-config` |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET_KEY` | JWT signing secret (32+ chars) |
| `OPENAI_API_KEY` | OpenAI API key |

## Step 5: First Deployment (Manual)

```bash
export KUBECONFIG=~/.kube/oke-config

# Install Dapr on OKE
dapr init --kubernetes --wait
dapr status -k

# Deploy app
helm upgrade --install todo-chatbot ./todo-chatbot \
  --set dapr.enabled=true \
  --set backend.image.repository=ghcr.io/hassanjhr/todo-backend \
  --set backend.image.tag=latest \
  --set backend.image.pullPolicy=Always \
  --set frontend.image.repository=ghcr.io/hassanjhr/todo-frontend \
  --set frontend.image.tag=latest \
  --set frontend.image.pullPolicy=Always \
  --set frontend.service.type=LoadBalancer \
  --set env.DATABASE_URL="postgresql+asyncpg://..." \
  --set env.JWT_SECRET_KEY="your-secret" \
  --set env.OPENAI_API_KEY="sk-..."

# Get public URL
kubectl get svc todo-chatbot-frontend
# EXTERNAL-IP = OKE Load Balancer IP
```

After this, subsequent deployments are fully automated via GitHub Actions on `git push origin main`.
