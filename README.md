# CogniTriage ⚡

[![Repo](https://img.shields.io/badge/repo-roboticspro1/DeepLearningWeek--ByteMe-blue)](https://github.com/roboticspro1/DeepLearningWeek-ByteMe)

**Moving from passive analytics to active intervention.**

CogniTriage is an AI-powered topic mastery platform that triages learning friction, highlights high-priority gaps, and generates targeted interventions.

## What Changed

This project now includes a **full web application** (not Streamlit-first):

- Dashboard with urgent-topic triage cards
- Mastery radar + telemetry charts
- Targeted remediation (auto-lock on highest urgency topic)
- Self remediation (choose any topic)
- AI micro-task generation
- AI-generated diagnostic quizzes with detailed explanations

The original Streamlit files (`app.py`, `utils.py`) are still present, but the recommended entry point is now the FastAPI website.

## Project Structure

```text
.
├── webapp/
│   ├── main.py              # FastAPI app + API routes
│   ├── analytics.py         # Diagnostic logic and topic telemetry
│   ├── ai_service.py        # OpenAI micro-task/quiz generation
│   ├── templates/
│   │   └── index.html       # Main web UI shell
│   └── static/
│       ├── styles.css       # App styling and responsive layout
│       └── app.js           # Frontend logic (API wiring + quiz flow + charts)
├── app.py                   # Legacy Streamlit UI
├── utils.py                 # Legacy Streamlit helpers
├── data.csv                 # Student performance data
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key (optional, required only for AI quiz/micro-task generation)

### Install

```bash
pip install -r requirements.txt
```

### Run Website

```bash
uvicorn webapp.main:app --reload
```

Open: [http://localhost:8000](http://localhost:8000)

## Using OpenAI

You can either:

- Paste API key in the website sidebar at runtime, or
- Set environment variable before launch:

```bash
export OPENAI_API_KEY="sk-..."
uvicorn webapp.main:app --reload
```

## Data Format

`data.csv` needs these columns:

- `timestamp` (ISO datetime)
- `topic` (string)
- `correct` (0 or 1)
- `time_taken` (seconds)

## Diagnostic Logic

```python
1. Active Decay: past_accuracy - recent_accuracy > 20% -> Urgency: 95
2. Careless/Fatigue: accuracy < 50% and time < 40s -> Urgency: 80
3. Deep Gap: accuracy < 50% and time >= 40s -> Urgency: 90
4. High Load: accuracy >= 50% and time > 120s -> Urgency: 60
5. Retained: otherwise -> Urgency: 10
```

## Tech Stack

- FastAPI + Uvicorn
- HTML/CSS/Vanilla JS
- Chart.js
- Pandas
- OpenAI API

## License

MIT
