# Simple example of TLS communication between client and server  

This is a simple example of TLS communication between a client and a server. The server is a simple python server that listens on port 443 and the client is a simple java client that connects to the server. The server and client communicate over TLS. The server and client are dockerized and can be run in a container.


## Let's generate the server and client certificates

```bash
openssl req -x509 -newkey rsa:4096 -keyout server-key.pem -out server-cert.pem -days 365 -nodes -subj "/CN=pythonsvc"
```


## Simple python server program and Dockerfile


```python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class SimpleHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, TLS!')
        self.wfile.flush()  # Ensure the response is flushed

def run(server_class=HTTPServer, handler_class=SimpleHandler):
    server_address = ('', 443)
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile='/etc/tls/tls.crt',
                                   keyfile='/etc/tls/tls.key',
                                   ssl_version=ssl.PROTOCOL_TLS)
    print('Starting server on port 443...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
```


#### Explanation

This Python code sets up a simple HTTPS server that responds with a plain text message. Here's a detailed explanation:

1. **Imports**:
   - The code imports `HTTPServer` and `SimpleHTTPRequestHandler` from the `http.server` module to handle HTTP requests.
   - The `ssl` module is imported to add TLS support to the server.

2. **SimpleHandler Class**:
   - This class extends `SimpleHTTPRequestHandler` and overrides the `do_GET` method to handle GET requests.
   - The `do_GET` method sends a 200 OK response with a `Content-type` header set to `text/plain`.
   - It writes the message `Hello, TLS!` to the response body and flushes the output to ensure it is sent.

3. **run Function**:
   - This function sets up and starts the HTTPS server.
   - It creates an `HTTPServer` instance bound to port 443.
   - The server's socket is wrapped with TLS using `ssl.wrap_socket`, specifying the server certificate and key files.
   - The server is started with `httpd.serve_forever()`.

4. **Main Block**:
   - The `if __name__ == '__main__':` block ensures that the `run` function is called when the script is executed directly.



```docker
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the server code
COPY SimpleTLSServer.py /app/server.py

# Install necessary packages
RUN pip install --no-cache-dir httpserver

# Run the server
CMD ["python", "server.py"]
```



From python directory, build the image  
```bash
az acr build --registry srinmantest --image tls-server:v4 .
```


#### Explanation

This Dockerfile is used to create a Docker image for running the simple HTTPS server written in Python. Here's a step-by-step explanation:

1. **Base Image**:
   ```dockerfile
   FROM python:3.9-slim
   ```
   - This line specifies the base image to use, which is a slim version of Python 3.9. This provides the necessary environment to run Python applications.

2. **Set Working Directory**:
   ```dockerfile
   WORKDIR /app
   ```
   - This sets the working directory inside the container to `/app`. All subsequent commands will be run in this directory.

3. **Copy Files**:
   ```dockerfile
   COPY SimpleTLSServer.py /app/server.py
   ```
   - This `COPY` command copies the Python server code `SimpleTLSServer.py` from the host machine to the `/app` directory in the container, renaming it to `server.py`.

4. **Install Necessary Packages**:
   ```dockerfile
   RUN pip install --no-cache-dir httpserver
   ```
   - This `RUN` command installs the necessary Python packages using `pip`. The `--no-cache-dir` option ensures that no cache is used, reducing the image size.

5. **Run the Server**:
   ```dockerfile
   CMD ["python", "server.py"]
   ```
   - This `CMD` instruction specifies the command to run when the container starts. It runs the Python server script `server.py`.



For deploying this on AKS, we need to create a secret in the namespace where the server is running.

From the root of the repo, create a secret (assuming certs are in certs directory)
```bash
kubectl create secret tls tls-secret --cert=certs/server-cert.pem --key=certs/server-key.pem 
```

Deployment of the server  

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-tls-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: simple-tls-server
  template:
    metadata:
      labels:
        app: simple-tls-server
    spec:
      containers:
      - name: simple-tls-server
        image: srinmantest.azurecr.io/tls-server:v4
        ports:
        - containerPort: 443
        volumeMounts:
        - name: tls-secret
          mountPath: "/etc/tls"
          readOnly: true
      volumes:
      - name: tls-secret
        secret:
          secretName: tls-secret
---
apiVersion: v1
kind: Service
metadata:
  name: pythonsvc
spec:
  selector:
    app: simple-tls-server
  ports:
    - protocol: TCP
      port: 443
      targetPort: 443
  type: ClusterIP
