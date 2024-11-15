# Workload Identity - step by step   



##  Few things to note before we start


tried to remove variable names and use the actual values for more readability.   

Following values are hardcoded for the sake of simplicity.  
cluster name: aks  
resource group: aksrg  
namespace: testns  
service account: testsa  
storage account name: srinmanwkldstorage.blob.core.windows.net

For more context, review https://blog.srinman.com/blog2/  

## Create a new AKS cluster with OIDC issuer enabled and workload identity enabled

```bash
az aks create -g aksrg -n aks --enable-oidc-issuer --enable-workload-identity  

export AKS_OIDC_ISSUER="$(az aks show -n aks -g aksrg --query "oidcIssuerProfile.issuerUrl" --output tsv)"
```

## Create a user assigned managed identity and a federated credential

```bash
az identity create --name aksappmi --resource-group aksrg --location eastus2

az identity federated-credential create --name fedaksappmi --identity-name aksappmi --resource-group aksrg --issuer AKS_OIDC_ISSUER --subject system:serviceaccount:testns:testsa --audience api://AzureADTokenExchange 

export UAMI_CLIENTID="$(az identity show -n aksappmi -g aksrg --query 'clientId' --output tsv)"
```

## Create a namespace and a service account in the namespace  

```bash
az aks get-credentials -g aksrg -n aks
k create ns testns 
```

## Create a service account in the namespace  
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: "${UAMI_CLIENTID}"
  name: testsa
  namespace: testns
EOF
```

## Create container image and run the application   

Use Dockerfile provided in the repo to build the image and push it to your container registry.  Use az acr build for building the image.    

```bash
az acr build -t srinmantest.azurecr.io/wkldtest:dacapim -r srinmantest .
```
This ACR has to be integrated with the AKS cluster.  Use the following command to integrate the ACR with AKS, if it's not done already.  

```bash
az aks update -n aks -g aksrg --attach-acr srinmantest
```  

Yaml for deploying the pod.  
```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: pythonpod
  namespace: testns
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: testsa
  containers:
  - name: blob-creator
    image: srinmantest.azurecr.io/wkldtest:dacapim
    imagePullPolicy: Always
    env: 
    - name: STORAGE_ACCOUNT_URL
      value: "https://srinmanwkldstorage.blob.core.windows.net/"
EOF
```








