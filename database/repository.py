"""
CareSim AI - Database Repository
Provides typed, parameterized data access operations for patients, sessions,
messages, assessments, care plans, and evaluation reports.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from .db import get_connection
from .models import (
    VirtualPatient,
    SimulationSession,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    EvaluationReport,
    RubricItemScore,
    ClinicalReviewStatus
)

def _row_to_patient(row: sqlite3.Row) -> VirtualPatient:
    return VirtualPatient(
        id=row["id"],
        name=row["name"],
        age=row["age"],
        gender=row["gender"],
        category=row["category"],
        care_setting=row["care_setting"],
        difficulty=row["difficulty"],
        estimated_duration_mins=row["estimated_duration_mins"],
        learning_objectives=json.loads(row["learning_objectives"]),
        presenting_concerns=row["presenting_concerns"],
        medical_history=json.loads(row["medical_history"]),
        current_medications=json.loads(row["current_medications"]),
        symptoms_and_limitations=json.loads(row["symptoms_and_limitations"]),
        living_situation=row["living_situation"],
        emotional_state=row["emotional_state"],
        communication_style=row["communication_style"],
        patient_preferences=json.loads(row["patient_preferences"]),
        hidden_facts=json.loads(row["hidden_facts"]),
        expected_assessment_areas=json.loads(row["expected_assessment_areas"]),
        safety_rules=json.loads(row["safety_rules"]),
        clinical_review_status=row["clinical_review_status"],
        created_at=row["created_at"],
        is_custom=bool(row["is_custom"])
    )

def get_all_patients(approved_only: bool = True) -> List[VirtualPatient]:
    """Retrieves all patients. If approved_only is True, filters for APPROVED."""
    conn = get_connection()
    cursor = conn.cursor()
    if approved_only:
        cursor.execute("SELECT * FROM patients WHERE clinical_review_status = ? ORDER BY name ASC", 
                       (ClinicalReviewStatus.APPROVED,))
    else:
        cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_patient(r) for r in rows]

def get_patient_by_id(patient_id: str) -> Optional[VirtualPatient]:
    """Finds a patient by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return _row_to_patient(row)
    return None

def save_patient(patient: VirtualPatient) -> None:
    """Inserts or updates a patient scenario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (
            id, name, age, gender, category, care_setting, difficulty,
            estimated_duration_mins, learning_objectives, presenting_concerns,
            medical_history, current_medications, symptoms_and_limitations,
            living_situation, emotional_state, communication_style,
            patient_preferences, hidden_facts, expected_assessment_areas,
            safety_rules, clinical_review_status, is_custom
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            age=excluded.age,
            gender=excluded.gender,
            category=excluded.category,
            care_setting=excluded.care_setting,
            difficulty=excluded.difficulty,
            estimated_duration_mins=excluded.estimated_duration_mins,
            learning_objectives=excluded.learning_objectives,
            presenting_concerns=excluded.presenting_concerns,
            medical_history=excluded.medical_history,
            current_medications=excluded.current_medications,
            symptoms_and_limitations=excluded.symptoms_and_limitations,
            living_situation=excluded.living_situation,
            emotional_state=excluded.emotional_state,
            communication_style=excluded.communication_style,
            patient_preferences=excluded.patient_preferences,
            hidden_facts=excluded.hidden_facts,
            expected_assessment_areas=excluded.expected_assessment_areas,
            safety_rules=excluded.safety_rules,
            clinical_review_status=excluded.clinical_review_status,
            is_custom=excluded.is_custom
    """, (
        patient.id,
        patient.name,
        patient.age,
        patient.gender,
        patient.category,
        patient.care_setting,
        patient.difficulty,
        patient.estimated_duration_mins,
        json.dumps(patient.learning_objectives),
        patient.presenting_concerns,
        json.dumps(patient.medical_history),
        json.dumps(patient.current_medications),
        json.dumps(patient.symptoms_and_limitations),
        patient.living_situation,
        patient.emotional_state,
        patient.communication_style,
        json.dumps(patient.patient_preferences),
        json.dumps(patient.hidden_facts),
        json.dumps(patient.expected_assessment_areas),
        json.dumps(patient.safety_rules),
        patient.clinical_review_status,
        1 if patient.is_custom else 0
    ))
    conn.commit()
    conn.close()

def create_session(session: SimulationSession) -> None:
    """Creates a new simulation session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (
            id, patient_id, patient_name, category, started_at, status, duration_seconds, message_count, is_demo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session.id,
        session.patient_id,
        session.patient_name,
        session.category,
        session.started_at,
        session.status,
        session.duration_seconds,
        session.message_count,
        1 if session.is_demo else 0
    ))
    # Pre-create empty assessment and care plan entries
    cursor.execute("INSERT OR IGNORE INTO assessments (session_id) VALUES (?)", (session.id,))
    cursor.execute("INSERT OR IGNORE INTO care_plans (session_id) VALUES (?)", (session.id,))
    conn.commit()
    conn.close()

def get_session_by_id(session_id: str) -> Optional[SimulationSession]:
    """Retrieves session metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return SimulationSession(
            id=row["id"],
            patient_id=row["patient_id"],
            patient_name=row["patient_name"],
            category=row["category"],
            started_at=str(row["started_at"]),
            ended_at=str(row["ended_at"]) if row["ended_at"] else None,
            status=row["status"],
            duration_seconds=row["duration_seconds"],
            message_count=row["message_count"],
            is_demo=bool(row["is_demo"])
        )
    return None

