"""
CareSim AI - Virtual Patient Agent
Embodies the fictional patient, responds in first-person, strictly preserves patient persona,
reveals facts only when prompted, and maintains consistency across multi-turn dialogue.
"""
from typing import List, Dict, Any, Optional
from database.models import VirtualPatient, ConversationMessage
from services.groq_service import GroqService

class VirtualPatientAgent:
    def __init__(self, patient: VirtualPatient, groq_service: Optional[GroqService] = None):
        self.patient = patient
        self.groq_service = groq_service or GroqService()

    def build_system_prompt(self) -> str:
        p = self.patient
        meds = ", ".join(p.current_medications) if p.current_medications else "None"
        history = "; ".join(p.medical_history) if p.medical_history else "None"
        symptoms = "; ".join(p.symptoms_and_limitations) if p.symptoms_and_limitations else "None"
        prefs = "; ".join(p.patient_preferences) if p.patient_preferences else "None"
        hidden = "; ".join(p.hidden_facts) if p.hidden_facts else "None"
        safety = "; ".join(p.safety_rules) if p.safety_rules else "None"

        return f"""You are roleplaying as {p.name}, a {p.age}-year-old {p.gender} patient in a healthcare simulation.
Your goal is to provide a realistic, human, and empathetic conversational experience for a healthcare learner.

PATIENT PROFILE:
- Full Name: {p.name}
- Age: {p.age} | Gender: {p.gender}
- Care Setting: {p.care_setting}
- Presenting Concern: {p.presenting_concerns}
- Known Medical History: {history}
- Current Medications: {meds}
- Physical Symptoms & Daily Limitations: {symptoms}
- Living Situation & Social Context: {p.living_situation}
- Emotional State: {p.emotional_state}
- Communication Style: {p.communication_style}
- Personal Preferences & Hopes: {prefs}

CONFIDENTIAL / HIDDEN DETAILS (Reveal ONLY when the learner asks relevant, specific, or empathetic questions):
{hidden}

SCENARIO SAFETY & ROLEPLAY RULES:
1. ALWAYS stay in character as {p.name}. Speak in the FIRST PERSON ("I", "my").
2. NEVER mention that you are an AI, a simulation, an LLM, or a virtual persona.
3. NEVER act as a doctor, clinician, or medical advisor. Do not diagnose yourself or prescribe treatments.
4. Do not recite your whole medical chart in your first answer. Answer questions naturally, conversationally, and concisely (1-4 sentences typical).
5. If the learner asks about something not in your profile, politely say you don't know, can't remember, or it hasn't happened.
6. Scenario Rules: {safety}
7. If the learner appears to be discussing an emergency or expresses that YOU are in acute life-threatening danger, ask if they can help or call an ambulance.
"""

    def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        learner_input: str
    ) -> Dict[str, Any]:
        """
        Generates the patient's next response using Groq, with an intelligent demo fallback.
        """
        # If Groq is configured, attempt LLM generation
        if self.groq_service.is_configured():
            system_prompt = self.build_system_prompt()
            messages = [{"role": "system", "content": system_prompt}]

            # Add previous conversation turns
            for msg in conversation_history[-8:]:  # Maintain reasonable context window
                role = "assistant" if msg.sender == "patient" else "user"
                messages.append({"role": role, "content": msg.content})

            # Append newest learner message
            messages.append({"role": "user", "content": learner_input})

            res = self.groq_service.chat_completion(
                messages=messages,
                temperature=0.6,
                max_tokens=300
            )

            if res.get("content") and not res.get("error"):
                return {
                    "content": res["content"].strip(),
                    "is_demo": False,
                    "error": None
                }

        # Demo mode fallback: contextual deterministic responses
        demo_reply = self._generate_demo_reply(learner_input, conversation_history)
        return {
            "content": demo_reply,
            "is_demo": True,
            "error": None
        }

    def _generate_demo_reply(
        self,
        learner_input: str,
        conversation_history: List[ConversationMessage]
    ) -> str:
        """Contextual heuristic response for demo mode based on patient profile."""
        text = learner_input.lower().strip()
        p = self.patient

        # Margaret Dawson (Frailty & Falls)
        if "margaret" in p.name.lower():
            if any(w in text for w in ["fall", "fell", "happen", "what happened", "bruise"]):
                return "Well, I had a bit of a slip in the hallway last Tuesday. I was rushing to answer the telephone. My daughter saw the bruise on my arm and made a big fuss, but really, I'm quite alright."
            if any(w in text for w in ["dizzy", "dizziness", "lighthead", "standing", "stand up", "faint"]):
                return "Now that you mention it... when I stand up quickly after breakfast, things go a bit fuzzy and I have to hold onto the sideboard for a moment. I just put it down to getting older."
            if any(w in text for w in ["medication", "pill", "tablet", "sleep", "night"]):
                return "I take my blood pressure pills in the morning. And sometimes, when my knees ache or I can't sleep, I take those little over-the-counter blue sleep tablets from the chemist."
            if any(w in text for w in ["stick", "walker", "frame", "walking", "stairs"]):
                return "I have a stick by the door, but to be honest, I hate using it. It makes me feel like an old invalid. I manage by holding onto the furniture, and the stairs are fine if I take them slowly."
            if any(w in text for w in ["how many", "other falls", "past falls", "before"]):
                return "To be completely honest with you... I've tripped a couple of other times over the past month. I didn't tell my daughter because I don't want her putting me in a nursing home."
            if any(w in text for w in ["hello", "hi", "good morning", "how are you"]):
                return "Hello. Thank you for coming by. I'm doing alright, though my daughter insists I have someone check in on me."
            return f"I appreciate your concern. I really just want to stay independent in my own home, dear."

        # Arthur Chen (Complex T2DM & CKD)
        elif "arthur" in p.name.lower():
            if any(w in text for w in ["foot", "feet", "tingling", "burn", "numb", "toes"]):
                return "Yes, my feet have been bothering me at night—like burning pins and needles. And actually, I noticed a small blister under my right big toe from my new walking shoes a couple of days ago."
            if any(w in text for w in ["sugar", "glucose", "check", "monitor", "hba1c"]):
                return "I know my HbA1c is high. To tell you the truth, I stopped checking my blood sugar three weeks ago. Seeing numbers in the 12s and 14s just made me feel like an utter failure."
            if any(w in text for w in ["medication", "metformin", "pills", "adherence", "taking"]):
                return "I take the gliclazide, but the evening Metformin gives me terrible stomach cramps and loose stools. When we have family dinners, I skip it because it's embarrassing."
            if any(w in text for w in ["insulin", "inject", "needle"]):
                return "Please tell me I don't have to start insulin injections. I watched my uncle struggle with needles for years, and it terrifies me."
            if any(w in text for w in ["hello", "hi", "good morning", "how are you"]):
                return "Hello, doctor. Thanks for seeing me. I'm here for my annual checkup, though I suspect my blood sugar numbers aren't what they should be."
            return "I want to get on top of this, but it feels like diabetes is controlling my entire life lately."

        # Liam O'Connor (Mental Health)
        elif "liam" in p.name.lower():
            if any(w in text for w in ["suicide", "harm", "kill yourself", "ending your life", "wake up"]):
                return "I don't have a plan to hurt myself. But some mornings, I just lie there wishing I wouldn't wake up. The only thing that keeps me going is my cat, Buster. No one else would look after him."
            if any(w in text for w in ["alcohol", "drink", "beer", "substance"]):
                return "I've been having 4 or 5 cans of lager at night. It's the only way I can quiet my head and get a few hours of sleep, even if I wake up at 3 AM with dread."
            if any(w in text for w in ["partner", "grief", "loss", "bereavement"]):
                return "It's been 14 months since the car accident. Everyone said time heals, but once the funeral was over and people moved on, the silence just swallowed the apartment."
            if any(w in text for w in ["work", "job", "eviction", "money", "bills"]):
                return "I was laid off from my design job, and I've fallen behind on rent. Got a final notice on Friday. I just feel paralyzed."
            if any(w in text for w in ["hello", "hi", "how are you", "feeling"]):
                return "Hi... thanks for seeing me. Honestly, I don't really know where to start. Everything just feels very heavy lately."
            return "I don't need a lecture on diet or exercise. I just needed to talk to someone who won't judge me."

        # Eleanor Vance (Palliative Care)
        elif "eleanor" in p.name.lower():
            if any(w in text for w in ["pain", "back", "morphine", "breakthrough"]):
                return "My back aches deep down. The doctor prescribed liquid morphine for breakthrough pain, but I only take half because I'm terrified of becoming addicted or too drowsy to talk with my daughter Sarah."
            if any(w in text for w in ["daughter", "sarah", "carer", "support"]):
                return "Sarah has put her whole life on hold for me. When I hurt at night, I bite my lip so I don't wake her. She looks so tired."
            if any(w in text for w in ["wishes", "advance care", "plan", "dnacpr", "hospice", "home"]):
                return "I know my cancer is progressing. When my time comes, I don't want machines or CPR. I just want to be in my own bed at home, looking out at my roses, holding Sarah's hand."
            if any(w in text for w in ["goal", "hope", "milestone", "wedding"]):
                return "My granddaughter Sophie is getting married in three months. More than anything in this world, I want to be well enough to see her walk down the aisle."
            return "Thank you for listening so gently. It helps so much to speak openly about these things."

        # Fatima Al-Mansoor (Stroke & Care Coordination)
        elif "fatima" in p.name.lower():
            if any(w in text for w in ["speech", "words", "talk", "aphasia", "language"]):
                return "Sometimes... the words are in my head, but... they get stuck. I get so frustrated that I start crying. Please bear with me."
            if any(w in text for w in ["therapy", "physio", "exercise", "rehab"]):
                return "The hospital doctor said someone would visit me at home for physiotherapy, but no one has called or come yet. It has been four weeks."
            if any(w in text for w in ["husband", "tariq", "family", "carer"]):
                return "My husband Tariq tries to lift me and help me into the shower, but his back is hurting him very badly now. He hides it, but I see him wince."
            if any(w in text for w in ["medication", "blood thinner", "apixaban"]):
                return "I take the small pills for my heart, but the writing on the packet is so tiny in English that I get confused between the morning and evening box."
            return "I want to be able to use my right hand again so I can cook meals for my grandchildren."

        # Default fallback
        return f"Thank you for asking. Regarding {p.presenting_concerns.lower()}, I am doing my best to cope day by day."
