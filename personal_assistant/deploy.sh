#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
SERVICE_NAME=${SERVICE_NAME:-"backend-api"}
REGION=${REGION:-"europe-west2"}
SECRET_NAME=${SECRET_NAME:-"GROQ_API_KEY"}
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

# Check if the secret exists
if ! gcloud secrets describe ${SECRET_NAME} >/dev/null 2>&1; then
  echo "Secret ${SECRET_NAME} does not exist. Creating it now..."
  
  # Prompt for API key
  read -p "Enter your Groq API key: " GROQ_API_KEY
  
  # Create the secret
  echo "Creating secret ${SECRET_NAME}"
  echo -n "${GROQ_API_KEY}" | gcloud secrets create ${SECRET_NAME} --replication-policy="automatic" --data-file=-
else
  echo "Secret ${SECRET_NAME} already exists."
fi

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
  --allow-unauthenticated \
  --update-secrets="${SECRET_NAME}=projects/${PROJECT_ID}/secrets/${SECRET_NAME}:latest"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format="value(status.url)")

echo "Deployment complete!"
echo "Your service is available at: ${SERVICE_URL}"
echo ""
echo "Update your frontend to use this URL by setting REACT_APP_API_BASE=${SERVICE_URL}/api" 