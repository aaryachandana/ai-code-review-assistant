from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .analyzer import review_code
from .models import ReviewRequest, ReviewResult

app = FastAPI(title="AI Code Review Assistant", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResult)
def review(request: ReviewRequest) -> ReviewResult:
    try:
        return review_code(request.code, request.filename, request.use_ai)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
