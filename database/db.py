"""
CareSim AI - Database Initialization & Connection Layer
Uses SQLite for local storage, fully parameterized, resilient and self-initializing.
"""
import sqlite3
import json
import os
from typing import Optional
from pathlib import Path
import config
from .seed_data import SEED_PATIENTS

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a sqlite3 connection with Row factory enabled."""
    path = db_path or config.DB_PATH
    # Ensure directory exists
    parent_dir = Path(path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(path, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    """Initializes tables and seeds default scenarios if not already present."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Patients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            category TEXT NOT NULL,
            care_setting TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            estimated_duration_mins INTEGER DEFAULT 15,
            learning_objectives TEXT NOT NULL,
            presenting_concerns TEXT NOT NULL,
            medical_history TEXT NOT NULL,
            current_medications TEXT NOT NULL,
            symptoms_and_limitations TEXT NOT NULL,
            living_situation TEXT NOT NULL,
            emotional_state TEXT NOT NULL,
            communication_style TEXT NOT NULL,
            patient_preferences TEXT NOT NULL,
            hidden_facts TEXT NOT NULL,
            expected_assessment_areas TEXT NOT NULL,
            safety_rules TEXT NOT NULL,
            clinical_review_status TEXT DEFAULT 'approved',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_custom INTEGER DEFAULT 0
        );
    """)

    # 2. Simulation Sessions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            category TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            status TEXT DEFAULT 'active',
            duration_seconds INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    # 3. Conversation Messages Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_demo INTEGER DEFAULT 0,
            flagged INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
    """)

    # 4. Learner Assessments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            session_id TEXT PRIMARY KEY,
            presenting_problem TEXT DEFAULT '',
            relevant_history TEXT DEFAULT '',
            symptoms_and_findings TEXT DEFAULT '',
            identified_risks TEXT DEFAULT '',
            social_and_environmental_factors TEXT DEFAULT '',
            further_assessments_required TEXT DEFAULT '',
            proposed_next_steps TEXT DEFAULT '',
            submitted INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
    """)

    # 5. Care Plans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS care_plans (
            session_id TEXT PRIMARY KEY,
            identified_needs TEXT DEFAULT '',
            patient_preferences_and_goals TEXT DEFAULT '',
            proposed_interventions TEXT DEFAULT '',
            multidisciplinary_team_services TEXT DEFAULT '',
            follow_up_and_monitoring TEXT DEFAULT '',
            risks_and_escalation TEXT DEFAULT '',
            submitted INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
    """)

    # 6. Evaluation Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            session_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            rubric_scores TEXT NOT NULL,
            strengths TEXT NOT NULL,
            areas_for_improvement TEXT NOT NULL,
            missed_questions_or_areas TEXT NOT NULL,
            missing_risk_considerations TEXT NOT NULL,
            care_plan_feedback TEXT NOT NULL,
            suggested_learning_activities TEXT NOT NULL,
            overall_summary TEXT NOT NULL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        );
    """)

    conn.commit()

    # Seed initial fictional patients if empty
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    count = cursor.fetchone()["count"]
    if count == 0:
        for p in SEED_PATIENTS:
            cursor.execute("""
                INSERT INTO patients (
                    id, name, age, gender, category, care_setting, difficulty,
                    estimated_duration_mins, learning_objectives, presenting_concerns,
                    medical_history, current_medications, symptoms_and_limitations,
                    living_situation, emotional_state, communication_style,
                    patient_preferences, hidden_facts, expected_assessment_areas,
                    safety_rules, clinical_review_status, is_custom
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"],
                p["name"],
                p["age"],
                p["gender"],
                p["category"],
                p["care_setting"],
                p["difficulty"],
                p["estimated_duration_mins"],
                json.dumps(p["learning_objectives"]),
                p["presenting_concerns"],
                json.dumps(p["medical_history"]),
                json.dumps(p["current_medications"]),
                json.dumps(p["symptoms_and_limitations"]),
                p["living_situation"],
                p["emotional_state"],
                p["communication_style"],
                json.dumps(p["patient_preferences"]),
                json.dumps(p["hidden_facts"]),
                json.dumps(p["expected_assessment_areas"]),
                json.dumps(p["safety_rules"]),
                p["clinical_review_status"],
                1 if p.get("is_custom") else 0
            ))
        conn.commit()
    
    conn.close()
