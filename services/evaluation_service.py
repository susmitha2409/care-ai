"""
CareSim AI - Evaluation Service
Manages retrieval and formatting of evaluation reports.
"""
from typing import Optional, Dict, Any
from database.models import EvaluationReport
from database import repository

def get_session_evaluation(session_id: str) -> Optional[EvaluationReport]:
    """Retrieves saved evaluation report for a session."""
    return repository.get_evaluation_by_session(session_id)

def calculate_completion_percentage(session_id: str) -> int:
    """Calculates completeness of learner assessment & care plan submission."""
    assessment = repository.get_assessment_by_session(session_id)
    care_plan = repository.get_care_plan_by_session(session_id)

    total_fields = 13
    filled_fields = 0

    if assessment:
        fields = [
            assessment.presenting_problem,
            assessment.relevant_history,
            assessment.symptoms_and_findings,
            assessment.identified_risks,
            assessment.social_and_environmental_factors,
            assessment.further_assessments_required,
            assessment.proposed_next_steps
        ]
        filled_fields += sum(1 for f in fields if f and len(f.strip()) > 5)

    if care_plan:
        fields = [
            care_plan.identified_needs,
            care_plan.patient_preferences_and_goals,
            care_plan.proposed_interventions,
            care_plan.multidisciplinary_team_services,
            care_plan.follow_up_and_monitoring,
            care_plan.risks_and_escalation
        ]
        filled_fields += sum(1 for f in fields if f and len(f.strip()) > 5)

    return int((filled_fields / total_fields) * 100)
