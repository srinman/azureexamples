# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y \
    curl \
    net-tools \
    dnsutils \
    vim \
    nano \
&& rm -rf /var/lib/apt/lists/*

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run pythonblob.py when the container launches
CMD ["python", "./pythonblobwic.py"]

# To allow shelling into the container, override the CMD with:
# docker run -it --entrypoint /bin/bash <image_name>