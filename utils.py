import pandas as pd
from openai import OpenAI

def load_data(filepath="data.csv"):
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def analyze_student_state(df):
    """Analyzes all data and returns a contradiction-free diagnostic profile per topic."""
    topics_analysis = []
    
    for topic in df["topic"].unique():
        tdf = df[df["topic"] == topic].sort_values("timestamp")
        
        # 1. Base Metrics
        overall_accuracy = tdf["correct"].mean()
        avg_time = tdf["time_taken"].mean()
        
        # 2. Trend & Decay Detection (Split history in half)
        mid = max(1, len(tdf) // 2)
        past_acc = tdf.iloc[:mid]["correct"].mean()
        recent_acc = tdf.iloc[mid:]["correct"].mean()
        
        # 3. CONTRADICTION-FREE DIAGNOSTIC LOGIC
        # If they used to know it, but recently failed -> Active Decay
        if past_acc - recent_acc > 0.20:
            diagnosis = "Active Decay (Forgetting)"
            urgency = 95
            color = "#ff4b4b" # Red
        # If they are fast but wrong -> Careless/Fatigue
        elif overall_accuracy < 0.5 and avg_time < 40:
            diagnosis = "Careless Errors / Fatigue"
            urgency = 80
            color = "#ffb74d" # Orange
        # If they are slow and wrong -> Conceptual Gap
        elif overall_accuracy < 0.5 and avg_time >= 40:
            diagnosis = "Deep Conceptual Gap"
            urgency = 90
            color = "#ff4b4b" # Red
        # If they are right, but taking way too long -> Translation/Execution Bottleneck
        elif overall_accuracy >= 0.5 and avg_time > 120:
            diagnosis = "High Cognitive Load (Slow Execution)"
            urgency = 60
            color = "#4dabf5" # Blue
        # Normal, good state
        else:
            diagnosis = "Retained Mastery"
            urgency = 10
            color = "#4caf50" # Green
            
        topics_analysis.append({
            "Topic": topic,
            "Mastery (%)": overall_accuracy * 100,
            "Recent Mastery (%)": recent_acc * 100,
            "Avg Time (s)": avg_time,
            "Diagnosis": diagnosis,
            "Urgency": urgency,
            "Color": color
        })
        
    # Sort by urgency so the most critical items are always first
    return sorted(topics_analysis, key=lambda x: x["Urgency"], reverse=True)

def generate_micro_task(api_key, topic, diagnosis):
    if not api_key:
        return "⚠️ Enter API Key in the sidebar to generate a micro-task."
    
    prompt = f"""
    The student is studying '{topic}'. 
    Their diagnostic system flagged them with: '{diagnosis}'.
    
    Do NOT give generic advice. Give them a single, highly specific 5-minute 'Micro-Task' to unblock them immediately.
    Format as:
    **Action:** [One sentence what to do]
    **Why:** [One sentence why this fixes their specific {diagnosis} issue]
    """
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Error reaching AI."