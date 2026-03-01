from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


def _resolve_api_key(runtime_key: str | None) -> str | None:
    return runtime_key or os.getenv("OPENAI_API_KEY")


def generate_micro_task(topic: str, diagnosis: str, runtime_key: str | None = None) -> str:
    api_key = _resolve_api_key(runtime_key)
    if not api_key:
        return "Provide an OpenAI API key to generate a micro-task."

    prompt = f"""
The student is studying '{topic}'.
Their diagnostic system flagged them with: '{diagnosis}'.

Do NOT give generic advice. Give a single, highly specific 5-minute micro-task.
Format as:
Action: [One sentence what to do]
Why: [One sentence why this fixes their specific issue]
"""

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=180,
        )
        return response.choices[0].message.content or "Could not generate micro-task."
    except Exception:
        return "Error reaching OpenAI. Check your API key and try again."


def generate_quiz(
    topic: str,
    diagnosis: str = "General practice and mastery",
    num_questions: int = 4,
    runtime_key: str | None = None,
) -> dict[str, Any] | None:
    api_key = _resolve_api_key(runtime_key)
    if not api_key:
        return None

    prompt = f"""
The student is studying '{topic}'. Context/Diagnosis: '{diagnosis}'.
Generate a {num_questions}-question multiple-choice diagnostic quiz.

CRITICAL: Return only a valid JSON object. No markdown.

Format exactly:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "B) ...",
      "detailed_explanation": "Detailed explanation and misconceptions for wrong options."
    }}
  ]
}}
"""

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw_text = (response.choices[0].message.content or "").strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception:
        return None
