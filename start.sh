#!/bin/sh
# Startup script with verbose logging for Railway debugging
echo "=== TrustHire Starting ==="
echo "PORT=${PORT:-8000}"
echo "ENV=${ENV:-dev}"
echo "Python: $(python3 --version)"
echo "=== Testing imports ==="
python3 -c "
import sys
steps = [
    ('fastapi', 'from fastapi import FastAPI'),
    ('config', 'from config import settings; print(f\"  ENV={settings.ENV}\")'),
    ('models.schemas', 'from models.schemas import AnalysisRequest'),
    ('models.user_models', 'from models.user_models import UserTier'),
    ('engine.pattern_engine', 'from engine.pattern_engine import AdvancedPatternEngine'),
    ('engine.risk_scoring', 'from engine.risk_scoring import RiskScoringEngine'),
    ('engine.ai_layer', 'from engine.ai_layer import AIAnalysisLayer'),
    ('core.analyzer', 'from core.analyzer import get_analyzer'),
    ('auth.auth_service', 'from auth.auth_service import create_access_token'),
    ('api.analysis', 'from api.analysis import router'),
    ('api.auth', 'from api.auth import router'),
    ('api.billing', 'from api.billing import router'),
    ('main', 'from main import app'),
]
for name, stmt in steps:
    try:
        exec(stmt)
        print(f'  OK: {name}')
    except Exception as e:
        print(f'  FAIL: {name} — {e}')
        sys.exit(1)
print('All imports OK — starting uvicorn')
"
if [ $? -ne 0 ]; then
    echo "=== IMPORT FAILED — see error above ==="
    exit 1
fi
echo "=== Starting uvicorn on port ${PORT:-8000} ==="
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
