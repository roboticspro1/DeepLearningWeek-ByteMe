import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, analyze_student_state, generate_micro_task, generate_quiz

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
    page = st.radio("Navigation", ["🚨 Action Dashboard", "⚡ Targeted Remediation", "🛠️ Self Remediation"])
    st.markdown("---")
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = st.text_input("OpenAI API Key", type="password")

# ==========================================
# PAGE 1: ACTION DASHBOARD
# ==========================================
if page == "🚨 Action Dashboard":
    st.title("Welcome back, Student 1")
    st.markdown("Here is your **Active Triage Queue**. We only show you what is breaking down, why, and exactly how to fix it.")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("🚨 Priority Action Center")
        urgent_topics = [t for t in student_state if t["Urgency"] > 30]
        
        if not urgent_topics:
            st.success("You are entirely up to date! No friction detected.")
        
        for data in urgent_topics:
            st.markdown(f"""
            <div class="triage-card" style="border-left: 4px solid {data['Color']};">
                <h4 style="margin:0; color: white;">{data['Topic']}</h4>
                <p style="margin:5px 0 0 0; color: #c5c6c7; font-size: 14px;">
                    <b>System Diagnosis:</b> {data['Diagnosis']} <br>
                    <b>Recent Accuracy Drop:</b> {int(data['Recent Mastery (%)'])}% (Overall: {int(data['Mastery (%)'])}%)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚡ Generate 5-Min Micro-Task for {data['Topic']}", key=f"btn_{data['Topic']}"):
                with st.spinner("Generating targeted intervention..."):
                    task = generate_micro_task(api_key, data['Topic'], data['Diagnosis'])
                    st.info(task)
            st.markdown("<br>", unsafe_allow_html=True)

    with col2:
        st.subheader("🕸️ Cognitive Profile Radar")
        categories = [d["Topic"] for d in student_state[:5]]
        accuracies = [d["Mastery (%)"] for d in student_state[:5]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=accuracies, theta=categories, fill='toself', line_color='#66fcf1'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    st.subheader("🔬 Telemetry & Root Cause Analysis")
    tabs = st.tabs([data["Topic"] for data in student_state])

    for i, data in enumerate(student_state):
        with tabs[i]:
            tc1, tc2 = st.columns(2)
            topic_history = df[df["topic"] == data["Topic"]].sort_values("timestamp")
            
            with tc1:
                st.markdown("**1. Accuracy Degradation Over Time**")
                fig_acc = px.bar(topic_history, x="timestamp", y="correct", labels={"correct": "Accuracy (1=Right, 0=Wrong)", "timestamp": "Attempt Time"}, color_discrete_sequence=[data["Color"]])
                fig_acc.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_acc, use_container_width=True)
                
            with tc2:
                st.markdown("**2. Execution Speed (Cognitive Load)**")
                fig_time = px.line(topic_history, x="timestamp", y="time_taken", markers=True, labels={"time_taken": "Time Taken (Seconds)", "timestamp": "Attempt Time"}, color_discrete_sequence=["#c5c6c7"])
                fig_time.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_time, use_container_width=True)

# ==========================================
# PAGE 2 & 3: QUIZ RENDERER LOGIC
# ==========================================
elif page in ["⚡ Targeted Remediation", "🛠️ Self Remediation"]:
    
    # 1. Page Header & Topic Selection
    if page == "⚡ Targeted Remediation":
        st.title("⚡ Auto-Remediation Engine")
        st.markdown("Interactive, AI-generated practice targeting your **highest-urgency friction point**.")
        weakest_topic_data = student_state[0] 
        selected_topic = weakest_topic_data["Topic"]
        diagnosis = weakest_topic_data["Diagnosis"]
        st.error(f"**System Target Locked:** {selected_topic} (Diagnosis: {diagnosis})")
        quiz_prefix = "target"
        
    else: # Self Remediation
        st.title("🛠️ Self Remediation Hub")
        st.markdown("Take control of your learning. Select any topic from your curriculum to generate a deep-dive diagnostic quiz.")
        # Create a dropdown from the dataset
        all_topics = df['topic'].unique()
        selected_topic = st.selectbox("Choose a topic to practice:", all_topics)
        diagnosis = "Student-initiated deep dive practice."
        quiz_prefix = "self"

    # 2. Session State Initialization (Clears if user switches topics or tabs)
    if "current_quiz_topic" not in st.session_state or st.session_state.current_quiz_topic != f"{quiz_prefix}_{selected_topic}":
        st.session_state.quiz_data = None
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.current_quiz_topic = f"{quiz_prefix}_{selected_topic}"

    # 3. Generate Button
    if st.button(f"Generate 4-Question Quiz on {selected_topic}", type="primary"):
        with st.spinner("AI is crafting detailed questions and mapping common misconceptions..."):
            quiz = generate_quiz(api_key, selected_topic, diagnosis, num_questions=4)
            if quiz:
                st.session_state.quiz_data = quiz
                st.session_state.user_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
            else:
                st.warning("Ensure your API key is entered in the sidebar.")

    st.divider()

    # 4. Quiz Rendering Engine
    if st.session_state.quiz_data:
        questions = st.session_state.quiz_data.get("questions", [])
        
        for i, q in enumerate(questions):
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**{q['question']}**")
            
            st.session_state.user_answers[i] = st.radio(
                "Select your answer:", 
                q['options'], 
                key=f"{quiz_prefix}_q_{i}", # Unique key prevents crossing answers between tabs
                disabled=st.session_state.quiz_submitted
            )
            st.markdown("<br>", unsafe_allow_html=True)
            
        if not st.session_state.quiz_submitted:
            if st.button("Submit Answers & See Explanations"):
                st.session_state.quiz_submitted = True
                st.rerun()
                
        # 5. Grading and Detailed Explanations
        if st.session_state.quiz_submitted:
            st.markdown("## 📊 Diagnostic Breakdown")
            score = 0
            
            for i, q in enumerate(questions):
                user_ans = st.session_state.user_answers.get(i)
                correct_ans = q['correct_answer']
                
                if user_ans == correct_ans:
                    score += 1
                    st.success(f"**Q{i+1}: Correct!** You chose {user_ans}")
                else:
                    st.error(f"**Q{i+1}: Incorrect.** You chose *{user_ans}*. The correct answer is *{correct_ans}*.")
                
                # The detailed breakdown is placed inside a clean info box
                st.info(f"💡 **AI Tutor Detailed Breakdown:** \n\n {q['detailed_explanation']}")
                st.markdown("---")
                
            st.metric("Final Remediation Score", f"{score} / {len(questions)}")
            
            if st.button("Clear and Retry"):
                st.session_state.quiz_data = None
                st.session_state.quiz_submitted = False
                st.rerun()