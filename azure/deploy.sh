#!/bin/bash
# QueryMind Azure Deployment Script

# === CONFIGURATION ===
RESOURCE_GROUP="rg-querymind"
LOCATION="westeurope"
ACR_NAME="acrquerymind$(openssl rand -hex 4)"  # Must be unique
CONTAINER_APP_ENV="cae-querymind"
CONTAINER_APP_NAME="querymind"

# === 1. Resource Group ===
echo "Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# === 2. Azure Container Registry ===
echo "Creating Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# === 3. Build and Push Image ===
echo "Building and pushing Docker image..."
cd ..
az acr build --registry $ACR_NAME --image querymind:latest --file docker/Dockerfile .

# === 4. Container Apps Environment ===
echo "Creating Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# === 5. Deploy Container App ===
echo "Deploying Container App..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image "$ACR_LOGIN_SERVER/querymind:latest" \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8000 \
    --ingress external \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 0 \
    --max-replicas 3 \
    --env-vars \
        "LLM_PROVIDER=openai" \
        "OPENAI_MODEL=gpt-4o-mini" \
        "LOG_LEVEL=info"

# === 6. Get App URL ===
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo ""
echo "✅ Deployment complete!"
echo "🌐 App URL: https://$APP_URL"
echo ""
echo "Next steps:"
echo "1. Add OPENAI_API_KEY as secret (see below)"
echo "2. Configure database connection"