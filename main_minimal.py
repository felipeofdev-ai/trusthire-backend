"""
MINIMAL TEST — só /health, sem imports do projeto
Use isto para confirmar que Railway/Docker funcionam:
  startCommand = "uvicorn main_minimal:app --host 0.0.0.0 --port ${PORT:-8000}"
"""
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0", "env": os.getenv("ENV", "dev")}
