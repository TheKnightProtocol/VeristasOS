import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.text_analyzer import analyze_text
from app.services.ai_analyzer import analyze_with_ai
from app.services.claim_analyzer import extract_claims
from app.services.provenance import analyze_provenance
from app.services.risk_engine import calculate_risk
from app.services.image_analyzer import analyze_image_bytes, analyze_text_image_consistency
from app.models.schemas import (
    UnifiedAnalyzeRequest,
    SimpleTextRequest,
    SemanticSearchRequest,
    InvestigationRequest,
)
from app.services.semantic_search import search_engine
from app.services.investigation_engine import run_full_investigation, generate_investigation_graph


# ============================================================
# VERISTASOS APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "VeristasOS"
APP_VERSION = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_INDEX = PROJECT_ROOT / "frontend" / "index.html"


# ============================================================
# LIFESPAN MANAGEMENT
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print()
    print("=" * 60)
    print("VERISTASOS — TRUTH INTELLIGENCE OPERATING ENVIRONMENT")
    print("=" * 60)
    print(f"Version : {APP_VERSION}")
    print("Backend : ONLINE")

    if FRONTEND_INDEX.exists():
        print("Frontend: AVAILABLE")
    else:
        print("Frontend: NOT FOUND")

    try:
        from app.ai.router import LocalAIRouter
        router = LocalAIRouter()
        if router.is_available():
            print("Local AI: CONNECTED (Qwen2.5-3B llama.cpp)")
        else:
            print("Local AI: OFFLINE (http://127.0.0.1:8080 unreachable)")
    except Exception:
        print("Local AI: OFFLINE")

    print("=" * 60)
    print()
    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "VeristasOS — Truth Intelligence Operating Environment. "
        "AI-assisted misinformation analysis, provenance, and explanation."
    ),
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class UnifiedAnalyzeRequest(BaseModel):
    """Request model for unified truth intelligence analysis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text content to analyze.",
    )
    source_url: Optional[str] = Field(None, description="Optional source URL.")
    source_name: Optional[str] = Field(None, description="Optional source name/publisher.")
    author: Optional[str] = Field(None, description="Optional author name.")
    publication_date: Optional[str] = Field(None, description="Optional publication date.")


class SimpleTextRequest(BaseModel):
    """Simple text request model for AI analysis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text content for AI analysis.",
    )


# ============================================================
# HELPER FOR UNIFIED ANALYSIS
# ============================================================

def run_unified_analysis(request: UnifiedAnalyzeRequest) -> dict[str, Any]:
    """Execute full VeristasOS Truth Intelligence analysis pipeline."""
    text = request.text.strip()
    linguistic = analyze_text(text)
    claims = extract_claims(text)

    provenance = analyze_provenance(
        source_url=request.source_url,
        source_name=request.source_name,
        author=request.author,
        publication_date=request.publication_date,
    )

    ai_result = analyze_with_ai(text, linguistic)

    risk_output = calculate_risk(
        text_analysis=linguistic,
        claims=claims,
        provenance=provenance,
        ai_analysis=ai_result,
    )

    return {
        "status": "success",
        "service": APP_NAME,
        "version": APP_VERSION,
        "analysis": {
            "overall_risk_score": risk_output["overall_risk_score"],
            "classification": risk_output["classification"],
            "confidence": risk_output["confidence"],
            "sensationalism_score": linguistic["sensationalism_score"],
            "linguistic_analysis": linguistic,
            "claims": claims,
            "risk_factors": risk_output["risk_factors"],
            "indicators": risk_output["indicators"],
            "ai_analysis": ai_result,
            "provenance": provenance,
            "recommendations": risk_output["recommendations"],
            "disclaimer": risk_output["disclaimer"],
        },
    }


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", include_in_schema=False)
def root():
    """Serve the VeristasOS frontend."""
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX, media_type="text/html")

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "VeristasOS backend is running.",
    }


@app.get("/health")
def health():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/api/version")
def api_version():
    """Return application version information."""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "healthy",
    }


