from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.text_analyzer import analyze_text


APP_NAME = "VeristasOS"
APP_VERSION = "1.0.0"


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Multimodal fake news detection and verification system "
        "combining text, image, audio, and source analysis."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text to analyze",
    )


@app.get("/")
async def root():
    return {
        "name": APP_NAME,
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "Welcome to VeristasOS",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": APP_NAME,
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    result = analyze_text(request.text)

    return {
        "success": True,
        "text_length": len(request.text),
        "analysis": result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )