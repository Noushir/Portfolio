#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
SERVICE_NAME=${SERVICE_NAME:-"frontend-web"}
REGION=${REGION:-"europe-west2"}
BACKEND_URL=${BACKEND_URL:-"https://backend-api-xxxxx-xx.a.run.app"}
SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
IMAGE_TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/web-repo/${SERVICE_NAME}:${SHORT_SHA}

# Check if the user is logged into gcloud
if ! gcloud auth print-identity-token >/dev/null 2>&1; then
  echo "Not logged into gcloud. Please run 'gcloud auth login' first."
  exit 1
fi

# Ensure Artifact Registry repository exists
if ! gcloud artifacts repositories describe web-repo --location=${REGION} >/dev/null 2>&1; then
  echo "Creating Artifact Registry repository 'web-repo' in ${REGION}..."
  gcloud artifacts repositories create web-repo \
    --repository-format=docker \
    --location=${REGION} \
    --description="Portfolio web application repository"
fi

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Check if BACKEND_URL is provided
if [ "$BACKEND_URL" = "https://backend-api-xxxxx-xx.a.run.app" ]; then
  echo "Warning: You are using a placeholder backend URL."
  read -p "Enter the actual backend service URL (leave empty to continue with placeholder): " NEW_BACKEND_URL
  if [ ! -z "$NEW_BACKEND_URL" ]; then
    BACKEND_URL=$NEW_BACKEND_URL
  fi
fi

# Create a temporary .env file for the build
echo "REACT_APP_API_BASE=${BACKEND_URL}/api" > .env.production
echo "Created temporary .env.production with REACT_APP_API_BASE=${BACKEND_URL}/api"

# Build the Docker image
echo "Building Docker image: ${IMAGE_TAG}"
docker build -t ${IMAGE_TAG} .

# Push to Artifact Registry
echo "Pushing image to Artifact Registry"
docker push ${IMAGE_TAG}

# Deploy to Cloud Run
echo "Deploying to Cloud Run in ${REGION}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format="value(status.url)")

# Clean up temporary environment file
rm .env.production

echo "Deployment complete!"
echo "Your frontend is available at: ${SERVICE_URL}"
echo "It is configured to use the backend at: ${BACKEND_URL}" 