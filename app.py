import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, analyze_student_state, generate_micro_task

# --- SETUP ---
st.set_page_config(page_title="Cognitive Triage", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .reportview-container { background: #0b0c10; color: white;}
    .stMetric { background-color: #1f2833; border-radius: 8px; padding: 15px; border-left: 4px solid #66fcf1; }
    .triage-card { background-color: #1f2833; padding: 20px; border-radius: 10px; border: 1px solid #2d303e; margin-bottom: 15px;}
    hr { border-color: #2d303e; }
</style>
""", unsafe_allow_html=True)

df = load_data()
student_state = analyze_student_state(df)

with st.sidebar:
    st.title("⚡ CogniTriage")
    st.markdown("Moving from passive analytics to active intervention.")
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key (For Unblocker)", type="password")

# --- HEADER ---
st.title("Welcome back, Student 1")
st.markdown("Here is your **Active Triage Queue**. We only show you what is breaking down, why, and exactly how to fix it.")
st.markdown("<br>", unsafe_allow_html=True)

# --- TOP ROW: THE TRIAGE QUEUE (ACTION FIRST) ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🚨 Priority Action Center")
    st.markdown("*Topics actively decaying or blocking your progress.*")
    
    # Filter to only show actionable/urgent things (Urgency > 30)
    urgent_topics = [t for t in student_state if t["Urgency"] > 30]
    
    if not urgent_topics:
        st.success("You are entirely up to date! No friction detected.")
    
    for data in urgent_topics:
        # Custom HTML for clean SaaS-like cards
        st.markdown(f"""
        <div class="triage-card" style="border-left: 4px solid {data['Color']};">
            <h4 style="margin:0; color: white;">{data['Topic']}</h4>
            <p style="margin:5px 0 0 0; color: #c5c6c7; font-size: 14px;">
                <b>System Diagnosis:</b> {data['Diagnosis']} <br>
                <b>Recent Accuracy Drop:</b> {int(data['Recent Mastery (%)'])}% (Overall: {int(data['Mastery (%)'])}%)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # The AI "Unblock Me" Button right inside the card flow
        if st.button(f"⚡ Generate 5-Min Micro-Task for {data['Topic']}", key=f"btn_{data['Topic']}"):
            with st.spinner("Generating targeted intervention..."):
                task = generate_micro_task(api_key, data['Topic'], data['Diagnosis'])
                st.info(task)
        st.markdown("<br>", unsafe_allow_html=True)

with col2:
    st.subheader("🕸️ Cognitive Profile Radar")
    st.markdown("*Your balance across speed, accuracy, and retention.*")
    
    # Build a beautiful Plotly Radar Chart
    categories = [d["Topic"] for d in student_state[:5]] # Top 5 topics
    accuracies = [d["Mastery (%)"] for d in student_state[:5]]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=accuracies,
        theta=categories,
        fill='toself',
        name='Mastery %',
        line_color='#66fcf1'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- BOTTOM ROW: DEEP ANALYTICS FOR ROOT CAUSE ---
st.subheader("🔬 Telemetry & Root Cause Analysis")
st.markdown("Why did the system flag these issues? Toggle the tabs to see your raw cognitive telemetry.")

tabs = st.tabs([data["Topic"] for data in student_state])

for i, data in enumerate(student_state):
    with tabs[i]:
        tc1, tc2 = st.columns(2)
        topic_history = df[df["topic"] == data["Topic"]].sort_values("timestamp")
        
        with tc1:
            st.markdown("**1. Accuracy Degradation Over Time**")
            # Bar chart comparing the individual attempts (Correct=1, Wrong=0) over time
            fig_acc = px.bar(topic_history, x="timestamp", y="correct", 
                             labels={"correct": "Accuracy (1=Right, 0=Wrong)", "timestamp": "Attempt Time"},
                             color_discrete_sequence=[data["Color"]])
            fig_acc.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_acc, use_container_width=True)
            
        with tc2:
            st.markdown("**2. Execution Speed (Cognitive Load)**")
            # Line chart showing if they are taking longer and longer to solve
            fig_time = px.line(topic_history, x="timestamp", y="time_taken", markers=True,
                               labels={"time_taken": "Time Taken (Seconds)", "timestamp": "Attempt Time"},
                               color_discrete_sequence=["#c5c6c7"])
            fig_time.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_time, use_container_width=True)