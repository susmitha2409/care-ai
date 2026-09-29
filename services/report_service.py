"""
CareSim AI - Report Generation Service
Produces professional, exportable Markdown clinical simulation reports.
Excludes all API keys, confidential system prompts, and hidden rubrics.
"""
from typing import Optional
from database.models import (
    SimulationSession,
    VirtualPatient,
    ConversationMessage,
    LearnerAssessment,
    CarePlan,
    EvaluationReport
)
from database import repository
import config

def generate_markdown_report(session_id: str) -> str:
    """Compiles a complete simulation and evaluation report into Markdown format."""
    session = repository.get_session_by_id(session_id)
    if not session:
        return "# Error\nSession record not found."
    
    patient = repository.get_patient_by_id(session.patient_id)
    messages = repository.get_messages_for_session(session_id)
    assessment = repository.get_assessment_by_session(session_id)
    care_plan = repository.get_care_plan_by_session(session_id)
    eval_report = repository.get_evaluation_by_session(session_id)

    duration_str = f"{session.duration_seconds // 60}m {session.duration_seconds % 60}s"
    mode_str = "Demo (Simulated)" if session.is_demo else f"Groq LLM ({config.GROQ_MODEL})"

    report = []
    report.append(f"# {config.APP_NAME} – Clinical Simulation Report")
    report.append(f"**Session ID:** `{session.id}`  ")
    report.append(f"**Date:** {session.started_at} | **Duration:** {duration_str} | **Engine:** {mode_str}\n")
    report.append("---\n")

    # Patient Section
    report.append("## 1. Patient & Scenario Profile")
    if patient:
        report.append(f"- **Patient Name:** {patient.name}")
        report.append(f"- **Demographics:** {patient.age} years old, {patient.gender}")
        report.append(f"- **Clinical Category:** {patient.category}")
        report.append(f"- **Care Setting:** {patient.care_setting}")
        report.append(f"- **Difficulty Level:** {patient.difficulty}")
        report.append(f"- **Presenting Concern:** {patient.presenting_concerns}\n")
    else:
        report.append(f"Patient ID: {session.patient_id}\n")

    # Evaluation Summary Section
    if eval_report:
        report.append("## 2. Educational Evaluation Summary")
        report.append(f"### **Overall Preliminary Score: {eval_report.overall_score} / 100**\n")
        report.append(f"> *{eval_report.overall_summary}*\n")

        report.append("### Rubric Domain Breakdown")
        report.append("| Domain | Score | Weight | Educational Feedback |")
        report.append("| :--- | :---: | :---: | :--- |")
        for key, item in eval_report.rubric_scores.items():
            name = key.replace("_", " ").title()
            report.append(f"| **{name}** | {item.score}% | {int(item.weight * 100)}% | {item.feedback} |")
        report.append("\n")

        report.append("### Key Strengths Demonstrated")
        for s in eval_report.strengths:
            report.append(f"- ✅ {s}")
        report.append("\n")

        report.append("### Priority Areas for Improvement")
        for a in eval_report.areas_for_improvement:
            report.append(f"- 💡 {a}")
        report.append("\n")

        if eval_report.missed_questions_or_areas:
            report.append("### Missed / Latent Clinical Focus Areas")
            for m in eval_report.missed_questions_or_areas:
                report.append(f"- ⚠️ {m}")
            report.append("\n")

        if eval_report.care_plan_feedback:
            report.append("### Care Plan Feedback")
            report.append(f"{eval_report.care_plan_feedback}\n")

        if eval_report.suggested_learning_activities:
            report.append("### Recommended Learning Activities")
            for act in eval_report.suggested_learning_activities:
                report.append(f"- 📚 {act}")
            report.append("\n")
    else:
        report.append("## 2. Evaluation Status")
        report.append("*Assessment and care plan evaluation has not yet been submitted or calculated.*\n")

    # Submitted Assessment
    if assessment and assessment.submitted:
        report.append("## 3. Submitted Clinical Assessment")
        report.append(f"**Presenting Problem:**\n{assessment.presenting_problem or '*(Not documented)*'}\n")
        report.append(f"**Relevant History:**\n{assessment.relevant_history or '*(Not documented)*'}\n")
        report.append(f"**Symptoms & Findings:**\n{assessment.symptoms_and_findings or '*(Not documented)*'}\n")
        report.append(f"**Identified Risks:**\n{assessment.identified_risks or '*(Not documented)*'}\n")
        report.append(f"**Social & Environmental Factors:**\n{assessment.social_and_environmental_factors or '*(Not documented)*'}\n")
        report.append(f"**Further Assessments Required:**\n{assessment.further_assessments_required or '*(Not documented)*'}\n")
        report.append(f"**Proposed Next Steps:**\n{assessment.proposed_next_steps or '*(Not documented)*'}\n")

    # Submitted Care Plan
    if care_plan and care_plan.submitted:
        report.append("## 4. Person-Centred Care Plan")
        report.append(f"**Identified Needs:**\n{care_plan.identified_needs or '*(Not documented)*'}\n")
        report.append(f"**Patient Preferences & Goals:**\n{care_plan.patient_preferences_and_goals or '*(Not documented)*'}\n")
        report.append(f"**Proposed Interventions:**\n{care_plan.proposed_interventions or '*(Not documented)*'}\n")
        report.append(f"**Multidisciplinary Team & Services:**\n{care_plan.multidisciplinary_team_services or '*(Not documented)*'}\n")
        report.append(f"**Follow-up & Monitoring:**\n{care_plan.follow_up_and_monitoring or '*(Not documented)*'}\n")
        report.append(f"**Risks & Escalation Considerations:**\n{care_plan.risks_and_escalation or '*(Not documented)*'}\n")

    # Dialogue Transcript
    report.append("## 5. Simulation Conversation Transcript")
    if messages:
        for m in messages:
            speaker = "Learner" if m.sender == "learner" else (patient.name if patient else "Patient")
            flag_note = " *(Flagged for review)*" if m.flagged else ""
            report.append(f"**[{m.timestamp}] {speaker}:**{flag_note}\n{m.content}\n")
    else:
        report.append("*No messages recorded during this session.*\n")

    # Disclaimer
    report.append("---\n")
    report.append(f"**EDUCATIONAL DISCLAIMER:** {config.DISCLAIMER_TEXT}")

    return "\n".join(report)
