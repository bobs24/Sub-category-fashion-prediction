FROM apache/airflow:2.4.2

# Copy the model folder into the Docker image
COPY model /model

# Set the working directory to /model
WORKDIR /model

COPY requirements.txt /requirements.txt

RUN pip install --user --upgrade pip

RUN pip install --no-cache-dir --user -r /requirements.txt