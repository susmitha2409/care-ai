"""
End-to-End Workflow & Integration Tests for CareSim AI
Tests complete simulation lifecycle from scenario selection to evaluation report generation.
"""
import unittest
import os
import tempfile
from database import db, repository
from agents.orchestrator import Orchestrator
from services.groq_service import GroqService
from services import report_service
import config

class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.orig_db = config.DB_PATH
        config.DB_PATH = self.temp_db_path
        db.init_db(self.temp_db_path)

        self.groq_service = GroqService(api_key="")
        self.orchestrator = Orchestrator(self.groq_service)

    def tearDown(self):
        config.DB_PATH = self.orig_db
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_full_simulation_workflow(self):
        # 1. Start simulation with Arthur Chen (T2DM & CKD)
        session = self.orchestrator.start_simulation("scenario_chronic_02", is_demo=True)
        self.assertIsNotNone(session)
        self.assertEqual(session.status, "active")

        # Verify initial opening patient message was stored
        initial_msgs = repository.get_messages_for_session(session.id)
        self.assertEqual(len(initial_msgs), 1)
        self.assertEqual(initial_msgs[0].sender, "patient")

        # 2. Multi-turn dialogue: Learner inquires about feet and medications
        res1 = self.orchestrator.process_learner_message(
            session.id, "Hello Arthur, how have your feet been feeling at night?"
        )
        self.assertIn("burning", res1["patient_message"].content.lower())

        res2 = self.orchestrator.process_learner_message(
            session.id, "Are you experiencing any stomach issues with your Metformin?"
        )
        self.assertIn("metformin", res2["patient_message"].content.lower())

        # 3. End consultation
        completed_session = self.orchestrator.end_simulation(session.id)
        self.assertEqual(completed_session.status, "completed")

        # 4. Submit Clinical Assessment & Care Plan
        assessment_data = {
            "presenting_problem": "Elevated HbA1c (78 mmol/mol) and nocturnal peripheral neuropathy in patient with T2DM and CKD Stage 3a.",
            "relevant_history": "14-year T2DM, CKD 3a (eGFR 52), hypertension, on Metformin and Gliclazide.",
            "symptoms_and_findings": "Bilateral burning soles of feet, newly discovered right great toe blister, evening Metformin GI intolerance.",
            "identified_risks": "Diabetic foot ulceration, infection, renal dosing hazard with Metformin, diabetes distress.",
            "social_and_environmental_factors": "Retired engineer, analytical, wife prepares high-carb traditional meals.",
            "further_assessments_required": "Monofilament 10g sensory test, foot pulses, urine ACR, eGFR recheck.",
            "proposed_next_steps": "Dressing and offloading for toe blister, discuss Metformin MR or alternative agent, podiatry referral."
        }

        care_plan_data = {
            "identified_needs": "Diabetic foot care, medication regimen optimization, glycemic support.",
            "patient_preferences_and_goals": "Strongly wishes to avoid daily insulin injections, wants to walk in park with grandkids.",
            "proposed_interventions": "Review Metformin tolerability, consider SGLT2i/GLP1-RA renally dosed, podiatry care.",
            "multidisciplinary_team_services": "Specialist Podiatrist, Diabetes Nurse Educator, GP.",
            "follow_up_and_monitoring": "Podiatry review in 48 hours for blister; HbA1c recheck in 3 months.",
            "risks_and_escalation": "Immediate same-day clinic contact if toe develops spreading erythema, warmth, or exudate."
        }

        eval_report = self.orchestrator.submit_assessment_and_care_plan(
            session_id=session.id,
            assessment_data=assessment_data,
            care_plan_data=care_plan_data
        )

        self.assertIsNotNone(eval_report)
        self.assertGreater(eval_report.overall_score, 50)
        self.assertEqual(len(eval_report.rubric_scores), 6)

        # 5. Verify Session Status updated to 'evaluated'
        updated_session = repository.get_session_by_id(session.id)
        self.assertEqual(updated_session.status, "evaluated")

        # 6. Verify Markdown Report generation
        report_md = report_service.generate_markdown_report(session.id)
        self.assertIn("Arthur Chen", report_md)
        self.assertIn("Clinical Simulation Report", report_md)
        self.assertIn("Rubric Domain Breakdown", report_md)
        self.assertIn("EDUCATIONAL DISCLAIMER", report_md)

        # 7. Verify Dashboard Metrics calculation
        metrics = repository.get_dashboard_metrics()
        self.assertGreaterEqual(metrics["total_sessions"], 1)
        self.assertGreaterEqual(metrics["completed_sessions"], 1)
        self.assertGreater(metrics["average_score"], 0)

if __name__ == "__main__":
    unittest.main()
