FROM apache/airflow:2.10.4

WORKDIR /opt/airflow
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./dags /opt/airflow/dags
USER root
RUN mkdir -p /var/log/vien && \
    chown -R 1000:0 /var/log/vien && \
    chmod -R 755 /var/log/vien

USER airflow