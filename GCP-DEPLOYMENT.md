# GCP Deployment Guide

This guide provides comprehensive instructions for deploying the Portfolio application to Google Cloud Platform (GCP) using a modern, production-ready architecture.

## Architecture Overview

The deployment uses:
- **Cloud Run** for serverless container hosting
- **Artifact Registry** for container image storage
- **Secret Manager** for secure API key management
- **Cloud Load Balancing** for domain mapping and traffic routing
- **Cloud Build** for CI/CD automation

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud CLI**: Install and set up the [gcloud CLI](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install [Docker](https://docs.docker.com/get-docker/) for building containers
4. **Groq API Key**: Get your API key from [Groq](https://console.groq.com/)
5. **Git**: Ensure Git is installed
6. **Domain Name**: (Optional) For custom domain mapping

## Required Google Cloud APIs

Before deployment, enable these APIs in your GCP project:

```bash
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  dns.googleapis.com
```

## Deployment Options

### Option 1: Automated CI/CD with Cloud Build

1. **Connect your GitHub repository to Cloud Build**:
   - Go to Cloud Build > Triggers
   - Connect to GitHub repository
   - Create a new trigger that:
     - Runs on push to `main` branch
     - Uses Cloud Build configuration file from repository (`cloudbuild.yaml`)

2. **Set up secrets in Secret Manager**:
   ```bash
   echo -n "your_groq_api_key" | gcloud secrets create GROQ_API_KEY --replication-policy="automatic" --data-file=-
   ```

3. **Create Artifact Registry repository**:
   ```bash
   gcloud artifacts repositories create web-repo \
     --repository-format=docker \
     --location=us-central1 \
     --description="Portfolio web application repository"
   ```

4. **Push to your repository**:
   - The CI/CD pipeline will automatically build and deploy your application

### Option 2: Manual Deployment Using Scripts

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Portfolio
   ```

2. **Set up environment variables**:
   ```bash
   export PROJECT_ID=$(gcloud config get-value project)
   export REGION="us-central1"  # Choose your preferred region
   ```

3. **Deploy backend**:
   ```bash
   cd personal_assistant
   ./deploy.sh
   ```
   
   The script will:
   - Create the Artifact Registry repository if needed
   - Configure Docker authentication
   - Prompt for your Groq API key and store it in Secret Manager
   - Build and push the backend Docker image
   - Deploy to Cloud Run
   - Output the service URL

4. **Deploy frontend**:
   ```bash
   cd ..
   ./deploy-frontend.sh
   ```
   
   The script will:
   - Prompt for the backend URL from the previous step
   - Build and push the frontend Docker image
   - Deploy to Cloud Run
   - Output the public URL

### Option 3: Manual Deployment (Without Scripts)

For advanced users who want more control over the deployment process:

```bash
# Set up environment variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export REPO=web-repo
export SHORT_SHA=$(date +%Y%m%d-%H%M%S)

# Create Artifact Registry repository
gcloud artifacts repositories create $REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="Portfolio web application repository"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev

# Store secrets
echo -n "your_groq_api_key" | gcloud secrets create GROQ_API_KEY \
  --replication-policy="automatic" \
  --data-file=-

# Deploy backend
cd personal_assistant
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend-api:$SHORT_SHA .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend-api:$SHORT_SHA
gcloud run deploy backend-api \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend-api:$SHORT_SHA \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --update-secrets="GROQ_API_KEY=projects/$PROJECT_ID/secrets/GROQ_API_KEY:latest"

# Get backend URL
BACKEND_URL=$(gcloud run services describe backend-api \
  --platform=managed \
  --region=$REGION \
  --format="value(status.url)")

# Deploy frontend
cd ..
# Create temporary env file for build
echo "REACT_APP_API_BASE=$BACKEND_URL/api" > .env.production
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/frontend-web:$SHORT_SHA .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/frontend-web:$SHORT_SHA
gcloud run deploy frontend-web \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/frontend-web:$SHORT_SHA \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated
```

## First Manual Deploy (Quick-Start)

For a quick first-time deployment:

```bash
# One-time auth & config
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud config set run/region europe-west2

# Deploy backend
./personal_assistant/deploy.sh
# Copy the printed backend URL, then:
./deploy-frontend.sh https://backend-api-XYZ-ew.run.app
```

This will:
1. Authenticate with Google Cloud
2. Set your project and default region
3. Deploy the backend service (with Secret Manager integration)
4. Deploy the frontend service configured to use your backend API

## Setting Up Domain Mapping

For production deployments, you'll want to map a custom domain with proper routing:

1. **Create serverless NEGs**:
   ```bash
   # For frontend
   gcloud compute network-endpoint-groups create frontend-neg \
     --region=$REGION \
     --network-endpoint-type=serverless \
     --cloud-run-service=frontend-web
   
   # For backend
   gcloud compute network-endpoint-groups create backend-neg \
     --region=$REGION \
     --network-endpoint-type=serverless \
     --cloud-run-service=backend-api
   ```

2. **Reserve a static IP address**:
   ```bash
   gcloud compute addresses create portfolio-static-ip \
     --network-tier=PREMIUM \
     --global
   
   # Get the allocated IP
   gcloud compute addresses describe portfolio-static-ip \
     --format="get(address)" \
     --global
   ```

3. **Create SSL certificate**:
   ```bash
   gcloud compute ssl-certificates create portfolio-cert \
     --domains=yourdomain.com \
     --global
   ```

4. **Create backend services**:
   ```bash
   # Frontend backend service
   gcloud compute backend-services create frontend-service \
     --global \
     --load-balancing-scheme=EXTERNAL_MANAGED
   
   gcloud compute backend-services add-backend frontend-service \
     --global \
     --network-endpoint-group=frontend-neg \
     --network-endpoint-group-region=$REGION
   
   # Backend API backend service
   gcloud compute backend-services create backend-service \
     --global \
     --load-balancing-scheme=EXTERNAL_MANAGED
   
   gcloud compute backend-services add-backend backend-service \
     --global \
     --network-endpoint-group=backend-neg \
     --network-endpoint-group-region=$REGION
   ```

5. **Create URL maps and forwarding rules**:
   ```bash
   # Create URL map with path routing
   gcloud compute url-maps create portfolio-lb \
     --default-service=frontend-service
   
   # Add path rule for API
   gcloud compute url-maps add-path-matcher portfolio-lb \
     --path-matcher-name=api-paths \
     --default-service=frontend-service \
     --path-rules="/api/*=backend-service"
   
   # Create HTTPS target proxy
   gcloud compute target-https-proxies create portfolio-https-proxy \
     --url-map=portfolio-lb \
     --ssl-certificates=portfolio-cert
   
   # Create forwarding rule
   gcloud compute forwarding-rules create portfolio-https-rule \
     --load-balancing-scheme=EXTERNAL_MANAGED \
     --network-tier=PREMIUM \
     --address=portfolio-static-ip \
     --target-https-proxy=portfolio-https-proxy \
     --global \
     --ports=443
   ```

6. **Update DNS records**:
   Add A and AAAA records pointing to your static IP address.

## Monitoring and Troubleshooting

- **Cloud Run Logs**: View logs in the Google Cloud Console under Cloud Run services
- **Cloud Build History**: Check build history and logs in Cloud Build
- **Error Reporting**: Monitor application errors
- **Debug Load Balancer**: Use Cloud Logging to debug load balancer issues

## Environment Variables

### Backend Environment Variables:
- `GROQ_API_KEY`: Your Groq API key (stored in Secret Manager)
- `GROQ_MODEL`: LLM model to use (default: llama3-8b-8192)
- `PORT`: Default port (8080 for Cloud Run)

### Frontend Environment Variables:
- `REACT_APP_API_BASE`: URL path for backend API (typically `/api`)
- `PORT`: Default port (8080 for Cloud Run)

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Load Balancing](https://cloud.google.com/load-balancing/docs/https)
- [Cloud Build Documentation](https://cloud.google.com/build/docs) 