import os
import time
import requests
from azure.identity import DefaultAzureCredential

# Retrieve environment variables
client_id = os.getenv('AZURE_CLIENT_ID')
tenant_id = os.getenv('AZURE_TENANT_ID')
apim_endpoint = os.getenv('APIM_ENDPOINT', 'https://apim.srinman.com/testhttpbin/')  # Add your APIM endpoint here

# Create a DefaultAzureCredential instance
credential = DefaultAzureCredential()

# Acquire a token using the default credential
#token = credential.get_token('https://management.azure.com/.default')
token = credential.get_token('api://mydummyapi/.default')

# Check if the token acquisition was successful
if token:
    access_token = token.token
    print(f'Access Token: {access_token}', flush=True)
else:
    print('Failed to acquire token', flush=True)

# Set the headers for the APIM request
apim_headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Function to call APIM endpoint
def call_apim():
    apim_response = requests.get(apim_endpoint, headers=apim_headers)
    print(f'APIM Response Status Code: {apim_response.status_code}', flush=True)
    print(f'APIM Response: {apim_response.json()}', flush=True)

# Issue a call every 60 seconds
while True:
    call_apim()
    time.sleep(60)