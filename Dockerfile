# Use the official Python base image
# FROM ubuntu
FROM python:3.9-slim

# Set the working directory inside the container
# WORKDIR /app
RUN mkdir app

# Copy the current directory contents into the container
# COPY server.py /app/

# Install necessary dependencies, including iptables and nano
RUN apt-get update && \
    apt-get install -y nano net-tools

# Command to run the server script
CMD ["python", "app/server.py"]
