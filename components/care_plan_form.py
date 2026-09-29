"""
CareSim AI - Person-Centred Care Plan Component
Structured care planning form capturing goals, multidisciplinary coordination, and safety escalation.
"""
import streamlit as st
from database import repository
from database.models import CarePlan

def render_care_plan_form(session_id: str, on_back_to_assessment, on_submit_final_evaluation):
    st.title("🌱 Step 2: Person-Centred Care Planning")
    st.write(
        "Design a tailored, person-centred care plan addressing the patient's holistic needs, "
        "personal preferences, and safety safeguards."
    )

    care_plan = repository.get_care_plan_by_session(session_id)
    session = repository.get_session_by_id(session_id)
    patient = repository.get_patient_by_id(session.patient_id) if session else None

    if patient:
        st.markdown(f"**Patient:** {patient.name} | **Care Setting:** {patient.care_setting}")

    st.markdown(
        "<div style='background: #f0fdf4; border-left: 4px solid #16a34a; padding: 10px 14px; border-radius: 4px; font-size: 0.85rem; color: #166534; margin-bottom: 16px;'>"
        "<strong>Person-Centred Principle:</strong> Ensure the patient's individual voice, autonomy, and values are reflected alongside clinical interventions.</div>",
        unsafe_allow_html=True
    )

    with st.form("care_plan_form"):
        needs = st.text_area(
            "1. Identified Health and Wellbeing Needs*",
            value=care_plan.identified_needs if care_plan else "",
            placeholder="Key physical, psychological, functional, and social needs requiring support...",
            height=90
        )

        goals = st.text_area(
            "2. Patient Preferences, Autonomy & Personal Goals*",
            value=care_plan.patient_preferences_and_goals if care_plan else "",
            placeholder="What matters most to the patient? (e.g. maintaining independence at home, walking granddaughter down aisle)...",
            height=90
        )

        interventions = st.text_area(
            "3. Proposed Support & Clinical Interventions*",
            value=care_plan.proposed_interventions if care_plan else "",
            placeholder="Specific evidence-based medical, nursing, rehabilitation, or assistive interventions...",
            height=100
        )

        team = st.text_area(
            "4. Multidisciplinary Team & Community Services*",
            value=care_plan.multidisciplinary_team_services if care_plan else "",
            placeholder="Relevant professionals to involve (e.g. GP, Physio, OT, Social Work, Hospice, Community Pharmacy)...",
            height=90
        )

        monitoring = st.text_area(
            "5. Follow-Up, Review Milestones & Monitoring*",
            value=care_plan.follow_up_and_monitoring if care_plan else "",
            placeholder="Target timelines for review, metrics of improvement, and monitoring plan...",
            height=80
        )

        risks_escalation = st.text_area(
            "6. Deterioration Risks & Escalation Protocol*",
            value=care_plan.risks_and_escalation if care_plan else "",
            placeholder="Red-flag triggers, emergency contact guidance, and contingency actions if condition declines...",
            height=90
        )

        st.caption("Educational Exercise: Plans will not trigger actual clinical orders or real-world interventions.")

        col1, col2, col3 = st.columns([1, 1, 1.5])
        with col1:
            back_clicked = st.form_submit_button("⬅️ Back to Assessment", use_container_width=True)
        with col2:
            save_draft_clicked = st.form_submit_button("💾 Save Plan Draft", use_container_width=True)
        with col3:
            submit_final_clicked = st.form_submit_button("Submit for AI Evaluation 🚀", type="primary", use_container_width=True)

    data = {
        "identified_needs": needs,
        "patient_preferences_and_goals": goals,
        "proposed_interventions": interventions,
        "multidisciplinary_team_services": team,
        "follow_up_and_monitoring": monitoring,
        "risks_and_escalation": risks_escalation
    }

    if back_clicked:
        on_back_to_assessment()

    if save_draft_clicked:
        new_plan = CarePlan(
            session_id=session_id,
            submitted=False,
            **data
        )
        repository.save_care_plan(new_plan)
        st.success("Care plan draft saved successfully!")

    if submit_final_clicked:
        if not needs.strip() or not goals.strip():
            st.error("Please complete at least Identified Needs and Patient Preferences & Goals before submitting.")
            return

        new_plan = CarePlan(
            session_id=session_id,
            submitted=True,
            **data
        )
        repository.save_care_plan(new_plan)
        on_submit_final_evaluation(data)
