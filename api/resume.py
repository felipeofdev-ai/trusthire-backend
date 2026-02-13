"""
TrustHire Resume Optimization API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
import os
from pathlib import Path

from models.user_models import ResumeOptimizationRequest, ResumeOptimizationResponse
from services.resume_optimizer import ATSResumeOptimizer
from auth.auth_service import require_auth
from config import settings
from utils.logger import get_logger
from utils.i18n import get_translator

logger = get_logger("api.resume")
router = APIRouter(prefix="/resume", tags=["Resume"])

# Initialize AI client if available
_ai_client = None
if settings.ANTHROPIC_API_KEY:
    try:
        import anthropic
        _ai_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    except ImportError:
        logger.warning("anthropic package not installed")


@router.post("/optimize", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    user=Depends(require_auth)
):
    """
    Optimize resume for ATS compatibility
    """
    
    if not settings.FEATURE_RESUME_OPTIMIZATION:
        raise HTTPException(
            status_code=503,
            detail="Resume optimization is not enabled"
        )
    
    # Check tier limits
    # TODO: Implement usage tracking
    
    optimizer = ATSResumeOptimizer(_ai_client)
    language = request.language or settings.DEFAULT_LANGUAGE
    
    try:
        analysis = await optimizer.analyze_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            target_ats=request.target_ats,
            industry=request.industry,
            language=language
        )
        
        # Generate report
        report = optimizer.generate_ats_report(analysis, language)
        
        return ResumeOptimizationResponse(
            ats_score=analysis.get("ats_score", 0),
            compatibility=analysis.get("compatibility", {}),
            keywords=analysis.get("keywords", {}),
            suggestions=analysis.get("suggestions", []),
            optimized_sections=analysis.get("optimized_sections", {}),
            format_issues=analysis.get("format_issues", []),
            missing_sections=analysis.get("missing_sections", []),
            report=report
        )
        
    except Exception as e:
        logger.error(f"Resume optimization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    target_ats: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    user=Depends(require_auth)
):
    """
    Upload resume file and optimize
    """
    
    # Check file type
    allowed_extensions = settings.SUPPORTED_RESUME_FORMATS
    file_ext = Path(file.filename).suffix.lstrip('.')
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    max_size = settings.MAX_RESUME_SIZE_MB * 1024 * 1024  # Convert to bytes
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_RESUME_SIZE_MB}MB"
        )
    
    # Extract text from file
    try:
        if file_ext == 'txt':
            resume_text = file_content.decode('utf-8')
        elif file_ext == 'pdf':
            # TODO: Implement PDF text extraction
            raise HTTPException(status_code=501, detail="PDF support coming soon")
        elif file_ext == 'docx':
            # TODO: Implement DOCX text extraction
            raise HTTPException(status_code=501, detail="DOCX support coming soon")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    
    except Exception as e:
        logger.error(f"File processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not process file"
        )
    
    # Optimize resume
    optimizer = ATSResumeOptimizer(_ai_client)
    
    try:
        analysis = await optimizer.analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            target_ats=target_ats,
            industry=industry,
            language=language or "en"
        )
        
        report = optimizer.generate_ats_report(analysis, language or "en")
        
        return {
            "filename": file.filename,
            "analysis": analysis,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Resume optimization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.get("/supported-ats")
async def get_supported_ats():
    """Get list of supported ATS systems"""
    return {
        "ats_systems": settings.SUPPORTED_ATS,
        "job_boards": settings.SUPPORTED_JOB_BOARDS
    }


@router.get("/industries")
async def get_industries():
    """Get list of supported industries"""
    return {
        "industries": [
            "technology",
            "marketing",
            "sales",
            "finance",
            "human_resources",
            "healthcare"
        ]
    }