def update_session(session: SimulationSession) -> None:
    """Updates session status, end time, duration, and message count."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sessions SET
            status = ?,
            ended_at = ?,
            duration_seconds = ?,
            message_count = ?
        WHERE id = ?
    """, (
        session.status,
        session.ended_at,
        session.duration_seconds,
        session.message_count,
        session.id
    ))
    conn.commit()
    conn.close()

def get_all_sessions() -> List[SimulationSession]:
    """Lists all simulation sessions ordered by started_at DESC."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY started_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        SimulationSession(
            id=r["id"],
            patient_id=r["patient_id"],
            patient_name=r["patient_name"],
            category=r["category"],
            started_at=str(r["started_at"]),
            ended_at=str(r["ended_at"]) if r["ended_at"] else None,
            status=r["status"],
            duration_seconds=r["duration_seconds"],
            message_count=r["message_count"],
            is_demo=bool(r["is_demo"])
        )
        for r in rows
    ]

def add_message(msg: ConversationMessage) -> int:
    """Appends a conversation message to the database and increments session count."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (session_id, sender, content, timestamp, is_demo, flagged)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        msg.session_id,
        msg.sender,
        msg.content,
        msg.timestamp,
        1 if msg.is_demo else 0,
        1 if msg.flagged else 0
    ))
    msg_id = cursor.lastrowid
    cursor.execute("UPDATE sessions SET message_count = message_count + 1 WHERE id = ?", (msg.session_id,))
    conn.commit()
    conn.close()
    return msg_id

def flag_message(message_id: int) -> None:
    """Marks a message as flagged for safety/inaccuracy."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET flagged = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_messages_for_session(session_id: str) -> List[ConversationMessage]:
    """Retrieves all conversation messages in order."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        ConversationMessage(
            id=r["id"],
            session_id=r["session_id"],
            sender=r["sender"],
            content=r["content"],
            timestamp=str(r["timestamp"]),
            is_demo=bool(r["is_demo"]),
            flagged=bool(r["flagged"])
        )
        for r in rows
    ]

def save_assessment(assessment: LearnerAssessment) -> None:
    """Saves learner assessment draft or final submission."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessments (
            session_id, presenting_problem, relevant_history, symptoms_and_findings,
            identified_risks, social_and_environmental_factors, further_assessments_required,
            proposed_next_steps, submitted, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            presenting_problem = excluded.presenting_problem,
            relevant_history = excluded.relevant_history,
            symptoms_and_findings = excluded.symptoms_and_findings,
            identified_risks = excluded.identified_risks,
            social_and_environmental_factors = excluded.social_and_environmental_factors,
            further_assessments_required = excluded.further_assessments_required,
            proposed_next_steps = excluded.proposed_next_steps,
            submitted = excluded.submitted,
            updated_at = CURRENT_TIMESTAMP
    """, (
        assessment.session_id,
        assessment.presenting_problem,
        assessment.relevant_history,
        assessment.symptoms_and_findings,
        assessment.identified_risks,
        assessment.social_and_environmental_factors,
        assessment.further_assessments_required,
        assessment.proposed_next_steps,
        1 if assessment.submitted else 0
    ))
    conn.commit()
    conn.close()

def get_assessment_by_session(session_id: str) -> Optional[LearnerAssessment]:
    """Retrieves learner assessment for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return LearnerAssessment(
            session_id=row["session_id"],
            presenting_problem=row["presenting_problem"] or "",
            relevant_history=row["relevant_history"] or "",
            symptoms_and_findings=row["symptoms_and_findings"] or "",
            identified_risks=row["identified_risks"] or "",
            social_and_environmental_factors=row["social_and_environmental_factors"] or "",
            further_assessments_required=row["further_assessments_required"] or "",
            proposed_next_steps=row["proposed_next_steps"] or "",
            submitted=bool(row["submitted"]),
            updated_at=str(row["updated_at"]) if row["updated_at"] else None
        )
    return None

def save_care_plan(care_plan: CarePlan) -> None:
    """Saves learner person-centred care plan draft or submission."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO care_plans (
            session_id, identified_needs, patient_preferences_and_goals, proposed_interventions,
            multidisciplinary_team_services, follow_up_and_monitoring, risks_and_escalation,
            submitted, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            identified_needs = excluded.identified_needs,
            patient_preferences_and_goals = excluded.patient_preferences_and_goals,
            proposed_interventions = excluded.proposed_interventions,
            multidisciplinary_team_services = excluded.multidisciplinary_team_services,
            follow_up_and_monitoring = excluded.follow_up_and_monitoring,
            risks_and_escalation = excluded.risks_and_escalation,
            submitted = excluded.submitted,
            updated_at = CURRENT_TIMESTAMP
    """, (
        care_plan.session_id,
        care_plan.identified_needs,
        care_plan.patient_preferences_and_goals,
        care_plan.proposed_interventions,
        care_plan.multidisciplinary_team_services,
        care_plan.follow_up_and_monitoring,
        care_plan.risks_and_escalation,
        1 if care_plan.submitted else 0
    ))
    conn.commit()
    conn.close()

def get_care_plan_by_session(session_id: str) -> Optional[CarePlan]:
    """Retrieves care plan for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM care_plans WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return CarePlan(
            session_id=row["session_id"],
            identified_needs=row["identified_needs"] or "",
            patient_preferences_and_goals=row["patient_preferences_and_goals"] or "",
            proposed_interventions=row["proposed_interventions"] or "",
            multidisciplinary_team_services=row["multidisciplinary_team_services"] or "",
            follow_up_and_monitoring=row["follow_up_and_monitoring"] or "",
            risks_and_escalation=row["risks_and_escalation"] or "",
            submitted=bool(row["submitted"]),
            updated_at=str(row["updated_at"]) if row["updated_at"] else None
        )
    return None

