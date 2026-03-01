# CogniTriage ⚡

[![Repo](https://img.shields.io/badge/repo-roboticspro1/DeepLearningWeek--ByteMe-blue)](https://github.com/roboticspro1/DeepLearningWeek-ByteMe)

**Moving from passive analytics to active intervention.**

CogniTriage is an AI-powered cognitive triage system that analyzes student learning patterns in real-time and generates personalized micro-interventions to unblock learning friction.

Quick links
- Repository: https://github.com/roboticspro1/DeepLearningWeek-ByteMe
- Run (local): `streamlit run app.py`

Quick note on API keys
- You can paste your OpenAI API key in the Streamlit sidebar at runtime.
- Or set the environment variable `OPENAI_API_KEY` before running:

```bash
export OPENAI_API_KEY="sk-..."
streamlit run app.py
```

Streamlit also supports a `.streamlit/secrets.toml` file with:

```toml
[openai]
api_key = "sk-..."
```


## Overview

Instead of overwhelming dashboards full of metrics, CogniTriage shows only what matters: **What is breaking down, why, and exactly how to fix it.**

### Key Features

- **Priority Action Center**: Displays only urgent topics where students are struggling (urgency > 30)
- **Contradiction-Free Diagnostics**: Intelligent classification of learning issues:
  - Active Decay (Forgetting) - Used to know it, but recently failed
  - Careless Errors/Fatigue - Fast but inaccurate responses
  - Deep Conceptual Gap - Slow and inaccurate
  - High Cognitive Load - Accurate but too slow
  - Retained Mastery - Performing well
- **Cognitive Profile Radar**: Visual summary of mastery across top 5 topics
- **AI-Generated Micro-Tasks**: 5-minute targeted interventions powered by GPT-4o-mini
- **Root Cause Telemetry**: Deep analytics showing trends, decay detection, and performance metrics

## Project Structure

```
.
├── app.py              # Streamlit UI and main application logic
├── utils.py            # Core analysis functions and AI integration
├── data.csv            # Student performance data (timestamp, topic, correct, time_taken)
├── requirements.txt    # Python dependencies
├── lib/                # Frontend libraries
│   ├── tom-select/     # Dropdown UI component
│   ├── vis-9.1.2/      # Network visualization library
│   └── bindings/       # Custom JS bindings
└── graph.html          # Generated network visualization
```

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for AI-generated micro-tasks)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/roboticspro1/DeepLearningWeek-ByteMe.git
   cd DeepLearningWeek-ByteMe
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser to `http://localhost:8501`

## Usage

1. **Enter OpenAI API Key**: Paste your API key in the sidebar under "OpenAI API Key (For Unblocker)"
2. **View Your Triage Queue**: The Priority Action Center displays topics requiring intervention, ordered by urgency
3. **Generate Micro-Tasks**: Click "⚡ Generate 5-Min Micro-Task" for AI-generated, targeted learning activities
4. **Analyze Cognitive Profile**: View your mastery radar and deep telemetry in the tabs below

## Data Format

The `data.csv` file should contain the following columns:

| Column | Description |
|--------|-------------|
| `timestamp` | When the activity occurred (ISO format) |
| `topic` | Topic being studied |
| `correct` | 1 if answer was correct, 0 if incorrect |
| `time_taken` | Time taken to answer (seconds) |

### Example:
```csv
timestamp,topic,correct,time_taken
2024-01-15T10:30:00,Calculus,1,45
2024-01-15T10:35:00,Calculus,0,120
2024-01-15T11:00:00,Linear Algebra,1,30
```

## Diagnostic Logic

The system uses contradiction-free logic to diagnose learning issues:

```python
1. Active Decay: past_accuracy - recent_accuracy > 20% → Urgency: 95 🔴
2. Careless/Fatigue: accuracy < 50% AND time < 40s → Urgency: 80 🟠
3. Deep Gap: accuracy < 50% AND time ≥ 40s → Urgency: 90 🔴
4. High Load: accuracy ≥ 50% AND time > 120s → Urgency: 60 🔵
5. Retained: Everything else → Urgency: 10 🟢
```

## Architecture

- **Frontend**: Streamlit (Python-based reactive UI)
- **Analytics Engine**: Pandas for data processing and trend detection
- **AI Backend**: OpenAI GPT-4o-mini for generating micro-tasks
- **Visualization**: Plotly (radar charts, graphs)

## Technologies Used

- `streamlit` - Interactive web UI
- `pandas` & `numpy` - Data analysis
- `openai` - AI-powered interventions
- `plotly` - Data visualization

## Contributing

This is a ByteMe hackathon project. Contributions welcome!

## License

MIT

---

**Built with ❤️ at Deep Learning NTU Week**
