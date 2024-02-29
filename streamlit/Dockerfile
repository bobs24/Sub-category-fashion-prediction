# Use the official Python image as the base image
FROM python:3.8-slim

# Install additional system dependencies
USER root
RUN apt-get update && apt-get install -y postgresql-client

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Copy model
COPY model .

# Install Streamlit and any other dependencies
RUN pip install -r requirements.txt

# Copy the rest of your Streamlit application code into the container
COPY . .

# Expose the port for Streamlit
EXPOSE 8601

# Set the entry point to run your Streamlit app
CMD ["streamlit", "run", "--server.port", "8601", "main.py"]