```


#### Explanation

1. **Kubernetes Secrets**:
   - Use Kubernetes Secrets to securely store and manage your TLS certificates and keys.
   - The secret is created using the `kubectl create secret tls` command.

2. **Volume Mounts**:
   - The Deployment YAML mounts the secret as a volume at `/etc/tls`.
   - The `volumeMounts` section specifies the path where the secret will be mounted in the container.

3. **Python Code**:
   - Update your Python code to read the certificate and key from the mounted volume at `/etc/tls/tls.crt` and `/etc/tls/tls.key`.


## Simple Java client program and Dockerfile  


### Java Program Explanation

This Java code is a simple TLS client that makes an HTTPS GET request to a specified URL and prints the response. Here's a detailed explanation:

```java
import java.net.URL;
import javax.net.ssl.HttpsURLConnection;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class SimpleTLSClient {
    public static void main(String[] args) {
        try {
            // Create a URL object pointing to the desired HTTPS endpoint
            URL url = new URL("https://pythonsvc");
            
            // Open a connection to the URL and cast it to HttpsURLConnection
            HttpsURLConnection connection = (HttpsURLConnection) url.openConnection();
            
            // Set the request method to GET
            connection.setRequestMethod("GET");

            // Create a BufferedReader to read the response from the input stream
            BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String inputLine;
            StringBuilder content = new StringBuilder();
            
            // Read the response line by line and append it to the content StringBuilder
            while ((inputLine = in.readLine()) != null) {
                content.append(inputLine);
            }

            // Close the BufferedReader
            in.close();
            
            // Disconnect the connection
            connection.disconnect();

            // Print the response content
            System.out.println("Response: " + content.toString());
        } catch (Exception e) {
            // Print the stack trace if an exception occurs
            e.printStackTrace();
        }
    }
}
```

#### Key Points

1. **URL and HttpsURLConnection**:
   - The code creates a `URL` object pointing to `https://pythonsvc`.
   - It opens a connection to this URL and casts it to `HttpsURLConnection`, which is used for HTTPS connections.

2. **Request Method**:
   - The request method is set to `GET` using `connection.setRequestMethod("GET")`.

3. **Reading the Response**:
   - A `BufferedReader` is created to read the response from the input stream of the connection.
   - The response is read line by line and appended to a `StringBuilder` object.

4. **Closing Resources**:
   - The `BufferedReader` is closed after reading the response.
   - The connection is disconnected using `connection.disconnect()`.

5. **Exception Handling**:
   - Any exceptions that occur during the process are caught and printed using `e.printStackTrace()`.

#### Relation to Keystore and Truststore

- **Truststore**: 
  - In the context of this code, the truststore is relevant because it contains the certificates of trusted Certificate Authorities (CAs) that the client uses to verify the server's certificate during the TLS handshake.
  - If the server's certificate is not trusted (i.e., not found in the truststore), the connection will fail.

- **Keystore**:
  - The keystore is not directly used in this code, but it would be relevant if the client needed to present a client certificate to the server for mutual TLS authentication.
  - The keystore would contain the client's private key and certificate.

This code assumes that the necessary certificates are already present in the default truststore used by the Java runtime. If custom certificates are needed, they would need to be added to the truststore as shown in the Dockerfile steps.

### Dockerfile Explanation

This Dockerfile is used to create a Docker image for running the `SimpleTLSClient` Java application. Here's a step-by-step explanation:

```dockerfile
FROM openjdk:11-jdk-slim

WORKDIR /app

COPY SimpleTLSClient.java /app/SimpleTLSClient.java
COPY certs/server-cert.pem /usr/local/share/ca-certificates/server-cert.crt

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates && \
    keytool -import -trustcacerts -file /usr/local/share/ca-certificates/server-cert.crt -alias server-cert -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt

RUN javac SimpleTLSClient.java

CMD ["java", "SimpleTLSClient"]
```

#### Key Points

1. **Base Image**:
   ```dockerfile
   FROM openjdk:11-jdk-slim
   ```
   - This line specifies the base image to use, which is a slim version of OpenJDK 11 with the JDK (Java Development Kit) installed. This provides the necessary environment to compile and run Java applications.

2. **Set Working Directory**:
   ```dockerfile
   WORKDIR /app
   ```
   - This sets the working directory inside the container to `/app`. All subsequent commands will be run in this directory.

3. **Copy Files**:
   ```dockerfile
   COPY SimpleTLSClient.java /app/SimpleTLSClient.java
   COPY certs/server-cert.pem /usr/local/share/ca-certificates/server-cert.crt
   ```
   - The first `COPY` command copies the Java source file `SimpleTLSClient.java` from the host machine to the `/app` directory in the container.
   - The second `COPY` command copies the TLS certificate `server-cert.pem` from the host machine to the 

