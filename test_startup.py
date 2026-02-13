"""
Run this locally to test if the app starts correctly:
  python test_startup.py
"""
import sys
print("Testing imports...")

try:
    from config import settings
    print(f"  ✓ config OK — ENV={settings.ENV}")
except Exception as e:
    print(f"  ✗ config FAILED: {e}"); sys.exit(1)

try:
    from models.schemas import AnalysisRequest, AnalysisResult, RiskLevel
    print("  ✓ models.schemas OK")
except Exception as e:
    print(f"  ✗ models.schemas FAILED: {e}"); sys.exit(1)

try:
    from models.user_models import UserTier, TokenData
    print("  ✓ models.user_models OK")
except Exception as e:
    print(f"  ✗ models.user_models FAILED: {e}"); sys.exit(1)

try:
    from engine.pattern_engine import AdvancedPatternEngine
    print("  ✓ engine.pattern_engine OK")
except Exception as e:
    print(f"  ✗ engine.pattern_engine FAILED: {e}"); sys.exit(1)

try:
    from engine.risk_scoring import RiskScoringEngine
    print("  ✓ engine.risk_scoring OK")
except Exception as e:
    print(f"  ✗ engine.risk_scoring FAILED: {e}"); sys.exit(1)

try:
    from engine.ai_layer import AIAnalysisLayer
    print("  ✓ engine.ai_layer OK")
except Exception as e:
    print(f"  ✗ engine.ai_layer FAILED: {e}"); sys.exit(1)

try:
    from core.analyzer import TrustHireAnalyzer, get_analyzer
    print("  ✓ core.analyzer OK")
except Exception as e:
    print(f"  ✗ core.analyzer FAILED: {e}"); sys.exit(1)

try:
    from auth.auth_service import create_access_token, hash_password
    print("  ✓ auth.auth_service OK")
except Exception as e:
    print(f"  ✗ auth.auth_service FAILED: {e}"); sys.exit(1)

try:
    from api.analysis import router as analysis_router
    print("  ✓ api.analysis OK")
except Exception as e:
    print(f"  ✗ api.analysis FAILED: {e}"); sys.exit(1)

try:
    from api.auth import router as auth_router
    print("  ✓ api.auth OK")
except Exception as e:
    print(f"  ✗ api.auth FAILED: {e}"); sys.exit(1)

try:
    from api.billing import router as billing_router
    print("  ✓ api.billing OK")
except Exception as e:
    print(f"  ✗ api.billing FAILED: {e}"); sys.exit(1)

print("\nAll imports OK — app should start correctly!")
