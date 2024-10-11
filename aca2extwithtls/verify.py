import requests

# Path to your certificate file
cert_path = '/home/srinman/git/aca/aca2extwithtls/certs/server-cert.pem'

# setup portforwardning k port-forward svc/pythonsvc 9090:443 
# add the following line to /etc/hosts
# 127.0.0.1       pythonsvc
# following request will send pythonsvc host header which is in the cert 
response = requests.get('https://pythonsvc:9090', verify=cert_path)
print(response.text)