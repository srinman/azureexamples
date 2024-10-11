# Use an official OpenJDK runtime as a parent image
FROM openjdk:11-jdk-slim

# Set the working directory
WORKDIR /app

# Copy the Java program and the certificate
COPY SimpleTLSClient.java /app/SimpleTLSClient.java
COPY certs/server-cert.pem /usr/local/share/ca-certificates/server-cert.crt

# Install the certificate and import it into the Java trust store
RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates && \
    keytool -import -trustcacerts -file /usr/local/share/ca-certificates/server-cert.crt -alias server-cert -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt

# Compile the Java program
RUN javac SimpleTLSClient.java

# Run the Java program
CMD ["java", "SimpleTLSClient"]