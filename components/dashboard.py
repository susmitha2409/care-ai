"""
CareSim AI - Dashboard Component
Displays high-level educational metrics, recent simulation activity, and quick-launch options.
"""
import streamlit as st
from database import repository
import config

def render_dashboard(on_start_simulation_click, on_view_session_click):
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f766e 0%, #1e3a8a 100%); padding: 24px; border-radius: 12px; color: white; margin-bottom: 24px;">
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: #ffffff;">CareSim AI</h1>
            <p style="margin-top: 6px; font-size: 1.1rem; opacity: 0.95; color: #e0f2fe;">Agentic Virtual Patient Simulation Platform for Healthcare Education</p>
            <div style="margin-top: 14px; font-size: 0.85rem; background: rgba(255,255,255,0.15); padding: 8px 14px; border-radius: 6px; display: inline-block;">
                ⚠️ Educational simulation only. Not a medical device or diagnostic tool.
            </div>
        </div>
    """, unsafe_allow_html=True)

    metrics = repository.get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Available Scenarios", value=metrics["total_scenarios"])
    with col2:
        st.metric(label="Total Simulations", value=metrics["total_sessions"])
    with col3:
        st.metric(label="Evaluations Completed", value=metrics["completed_sessions"])
    with col4:
        st.metric(label="Average Educational Score", value=f"{metrics['average_score']}%" if metrics["average_score"] > 0 else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Action Callout
    c_btn1, c_btn2 = st.columns([2, 1])
    with c_btn1:
        st.subheader("Ready to Practice?")
        st.write(
            "Select from five comprehensive clinical scenarios including frailty, chronic diseases, "
            "mental health, palliative care, and stroke rehabilitation to refine your communication and reasoning."
        )
    with c_btn2:
        st.write("")
        st.write("")
        if st.button("🚀 Start New Simulation", type="primary", use_container_width=True):
            on_start_simulation_click()

    st.markdown("---")

    # Recent Activity
    st.subheader("Recent Simulation Activity")
    sessions = repository.get_all_sessions()
    if not sessions:
        st.info("No simulation sessions recorded yet. Start your first clinical scenario above!")
    else:
        for s in sessions[:5]:
            with st.container():
                cols = st.columns([3, 2, 2, 2, 2])
                with cols[0]:
                    st.markdown(f"**{s.patient_name}**")
                    st.caption(s.category)
                with cols[1]:
                    st.text(f"📅 {s.started_at[:16]}")
                with cols[2]:
                    duration_text = f"{s.duration_seconds // 60}m {s.duration_seconds % 60}s" if s.duration_seconds > 0 else "< 1m"
                    st.text(f"⏱️ {duration_text}")
                with cols[3]:
                    status_color = "green" if s.status == "evaluated" else ("blue" if s.status == "completed" else "orange")
                    st.markdown(f":{status_color}[● {s.status.title()}]")
                with cols[4]:
                    if st.button("View", key=f"dash_sess_{s.id}", use_container_width=True):
                        on_view_session_click(s.id)
                st.divider()

    # Safety Notice Banner
    st.markdown(
        f"<div style='background-color: #f8fafc; border-left: 4px solid #0f766e; padding: 12px 16px; border-radius: 4px; font-size: 0.85rem; color: #334155; margin-top: 30px;'>"
        f"<strong>Healthcare Simulation Notice:</strong> {config.DISCLAIMER_TEXT}</div>",
        unsafe_allow_html=True
    )