@app.get("/api")
def api_info():
    """API description and capability summary."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "architecture": "VeristasOS Truth Intelligence Platform",
        "capabilities": [
            "unified text analysis",
            "sensationalism detection",
            "linguistic analysis",
            "factual claim extraction",
            "source provenance evaluation",
            "image media analysis & OCR",
            "local Qwen AI interpretation",
            "risk classification engine",
            "actionable recommendations",
        ],
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_version": "/api/version",
            "api_info": "/api",
            "api_status": "/api/status",
            "ai_status": "/api/ai/status",
            "ai_analyze": "/api/ai/analyze",
            "analyze": "/analyze",
            "api_analyze": "/api/analyze",
            "analyze_image": "/api/analyze-image",
            "docs": "/docs",
        },
    }


@app.get("/api/status")
def api_status():
    """Return backend + local AI system status."""
    ai_available = False
    try:
        from app.ai.router import LocalAIRouter
        router = LocalAIRouter()
        ai_available = router.is_available()
    except Exception:
        ai_available = False

    return {
        "status": "healthy",
        "backend": "online",
        "ai": {
            "available": ai_available,
            "provider": "llama.cpp",
            "model": "Qwen2.5-3B",
            "endpoint": "http://127.0.0.1:8080" if ai_available else "OFFLINE / LOCAL DEVELOPMENT ONLY",
        },
        "version": APP_VERSION,
        "features": [
            "text analysis",
            "sensationalism detection",
            "claim extraction",
            "provenance evaluation",
            "image OCR analysis",
            "local AI explanation",
        ],
    }


@app.get("/api/ai/status")
def ai_status():
    """Check live status of local llama.cpp server and Qwen model."""
    ai_available = False
    try:
        from app.ai.router import LocalAIRouter
        router = LocalAIRouter()
        ai_available = router.is_available()
    except Exception:
        ai_available = False

    return {
        "available": ai_available,
        "provider": "llama.cpp",
        "model": "Qwen2.5-3B-Instruct",
        "local": True,
        "endpoint": "http://127.0.0.1:8080",
    }


@app.post("/api/ai/analyze")
def ai_analyze(request: SimpleTextRequest):
    """
    Dedicated AI analysis endpoint returning structured reasoning.
    """
    text = request.text.strip()
    linguistic = analyze_text(text)
    ai_res = analyze_with_ai(text, linguistic)

    success = ai_res.get("available", False)
    verdict = ai_res.get("verdict", "UNAVAILABLE")
    confidence = float(ai_res.get("confidence", 0))
    risk_level = verdict.replace(" RISK", "") if "RISK" in verdict else "MEDIUM"
    reasoning = ai_res.get("summary", "AI explanation unavailable.")
    signals = ai_res.get("risk_factors", [])
    recommendations = ai_res.get("verification_steps", [])

    return {
        "success": success,
        "verdict": verdict,
        "confidence": confidence,
        "risk_level": risk_level,
        "reasoning": reasoning,
        "signals": signals,
        "recommendations": recommendations,
        "message": ai_res.get("message", "AI analysis complete"),
    }


@app.post("/analyze")
def analyze(request: UnifiedAnalyzeRequest):
    """Primary unified text analysis endpoint."""
    try:
        return run_unified_analysis(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {exc}",
        )


@app.post("/api/analyze")
def api_analyze(request: UnifiedAnalyzeRequest):
    """Consistent alias endpoint for unified analysis."""
    return analyze(request)


@app.post("/api/investigate")
def api_investigate(request: InvestigationRequest):
    """
    Master investigation endpoint combining claims, semantic search,
    evidence retrieval, source intelligence, correlation, and relationship graph.
    """
    try:
        return run_full_investigation(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {exc}",
        )


@app.post("/api/semantic-search")
def api_semantic_search(request: SemanticSearchRequest):
    """
    Semantic evidence search endpoint over indexed authoritative records.
    """
    try:
        matches = search_engine.search_similar_claims(
            query=request.query,
            top_k=request.top_k,
            category=request.category,
        )
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(matches),
            "results": [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in matches],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {exc}",
        )


@app.get("/api/evidence")
def api_get_evidence():
    """Return local evidence index repository records."""
    return {
        "status": "success",
        "total_records": len(search_engine.evidence_list),
        "evidence": [item.model_dump() if hasattr(item, "model_dump") else item.dict() for item in search_engine.evidence_list],
    }


@app.get("/api/investigation/{investigation_id}/graph")
def api_investigation_graph(investigation_id: str):
    """Return evidence relationship graph nodes and edges for visual rendering."""
    sample_request = UnifiedAnalyzeRequest(
        text="Sample demonstration article for graph visualization.",
        source_name="Sample Source",
    )
    graph = generate_investigation_graph(
        investigation_id=investigation_id,
        request=sample_request,
        claims=[{"claim": "Sample factual claim for visualization", "verification_status": "CORROBORATED"}],
        evidence_matches=[],
    )
    return {
        "investigation_id": investigation_id,
        "graph": graph.model_dump() if hasattr(graph, "model_dump") else graph.dict(),
    }


ALLOWED_IMAGE_MIMES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "application/octet-stream",
}

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpeg", ".jpg", ".png", ".webp", ".gif", ".bmp", ".tiff"
}


@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    article_text: Optional[str] = Form(None),
):
    """
    Image and media analysis endpoint with security validation.
    Performs metadata extraction, hashing, OCR text extraction (if available),
    and image-text consistency scoring.
    """
    try:
        safe_filename = Path(file.filename or "uploaded_image.png").name
        ext = Path(safe_filename).suffix.lower()

        if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}",
            )

        if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported MIME type '{file.content_type}'. Upload a valid image file.",
            )

        contents = await file.read()
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size exceeds 20MB limit.")

        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty image file submitted.")

        result = analyze_image_bytes(
            file_bytes=contents,
            filename=safe_filename,
            content_type=file.content_type,
        )

        consistency = None
        if article_text and article_text.strip():
            consistency = analyze_text_image_consistency(
                article_text=article_text,
                ocr_text=result.get("ocr_text", ""),
            )

        return {
            "status": "success",
            "image_analysis": result,
            "consistency": consistency,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {exc}",
        )