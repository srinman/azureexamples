#  AKS App routing in internal mode deployment  


## Prep work  

``` 
az group create --name approutingrg --location eastus 

az network vnet create --name aksvnet --resource-group approutingrg --location eastus --address-prefix 10.2.0.0/16 --subnet-name akssubnet --subnet-prefixes 10.2.0.0/24  

az aks create --resource-group approutingrg --name approutingaks --location eastus --enable-app-routing --generate-ssh-keys  --vnet-subnet-id /subscriptions/abcd/resourceGroups/approutingrg/providers/Microsoft.Network/virtualNetworks/aksvnet/subnets/akssubnet

az aks get-credentials --resource-group approutingrg --name approutingaks   

k apply -f nginx-internal-controller.yaml  

kubectl get nginxingresscontroller  

kubectl create namespace hello-web-app-routing  

k apply -f workload.yaml  

k apply -f ingress.yaml  
k apply -f ingress-public.yaml    
```   


Test connectivity to public Ingress.   

```

curl http://57.152.16.240 --header "Host: test.srinman.com"  

```

For testing connectivity to internal Ingress, use the internal IP address of the Ingress controller.  You need to be on a VM in the same VNET as the AKS cluster or any other VNET peered or on-premises connected to the VNET.    

Creating app routing with internal ingress as default will be supported soon, I hope. 

This assumes that DNS is not managed by Azure.  It's not leveraging Azure DNS integration.  

If needed, use this link for DNS integration with Azure DNS.  
https://learn.microsoft.com/en-us/azure/aks/create-nginx-ingress-private-controller  