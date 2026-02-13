FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

RUN useradd -m -u 1000 trusthire && chown -R trusthire:trusthire /app
USER trusthire

EXPOSE 8000

# Give the app 60s to start before healthcheck fires
HEALTHCHECK --interval=20s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["./start.sh"]
