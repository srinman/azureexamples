# for Common Name (server FQDN) - use localhost (if both server and client are on the same local machine)
# Generate a private key for the CA
openssl genrsa -out ca.key 2048

# Generate a self-signed certificate for the CA
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Generate a private key for the server
openssl genrsa -out server.key 2048

# Generate a certificate signing request (CSR) for the server
openssl req -new -key server.key -out server.csr

# Generate a self-signed certificate for the server using the CA certificate
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

# Generate a private key for the client
openssl genrsa -out client.key 2048

# Generate a certificate signing request (CSR) for the client
openssl req -new -key client.key -out client.csr

# Generate a self-signed certificate for the client using the CA certificate
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt

# create pem for client
cat client.key client.crt > client.pem

