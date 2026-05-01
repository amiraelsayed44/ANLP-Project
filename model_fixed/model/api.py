from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas.cv_schema import AnalyzeRequest, AnalyzeResponse
from nlp_analyzer import analyze_cv

app = FastAPI(
    title="Resume Analyzer API",
    description="Analyzes CVs with spaCy NER and returns structured feedback.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "Resume Analyzer", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    result = analyze_cv(req.cv_text, use_ai=True)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return AnalyzeResponse(**{k: result[k] for k in AnalyzeResponse.model_fields})
