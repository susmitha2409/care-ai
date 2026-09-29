"""
CareSim AI - Session History Component
Enables learners to review previous simulation sessions, access evaluations, and export reports.
"""
import streamlit as st
from database import repository
from services import report_service

def render_session_history(on_view_session):
    st.title("📜 Simulation Session History")
    st.write("Browse through past patient consultations, review feedback reports, and track your clinical learning progression.")

    sessions = repository.get_all_sessions()
    if not sessions:
        st.info("No recorded simulation sessions yet. Start a case in the Patient Library!")
        return

    filter_status = st.selectbox("Filter by Status", ["All Sessions", "Evaluated", "Completed", "Active"])
    
    filtered = sessions
    if filter_status == "Evaluated":
        filtered = [s for s in filtered if s.status == "evaluated"]
    elif filter_status == "Completed":
        filtered = [s for s in filtered if s.status == "completed"]
    elif filter_status == "Active":
        filtered = [s for s in filtered if s.status == "active"]

    st.markdown(f"**Found {len(filtered)} session(s)**")

    for s in filtered:
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown(f"**{s.patient_name}**")
                st.caption(f"ID: `{s.id}` | {s.category}")
            with c2:
                st.text(f"📅 {s.started_at[:16]}")
                st.caption(f"Turns: {s.message_count}")
            with c3:
                duration_m = s.duration_seconds // 60
                duration_s = s.duration_seconds % 60
                st.text(f"⏱️ {duration_m}m {duration_s}s")
                status_color = "green" if s.status == "evaluated" else ("blue" if s.status == "completed" else "orange")
                st.markdown(f":{status_color}[● {s.status.title()}]")
            with c4:
                col_view, col_down = st.columns([1, 1])
                with col_view:
                    if st.button("Open", key=f"hist_open_{s.id}", use_container_width=True):
                        on_view_session(s.id)
                with col_down:
                    if s.status == "evaluated":
                        md_data = report_service.generate_markdown_report(s.id)
                        st.download_button("📥", data=md_data, file_name=f"report_{s.id}.md", mime="text/markdown", key=f"hist_dl_{s.id}", help="Download report")

            st.divider()
