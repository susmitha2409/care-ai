"""
CareSim AI - Administration & Scenario Authoring Component
Enables clinical educators to author, AI-generate, review, validate, and approve scenarios.
"""
import streamlit as st
import json
from database import repository
from database.models import VirtualPatient, ClinicalReviewStatus
from agents.orchestrator import Orchestrator

def render_admin_portal(orchestrator: Orchestrator):
    st.title("⚙️ Scenario Authoring & Administration")
    st.write(
        "Author new fictional patient scenarios, generate drafts using AI, "
        "and conduct clinical reviews before approving scenarios for learner access."
    )

    tab_author, tab_manage = st.tabs(["✍️ Author New Scenario", "📂 Manage Existing Scenarios"])

    with tab_author:
        st.subheader("Generate Fictional Scenario with AI")
        st.caption("AI generates a draft scenario. All drafts must be reviewed and manually approved by a human educator.")

        with st.form("author_scenario_form"):
            col_cat, col_set = st.columns(2)
            with col_cat:
                category = st.selectbox(
                    "Scenario Category*",
                    [
                        "Frailty and fall risk",
                        "Complex long-term conditions",
                        "Mental health and social isolation",
                        "End-of-life and palliative care communication",
                        "Integrated care coordination",
                        "Cardiovascular and chest pain triage",
                        "Pediatric fever and parent communication",
                        "Substance misuse and harm reduction"
                    ]
                )
            with col_set:
                care_setting = st.selectbox(
                    "Care Setting*",
                    [
                        "Primary Care / GP Clinic",
                        "Community / Home Visit",
                        "Emergency Department Triage",
                        "Inpatient Hospital Ward",
                        "Hospice Day Care",
                        "Outpatient Specialty Clinic"
                    ]
                )

            col_diff, col_dur = st.columns(2)
            with col_diff:
                difficulty = st.selectbox("Difficulty Level*", ["Beginner", "Intermediate", "Advanced"])
            with col_dur:
                duration_mins = st.slider("Target Duration (minutes)", min_value=10, max_value=30, value=15, step=5)

            learning_objs = st.text_area(
                "Key Learning Objectives*",
                placeholder="e.g. Conduct a home fall risk assessment, explore polypharmacy, identify orthostatic dizziness...",
                height=80
            )

            extra_notes = st.text_input(
                "Additional Guidance / Clinical Parameters",
                placeholder="e.g. Patient is fearful of hospitals, reluctant to admit pain..."
            )

            generate_clicked = st.form_submit_button("🤖 Generate Draft Scenario with AI", type="primary", use_container_width=True)

        if generate_clicked:
            if not learning_objs.strip():
                st.error("Please enter at least one learning objective.")
            else:
                with st.spinner("Authoring Agent is generating structured fictional profile..."):
                    result = orchestrator.author_scenario(
                        category=category,
                        care_setting=care_setting,
                        difficulty=difficulty,
                        learning_objectives=learning_objs,
                        additional_notes=extra_notes
                    )
                    st.session_state["reviewing_draft"] = result["patient"]
                    st.session_state["reviewing_flags"] = result["flags"]
                    st.success("Draft scenario generated! Please review and validate below.")
                    st.rerun()

        # Display Draft Review Form if present
        if "reviewing_draft" in st.session_state:
            draft: VirtualPatient = st.session_state["reviewing_draft"]
            flags = st.session_state.get("reviewing_flags", [])

            st.markdown("---")
            st.subheader("🔍 Clinical Educator Review & Editing")
            
            if flags:
                st.markdown("**AI Consistency Checks & Notes:**")
                for f in flags:
                    st.warning(f)

            with st.form("review_edit_form"):
                e_name = st.text_input("Patient Name", value=draft.name)
                c_age, c_gen = st.columns(2)
                with c_age:
                    e_age = st.number_input("Age", min_value=1, max_value=110, value=draft.age)
                with c_gen:
                    e_gen = st.selectbox("Gender", ["Female", "Male", "Non-binary", "Other"], index=0 if draft.gender == "Female" else 1)

                e_presenting = st.text_area("Presenting Concerns", value=draft.presenting_concerns, height=80)
                e_med_hist = st.text_area("Medical History (one per line)", value="\n".join(draft.medical_history), height=80)
                e_meds = st.text_area("Current Medications (one per line)", value="\n".join(draft.current_medications), height=80)
                e_symptoms = st.text_area("Symptoms & Limitations (one per line)", value="\n".join(draft.symptoms_and_limitations), height=80)
                e_living = st.text_input("Living Situation", value=draft.living_situation)
                e_emotion = st.text_input("Emotional State", value=draft.emotional_state)
                e_comm = st.text_input("Communication Style", value=draft.communication_style)
                e_hidden = st.text_area("Hidden Facts (revealed only upon probing)", value="\n".join(draft.hidden_facts), height=90)
                e_assessment = st.text_area("Expected Assessment Focus Areas", value="\n".join(draft.expected_assessment_areas), height=90)

                st.markdown("---")
                c_draft_btn, c_appr_btn = st.columns(2)
                with c_draft_btn:
                    save_draft = st.form_submit_button("💾 Save as Unapproved Draft", use_container_width=True)
                with c_appr_btn:
                    approve_now = st.form_submit_button("✅ Clinically Validate & Approve", type="primary", use_container_width=True)

            if save_draft or approve_now:
                status = ClinicalReviewStatus.APPROVED if approve_now else ClinicalReviewStatus.DRAFT
                updated_patient = VirtualPatient(
                    id=draft.id,
                    name=e_name,
                    age=int(e_age),
                    gender=e_gen,
                    category=draft.category,
                    care_setting=draft.care_setting,
                    difficulty=draft.difficulty,
                    estimated_duration_mins=draft.estimated_duration_mins,
                    learning_objectives=draft.learning_objectives,
                    presenting_concerns=e_presenting,
                    medical_history=[x.strip() for x in e_med_hist.split("\n") if x.strip()],
                    current_medications=[x.strip() for x in e_meds.split("\n") if x.strip()],
                    symptoms_and_limitations=[x.strip() for x in e_symptoms.split("\n") if x.strip()],
                    living_situation=e_living,
                    emotional_state=e_emotion,
                    communication_style=e_comm,
                    patient_preferences=draft.patient_preferences,
                    hidden_facts=[x.strip() for x in e_hidden.split("\n") if x.strip()],
                    expected_assessment_areas=[x.strip() for x in e_assessment.split("\n") if x.strip()],
                    safety_rules=draft.safety_rules,
                    clinical_review_status=status,
                    is_custom=True
                )
                repository.save_patient(updated_patient)
                st.session_state.pop("reviewing_draft", None)
                st.session_state.pop("reviewing_flags", None)
                msg = "Scenario clinically validated and published to library!" if approve_now else "Draft saved."
                st.success(msg)
                st.rerun()

    with tab_manage:
        st.subheader("Registered Scenarios Directory")
        all_patients = repository.get_all_patients(approved_only=False)
        for p in all_patients:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown(f"**{p.name}** ({p.age}y, {p.gender})")
                st.caption(p.category)
            with c2:
                status_color = "green" if p.clinical_review_status == ClinicalReviewStatus.APPROVED else "orange"
                st.markdown(f":{status_color}[● {p.clinical_review_status.upper()}]")
            with c3:
                origin = "Custom / Authored" if p.is_custom else "Pre-seeded Core"
                st.caption(origin)
            with c4:
                if p.clinical_review_status != ClinicalReviewStatus.APPROVED:
                    if st.button("Approve", key=f"appr_{p.id}", use_container_width=True):
                        p.clinical_review_status = ClinicalReviewStatus.APPROVED
                        repository.save_patient(p)
                        st.success(f"{p.name} approved!")
                        st.rerun()
                else:
                    st.text("Ready")
            st.divider()
