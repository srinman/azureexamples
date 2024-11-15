import os
import requests
import time

# Retrieve environment variables
client_id = os.getenv('AZURE_CLIENT_ID')
tenant_id = os.getenv('AZURE_TENANT_ID')
federated_token_file = os.getenv('AZURE_FEDERATED_TOKEN_FILE')
apim_endpoint = os.getenv('APIM_ENDPOINT', 'https://apim.srinman.com/testhttpbin/')  # Add your APIM endpoint here

# Read the federated token from the file
with open(federated_token_file, 'r') as file:
    federated_token = file.read().strip()

# Set the URL for the token request
url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

# Set the headers and data for the POST request
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

#     'scope': 'api://mydummyapi/Dummy.Read',

data = {
    'client_id': client_id,
    'scope': 'https://management.azure.com/.default',
    'client_assertion': federated_token,
    'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
    'grant_type': 'client_credentials'
}

# Make the POST request
response = requests.post(url, headers=headers, data=data)

# Extract the access token from the response
response_data = response.json()
access_token = response_data.get('access_token')

# Store the access token in a variable
ACCESS_TOKEN = access_token

# Print the access token
print(f'Access Token: {ACCESS_TOKEN}', flush=True)

# Set the headers for the APIM request
apim_headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
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