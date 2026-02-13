"""
TrustHire Analysis API — SaaS Edition
Core analysis endpoints with per-tier rate limiting
"""

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import AnalysisRequest, AnalysisResult
from models.user_models import TokenData, UserTier
from core.analyzer import get_analyzer
from auth.auth_service import get_current_user
from database.user_repository import UserRepository
from utils.logger import get_logger

logger = get_logger("api.analysis")
router = APIRouter()


async def enforce_rate_limit(user: TokenData) -> None:
    """Check and enforce daily usage limits per tier"""
    db = UserRepository()
    can_analyze, used, daily_limit = await db.check_daily_limit(user.user_id)
    if not can_analyze:
        tier_upgrade = {
            UserTier.FREE: "Upgrade to Pro for 100/day → /api/v1/billing/checkout",
            UserTier.PRO: "Upgrade to Enterprise for 10,000/day",
            UserTier.ENTERPRISE: "Contact sales@trusthire.dev for custom limits",
        }
        raise HTTPException(
            status_code=429,
            detail={
                "error": "daily_limit_reached",
                "message": f"Daily limit reached ({used}/{daily_limit})",
                "upgrade_info": tier_upgrade.get(user.tier, ""),
            },
        )


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_message(
    request: AnalysisRequest,
    user: TokenData = Depends(get_current_user),
):
    """
    Analyze a recruitment message for scam indicators.

    - **Free tier**: 10/day, pattern detection only
    - **Pro tier**: 100/day + AI (Claude) analysis
    - **Enterprise**: 10,000/day + all features
    """
    if user is None:
        user = TokenData(user_id="anonymous", tier=UserTier.FREE)
        request.include_ai_analysis = False
    else:
        await enforce_rate_limit(user)
        if user.tier == UserTier.FREE:
            request.include_ai_analysis = False

    try:
        analyzer = get_analyzer()
        result = await analyzer.analyze(
            text=request.text,
            include_ai=request.include_ai_analysis and user.tier != UserTier.FREE,
            include_links=request.include_link_scan,
            user_id=user.user_id,
        )
        if user.user_id != "anonymous":
            db = UserRepository()
            await db.increment_analysis_count(user.user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.get("/stats")
async def get_stats(user: TokenData = Depends(get_current_user)):
    return {
        "total_analyses": 0,
        "high_risk_percentage": 0.0,
        "your_usage": {"tier": user.tier.value if user else "anonymous"},
    }
