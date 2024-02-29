FROM apache/airflow:2.4.2

COPY .env /.env

COPY requirements.txt /requirements.txt

RUN pip install --user --upgrade pip

RUN pip install -r /requirements.txt