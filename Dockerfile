FROM python:3.9

RUN pip install pandas sqlalchemy psycopg2 openmeteo_requests requests_cache retry_requests

WORKDIR /app

COPY get_data.py get_data.py

ENTRYPOINT [ "python", "get_data.py" ]