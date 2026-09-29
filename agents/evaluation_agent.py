"""
CareSim AI - Assessment and Care Plan Evaluation Agent
Evaluates communication, clinical reasoning, risk identification, and person-centred care.
Compares against scenario learning objectives and generates validated structured feedback.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from database.models import (
    VirtualPatient,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    EvaluationReport,
    RubricItemScore
)
import config
from services.groq_service import GroqService

logger = logging.getLogger(__name__)

class EvaluationAgent:
    def __init__(self, groq_service: Optional[GroqService] = None):
        self.groq_service = groq_service or GroqService()

    def build_eval_prompt(
        self,
        patient: VirtualPatient,
        conversation_history: List[ConversationMessage],
        assessment: LearnerAssessment,
        care_plan: CarePlan
    ) -> str:
        transcript = "\n".join([f"{m.sender.upper()}: {m.content}" for m in conversation_history])
        expected_areas = "\n- ".join(patient.expected_assessment_areas)
        learning_objs = "\n- ".join(patient.learning_objectives)
        hidden_facts = "\n- ".join(patient.hidden_facts)

        return f"""You are an expert healthcare simulation educator evaluating a healthcare learner's performance.

CASE PROFILE:
- Patient: {patient.name}, {patient.age}yo {patient.gender}
- Category: {patient.category} | Setting: {patient.care_setting}
- Presenting Concern: {patient.presenting_concerns}
- Key Learning Objectives:
- {learning_objs}
- Expected Assessment Focus Areas:
- {expected_areas}
- Hidden / Latent Patient Facts:
- {hidden_facts}

SIMULATION TRANSCRIPT:
{transcript if transcript else "[No conversation recorded]"}

LEARNER CLINICAL ASSESSMENT SUBMISSION:
- Presenting Problem: {assessment.presenting_problem}
- Relevant History: {assessment.relevant_history}
- Symptoms and Findings: {assessment.symptoms_and_findings}
- Identified Risks: {assessment.identified_risks}
- Social and Environmental Factors: {assessment.social_and_environmental_factors}
- Further Assessments Required: {assessment.further_assessments_required}
- Proposed Next Steps: {assessment.proposed_next_steps}

LEARNER PERSON-CENTRED CARE PLAN:
- Identified Needs: {care_plan.identified_needs}
- Patient Preferences & Goals: {care_plan.patient_preferences_and_goals}
- Proposed Support / Interventions: {care_plan.proposed_interventions}
- Multidisciplinary Team & Services: {care_plan.multidisciplinary_team_services}
- Follow-up and Monitoring: {care_plan.follow_up_and_monitoring}
- Risks and Escalation Considerations: {care_plan.risks_and_escalation}

TASK:
Evaluate the learner objectively on a 0-100 scale across the 6 educational domains:
1. 'communication': (Weight 0.15) Empathy, clarity, rapport building, pacing.
2. 'information_gathering': (Weight 0.20) Breadth, targeted inquiry, uncovering hidden details.
3. 'holistic_assessment': (Weight 0.15) Biological, psychological, social, and environmental evaluation.
4. 'risk_identification': (Weight 0.20) Recognition of acute and chronic safety threats, red flags.
5. 'clinical_reasoning': (Weight 0.15) Synthesis of findings, logical justification, prioritization.
6. 'person_centred_care': (Weight 0.15) Alignment with patient's voice, autonomy, and personal goals.

