"""
CareSim AI – Agentic Virtual Patient Simulation Platform
Main Streamlit Application Entrypoint
"""
import streamlit as st
import os
import config
from database import db, repository
from services.groq_service import GroqService
from agents.orchestrator import Orchestrator
from components.dashboard import render_dashboard
from components.patient_library import render_patient_library
from components.simulation_chat import render_simulation_chat
from components.assessment_form import render_assessment_form
from components.care_plan_form import render_care_plan_form
from components.results import render_results
from components.session_history import render_session_history
from components.admin import render_admin_portal

# Configure Streamlit Page
st.set_page_config(
    page_title="CareSim AI – Virtual Patient Simulation",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Healthcare Clean Aesthetic (Muted Teal, Navy, Accessible Contrast)
st.markdown("""
<style>
    /* Base typography and clean white theme */
    .main {
        background-color: #ffffff;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    
    /* Primary buttons in healthcare teal */
    .stButton > button[kind="primary"] {
        background-color: #0f766e;
        border-color: #0f766e;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #115e59;
        border-color: #115e59;
    }
    
    /* Metrics card styling */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* Sidebar header */
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f766e;
        margin-bottom: 2px;
    }
    .sidebar-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Initialize Database on startup
@st.cache_resource
def setup_database():
    db.init_db()
    return True

setup_database()

# 2. Initialize Services & Orchestrator
@st.cache_resource
def get_orchestrator():
    groq_service = GroqService()
    return Orchestrator(groq_service=groq_service)

orchestrator = get_orchestrator()

# 3. Session State Navigation Management
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = None

if "temp_assessment_data" not in st.session_state:
    st.session_state["temp_assessment_data"] = {}

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-header">🩺 CareSim AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Virtual Patient Simulation Platform</div>', unsafe_allow_html=True)

    nav_options = [
        "Dashboard",
        "Patient Library",
        "Active Simulation",
        "Clinical Assessment",
        "Person-Centred Care Plan",
        "Evaluation & Results",
        "Session History",
        "Authoring & Admin",
        "Settings & Health"
    ]

    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state["current_page"]) if st.session_state["current_page"] in nav_options else 0
    )
    if selected_nav != st.session_state["current_page"]:
        st.session_state["current_page"] = selected_nav
        st.rerun()

    st.markdown("---")

    # Groq Engine Status Card
    st.caption("**AI INFERENCE STATUS**")
    groq_status = orchestrator.groq_service.is_configured()
    if groq_status:
        st.success(f"🟢 Groq Connected\n\nModel: `{orchestrator.groq_service.model}`")
    else:
        st.warning("🟡 Demo Mode Active\n\nDeterministic educational responses.")

    st.markdown("---")
    st.caption(f"**Version:** {config.APP_VERSION}")
    st.caption("Educational Healthcare Simulation Only.")

# Routing Callbacks
def start_simulation_from_patient(patient_id: str):
    session = orchestrator.start_simulation(patient_id)
    st.session_state["active_session_id"] = session.id
    st.session_state["current_page"] = "Active Simulation"
    st.rerun()

def view_past_session(session_id: str):
    st.session_state["active_session_id"] = session_id
    sess = repository.get_session_by_id(session_id)
    if sess and sess.status == "evaluated":
        st.session_state["current_page"] = "Evaluation & Results"
    elif sess and sess.status == "completed":
        st.session_state["current_page"] = "Clinical Assessment"
    else:
        st.session_state["current_page"] = "Active Simulation"
    st.rerun()

def finish_consultation_callback(session_id: str):
    st.session_state["active_session_id"] = session_id
    st.session_state["current_page"] = "Clinical Assessment"
    st.rerun()

def proceed_to_care_plan_callback(assessment_data: dict):
    st.session_state["temp_assessment_data"] = assessment_data
    st.session_state["current_page"] = "Person-Centred Care Plan"
    st.rerun()

def submit_final_evaluation_callback(care_plan_data: dict):
    session_id = st.session_state["active_session_id"]
    assessment_data = st.session_state.get("temp_assessment_data", {})
    if not assessment_data:
        saved_ass = repository.get_assessment_by_session(session_id)
        if saved_ass:
            assessment_data = saved_ass.model_dump() if hasattr(saved_ass, "model_dump") else saved_ass.__dict__

    with st.spinner("Evaluation Agent is analyzing dialogue, clinical assessment, and care plan..."):
        orchestrator.submit_assessment_and_care_plan(
            session_id=session_id,
            assessment_data=assessment_data,
            care_plan_data=care_plan_data
        )
    st.session_state["current_page"] = "Evaluation & Results"
    st.rerun()

# Page Rendering
current_page = st.session_state["current_page"]

if current_page == "Dashboard":
    render_dashboard(
        on_start_simulation_click=lambda: (st.session_state.update({"current_page": "Patient Library"}), st.rerun()),
        on_view_session_click=view_past_session
    )

elif current_page == "Patient Library":
    render_patient_library(on_select_patient=start_simulation_from_patient)

elif current_page == "Active Simulation":
    active_id = st.session_state.get("active_session_id")
    if not active_id:
        st.info("No active consultation session. Please choose a fictional patient from the Patient Library.")
        if st.button("Browse Patient Library 📚"):
            st.session_state["current_page"] = "Patient Library"
            st.rerun()
    else:
        render_simulation_chat(
            session_id=active_id,
            orchestrator=orchestrator,
            on_finish_consultation=finish_consultation_callback
        )

elif current_page == "Clinical Assessment":
    active_id = st.session_state.get("active_session_id")
    if not active_id:
        st.warning("Please start or resume a simulation session first.")
    else:
        render_assessment_form(
            session_id=active_id,
            on_save_draft=lambda: None,
            on_proceed_to_care_plan=proceed_to_care_plan_callback
        )

elif current_page == "Person-Centred Care Plan":
    active_id = st.session_state.get("active_session_id")
    if not active_id:
        st.warning("Please start a simulation session first.")
    else:
        render_care_plan_form(
            session_id=active_id,
            on_back_to_assessment=lambda: (st.session_state.update({"current_page": "Clinical Assessment"}), st.rerun()),
            on_submit_final_evaluation=submit_final_evaluation_callback
        )

elif current_page == "Evaluation & Results":
    active_id = st.session_state.get("active_session_id")
    if not active_id:
        st.warning("Select a completed session from Session History to view results.")
    else:
        render_results(
            session_id=active_id,
            on_restart_simulation=lambda: (st.session_state.update({"current_page": "Patient Library"}), st.rerun())
        )

elif current_page == "Session History":
    render_session_history(on_view_session=view_past_session)

elif current_page == "Authoring & Admin":
    render_admin_portal(orchestrator=orchestrator)

elif current_page == "Settings & Health":
    st.title("🔧 Settings & System Health")
    st.write("Inspect Groq API connectivity, configuration settings, and educational parameters.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Groq API Configuration")
        st.text_input("Configured Model", value=orchestrator.groq_service.model, disabled=True)
        key_configured = bool(orchestrator.groq_service.api_key)
        st.text_input("API Key Status", value="Configured (Server-Side)" if key_configured else "Not Configured (Demo Mode)", disabled=True)
        
        if st.button("🧪 Test Groq Connection"):
            with st.spinner("Testing API connection..."):
                test_result = orchestrator.groq_service.test_connection()
                if test_result["success"]:
                    st.success(test_result["message"])
                else:
                    st.warning(test_result["message"])

    with col2:
        st.subheader("Evaluation Rubric Weights")
        st.write("Configured criteria weights used by the Evaluation Agent:")
        for k, v in config.RUBRIC_WEIGHTS.items():
            st.write(f"- **{k.replace('_', ' ').title()}:** {int(v * 100)}%")

    st.markdown("---")
    st.subheader("Database & Storage")
    st.text_input("Active SQLite Database Path", value=config.DB_PATH, disabled=True)
    if st.button("🔄 Re-seed Default Patient Scenarios"):
        db.init_db()
        st.success("Default fictional scenarios re-synchronized.")
