"""
Unit tests for CareSim AI Database layer and SQLite persistence.
"""
import unittest
import os
import tempfile
import json
from database import db, repository
from database.models import (
    VirtualPatient,
    SimulationSession,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    EvaluationReport,
    RubricItemScore,
    ClinicalReviewStatus
)
import config

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Point config to temp DB
        self.orig_db_path = config.DB_PATH
        config.DB_PATH = self.temp_db_path
        db.init_db(self.temp_db_path)

    def tearDown(self):
        config.DB_PATH = self.orig_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_database_initialization_and_seeding(self):
        patients = repository.get_all_patients(approved_only=False)
        self.assertGreaterEqual(len(patients), 5)
        
        # Verify 5 primary core categories
        categories = [p.category for p in patients]
        self.assertTrue(any("Frailty" in c for c in categories))
        self.assertTrue(any("Complex" in c for c in categories))
        self.assertTrue(any("Mental" in c for c in categories))
        self.assertTrue(any("End-of-life" in c or "palliative" in c.lower() for c in categories))
        self.assertTrue(any("Integrated" in c for c in categories))

    def test_session_lifecycle(self):
        patient = repository.get_all_patients()[0]
        session = SimulationSession(
            id="test_sess_001",
            patient_id=patient.id,
            patient_name=patient.name,
            category=patient.category,
            started_at="2026-09-29 10:00:00",
            status="active",
            duration_seconds=0,
            message_count=0,
            is_demo=True
        )
        repository.create_session(session)

        retrieved = repository.get_session_by_id("test_sess_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.patient_name, patient.name)
        self.assertEqual(retrieved.status, "active")

        # Add messages
        msg1 = ConversationMessage(
            session_id="test_sess_001",
            sender="learner",
            content="Hello Margaret, how are you feeling?",
            timestamp="2026-09-29 10:01:00"
        )
        msg_id = repository.add_message(msg1)
        self.assertIsNotNone(msg_id)

        messages = repository.get_messages_for_session("test_sess_001")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Hello Margaret, how are you feeling?")

        # Flag message
        repository.flag_message(msg_id)
        messages_updated = repository.get_messages_for_session("test_sess_001")
        self.assertTrue(messages_updated[0].flagged)

    def test_assessment_and_care_plan_storage(self):
        patient = repository.get_all_patients()[0]
        session = SimulationSession(
            id="test_sess_002",
            patient_id=patient.id,
            patient_name=patient.name,
            category=patient.category,
            started_at="2026-09-29 10:00:00"
        )
        repository.create_session(session)

        assessment = LearnerAssessment(
            session_id="test_sess_002",
            presenting_problem="Recurrent unsteadiness and falls",
            relevant_history="Osteoporosis, HTN on amlodipine",
            symptoms_and_findings="Gait instability, orthostasis",
            identified_risks="Fracture risk, polypharmacy",
            social_and_environmental_factors="Lives alone, loose rugs",
            further_assessments_required="Lying/standing BP, medication review",
            proposed_next_steps="Refer to falls prevention clinic",
            submitted=True
        )
        repository.save_assessment(assessment)
        retrieved_ass = repository.get_assessment_by_session("test_sess_002")
        self.assertIsNotNone(retrieved_ass)
        self.assertEqual(retrieved_ass.presenting_problem, "Recurrent unsteadiness and falls")
        self.assertTrue(retrieved_ass.submitted)

        care_plan = CarePlan(
            session_id="test_sess_002",
            identified_needs="Mobility support and medication safety",
            patient_preferences_and_goals="Wants to remain safely at home",
            proposed_interventions="Physio home safety assessment",
            multidisciplinary_team_services="Community OT, Pharmacist",
            follow_up_and_monitoring="Review in 2 weeks",
            risks_and_escalation="Emergency call pendant installation",
            submitted=True
        )
        repository.save_care_plan(care_plan)
        retrieved_plan = repository.get_care_plan_by_session("test_sess_002")
        self.assertIsNotNone(retrieved_plan)
        self.assertEqual(retrieved_plan.patient_preferences_and_goals, "Wants to remain safely at home")

if __name__ == "__main__":
    unittest.main()
