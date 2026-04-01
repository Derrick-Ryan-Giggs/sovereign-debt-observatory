#!/bin/bash

set -e

PROJECT_ID="sovereign-debt-observatory"
REGION="us-central1"
SA_NAME="sovereign-debt-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_PATH="$(pwd)/credentials/sovereign-debt-sa-key.json"

if [ -z "${BILLING_ACCOUNT}" ]; then
    echo "Error: BILLING_ACCOUNT environment variable is not set."
    echo "Usage: BILLING_ACCOUNT=your-billing-id bash scripts/setup_gcp.sh"
    exit 1
fi

echo "Creating GCP project..."
gcloud projects create ${PROJECT_ID} --name="Sovereign Debt Observatory"

echo "Setting active project..."
gcloud config set project ${PROJECT_ID}

echo "Linking billing account..."
gcloud billing projects link ${PROJECT_ID} --billing-account=${BILLING_ACCOUNT}

echo "Enabling required APIs..."
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

echo "Creating service account..."
gcloud iam service-accounts create ${SA_NAME}     --display-name="Sovereign Debt Observatory SA"

echo "Granting IAM roles..."
gcloud projects add-iam-policy-binding ${PROJECT_ID}     --member="serviceAccount:${SA_EMAIL}"     --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID}     --member="serviceAccount:${SA_EMAIL}"     --role="roles/storage.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID}     --member="serviceAccount:${SA_EMAIL}"     --role="roles/iam.serviceAccountTokenCreator"

echo "Creating credentials directory..."
mkdir -p $(pwd)/credentials

echo "Downloading service account key..."
gcloud iam service-accounts keys create ${KEY_PATH}     --iam-account=${SA_EMAIL}

echo ""
echo "Setup complete."
echo "Project  : ${PROJECT_ID}"
echo "SA email : ${SA_EMAIL}"
echo "Key path : ${KEY_PATH}"
echo "Next step: cd terraform && terraform init"
