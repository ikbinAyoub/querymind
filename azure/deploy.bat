@echo off
REM QueryMind Azure Deployment Script for Windows

REM === CONFIGURATION ===
set RESOURCE_GROUP=rg-querymind
set LOCATION=westeurope
set ACR_NAME=acrquerymind%RANDOM%
set CONTAINER_APP_ENV=cae-querymind
set CONTAINER_APP_NAME=querymind

echo === 1. Creating Resource Group ===
az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo === 2. Creating Container Registry ===
az acr create --resource-group %RESOURCE_GROUP% --name %ACR_NAME% --sku Basic --admin-enabled true

REM Get ACR login server
for /f "tokens=*" %%i in ('az acr show --name %ACR_NAME% --query loginServer -o tsv') do set ACR_LOGIN_SERVER=%%i

echo === 3. Building and Pushing Image ===
cd ..
az acr build --registry %ACR_NAME% --image querymind:latest --file docker/Dockerfile .

echo === 4. Creating Container Apps Environment ===
az containerapp env create --name %CONTAINER_APP_ENV% --resource-group %RESOURCE_GROUP% --location %LOCATION%

echo === 5. Deploying Container App ===
az containerapp create ^
    --name %CONTAINER_APP_NAME% ^
    --resource-group %RESOURCE_GROUP% ^
    --environment %CONTAINER_APP_ENV% ^
    --image %ACR_LOGIN_SERVER%/querymind:latest ^
    --registry-server %ACR_LOGIN_SERVER% ^
    --target-port 8000 ^
    --ingress external ^
    --cpu 0.5 ^
    --memory 1.0Gi ^
    --min-replicas 0 ^
    --max-replicas 3

echo === 6. Getting App URL ===
az containerapp show --name %CONTAINER_APP_NAME% --resource-group %RESOURCE_GROUP% --query properties.configuration.ingress.fqdn -o tsv

echo.
echo Deployment complete! Add secrets with:
echo az containerapp secret set --name %CONTAINER_APP_NAME% --resource-group %RESOURCE_GROUP% --secrets openai-key=YOUR_KEY
pause