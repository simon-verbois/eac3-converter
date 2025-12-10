FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg procps && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir tomli

WORKDIR /app

COPY main.py .
COPY src/ ./src/

CMD ["python", "-u", "main.py"]
