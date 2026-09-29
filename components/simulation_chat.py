"""
CareSim AI - Simulation Chat Component
Real-time conversational interface with the Virtual Patient Agent.
Supports multi-turn interaction, suggested questions, response flagging, and safety alerts.
"""
import streamlit as st
import datetime
from database import repository
from services import simulation_service
from agents.orchestrator import Orchestrator

def render_simulation_chat(session_id: str, orchestrator: Orchestrator, on_finish_consultation):
    session = repository.get_session_by_id(session_id)
    if not session:
        st.error("Simulation session not found.")
        return

    patient = repository.get_patient_by_id(session.patient_id)
    if not patient:
        st.error("Patient profile not found.")
        return

    # Header Card with Patient Info and Session Controls
    with st.container():
        h_left, h_mid, h_right = st.columns([3, 2, 2])
        with h_left:
            st.markdown(f"### 🩺 Consulting: {patient.name}")
            st.caption(f"{patient.age}y {patient.gender} | {patient.category} | {patient.care_setting}")
        with h_mid:
            mode_badge = "🟡 Demo Mode" if session.is_demo else "🟢 Groq LLM"
            st.markdown(f"**Engine:** `{mode_badge}`")
            # Calculate elapsed time
            try:
                start_dt = datetime.datetime.strptime(session.started_at, "%Y-%m-%d %H:%M:%S")
                elapsed_secs = int((datetime.datetime.now() - start_dt).total_seconds())
                elapsed_str = simulation_service.format_duration(elapsed_secs)
            except Exception:
                elapsed_str = "Active"
            st.markdown(f"**Elapsed Time:** ⏱️ `{elapsed_str}`")
        with h_right:
            st.write("")
            if st.button("⏹️ Complete Consultation", type="secondary", use_container_width=True):
                st.session_state["confirm_end_dialog"] = True

    # End Session Confirmation Dialog
    if st.session_state.get("confirm_end_dialog", False):
        st.warning("Are you ready to conclude your conversation with the patient and proceed to the Clinical Assessment & Care Plan?")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("Yes, Finish & Assess 📝", type="primary", use_container_width=True):
                orchestrator.end_simulation(session_id)
                st.session_state["confirm_end_dialog"] = False
                on_finish_consultation(session_id)
                st.rerun()
        with d_col2:
            if st.button("Cancel & Continue Chatting", use_container_width=True):
                st.session_state["confirm_end_dialog"] = False
                st.rerun()
        st.markdown("---")

    # Presenting Concern banner
    with st.expander("📋 Patient Brief & Presenting Concern", expanded=False):
        st.write(patient.presenting_concerns)
        st.caption("Tip: Inquire about symptoms, living context, daily impact, and medication habits. Patient reveals latent details progressively.")

    # Suggested Opening Questions
    suggested = simulation_service.get_suggested_questions(patient)
    st.markdown("**Suggested Questions:**")
    sq_cols = st.columns(len(suggested))
    for i, q in enumerate(suggested):
        with sq_cols[i]:
            if st.button(f"💡 Q{i+1}", key=f"sq_btn_{i}", help=q, use_container_width=True):
                st.session_state["quick_prompt_fill"] = q
                st.rerun()

    st.markdown("---")

    # Conversation History Display
    messages = repository.get_messages_for_session(session_id)
    chat_container = st.container()

    with chat_container:
        for m in messages:
            if m.sender == "learner":
                with st.chat_message("user", avatar="🧑‍⚕️"):
                    st.write(m.content)
                    st.caption(f"Sent at {m.timestamp[11:19]}")
            else:
                with st.chat_message("assistant", avatar="👤"):
                    st.write(m.content)
                    c_time, c_flag = st.columns([4, 1])
                    with c_time:
                        engine_note = " (Simulated)" if m.is_demo else " (Groq)"
                        st.caption(f"{patient.name} • {m.timestamp[11:19]}{engine_note}")
                    with c_flag:
                        if m.flagged:
                            st.caption("🚩 Flagged for review")
                        elif m.id:
                            if st.button("🚩 Flag", key=f"flag_{m.id}", help="Flag inaccurate or unsafe response"):
                                repository.flag_message(m.id)
                                st.toast("Response flagged for clinical review.")
                                st.rerun()

    # User Input Field
    default_text = st.session_state.pop("quick_prompt_fill", "")
    with st.container():
        user_input = st.chat_input("Ask the patient a question (e.g. How has your walking been?)...")
        if default_text and not user_input:
            user_input = default_text

        if user_input:
            # Check for simulated life-threatening medical emergency
            lowered = user_input.lower()
            if any(term in lowered for term in ["cardiac arrest", "unresponsive", "bleeding out", "overdose now"]):
                st.error("🚨 EMERGENCY PROTOCOL TRIGGER: If a real-world medical emergency is suspected, immediately stop simulation and call emergency services (911/999/112).")
            
            with st.spinner(f"{patient.name} is responding..."):
                orchestrator.process_learner_message(session_id, user_input)
            st.rerun()
