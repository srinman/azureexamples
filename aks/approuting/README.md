#  AKS App routing in internal mode deployment  


## Prep work  

``` 
az group create --name approutingrg --location eastus2

az network vnet create --name aksvnet --resource-group approutingrg --location eastus2 --address-prefix 10.2.0.0/16 --subnet-name akssubnet --subnet-prefixes 10.2.0.0/24  
```

## Create AKS cluster with web app routing  

### Create AKS cluster with web app routing enabled 
```  
az aks create --resource-group approutingrg --name approutingaks --location eastus2 --enable-app-routing --generate-ssh-keys  --vnet-subnet-id /subscriptions/xyz/resourceGroups/approutingrg/providers/Microsoft.Network/virtualNetworks/aksvnet/subnets/akssubnet --node-vm-size Standard_DS2_v2
```  

### Enable Key vault integration with web app routing  
```
az aks approuting update  --resource-group approutingrg --name approutingaks --enable-kv 
``` 

### Get AKS credentials and verify the cluster  
```
az aks get-credentials --resource-group approutingrg --name approutingaks   
az aks show -n approutingaks -g approutingrg
```

### Generate self-signed cert and upload to AKV.  Alternatively, generate a cert from a CA and upload to AKV.    
```
openssl req -new -x509 -nodes -out aks-ingress-tls.crt -keyout aks-ingress-tls.key -subj "/CN=testwebapprouting.srinman.com" -addext "subjectAltName=DNS:testwebapprouting.srinman.com"
openssl pkcs12 -export -in aks-ingress-tls.crt -inkey aks-ingress-tls.key -out aks-ingress-tls.pfx
``` 

- Upload this cert to AKV. 
- Provide 'Key Vault Certificate User' access to MI webapprouting - it's managed by AKS and it starts with webapprouting-*.  You can locate this in az aks show output.


### Start using ingress controller with custom cert

```
az aks get-credentials --resource-group approutingrg --name approutingaks   

k apply -f nginx-internal-controller.yaml  
```

nginx-internal-controller.yaml definition:  
```
apiVersion: approuting.kubernetes.azure.com/v1alpha1
kind: NginxIngressController
metadata:
  name: nginx-internal
spec:
  ingressClassName: nginx-internal
  controllerNamePrefix: nginx-internal
  loadBalancerAnnotations: 
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
``` 


kubectl get nginxingresscontroller  

kubectl create namespace hello-web-app-routing  

k apply -f workload.yaml  
```

workload.yaml definition:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aks-helloworld  
  namespace: hello-web-app-routing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aks-helloworld
  template:
    metadata:
      labels:
        app: aks-helloworld
    spec:
      containers:
      - name: aks-helloworld
        image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
        ports:
        - containerPort: 80
        env:
        - name: TITLE
          value: "Welcome to Azure Kubernetes Service (AKS)"
---
apiVersion: v1
kind: Service
metadata:
  name: aks-helloworld
  namespace: hello-web-app-routing
spec:
  type: ClusterIP
  ports:
  - port: 80
  selector:
    app: aks-helloworld
```


k apply -f testingress.yaml  
```

tsetingress.yaml definition:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.azure.com/tls-cert-keyvault-uri: https://testakv.vault.azure.net/certificates/testwebapprouting/f9bq87093734f
  name: aks-helloworld
  namespace: hello-web-app-routing
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
  rules:
  - host: testwebapprouting.srinman.com 
    http:
      paths:
      - backend:
          service:
            name: aks-helloworld
            port:
              number: 80
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - testwebapprouting.srinman.com
    secretName: keyvault-aks-helloworld
``` 

#k apply -f ingress-public.yaml    

k get svc -n app-routing-system

use external IP address of the public Ingress controller.


