FROM python:3.12-slim

WORKDIR /app

COPY app/ /app/
COPY config/ /config/

RUN pip install --no-cache-dir -r requirements.txt

ENV CONFIG_DIR=/config

CMD ["python", "app/main.py"]