def save_evaluation(eval_report: EvaluationReport) -> None:
    """Saves AI-powered evaluation report."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Serialize rubric scores
    rubric_dict = {}
    for k, v in eval_report.rubric_scores.items():
        if hasattr(v, "model_dump"):
            rubric_dict[k] = v.model_dump()
        elif isinstance(v, dict):
            rubric_dict[k] = v
        else:
            rubric_dict[k] = {"criterion": k, "score": getattr(v, "score", 0), "weight": getattr(v, "weight", 0.0), "feedback": getattr(v, "feedback", "")}

    cursor.execute("""
        INSERT INTO evaluations (
            session_id, patient_id, overall_score, rubric_scores, strengths,
            areas_for_improvement, missed_questions_or_areas, missing_risk_considerations,
            care_plan_feedback, suggested_learning_activities, overall_summary,
            evaluated_at, is_demo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            overall_score = excluded.overall_score,
            rubric_scores = excluded.rubric_scores,
            strengths = excluded.strengths,
            areas_for_improvement = excluded.areas_for_improvement,
            missed_questions_or_areas = excluded.missed_questions_or_areas,
            missing_risk_considerations = excluded.missing_risk_considerations,
            care_plan_feedback = excluded.care_plan_feedback,
            suggested_learning_activities = excluded.suggested_learning_activities,
            overall_summary = excluded.overall_summary,
            evaluated_at = CURRENT_TIMESTAMP,
            is_demo = excluded.is_demo
    """, (
        eval_report.session_id,
        eval_report.patient_id,
        eval_report.overall_score,
        json.dumps(rubric_dict),
        json.dumps(eval_report.strengths),
        json.dumps(eval_report.areas_for_improvement),
        json.dumps(eval_report.missed_questions_or_areas),
        json.dumps(eval_report.missing_risk_considerations),
        eval_report.care_plan_feedback,
        json.dumps(eval_report.suggested_learning_activities),
        eval_report.overall_summary,
        1 if eval_report.is_demo else 0
    ))
    cursor.execute("UPDATE sessions SET status = 'evaluated' WHERE id = ?", (eval_report.session_id,))
    conn.commit()
    conn.close()

def get_evaluation_by_session(session_id: str) -> Optional[EvaluationReport]:
    """Retrieves evaluation report for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    
    rubric_raw = json.loads(row["rubric_scores"])
    rubric_scores = {}
    for k, v in rubric_raw.items():
        rubric_scores[k] = RubricItemScore(
            criterion=v.get("criterion", k),
            score=v.get("score", 0),
            weight=v.get("weight", 0.0),
            feedback=v.get("feedback", "")
        )

    return EvaluationReport(
        session_id=row["session_id"],
        patient_id=row["patient_id"],
        overall_score=row["overall_score"],
        rubric_scores=rubric_scores,
        strengths=json.loads(row["strengths"]),
        areas_for_improvement=json.loads(row["areas_for_improvement"]),
        missed_questions_or_areas=json.loads(row["missed_questions_or_areas"]),
        missing_risk_considerations=json.loads(row["missing_risk_considerations"]),
        care_plan_feedback=row["care_plan_feedback"],
        suggested_learning_activities=json.loads(row["suggested_learning_activities"]),
        overall_summary=row["overall_summary"],
        evaluated_at=str(row["evaluated_at"]),
        is_demo=bool(row["is_demo"])
    )

def get_dashboard_metrics() -> Dict[str, Any]:
    """Returns analytics metrics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM patients WHERE clinical_review_status = ?", (ClinicalReviewStatus.APPROVED,))
    total_scenarios = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as total FROM sessions")
    total_sessions = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as total FROM sessions WHERE status = 'evaluated'")
    completed_sessions = cursor.fetchone()["total"]
    
    cursor.execute("SELECT AVG(overall_score) as avg_score FROM evaluations")
    avg_score_row = cursor.fetchone()["avg_score"]
    avg_score = round(avg_score_row, 1) if avg_score_row else 0.0

    conn.close()
    return {
        "total_scenarios": total_scenarios,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "average_score": avg_score
    }
