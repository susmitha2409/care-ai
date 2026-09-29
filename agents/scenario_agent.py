"""
CareSim AI - Patient Scenario Authoring Agent
Generates draft fictional scenarios from administrator parameters, validates structure,
flags contradictions, and preserves strict draft/unapproved clinical review status.
"""
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from database.models import VirtualPatient, ClinicalReviewStatus
from services.groq_service import GroqService

logger = logging.getLogger(__name__)

class ScenarioAuthoringAgent:
    def __init__(self, groq_service: Optional[GroqService] = None):
        self.groq_service = groq_service or GroqService()

    def generate_draft_scenario(
        self,
        category: str,
        care_setting: str,
        difficulty: str,
        learning_objectives_input: str,
        additional_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Generates a draft fictional patient scenario.
        Returns a dictionary containing 'patient': VirtualPatient, 'flags': List[str], 'is_demo': bool.
        """
        prompt = f"""You are an expert clinical education author designing a fictional virtual patient scenario.

REQUIREMENTS:
- Scenario Category: {category}
- Care Setting: {care_setting}
- Difficulty Level: {difficulty}
- Core Learning Objectives: {learning_objectives_input}
- Author Guidelines: {additional_notes if additional_notes else "Ensure realistic psychosocial depth and plausible clinical parameters."}

Produce a complete, structured fictional patient profile in JSON format with the following exact keys:
{{
  "name": "<Realistic fictional full name>",
  "age": <integer>,
  "gender": "<Male/Female/Non-binary>",
  "estimated_duration_mins": 15,
  "learning_objectives": ["<objective 1>", "<objective 2>", "<objective 3>"],
  "presenting_concerns": "<2-3 sentences presenting situation>",
  "medical_history": ["<condition 1>", "<condition 2>"],
  "current_medications": ["<medication 1 with dose>", "<medication 2>"],
  "symptoms_and_limitations": ["<symptom 1>", "<symptom 2>"],
  "living_situation": "<description of home, support, family>",
  "emotional_state": "<current mood, fears, attitude>",
  "communication_style": "<tone, speed, hesitations, dialect>",
  "patient_preferences": ["<preference 1>", "<preference 2>"],
  "hidden_facts": ["<hidden fact 1 to reveal when prompted>", "<hidden fact 2>"],
  "expected_assessment_areas": ["<area 1>", "<area 2>", "<area 3>"],
  "safety_rules": ["<rule 1>", "<rule 2>"]
}}
"""
        flags: List[str] = []
        is_demo = True
        patient_data = {}

        if self.groq_service.is_configured():
            res = self.groq_service.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a healthcare simulation author. Return only strict JSON. All content must be fictional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1800,
                response_format={"type": "json_object"}
            )
            if res.get("content") and not res.get("error"):
                try:
                    patient_data = json.loads(res["content"])
                    is_demo = False
                except Exception as e:
                    logger.warning(f"Error parsing generated scenario JSON: {e}")

        # Fallback generator if Groq not available or failed
        if not patient_data:
            patient_data = self._generate_fallback_scenario(category, care_setting, difficulty, learning_objectives_input)
            is_demo = True

        # Validation & Consistency Checks
        flags = self._validate_and_check_consistency(patient_data)

        # Build VirtualPatient model in DRAFT state
        patient_id = f"custom_{uuid.uuid4().hex[:8]}"
        patient = VirtualPatient(
            id=patient_id,
            name=patient_data.get("name", "Fictional Patient"),
            age=int(patient_data.get("age", 65)),
            gender=patient_data.get("gender", "Other"),
            category=category,
            care_setting=care_setting,
            difficulty=difficulty,
            estimated_duration_mins=int(patient_data.get("estimated_duration_mins", 15)),
            learning_objectives=patient_data.get("learning_objectives", [learning_objectives_input]),
            presenting_concerns=patient_data.get("presenting_concerns", "Initial assessment consultation."),
            medical_history=patient_data.get("medical_history", []),
            current_medications=patient_data.get("current_medications", []),
            symptoms_and_limitations=patient_data.get("symptoms_and_limitations", []),
            living_situation=patient_data.get("living_situation", "Lives independently."),
            emotional_state=patient_data.get("emotional_state", "Calm and cooperative."),
            communication_style=patient_data.get("communication_style", "Clear, open communication."),
            patient_preferences=patient_data.get("patient_preferences", []),
            hidden_facts=patient_data.get("hidden_facts", []),
            expected_assessment_areas=patient_data.get("expected_assessment_areas", []),
            safety_rules=patient_data.get("safety_rules", ["Maintain professional boundaries", "Do not give medical advice"]),
            clinical_review_status=ClinicalReviewStatus.DRAFT,  # AI-generated scenarios are always DRAFT initially
            is_custom=True
        )

        return {
            "patient": patient,
            "flags": flags,
            "is_demo": is_demo
        }

    def _validate_and_check_consistency(self, data: Dict[str, Any]) -> List[str]:
        """Flags potential omissions, safety gaps, or contradictions."""
        flags = []
        if not data.get("name"):
            flags.append("Warning: Patient name is missing.")
        if not data.get("age") or data.get("age", 0) <= 0:
            flags.append("Warning: Valid patient age is required.")
        if not data.get("hidden_facts") or len(data.get("hidden_facts", [])) == 0:
            flags.append("Recommendation: Add at least one latent/hidden fact to enable progressive disclosure.")
        if not data.get("expected_assessment_areas"):
            flags.append("Notice: Expected assessment areas list is empty; rubric scoring may lack specificity.")
        
        # Clinical sanity check
        meds = " ".join(data.get("current_medications", [])).lower()
        history = " ".join(data.get("medical_history", [])).lower()
        if "diabetes" in history and not any(w in meds for w in ["metformin", "insulin", "gliclazide", "diet"]):
            flags.append("Clinical Note: Patient has diabetes history but no glucose-lowering therapy or diet management listed.")
        
        flags.append("Review Requirement: Scenario generated by AI. Clinical review and human approval required before use in student evaluations.")
        return flags

    def _generate_fallback_scenario(
        self,
        category: str,
        care_setting: str,
        difficulty: str,
        objectives: str
    ) -> Dict[str, Any]:
        return {
            "name": "David Miller",
            "age": 71,
            "gender": "Male",
            "estimated_duration_mins": 15,
            "learning_objectives": [
                objectives or "Assess holistic health needs and manage care plan"
            ],
            "presenting_concerns": f"Referred for assessment in {care_setting}. Patient seeks guidance regarding {category.lower()} management.",
            "medical_history": ["Mild hypertension", "History of knee replacement"],
            "current_medications": ["Lisinopril 10mg once daily", "Paracetamol 500mg as needed"],
            "symptoms_and_limitations": ["Occasional joint stiffness", "Fatigue during prolonged exertion"],
            "living_situation": "Lives in a single-storey apartment with spouse.",
            "emotional_state": "Slightly guarded but willing to discuss daily routine.",
            "communication_style": "Answers questions thoughtfully; appreciates concise explanations.",
            "patient_preferences": ["Prefers non-pharmacological interventions where suitable", "Values daily walking routines"],
            "hidden_facts": [
                "Has been forgetting morning tablets twice a week due to altered morning schedule.",
                "Worries about increasing prescription expenses."
            ],
            "expected_assessment_areas": [
                "Medication routine and compliance aids",
                "Mobility and home safety check",
                "Psychosocial wellbeing and lifestyle goals"
            ],
            "safety_rules": [
                "Do not diagnose new conditions",
                "Encourage consultation with primary GP for medication adjustments"
            ]
        }
