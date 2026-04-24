

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from nlp_analyzer import analyze_cv


app = FastAPI(
    title="Resume Analyzer API",
    description="Analyzes student CVs with spaCy and returns structured feedback.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas

class AnalyzeRequest(BaseModel):
    cv_text: str

    @field_validator("cv_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("cv_text must not be empty")
        if len(v) > 50_000:
            raise ValueError("cv_text is too long (max 50 000 characters)")
        return v


class AnalyzeResponse(BaseModel):
    sections_found:  list[str]
    skills:          list[str]
    contact_info:    dict
    named_entities:  list[dict]
    suggestions:     list[str]
    word_count:      int
    character_count: int


# Routes

@app.get("/")
def root():
    return {
        "service": "Resume Analyzer",
        "usage":   "POST /analyze  body: {\"cv_text\": \"...\"}",
        "docs":    "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": "spaCy en_core_web_sm"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
   
    result = analyze_cv(req.cv_text)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return AnalyzeResponse(**{k: result[k] for k in AnalyzeResponse.model_fields})
