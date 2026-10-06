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
from app.services.verification_engine import run_dual_layer_verification
from app.services.trust_lens_engine import analyze_trust_lens
from app.services.scam_dna import generate_scam_dna
from app.services.bharat_language_engine import analyze_bharat_language
from app.services.trust_firewall import TrustFirewall
from app.services.saathi_agent import AISaathiAgent
from app.services.email_service import EmailService
from app.services.policy_engine import UserPolicyEngine
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
    print("VERISTASOS — DIGITAL TRUST & SAFETY LAYER")
    print("Your truth. Your data. Your device.")
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
        "VeristasOS — AI-Powered Digital Trust & Safety Layer. "
        "Your truth. Your data. Your device."
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
    """Request model for unified truth & privacy analysis."""

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
    """Simple text request model for AI & verification analysis."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text content for analysis.",
    )


# ============================================================
# HELPER FOR UNIFIED ANALYSIS
# ============================================================

def run_unified_analysis(request: UnifiedAnalyzeRequest) -> dict[str, Any]:
    """Execute full VeristasOS Digital Trust & Safety analysis pipeline."""
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

    verification = run_dual_layer_verification(
        text=text,
        source_url=request.source_url,
        source_name=request.source_name,
        author=request.author,
        publication_date=request.publication_date,
    )

    trust_lens = analyze_trust_lens(
        text=text,
        source_url=request.source_url,
        source_name=request.source_name,
    )

    return {
        "status": "success",
        "service": APP_NAME,
        "version": APP_VERSION,
        "trust_lens": trust_lens,
        "verification": verification,
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
    """System health check endpoint."""
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "production"),
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
        "architecture": "VeristasOS AI-Powered Digital Trust & Safety Layer",
        "tagline": "Your truth. Your data. Your device.",
        "capabilities": [
            "Trust Lens (WHY → RISK → ACTION decision framework)",
            "Digital Trust Graph (Multi-signal node/edge graph)",
            "Scam DNA Engine (5-part attack vector fingerprinting)",
            "Bharat Language Safety Engine (Hinglish/English code-mixed intent detection)",
            "Privacy Shield (Aadhaar/PAN/UPI/OTP Scanner & Data Masking)",
            "Content Trust Engine & Sensationalism Highlighter",
            "Media Forensics & Deepfake Lens",
            "Local-First AI Architecture Integration",
        ],
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_version": "/api/version",
            "api_info": "/api",
            "api_status": "/api/status",
            "ai_status": "/api/ai/status",
            "trust_lens": "/api/trust-lens",
            "scam_dna": "/api/scam-dna",
            "bharat_safety": "/api/bharat-safety",
            "verify": "/api/verify",
            "forward_check": "/api/forward-check",
            "analyze": "/analyze",
            "api_analyze": "/api/analyze",
            "analyze_image": "/api/analyze-image",
            "search": "/api/search",
            "evidence": "/api/evidence",
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

    from app.services.deepfake_detector import deepfake_detector

    return {
        "status": "healthy",
        "backend": "online",
        "local_ai": {
            "available": ai_available,
            "label": "● Local model available" if ai_available else "○ Local model not configured",
            "provider": "llama.cpp" if ai_available else "Deterministic Heuristics Engine",
        },
        "media_authenticity": {
            "available": True,
            "model": "heuristic-cpu-v1",
        },
        "deepfake_detection": {
            "available": deepfake_detector.is_enabled(),
            "model": deepfake_detector.default_model,
        },
        "version": APP_VERSION,
    }


@app.post("/api/trust-lens")
def api_trust_lens(request: UnifiedAnalyzeRequest):
    """Primary endpoint for Trust Lens analysis returning WHY → RISK → ACTION."""
    try:
        return {
            "status": "success",
            "trust_lens": analyze_trust_lens(
                text=request.text,
                source_url=request.source_url,
                source_name=request.source_name,
            ),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trust Lens analysis failed: {exc}")


@app.post("/api/scam-dna")
def api_scam_dna(request: SimpleTextRequest):
    """Dedicated endpoint for Scam DNA fingerprint extraction."""
    try:
        return {
            "status": "success",
            "scam_dna": generate_scam_dna(request.text),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Scam DNA extraction failed: {exc}")


@app.post("/api/bharat-safety")
def api_bharat_safety(request: SimpleTextRequest):
    """Dedicated endpoint for Bharat Language Safety Engine (Hinglish/English)."""
    try:
        return {
            "status": "success",
            "bharat_safety": analyze_bharat_language(request.text),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bharat Language Safety analysis failed: {exc}")


@app.get("/api/ai/status")
def ai_status():
    """Check live status of local llama.cpp server."""
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


@app.get("/api/media/authenticity/status")
def media_authenticity_status():
    """Return status of CPU media authenticity screening engine."""
    from app.services.media_authenticity import authenticity_analyzer
    return {
        "available": authenticity_analyzer.is_available(),
        "model": authenticity_analyzer.model_name,
        "type": "heuristic-cpu-v1",
        "description": "AI-assisted media authenticity screening (CPU-compatible). Not definitive proof of synthetic media.",
    }


@app.get("/api/media/deepfake/status")
def media_deepfake_status():
    """Return status of deepfake & manipulation detector module."""
    from app.services.deepfake_detector import deepfake_detector
    return {
        "available": deepfake_detector.is_enabled(),
        "model": deepfake_detector.default_model,
        "type": "lightweight-forensic-analysis",
        "description": "Deepfake / Manipulation Risk screening. AI-assisted forensic estimate, not definitive proof.",
    }


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


@app.post("/api/verify")
def api_verify(request: UnifiedAnalyzeRequest):
    """Primary endpoint for Master Dual-Layer Verification."""
    try:
        return run_unified_analysis(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}")


@app.post("/api/forward-check")
def api_forward_check(request: SimpleTextRequest):
    """Dedicated endpoint for Forward Checker mode."""
    try:
        res = run_dual_layer_verification(text=request.text)
        trust_lens = analyze_trust_lens(text=request.text)
        return {
            "status": "success",
            "mode": "Forward Checker",
            "trust_lens": trust_lens,
            "verification": res,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forward check failed: {exc}")


@app.post("/api/ai/analyze")
def ai_analyze(request: SimpleTextRequest):
    """Dedicated AI analysis endpoint returning structured reasoning."""
    text = request.text.strip()
    linguistic = analyze_text(text)
    ai_res = analyze_with_ai(text, linguistic)

    success = ai_res.get("available", False)
    verdict = ai_res.get("verdict", "UNAVAILABLE")
    confidence = float(ai_res.get("confidence", 0))
    risk_level = verdict.replace(" RISK", "") if "RISK" in verdict else "MEDIUM"
    reasoning = ai_res.get("summary", "AI explanation unavailable.")

    return {
        "success": success,
        "verdict": verdict,
        "confidence": confidence,
        "risk_level": risk_level,
        "reasoning": reasoning,
    }


@app.post("/analyze")
def analyze(request: UnifiedAnalyzeRequest):
    """Primary unified text analysis endpoint."""
    try:
        return run_unified_analysis(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@app.post("/api/analyze")
def api_analyze(request: UnifiedAnalyzeRequest):
    """Consistent alias endpoint for unified analysis."""
    return analyze(request)


@app.post("/api/investigate")
def api_investigate(request: InvestigationRequest):
    """Master investigation endpoint."""
    try:
        return run_full_investigation(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {exc}")


@app.get("/api/search")
def api_search(
    q: str,
    limit: int = 20,
    offset: int = 0,
    category: Optional[str] = None,
    sort_by: str = "relevance",
):
    """Search full indexed evidence corpus with pagination."""
    if not q or not q.strip():
        return {
            "status": "success",
            "query": q,
            "results_count": 0,
            "total_matches": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False,
            "results": [],
        }

    total_matches = search_engine.count_matches(q, category=category)
    matches = search_engine.search_similar_claims(
        query=q,
        top_k=None,
        limit=limit,
        offset=offset,
        category=category,
        sort_by=sort_by,
    )

    return {
        "status": "success",
        "query": q,
        "results_count": len(matches),
        "total_matches": total_matches,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_matches,
        "results": [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in matches],
    }


@app.post("/api/semantic-search")
def api_semantic_search(request: SemanticSearchRequest):
    """Semantic evidence search endpoint."""
    try:
        total_matches = search_engine.count_matches(request.query, category=request.category)
        matches = search_engine.search_similar_claims(
            query=request.query,
            top_k=request.top_k,
            limit=request.limit,
            offset=request.offset,
            category=request.category,
            sort_by=request.sort_by,
        )
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(matches),
            "total_matches": total_matches,
            "limit": request.limit,
            "offset": request.offset,
            "has_more": (request.offset + len(matches)) < total_matches,
            "results": [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in matches],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {exc}")


ALLOWED_IMAGE_MIMES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif", "image/bmp", "image/tiff", "application/octet-stream",
}
ALLOWED_IMAGE_EXTENSIONS = {
    ".jpeg", ".jpg", ".png", ".webp", ".gif", ".bmp", ".tiff"
}


@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    article_text: Optional[str] = Form(None),
):
    """Image media analysis endpoint with security validation and dual-layer verification."""
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
            article_text=article_text,
        )

        verification = run_dual_layer_verification(
            text=article_text or result.get("ocr_text", ""),
            image_analysis=result,
        )

        trust_lens = analyze_trust_lens(
            text=article_text or result.get("ocr_text", ""),
            image_analysis=result,
        )

        return {
            "status": "success",
            "image_analysis": result,
            "verification": verification,
            "trust_lens": trust_lens,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {exc}")


# ============================================================
# AI SAATHI & TRUST FIREWALL ENDPOINTS
# ============================================================

class SaathiChatRequest(BaseModel):
    query: str
    context: Optional[str] = None
    user_mode: Optional[str] = "Adult"


class EmailActionRequest(BaseModel):
    email_id: str
    user_approved: Optional[bool] = False
    user_mode: Optional[str] = "Adult"


class TrustFirewallRequest(BaseModel):
    action_name: str
    content: str
    user_mode: Optional[str] = "Adult"


class PolicySettingsRequest(BaseModel):
    user_mode: str
    allow_medium_risk: Optional[bool] = False


saathi_agent_instance = AISaathiAgent()
email_service_instance = EmailService()
trust_firewall_instance = TrustFirewall()


@app.post("/api/saathi/chat")
def saathi_chat_endpoint(req: SaathiChatRequest):
    """Conversational AI Saathi interface for natural language query processing."""
    try:
        saathi_agent_instance.set_user_mode(req.user_mode or "Adult")
        res = saathi_agent_instance.process_chat_query(
            query=req.query,
            context_content=req.context or ""
        )
        return {"status": "success", "result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI Saathi chat processing failed: {exc}")


@app.get("/api/saathi/brief")
def saathi_brief_endpoint(user_mode: Optional[str] = "Adult"):
    """Returns Daily Saathi Brief statistics and high/medium/low risk summaries."""
    try:
        saathi_agent_instance.set_user_mode(user_mode or "Adult")
        brief = saathi_agent_instance.get_daily_brief()
        return {"status": "success", "brief": brief}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Daily Saathi Brief fetch failed: {exc}")


@app.get("/api/email/inbox")
def get_email_inbox_endpoint(user_mode: Optional[str] = "Adult"):
    """Returns email inbox items with Trust Firewall risk decision evaluations."""
    try:
        email_service_instance.set_user_mode(user_mode or "Adult")
        inbox = email_service_instance.get_inbox()
        return {"status": "success", "count": len(inbox), "inbox": inbox}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email inbox fetch failed: {exc}")


@app.post("/api/email/action")
def execute_email_action_endpoint(req: EmailActionRequest):
    """Executes or requests user confirmation for an email action subject to Trust Firewall gate."""
    try:
        email_service_instance.set_user_mode(req.user_mode or "Adult")
        res = email_service_instance.execute_email_action(
            email_id=req.email_id,
            user_approved=req.user_approved or False
        )
        return {"status": "success", "result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email action execution failed: {exc}")


@app.post("/api/trust/firewall")
def trust_firewall_evaluate_endpoint(req: TrustFirewallRequest):
    """Evaluates proposed AI actions against Content, Privacy, Financial, and Reliability risks."""
    try:
        trust_firewall_instance.set_user_mode(req.user_mode or "Adult")
        res = trust_firewall_instance.evaluate_proposed_action(
            action_name=req.action_name,
            content=req.content
        )
        return {"status": "success", "evaluation": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trust Firewall evaluation failed: {exc}")


@app.post("/api/policy/settings")
def update_policy_settings_endpoint(req: PolicySettingsRequest):
    """Updates user policy preferences and mode (Adult vs Senior Citizen)."""
    try:
        saathi_agent_instance.set_user_mode(req.user_mode)
        email_service_instance.set_user_mode(req.user_mode)
        trust_firewall_instance.set_user_mode(req.user_mode)
        
        if req.allow_medium_risk:
            trust_firewall_instance.policy_engine.user_custom_allow_medium = True

        return {
            "status": "success",
            "message": f"User mode updated to '{req.user_mode}' successfully.",
            "mode": req.user_mode,
            "allow_medium_risk": req.allow_medium_risk
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Policy update failed: {exc}")