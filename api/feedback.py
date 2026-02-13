"""
TrustHire Feedback API
User feedback and reporting
"""

from fastapi import APIRouter, HTTPException
from models.schemas import FeedbackRequest, ReportScamRequest
from utils.logger import get_logger

logger = get_logger("api.feedback")
router = APIRouter()


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback on analysis accuracy
    
    Helps improve the system through user validation
    """
    try:
        # TODO: Store in database
        logger.info(
            "feedback_received",
            extra={
                "analysis_id": feedback.analysis_id,
                "was_accurate": feedback.was_accurate,
                "user_id": feedback.user_id,
            },
        )
        
        return {"status": "received", "message": "Thank you for your feedback"}
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.post("/report-scam")
async def report_scam(report: ReportScamRequest):
    """
    Report a scam to the community database
    
    Contributes to collective scam intelligence
    """
    try:
        # TODO: Store in database and queue for verification
        logger.info(
            "scam_reported",
            extra={
                "domain": report.domain,
                "company": report.company_name,
                "reported_by": report.reported_by,
            },
        )
        
        return {
            "status": "received",
            "message": "Thank you for reporting. We will review this submission.",
        }
        
    except Exception as e:
        logger.error(f"Scam report failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit report")
