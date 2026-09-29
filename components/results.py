"""
CareSim AI - Results & Evaluation Feedback Component
Displays structured rubric scores, strengths, improvement areas, and downloadable report.
"""
import streamlit as st
from database import repository
from services import report_service

def render_results(session_id: str, on_restart_simulation):
    eval_report = repository.get_evaluation_by_session(session_id)
    session = repository.get_session_by_id(session_id)
    if not session:
        st.error("Session not found.")
        return

    patient = repository.get_patient_by_id(session.patient_id)
    patient_name = patient.name if patient else "Patient"

    st.markdown("""
        <div style="background: linear-gradient(135deg, #047857 0%, #0f766e 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 2rem; color: #ffffff;">Simulation Evaluation & Feedback</h1>
            <p style="margin-top: 4px; opacity: 0.9; color: #ecfdf5;">Preliminary Educational Assessment Report</p>
        </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ Disclaimer: Scores and feedback are AI-generated for educational simulation practice only and do NOT represent formal clinical competency certification.")

    if not eval_report:
        st.info("No evaluation record found for this session yet.")
        return

    # Top KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Overall Score", f"{eval_report.overall_score} / 100")
    with kpi2:
        st.metric("Simulation Turns", session.message_count)
    with kpi3:
        mins = session.duration_seconds // 60
        st.metric("Consultation Time", f"{mins} mins" if mins > 0 else "< 1 min")
    with kpi4:
        engine = "Demo Simulation" if eval_report.is_demo else "Groq Evaluator"
        st.metric("Evaluation Engine", engine)

    st.markdown("---")

    # Overall Summary
    st.subheader("Executive Educational Summary")
    st.markdown(f"> *{eval_report.overall_summary}*")

    st.markdown("<br>", unsafe_allow_html=True)

    # Rubric Domain Scores
    st.subheader("📊 Rubric Domain Breakdown")
    for key, item in eval_report.rubric_scores.items():
        title = key.replace("_", " ").title()
        col_name, col_bar, col_score = st.columns([2, 4, 1])
        with col_name:
            st.markdown(f"**{title}**")
            st.caption(f"Weight: {int(item.weight * 100)}%")
        with col_bar:
            st.progress(item.score / 100.0)
            st.caption(item.feedback)
        with col_score:
            st.markdown(f"### {item.score}%")
        st.divider()

    # Two column: Strengths vs Areas for Improvement
    c_str, c_imp = st.columns(2)
    with c_str:
        st.subheader("🌟 Key Strengths Demonstrated")
        for s in eval_report.strengths:
            st.markdown(f"- ✅ **{s}**")

    with c_imp:
        st.subheader("🎯 Areas for Growth")
        for imp in eval_report.areas_for_improvement:
            st.markdown(f"- 💡 **{imp}**")

    st.markdown("---")

    # Latent Details & Missed Areas
    col_missed, col_risks = st.columns(2)
    with col_missed:
        st.subheader("🔍 Missed / Latent Inquiries")
        if eval_report.missed_questions_or_areas:
            for m in eval_report.missed_questions_or_areas:
                st.markdown(f"- ⚠️ {m}")
        else:
            st.write("Comprehensive information coverage demonstrated.")

    with col_risks:
        st.subheader("🛡️ Risk Factor Considerations")
        if eval_report.missing_risk_considerations:
            for r in eval_report.missing_risk_considerations:
                st.markdown(f"- ⚠️ {r}")
        else:
            st.write("All core acute and chronic risk factors addressed.")

    st.markdown("---")

    # Care Plan Feedback
    if eval_report.care_plan_feedback:
        st.subheader("📝 Care Plan Critique")
        st.info(eval_report.care_plan_feedback)

    # Suggested Learning Activities
    if eval_report.suggested_learning_activities:
        st.subheader("📚 Recommended Learning Activities")
        for act in eval_report.suggested_learning_activities:
            st.markdown(f"- 📖 {act}")

    st.markdown("---")

    # Transcripts & Submitted Work Expander
    with st.expander("🔎 Review Full Consultation Dialogue"):
        msgs = repository.get_messages_for_session(session_id)
        for m in msgs:
            speaker = "Learner" if m.sender == "learner" else patient_name
            flag_note = " 🚩 [Flagged]" if m.flagged else ""
            st.markdown(f"**{speaker} ({m.timestamp[11:19]}):**{flag_note}\n\n{m.content}\n")
            st.divider()

    with st.expander("📝 Review Submitted Assessment & Care Plan"):
        assessment = repository.get_assessment_by_session(session_id)
        care_plan = repository.get_care_plan_by_session(session_id)
        if assessment:
            st.markdown("### Clinical Assessment")
            st.markdown(f"**Chief Complaint:** {assessment.presenting_problem}")
            st.markdown(f"**Relevant History:** {assessment.relevant_history}")
            st.markdown(f"**Symptoms & Findings:** {assessment.symptoms_and_findings}")
            st.markdown(f"**Identified Risks:** {assessment.identified_risks}")
            st.markdown(f"**Social Factors:** {assessment.social_and_environmental_factors}")
            st.markdown(f"**Further Tests:** {assessment.further_assessments_required}")
            st.markdown(f"**Next Steps:** {assessment.proposed_next_steps}")
        if care_plan:
            st.markdown("### Care Plan")
            st.markdown(f"**Identified Needs:** {care_plan.identified_needs}")
            st.markdown(f"**Preferences & Goals:** {care_plan.patient_preferences_and_goals}")
            st.markdown(f"**Interventions:** {care_plan.proposed_interventions}")
            st.markdown(f"**MDT Services:** {care_plan.multidisciplinary_team_services}")
            st.markdown(f"**Follow-Up:** {care_plan.follow_up_and_monitoring}")
            st.markdown(f"**Escalation:** {care_plan.risks_and_escalation}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Export & Navigation
    md_content = report_service.generate_markdown_report(session_id)
    c_down, c_new = st.columns([1, 1])
    with c_down:
        st.download_button(
            label="📥 Download Clinical Report (Markdown)",
            data=md_content,
            file_name=f"caresim_report_{session_id}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with c_new:
        if st.button("🔄 Start Another Simulation", type="primary", use_container_width=True):
            on_restart_simulation()
