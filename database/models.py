"""
CareSim AI - Data Models and Schemas
Supports both Pydantic and fallback dataclass representations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    # Minimal fallback shim for BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def model_dump(self) -> Dict[str, Any]:
            return {
                k: v.model_dump() if hasattr(v, "model_dump") else v
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            }
        
        def dict(self) -> Dict[str, Any]:
            return self.model_dump()
        
        @classmethod
        def model_validate(cls, data: Any):
            if isinstance(data, dict):
                return cls(**data)
            return data

class ClinicalReviewStatus:
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class VirtualPatient(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    category: str
    care_setting: str
    difficulty: str
    estimated_duration_mins: int = 15
    learning_objectives: List[str] = []
    presenting_concerns: str
    medical_history: List[str] = []
    current_medications: List[str] = []
    symptoms_and_limitations: List[str] = []
    living_situation: str
    emotional_state: str
    communication_style: str
    patient_preferences: List[str] = []
    hidden_facts: List[str] = []  # Revealed only when relevant questions asked
    expected_assessment_areas: List[str] = []
    safety_rules: List[str] = []
    clinical_review_status: str = ClinicalReviewStatus.APPROVED
    created_at: Optional[str] = None
    is_custom: bool = False

class ConversationMessage(BaseModel):
    id: Optional[int] = None
    session_id: str
    sender: str  # 'learner' or 'patient' or 'system'
    content: str
    timestamp: str
    is_demo: bool = False
    flagged: bool = False

class SimulationSession(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    category: str
    started_at: str
    ended_at: Optional[str] = None
    status: str = "active"  # active, completed, evaluated
    duration_seconds: int = 0
    message_count: int = 0
    is_demo: bool = False

class LearnerAssessment(BaseModel):
    session_id: str
    presenting_problem: str
    relevant_history: str
    symptoms_and_findings: str
    identified_risks: str
    social_and_environmental_factors: str
    further_assessments_required: str
    proposed_next_steps: str
    submitted: bool = False
    updated_at: Optional[str] = None

class CarePlan(BaseModel):
    session_id: str
    identified_needs: str
    patient_preferences_and_goals: str
    proposed_interventions: str
    multidisciplinary_team_services: str
    follow_up_and_monitoring: str
    risks_and_escalation: str
    submitted: bool = False
    updated_at: Optional[str] = None

class RubricItemScore(BaseModel):
    criterion: str
    score: int  # 0 to 100
    weight: float
    feedback: str

class EvaluationReport(BaseModel):
    session_id: str
    patient_id: str
    overall_score: int  # 0 to 100
    rubric_scores: Dict[str, RubricItemScore] = {}
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    missed_questions_or_areas: List[str] = []
    missing_risk_considerations: List[str] = []
    care_plan_feedback: str = ""
    suggested_learning_activities: List[str] = []
    overall_summary: str = ""
    evaluated_at: str = ""
    is_demo: bool = False
