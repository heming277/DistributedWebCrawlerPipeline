FROM python:3.8-slim

WORKDIR /usr/src/data_pipeline

COPY data_pipeline/ .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD rm -f /tmp/processing_complete && python process_data.py
