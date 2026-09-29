"""
CareSim AI - Clinical Assessment Form Component
Structured 7-domain clinical history and diagnostic synthesis form.
Supports Save Draft, Edit, and Submit actions.
"""
import streamlit as st
from database import repository
from database.models import LearnerAssessment

def render_assessment_form(session_id: str, on_save_draft, on_proceed_to_care_plan):
    st.title("📋 Step 1: Clinical Assessment Documentation")
    st.write(
        "Synthesize your findings from the virtual patient consultation across the structured clinical domains below. "
        "You may save drafts as you work."
    )

    assessment = repository.get_assessment_by_session(session_id)
    session = repository.get_session_by_id(session_id)
    patient = repository.get_patient_by_id(session.patient_id) if session else None

    if patient:
        st.markdown(f"**Patient:** {patient.name} ({patient.age}y, {patient.gender}) | **Category:** {patient.category}")

    # Form Fields
    with st.form("clinical_assessment_form"):
        presenting_prob = st.text_area(
            "1. Presenting Problem & Chief Complaint*",
            value=assessment.presenting_problem if assessment else "",
            placeholder="Summarize the patient's primary reason for consultation in your own clinical words...",
            height=100
        )
        
        rel_history = st.text_area(
            "2. Relevant Medical, Pharmacological & Past History*",
            value=assessment.relevant_history if assessment else "",
            placeholder="Key past conditions, current prescribed/OTC medications, allergies, and adherence issues...",
            height=100
        )
        
        symptoms_findings = st.text_area(
            "3. Reported Symptoms & Functional Limitations*",
            value=assessment.symptoms_and_findings if assessment else "",
            placeholder="Specific physical or psychological symptoms, duration, triggers, and impact on daily activities...",
            height=100
        )

        risks = st.text_area(
            "4. Identified Clinical & Safety Risks (Red Flags)*",
            value=assessment.identified_risks if assessment else "",
            placeholder="Immediate or potential hazards (e.g. falls, medication side effects, self-harm, deterioration)...",
            height=100
        )

        social_factors = st.text_area(
            "5. Social, Psychosocial & Environmental Determinants*",
            value=assessment.social_and_environmental_factors if assessment else "",
            placeholder="Living arrangements, housing hazards, family/caregiver situation, financial distress, isolation...",
            height=100
        )

        further_tests = st.text_area(
            "6. Further Assessments or Investigations Required*",
            value=assessment.further_assessments_required if assessment else "",
            placeholder="Recommended physical exams, laboratory tests, vitals, cognitive screening, OT home hazard reviews...",
            height=90
        )

        next_steps = st.text_area(
            "7. Immediate Proposed Next Steps*",
            value=assessment.proposed_next_steps if assessment else "",
            placeholder="Priority clinical actions and short-term clinical management recommendations...",
            height=90
        )

        st.caption("* All assessments are evaluated in the final feedback report against educational learning objectives.")
        
        c_left, c_right = st.columns([1, 1])
        with c_left:
            save_draft_clicked = st.form_submit_button("💾 Save Assessment Draft", use_container_width=True)
        with c_right:
            submit_clicked = st.form_submit_button("Proceed to Care Plan ➡️", type="primary", use_container_width=True)

    data = {
        "presenting_problem": presenting_prob,
        "relevant_history": rel_history,
        "symptoms_and_findings": symptoms_findings,
        "identified_risks": risks,
        "social_and_environmental_factors": social_factors,
        "further_assessments_required": further_tests,
        "proposed_next_steps": next_steps,
    }

    if save_draft_clicked:
        new_assessment = LearnerAssessment(
            session_id=session_id,
            submitted=False,
            **data
        )
        repository.save_assessment(new_assessment)
        st.success("Assessment draft saved successfully!")
        on_save_draft()

    if submit_clicked:
        if not presenting_prob.strip() or not risks.strip():
            st.error("Please fill in at least the Presenting Problem and Identified Risks before proceeding.")
            return

        new_assessment = LearnerAssessment(
            session_id=session_id,
            submitted=True,
            **data
        )
        repository.save_assessment(new_assessment)
        on_proceed_to_care_plan(data)
