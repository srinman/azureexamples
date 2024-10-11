# Use an official Python runtime as a parent image
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