ca-certificates

 directory in the container, renaming it to `server-cert.crt`.

4. **Install Certificate and Update Trust Store**:
   ```dockerfile
   RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates && \
       keytool -import -trustcacerts -file /usr/local/share/ca-certificates/server-cert.crt -alias server-cert -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt
   ```
   - This `RUN` command performs several actions:
     - Updates the package list (`apt-get update`).
     - Installs the `ca-certificates` package (`apt-get install -y ca-certificates`).
     - Updates the CA certificates (`update-ca-certificates`).
     - Imports the copied certificate into the Java trust store using the `keytool` command. The certificate is added with the alias `server-cert` to the default Java trust store located at `$JAVA_HOME/lib/security/cacerts`, using the default password `changeit`.

   **Relation to Java Code**:
   - The truststore is crucial for the `SimpleTLSClient` Java application to verify the server's certificate during the TLS handshake. By adding the server's certificate to the truststore, the client can trust the server's identity.

5. **Compile Java Program**:
   ```dockerfile
   RUN javac SimpleTLSClient.java
   ```
   - This `RUN` command compiles the Java source file `SimpleTLSClient.java` into bytecode.

6. **Run Java Program**:
   ```dockerfile
   CMD ["java", "SimpleTLSClient"]
   ```
   - This `CMD` instruction specifies the command to run when the container starts. It runs the compiled Java program `SimpleTLSClient`.

   **Relation to Java Code**:
   - This step runs the `SimpleTLSClient` Java application, which makes an HTTPS GET request to a specified URL and prints the response. The application relies on the truststore to verify the server's certificate during the TLS handshake, which is essential for establishing a secure connection.

### Summary

- The Dockerfile sets up a container with OpenJDK 11, installs a specific TLS certificate, compiles the `SimpleTLSClient` Java program, and specifies that the program should be run when the container starts.
- The truststore configuration in the Dockerfile ensures that the `SimpleTLSClient` can verify the server's certificate during the TLS handshake, which is essential for establishing a secure connection.





Certainly! Below is the documentation for the provided Python program in Markdown format:

```markdown
# Python Program Explanation

This Python code sets up a simple HTTPS server that responds with a plain text message. Here's a detailed explanation:

```python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class SimpleHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, TLS!')
        self.wfile.flush()  # Ensure the response is flushed

def run(server_class=HTTPServer, handler_class=SimpleHandler):
    server_address = ('', 443)
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile='/certs/server-cert.pem',
                                   keyfile='/certs/server-key.pem',
                                   ssl_version=ssl.PROTOCOL_TLS)
    print('Starting server on port 443...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
```

## Key Points

1. **Imports**:
   - The code imports `HTTPServer` and `SimpleHTTPRequestHandler` from the `http.server` module to handle HTTP requests.
   - The `ssl` module is imported to add TLS support to the server.

2. **SimpleHandler Class**:
   - This class extends `SimpleHTTPRequestHandler` and overrides the `do_GET` method to handle GET requests.
   - The `do_GET` method sends a 200 OK response with a `Content-type` header set to `text/plain`.
   - It writes the message `Hello, TLS!` to the response body and flushes the output to ensure it is sent.

3. **run Function**:
   - This function sets up and starts the HTTPS server.
   - It creates an `HTTPServer` instance bound to port 443.
   - The server's socket is wrapped with TLS using `ssl.wrap_socket`, specifying the server certificate and key files.
   - The server is started with `httpd.serve_forever()`.

4. **Main Block**:
   - The `if __name__ == '__main__':` block ensures that the `run` function is called when the script is executed directly.

## Relation to Certificates

- **Server Certificate and Key**:
  - The server uses a certificate (`/certs/server-cert.pem`) and a private key (`/certs/server-key.pem`) to establish a secure TLS connection.
  - These files are specified in the `ssl.wrap_socket` call to enable TLS on the server.

## Summary

- This Python program sets up a simple HTTPS server that listens on port 443 and responds with a plain text message.
- The server uses TLS to secure the connection, requiring a server certificate and private key.
- The `SimpleHandler` class handles GET requests, and the `run` function sets up and starts the server.





## Sample commands 

docker build -t simple-tls-client:latest .

docker build -t tls-server:latest .

docker tag tls-server:latest srinmantest.azurecr.io/tls-server:v1
docker push srinmantest.azurecr.io/tls-server:v1


docker tag simple-tls-client:latest srinmantest.azurecr.io/simple-tls-client:v1
docker push srinmantest.azurecr.io/simple-tls-client:v1


az acr build --registry srinmantest --image tls-server:v3 .

az acr build --registry srinmantest --image simple-tls-client:v3 .