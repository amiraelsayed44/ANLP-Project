from pydantic import BaseModel, field_validator

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
