FROM python:3.8-slim

WORKDIR /usr/src/app

COPY backend_api/ .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests

EXPOSE 5000

ENV NAME World

CMD ["python", "app.py"]