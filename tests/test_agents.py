"""
Unit tests for CareSim AI Agent modules:
- VirtualPatientAgent
- EvaluationAgent
- ScenarioAuthoringAgent
- Demo Mode Fallbacks for all 5 patient personas
"""
import unittest
import os
import tempfile
from database import db, repository
from database.models import (
    VirtualPatient,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    ClinicalReviewStatus
)
from agents.patient_agent import VirtualPatientAgent
from agents.evaluation_agent import EvaluationAgent
from agents.scenario_agent import ScenarioAuthoringAgent
from services.groq_service import GroqService
import config

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.orig_db = config.DB_PATH
        config.DB_PATH = self.temp_db_path
        db.init_db(self.temp_db_path)
        self.groq_mock = GroqService(api_key="")  # Unconfigured to test demo/mock mode

    def tearDown(self):
        config.DB_PATH = self.orig_db
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_all_five_patient_personas_respond_in_character(self):
        patient_ids = [
            ("scenario_frailty_01", "dizzy", "fuzzy"),
            ("scenario_chronic_02", "foot", "pins and needles"),
            ("scenario_mental_03", "suicide", "buster"),
            ("scenario_palliative_04", "morphine", "addicted"),
            ("scenario_integrated_05", "physio", "hospital")
        ]
        for pid, query, expected_snippet in patient_ids:
            patient = repository.get_patient_by_id(pid)
            self.assertIsNotNone(patient, f"Patient {pid} should exist in seed data")
            agent = VirtualPatientAgent(patient, self.groq_mock)
            reply = agent.generate_response([], query)
            self.assertTrue(reply["is_demo"])
            self.assertIn(expected_snippet.lower(), reply["content"].lower(), f"Failed for {pid} on '{query}'")

    def test_evaluation_agent_scoring_and_rubric(self):
        patient = repository.get_patient_by_id("scenario_frailty_01")
        eval_agent = EvaluationAgent(self.groq_mock)
        history = [
            ConversationMessage(session_id="s1", sender="learner", content="Tell me about your fall.", timestamp="10:00:00"),
            ConversationMessage(session_id="s1", sender="patient", content="I tripped on the rug.", timestamp="10:00:05")
        ]
        assessment = LearnerAssessment(
            session_id="s1",
            presenting_problem="Fall in hallway",
            relevant_history="Osteoporosis, amlodipine",
            symptoms_and_findings="Gait hesitation",
            identified_risks="Fractures, loose hallway rug",
            social_and_environmental_factors="Lives alone in 2-storey house",
            further_assessments_required="Lying and standing BP",
            proposed_next_steps="Refer to falls team",
            submitted=True
        )
        care_plan = CarePlan(
            session_id="s1",
            identified_needs="Fall prevention, environmental hazard clearance",
            patient_preferences_and_goals="Maintain independence at home",
            proposed_interventions="Occupational therapy home assessment",
            multidisciplinary_team_services="OT, Physiotherapy, GP",
            follow_up_and_monitoring="Review in 4 weeks",
            risks_and_escalation="Emergency response pendant",
            submitted=True
        )

        report = eval_agent.evaluate("s1", patient, history, assessment, care_plan)
        self.assertIsNotNone(report)
        self.assertGreater(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 100)
        self.assertEqual(len(report.rubric_scores), 6)
        self.assertTrue(report.is_demo)
        self.assertGreaterEqual(len(report.strengths), 1)
        self.assertGreaterEqual(len(report.areas_for_improvement), 1)

    def test_scenario_authoring_agent_validation(self):
        author_agent = ScenarioAuthoringAgent(self.groq_mock)
        result = author_agent.generate_draft_scenario(
            category="Cardiovascular",
            care_setting="Primary Care",
            difficulty="Intermediate",
            learning_objectives_input="Identify atypical angina in older female",
            additional_notes="Patient minimises chest heaviness as indigestion"
        )
        patient = result["patient"]
        flags = result["flags"]
        
        self.assertIsNotNone(patient)
        self.assertEqual(patient.clinical_review_status, ClinicalReviewStatus.DRAFT)
        self.assertTrue(patient.is_custom)
        self.assertGreater(len(patient.learning_objectives), 0)
        self.assertTrue(any("Review Requirement" in f for f in flags))

    def test_groq_service_safe_connection_check(self):
        # When no API key is provided
        unconfigured_svc = GroqService(api_key="")
        status = unconfigured_svc.test_connection()
        self.assertFalse(status["success"])
        self.assertTrue(status["demo_mode"])

if __name__ == "__main__":
    unittest.main()
