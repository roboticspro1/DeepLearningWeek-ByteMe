from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class TopicState:
    topic: str
    mastery_pct: float
    recent_mastery_pct: float
    avg_time_s: float
    diagnosis: str
    urgency: int
    color: str


def load_data(filepath: str | Path = "data.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def analyze_student_state(df: pd.DataFrame) -> list[TopicState]:
    topics_analysis: list[TopicState] = []

    for topic in df["topic"].unique():
        tdf = df[df["topic"] == topic].sort_values("timestamp")

        overall_accuracy = float(tdf["correct"].mean())
        avg_time = float(tdf["time_taken"].mean())

        mid = max(1, len(tdf) // 2)
        past_acc = float(tdf.iloc[:mid]["correct"].mean())
        recent_acc = float(tdf.iloc[mid:]["correct"].mean())

        if past_acc - recent_acc > 0.20:
            diagnosis = "Active Decay (Forgetting)"
            urgency = 95
            color = "#D9426A"
        elif overall_accuracy < 0.5 and avg_time < 40:
            diagnosis = "Careless Errors / Fatigue"
            urgency = 80
            color = "#E67E22"
        elif overall_accuracy < 0.5 and avg_time >= 40:
            diagnosis = "Deep Conceptual Gap"
            urgency = 90
            color = "#C0392B"
        elif overall_accuracy >= 0.5 and avg_time > 120:
            diagnosis = "High Cognitive Load (Slow Execution)"
            urgency = 60
            color = "#2D7DD2"
        else:
            diagnosis = "Retained Mastery"
            urgency = 10
            color = "#1E9B62"

        topics_analysis.append(
            TopicState(
                topic=topic,
                mastery_pct=round(overall_accuracy * 100, 2),
                recent_mastery_pct=round(recent_acc * 100, 2),
                avg_time_s=round(avg_time, 2),
                diagnosis=diagnosis,
                urgency=urgency,
                color=color,
            )
        )

    return sorted(topics_analysis, key=lambda x: x.urgency, reverse=True)


def topic_history(df: pd.DataFrame, topic: str) -> list[dict[str, Any]]:
    topic_df = df[df["topic"] == topic].sort_values("timestamp")
    history: list[dict[str, Any]] = []
    for row in topic_df.itertuples(index=False):
        history.append(
            {
                "timestamp": pd.Timestamp(row.timestamp).isoformat(),
                "correct": int(row.correct),
                "time_taken": float(row.time_taken),
            }
        )
    return history
