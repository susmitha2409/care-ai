"""
CareSim AI - Virtual Patient Library Component
Filterable, searchable directory of verified fictional patient scenarios.
"""
import streamlit as st
from database import repository
from database.models import VirtualPatient

def render_patient_library(on_select_patient):
    st.title("📚 Virtual Patient Library")
    st.write(
        "Explore realistic fictional patient scenarios designed to practice clinical history taking, "
        "risk identification, communication, and person-centred care planning."
    )

    st.info("ℹ️ All patient profiles in this library are fictional and created solely for healthcare simulation and education.")

    patients = repository.get_all_patients(approved_only=True)

    # Filter Bar
    f1, f2, f3 = st.columns([2, 1.5, 1.5])
    with f1:
        search_query = st.text_input("🔍 Search by name or presenting problem", placeholder="e.g. Margaret, diabetes, fall...")
    with f2:
        categories = ["All Categories"] + sorted(list(set(p.category for p in patients)))
        selected_category = st.selectbox("Category", categories)
    with f3:
        difficulties = ["All Difficulties", "Beginner", "Intermediate", "Advanced"]
        selected_difficulty = st.selectbox("Difficulty", difficulties)

    # Filter logic
    filtered = patients
    if search_query:
        q = search_query.lower()
        filtered = [
            p for p in filtered 
            if q in p.name.lower() or q in p.presenting_concerns.lower() or q in p.category.lower()
        ]
    if selected_category != "All Categories":
        filtered = [p for p in filtered if p.category == selected_category]
    if selected_difficulty != "All Difficulties":
        filtered = [p for p in filtered if p.difficulty.lower() == selected_difficulty.lower()]

    st.markdown(f"**Showing {len(filtered)} scenario(s)**")

    if not filtered:
        st.warning("No scenarios matched your selected filters.")
        return

    for p in filtered:
        with st.container():
            st.markdown(f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; background: white; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0; color: #0f766e; font-size: 1.3rem;">{p.name} <span style="font-size: 0.95rem; color: #64748b; font-weight: normal;">({p.age}y, {p.gender})</span></h3>
                            <div style="margin-top: 6px;">
                                <span style="background: #e0f2fe; color: #0369a1; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 500; margin-right: 8px;">🏷️ {p.category}</span>
                                <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; margin-right: 8px;">🏥 {p.care_setting}</span>
                                <span style="background: #fef3c7; color: #92400e; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;">⚡ {p.difficulty}</span>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_details, col_action = st.columns([3, 1])
            with col_details:
                st.markdown(f"**Presenting Situation:** {p.presenting_concerns}")
                with st.expander("🎯 Learning Objectives & Assessment Focus"):
                    st.markdown("**Learning Objectives:**")
                    for obj in p.learning_objectives:
                        st.markdown(f"- {obj}")
                    st.markdown(f"**Estimated Session Duration:** ~{p.estimated_duration_mins} minutes")
            with col_action:
                st.write("")
                if st.button("Begin Simulation 🩺", key=f"start_sim_{p.id}", type="primary", use_container_width=True):
                    on_select_patient(p.id)

            st.markdown("<hr style='border: 0; border-top: 1px dashed #cbd5e1; margin: 15px 0;'>", unsafe_allow_html=True)
