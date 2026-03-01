from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from webapp.ai_service import generate_micro_task, generate_quiz
from webapp.analytics import analyze_student_state, load_data, topic_history

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data.csv"
TEMPLATES_DIR = BASE_DIR / "webapp" / "templates"
STATIC_DIR = BASE_DIR / "webapp" / "static"

app = FastAPI(title="CogniTriage Web", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class MicroTaskRequest(BaseModel):
    topic: str
    diagnosis: str
    api_key: str | None = None


class QuizRequest(BaseModel):
    topic: str
    diagnosis: str = "General practice and mastery"
    num_questions: int = Field(default=4, ge=2, le=10)
    api_key: str | None = None


def _student_state_payload() -> list[dict[str, Any]]:
    df = load_data(DATA_FILE)
    state = analyze_student_state(df)
    return [
        {
            "topic": item.topic,
            "mastery_pct": item.mastery_pct,
            "recent_mastery_pct": item.recent_mastery_pct,
            "avg_time_s": item.avg_time_s,
            "diagnosis": item.diagnosis,
            "urgency": item.urgency,
            "color": item.color,
        }
        for item in state
    ]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = TEMPLATES_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/topics")
def topics() -> dict[str, Any]:
    state = _student_state_payload()
    return {
        "topics": [item["topic"] for item in state],
        "state": state,
    }


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    df = load_data(DATA_FILE)
    state = _student_state_payload()

    urgent = [item for item in state if item["urgency"] > 30]
    radar = {
        "labels": [item["topic"] for item in state[:5]],
        "values": [item["mastery_pct"] for item in state[:5]],
    }

    telemetry: dict[str, list[dict[str, Any]]] = {}
    for item in state:
        telemetry[item["topic"]] = topic_history(df, item["topic"])

    return {
        "state": state,
        "urgent": urgent,
        "radar": radar,
        "telemetry": telemetry,
    }


@app.get("/api/topics/{topic}/history")
def history(topic: str) -> dict[str, Any]:
    df = load_data(DATA_FILE)
    if topic not in df["topic"].unique():
        raise HTTPException(status_code=404, detail="Topic not found")

    return {"topic": topic, "history": topic_history(df, topic)}


@app.post("/api/micro-task")
def micro_task(payload: MicroTaskRequest) -> dict[str, Any]:
    task = generate_micro_task(payload.topic, payload.diagnosis, payload.api_key)
    return {"task": task}


@app.post("/api/quiz")
def quiz(payload: QuizRequest) -> dict[str, Any]:
    generated = generate_quiz(
        topic=payload.topic,
        diagnosis=payload.diagnosis,
        num_questions=payload.num_questions,
        runtime_key=payload.api_key,
    )
    if not generated:
        raise HTTPException(status_code=400, detail="Could not generate quiz. Add a valid API key.")
    return generated
