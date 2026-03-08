# K3s Deployment with Kustomize

This directory contains the Kubernetes manifests for deploying the `okard-backend` application to a K3s cluster.

## Structure

We use **Kustomize** to manage base configurations and environment-specific overlays.

```text
k3s/
├── base/
│   ├── deployment.yaml      # Main application deployment (FastAPI)
│   ├── kustomization.yaml   # Base kustomize config
│   ├── pvc.yaml             # Persistent volume claim for uploads
│   └── service.yaml         # Internal cluster service
└── overlays/
    └── uat/
        ├── deployment-patch.yaml # Injects UAT secrets & custom image tag
        ├── ingress.yaml          # Exposes the service to the internet
        └── kustomization.yaml    # UAT kustomize config (adds prefix uat-)
```

## How to Deploy (UAT)

1. **Prepare Secrets**
   Copy your local `.env.local` to `.env` inside the `overlays/uat` directory.
   *Note: Do not commit the `.env` file to version control.*
   ```bash
   cp ../../.env.local k3s/overlays/uat/.env
   ```

2. **Review the Configuration**
   Check what Kustomize will generate before applying:
   ```bash
   kubectl kustomize k3s/overlays/uat
   ```

3. **Apply the Configuration**
   Deploy to your K3s cluster:
   ```bash
   kubectl apply -k k3s/overlays/uat
   ```

4. **Verify Deployment**
   ```bash
   kubectl get pods -l app=okard-backend
   kubectl get ingress uat-okard-backend-ingress
   ```

## Notes
- **Ingress**: K3s comes with Traefik by default. The `ingress.yaml` is configured for Traefik. Please update the `host` in `ingress.yaml` to match your actual UAT domain name.
- **Storage**: The `pvc.yaml` requests a standard `5Gi` volume for handling media uploads across container restarts. K3s uses the Local Path Provisioner by default, which works perfectly for single-node setups.