Return ONLY a valid JSON object with the following exact keys:
{{
  "overall_score": <int 0-100>,
  "rubric_scores": {{
    "communication": {{"score": <int>, "feedback": "<str>"}},
    "information_gathering": {{"score": <int>, "feedback": "<str>"}},
    "holistic_assessment": {{"score": <int>, "feedback": "<str>"}},
    "risk_identification": {{"score": <int>, "feedback": "<str>"}},
    "clinical_reasoning": {{"score": <int>, "feedback": "<str>"}},
    "person_centred_care": {{"score": <int>, "feedback": "<str>"}}
  }},
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "areas_for_improvement": ["<area 1>", "<area 2>", "<area 3>"],
  "missed_questions_or_areas": ["<missed area 1>", "<missed area 2>"],
  "missing_risk_considerations": ["<missing risk 1>", "<missing risk 2>"],
  "care_plan_feedback": "<paragraph evaluating feasibility, coordination, and person-centeredness>",
  "suggested_learning_activities": ["<activity 1>", "<activity 2>"],
  "overall_summary": "<paragraph educational summary with encouragement and guidance>"
}}
"""

    def evaluate(
        self,
        session_id: str,
        patient: VirtualPatient,
        conversation_history: List[ConversationMessage],
        assessment: LearnerAssessment,
        care_plan: CarePlan
    ) -> EvaluationReport:
        """
        Runs the evaluation pipeline via Groq or fallback rule-based analyzer.
        """
        if self.groq_service.is_configured():
            prompt = self.build_eval_prompt(patient, conversation_history, assessment, care_plan)
            res = self.groq_service.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a clinical education evaluation specialist. Return only strict JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            if res.get("content") and not res.get("error"):
                try:
                    data = json.loads(res["content"])
                    return self._parse_json_to_report(session_id, patient.id, data, is_demo=False)
                except Exception as e:
                    logger.warning(f"Failed to parse Groq JSON evaluation: {e}")

        # Fallback heuristic / demo evaluation
        return self._generate_heuristic_evaluation(session_id, patient, conversation_history, assessment, care_plan)

    def _parse_json_to_report(
        self,
        session_id: str,
        patient_id: str,
        data: Dict[str, Any],
        is_demo: bool = False
    ) -> EvaluationReport:
        rubric_scores = {}
        for criterion, weight in config.RUBRIC_WEIGHTS.items():
            criterion_data = data.get("rubric_scores", {}).get(criterion, {})
            score = criterion_data.get("score", 70)
            feedback = criterion_data.get("feedback", f"Solid demonstration in {criterion.replace('_', ' ')}.")
            rubric_scores[criterion] = RubricItemScore(
                criterion=criterion,
                score=score,
                weight=weight,
                feedback=feedback
            )

        overall = data.get("overall_score")
        if overall is None:
            # Weighted average
            overall = int(sum(r.score * r.weight for r in rubric_scores.values()))

        return EvaluationReport(
            session_id=session_id,
            patient_id=patient_id,
            overall_score=overall,
            rubric_scores=rubric_scores,
            strengths=data.get("strengths", ["Engaged with patient", "Documented baseline history"]),
            areas_for_improvement=data.get("areas_for_improvement", ["Explore social determinants in greater depth"]),
            missed_questions_or_areas=data.get("missed_questions_or_areas", ["Specific review of non-prescription medications"]),
            missing_risk_considerations=data.get("missing_risk_considerations", ["Postural hypotension screen"]),
            care_plan_feedback=data.get("care_plan_feedback", "Care plan addresses primary concerns with constructive next steps."),
            suggested_learning_activities=data.get("suggested_learning_activities", ["Review NICE guideline on falls/chronic care management"]),
            overall_summary=data.get("overall_summary", "Good simulation completion showing developing clinical competence."),
            evaluated_at="",
            is_demo=is_demo
        )

    def _generate_heuristic_evaluation(
        self,
        session_id: str,
        patient: VirtualPatient,
        conversation_history: List[ConversationMessage],
        assessment: LearnerAssessment,
        care_plan: CarePlan
    ) -> EvaluationReport:
        """Deterministic rubric calculation for demo mode."""
        msg_count = len([m for m in conversation_history if m.sender == "learner"])
        assessment_text = f"{assessment.presenting_problem} {assessment.relevant_history} {assessment.identified_risks} {assessment.symptoms_and_findings}"
        plan_text = f"{care_plan.identified_needs} {care_plan.proposed_interventions} {care_plan.risks_and_escalation}"

        # Information gathering score
        info_score = min(92, max(50, 60 + msg_count * 4 + (len(assessment_text.split()) // 15)))
        # Risk score
        has_risks = len(assessment.identified_risks.strip()) > 20
        risk_score = 85 if has_risks else 62
        # Communication score
        comm_score = min(90, max(55, 65 + msg_count * 3))
        # Person-centred score
        has_goals = len(care_plan.patient_preferences_and_goals.strip()) > 15
        pc_score = 88 if has_goals else 65
        # Clinical reasoning & Holistic
        reasoning_score = min(90, max(55, 70 + (len(assessment.proposed_next_steps.split()) // 5)))
        holistic_score = min(88, max(55, 68 + (len(assessment.social_and_environmental_factors.split()) // 5)))

        rubric_scores = {
            "communication": RubricItemScore(
                criterion="communication",
                score=comm_score,
                weight=config.RUBRIC_WEIGHTS["communication"],
                feedback="Good empathetic questioning and active listening maintained throughout the patient dialogue."
            ),
            "information_gathering": RubricItemScore(
                criterion="information_gathering",
                score=info_score,
                weight=config.RUBRIC_WEIGHTS["information_gathering"],
                feedback=f"Gathered key clinical indicators across {msg_count} interaction turns with appropriate focus on presenting symptoms."
            ),
            "holistic_assessment": RubricItemScore(
                criterion="holistic_assessment",
                score=holistic_score,
                weight=config.RUBRIC_WEIGHTS["holistic_assessment"],
                feedback="Considered living arrangements, family dynamics, and daily functional limitations alongside physical signs."
            ),
            "risk_identification": RubricItemScore(
                criterion="risk_identification",
                score=risk_score,
                weight=config.RUBRIC_WEIGHTS["risk_identification"],
                feedback="Recognized primary safety hazards; ensure proactive screening for unprompted latent risks (e.g. orthostasis, polypharmacy)."
            ),
            "clinical_reasoning": RubricItemScore(
                criterion="clinical_reasoning",
                score=reasoning_score,
                weight=config.RUBRIC_WEIGHTS["clinical_reasoning"],
                feedback="Clear structured synthesis of findings leading into actionable investigative and management steps."
            ),
            "person_centred_care": RubricItemScore(
                criterion="person_centred_care",
                score=pc_score,
                weight=config.RUBRIC_WEIGHTS["person_centred_care"],
                feedback="Demonstrated respect for patient autonomy, preferences, and personal goals in the proposed support plan."
            ),
        }

        overall_score = int(sum(item.score * item.weight for item in rubric_scores.values()))

        strengths = [
            f"Active professional engagement with {patient.name}, building constructive rapport",
            "Structured completion of core clinical assessment domains",
            "Integration of person-centred goals into the care planning framework"
        ]

        areas_for_improvement = [
            "Probe deeper into secondary medication side effects and over-the-counter remedies",
            "Broaden environmental safety assessment (e.g. lighting, footwear, home hazards)",
            "Explicitly define follow-up timeframes and escalation thresholds in the care plan"
        ]

        missed = [
            f"Detailed inquiry regarding {patient.expected_assessment_areas[0] if patient.expected_assessment_areas else 'orthostatic vitals'}",
            "Exploration of latent psychosocial stressors or caregiver burden"
        ]

        missing_risks = [
            "Proactive medication review for drug-drug interactions or sedative effects",
            "Contingency plan if patient condition acutely deteriorates out-of-hours"
        ]

        return EvaluationReport(
            session_id=session_id,
            patient_id=patient.id,
            overall_score=overall_score,
            rubric_scores=rubric_scores,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            missed_questions_or_areas=missed,
            missing_risk_considerations=missing_risks,
            care_plan_feedback=(
                "The submitted care plan presents practical, empathetic steps aligned with the patient's "
                "desire for independence. To strengthen future plans, incorporate specific multi-agency referrals "
                "(e.g., community occupational therapy, pharmacy medication review) with clear review milestones."
            ),
            suggested_learning_activities=[
                "Review evidence-based clinical guidelines on multidisciplinary care transitions",
                "Practice motivational interviewing techniques to uncover hidden medication non-adherence",
                "Explore local community assets and caregiver support services"
            ],
            overall_summary=(
                f"Overall, a commendable and thoughtful simulation with {patient.name}. The assessment reflects "
                "a caring, patient-centred approach with sound baseline clinical reasoning. Incorporating deeper "
                "exploration of latent risks will elevate future clinical consultations."
            ),
            evaluated_at="",
            is_demo=True
        )
