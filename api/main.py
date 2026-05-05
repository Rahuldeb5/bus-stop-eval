# api/main.py

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.db import init_db, save_evaluation, get_evaluation
from api.cleanup import cleanup_old_images, cleanup_images
from src.pipeline import evaluate_from_coordinates
from src.config import IMAGE_DIR

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    cleanup_old_images(max_age_hours=24)
    yield

app = FastAPI(title="Bus Stop Evaluator", lifespan=lifespan)

web_image_dir = os.path.join(IMAGE_DIR, "web")
os.makedirs(web_image_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=web_image_dir), name="images")


class EvaluateRequest(BaseModel):
    lat: float
    lng: float

class CriterionResponse(BaseModel):
    criterion: str
    passed: bool | None
    importance: str | None
    notes: str | None

class FailureGroup(BaseModel):
    critical: list[dict]
    high:     list[dict]
    medium:   list[dict]
    low:      list[dict]

class EvaluateResponse(BaseModel):
    job_id:      str
    snapped_lat: float
    snapped_lng: float
    score:       float | None
    verdict:     str
    failures:    FailureGroup
    results:     list[CriterionResponse]
    image_urls:  list[str]


def _image_urls(job_id: str) -> list[str]:
    """Return public URLs for all images associated with a job."""
    folder = os.path.join(web_image_dir, job_id)
    if not os.path.isdir(folder):
        return []
    return [
        f"/images/{job_id}/{fname}"
        for fname in sorted(os.listdir(folder))
        if fname.endswith(".jpg") and "_enhanced" not in fname
    ]

def _format_results(raw_results) -> list[CriterionResponse]:
    """Convert CriterionResult dataclasses (pipeline) or dicts (DB) to response model."""
    out = []
    for r in raw_results:
        if isinstance(r, dict):
            out.append(CriterionResponse(
                criterion=r["criterion"],
                passed=r["passed"],
                importance=r["importance"],
                notes=r["notes"],
            ))
        else:
            out.append(CriterionResponse(
                criterion=r.criterion,
                passed=r.passed,
                importance=r.importance.value if r.importance else None,
                notes=r.notes,
            ))
    return out

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest, background_tasks=None):
    """
    Run the full evaluation pipeline for a lat/lng coordinate.
    Fetches Street View images, runs API + LLM checks, saves to DB.
    """
    result = await asyncio.to_thread(
        evaluate_from_coordinates, req.lat, req.lng, "web"
    )

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    save_evaluation(result)

    asyncio.create_task(cleanup_images(result["job_id"], delay_hours=24))

    return EvaluateResponse(
        job_id=result["job_id"],
        snapped_lat=result["snapped_lat"],
        snapped_lng=result["snapped_lng"],
        score=result.get("score"),
        verdict=result.get("verdict", "UNKNOWN"),
        failures=FailureGroup(**result.get("failures", {
            "critical": [], "high": [], "medium": [], "low": []
        })),
        results=_format_results(result["results"]),
        image_urls=_image_urls(result["job_id"]),
    )


@app.get("/evaluation/{job_id}", response_model=EvaluateResponse)
async def get_evaluation_by_id(job_id: str):
    """
    Retrieve a previously computed evaluation by job_id.
    """
    saved = get_evaluation(job_id)
    if not saved:
        raise HTTPException(status_code=404, detail=f"No evaluation found for job_id '{job_id}'")

    return EvaluateResponse(
        job_id=job_id,
        snapped_lat=saved["snapped_lat"],
        snapped_lng=saved["snapped_lng"],
        score=saved.get("score"),
        verdict=saved.get("verdict", "UNKNOWN"),
        failures=FailureGroup(**saved.get("failures", {
            "critical": [], "high": [], "medium": [], "low": []
        })),
        results=_format_results(saved["results"]),
        image_urls=_image_urls(job_id),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
