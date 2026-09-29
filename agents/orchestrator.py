"""
CareSim AI - Agent Orchestrator
Coordinates workflow stages: starting sessions, conversational turns, assessment,
care planning, AI evaluation, and scenario authoring.
Ensures context isolation and transaction safety.
"""
import uuid
import datetime
from typing import Dict, Any, List, Optional
from database.models import (
    VirtualPatient,
    SimulationSession,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    EvaluationReport,
    ClinicalReviewStatus
)
from database import repository
from services.groq_service import GroqService
from .patient_agent import VirtualPatientAgent
from .evaluation_agent import EvaluationAgent
from .scenario_agent import ScenarioAuthoringAgent

class Orchestrator:
    def __init__(self, groq_service: Optional[GroqService] = None):
        self.groq_service = groq_service or GroqService()
        self.evaluation_agent = EvaluationAgent(self.groq_service)
        self.scenario_agent = ScenarioAuthoringAgent(self.groq_service)

    def start_simulation(self, patient_id: str, is_demo: bool = False) -> SimulationSession:
        """Initializes a new simulation session for a selected patient."""
        patient = repository.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found.")

        session_id = f"sim_{uuid.uuid4().hex[:10]}"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        session = SimulationSession(
            id=session_id,
            patient_id=patient.id,
            patient_name=patient.name,
            category=patient.category,
            started_at=now_str,
            status="active",
            duration_seconds=0,
            message_count=0,
            is_demo=is_demo or not self.groq_service.is_configured()
        )
        repository.create_session(session)

        # Initial opening patient greeting
        patient_agent = VirtualPatientAgent(patient, self.groq_service)
        greeting = patient_agent.generate_response([], "Hello")
        
        greeting_msg = ConversationMessage(
            session_id=session_id,
            sender="patient",
            content=greeting["content"],
            timestamp=now_str,
            is_demo=greeting["is_demo"]
        )
        repository.add_message(greeting_msg)
        return session

    def process_learner_message(
        self,
        session_id: str,
        learner_text: str
    ) -> Dict[str, Any]:
        """
        Receives learner question, appends it to database, invokes Patient Agent,
        stores patient response, and returns response payload.
        """
        session = repository.get_session_by_id(session_id)
        if not session:
            return {"error": "Session not found"}
        
        patient = repository.get_patient_by_id(session.patient_id)
        if not patient:
            return {"error": "Patient profile not found"}

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Store learner message
        learner_msg = ConversationMessage(
            session_id=session_id,
            sender="learner",
            content=learner_text,
            timestamp=now_str,
            is_demo=False
        )
        repository.add_message(learner_msg)

        # 2. Retrieve history for context
        history = repository.get_messages_for_session(session_id)

        # 3. Call Virtual Patient Agent
        patient_agent = VirtualPatientAgent(patient, self.groq_service)
        result = patient_agent.generate_response(history[:-1], learner_text)

        # 4. Store patient response
        patient_msg = ConversationMessage(
            session_id=session_id,
            sender="patient",
            content=result["content"],
            timestamp=now_str,
            is_demo=result["is_demo"]
        )
        msg_id = repository.add_message(patient_msg)
        patient_msg.id = msg_id

        return {
            "learner_message": learner_msg,
            "patient_message": patient_msg,
            "is_demo": result["is_demo"]
        }

    def end_simulation(self, session_id: str) -> SimulationSession:
        """Concludes the conversation phase and prepares for assessment/care plan."""
        session = repository.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        now = datetime.datetime.now()
        session.ended_at = now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            start_dt = datetime.datetime.strptime(session.started_at, "%Y-%m-%d %H:%M:%S")
            session.duration_seconds = max(10, int((now - start_dt).total_seconds()))
        except Exception:
            session.duration_seconds = 300

        session.status = "completed"
        repository.update_session(session)
        return session

    def submit_assessment_and_care_plan(
        self,
        session_id: str,
        assessment_data: Dict[str, Any],
        care_plan_data: Dict[str, Any]
    ) -> EvaluationReport:
        """
        Saves learner submissions and triggers the separate Evaluation Agent.
        """
        session = repository.get_session_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        patient = repository.get_patient_by_id(session.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Save Assessment
        assessment = LearnerAssessment(
            session_id=session_id,
            presenting_problem=assessment_data.get("presenting_problem", ""),
            relevant_history=assessment_data.get("relevant_history", ""),
            symptoms_and_findings=assessment_data.get("symptoms_and_findings", ""),
            identified_risks=assessment_data.get("identified_risks", ""),
            social_and_environmental_factors=assessment_data.get("social_and_environmental_factors", ""),
            further_assessments_required=assessment_data.get("further_assessments_required", ""),
            proposed_next_steps=assessment_data.get("proposed_next_steps", ""),
            submitted=True
        )
        repository.save_assessment(assessment)

        # Save Care Plan
        care_plan = CarePlan(
            session_id=session_id,
            identified_needs=care_plan_data.get("identified_needs", ""),
            patient_preferences_and_goals=care_plan_data.get("patient_preferences_and_goals", ""),
            proposed_interventions=care_plan_data.get("proposed_interventions", ""),
            multidisciplinary_team_services=care_plan_data.get("multidisciplinary_team_services", ""),
            follow_up_and_monitoring=care_plan_data.get("follow_up_and_monitoring", ""),
            risks_and_escalation=care_plan_data.get("risks_and_escalation", ""),
            submitted=True
        )
        repository.save_care_plan(care_plan)

        # Retrieve transcript
        history = repository.get_messages_for_session(session_id)

        # Execute Evaluation Agent
        eval_report = self.evaluation_agent.evaluate(
            session_id=session_id,
            patient=patient,
            conversation_history=history,
            assessment=assessment,
            care_plan=care_plan
        )

        repository.save_evaluation(eval_report)
        return eval_report

    def author_scenario(
        self,
        category: str,
        care_setting: str,
        difficulty: str,
        learning_objectives: str,
        additional_notes: str = ""
    ) -> Dict[str, Any]:
        """Coordinates authoring of a new scenario draft."""
        result = self.scenario_agent.generate_draft_scenario(
            category=category,
            care_setting=care_setting,
            difficulty=difficulty,
            learning_objectives_input=learning_objectives,
            additional_notes=additional_notes
        )
        patient = result["patient"]
        repository.save_patient(patient)
        return result
