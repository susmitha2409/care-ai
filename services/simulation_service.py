"""
CareSim AI - Simulation Service
Utility helpers for simulation sessions, question prompts, and timer calculation.
"""
from typing import List, Dict, Any, Optional
from database.models import VirtualPatient, SimulationSession, ConversationMessage
from database import repository

def get_suggested_questions(patient: VirtualPatient) -> List[str]:
    """Returns contextual opening/probing questions tailored to the scenario."""
    cat = patient.category.lower()
    if "frailty" in cat or "fall" in cat:
        return [
            "Good morning, Margaret. Can you tell me what happened when you had your fall last week?",
            "Do you ever feel dizzy, lightheaded, or unsteady when getting out of bed or rising from a chair?",
            "What medications or sleep remedies do you take on a daily basis?",
            "How are you managing with stairs and getting around your home independently?"
        ]
    elif "chronic" in cat or "diabetes" in cat:
        return [
            "Hello, Arthur. How have you been feeling since your last chronic disease checkup?",
            "You mentioned fatigue and tingling in your feet—could you describe when that happens?",
            "How are you finding your current medications, including your Metformin doses?",
            "Have you noticed any sores, cuts, or blisters on your feet recently?"
        ]
    elif "mental" in cat or "isolation" in cat:
        return [
            "Hello, Liam. Thank you for coming today. How have things been feeling for you lately?",
            "You mentioned feeling like walking through wet cement—what does an average day look like for you?",
            "When things feel so heavy, do you ever have thoughts that life isn't worth living?",
            "Who or what brings you even a small amount of comfort or routine right now?"
        ]
    elif "palliative" in cat or "end-of-life" in cat:
        return [
            "Hello, Eleanor. How has your pain and breathing been over the past few days?",
            "Can you tell me about how you manage your breakthrough pain medication?",
            "How is Sarah coping with caring for you at home, and what support do you both have?",
            "Have you had a chance to think about what matters most to you for your future care?"
        ]
    elif "stroke" in cat or "integrated" in cat:
        return [
            "Hello, Fatima. How has your recovery been since returning home from the hospital?",
            "Take all the time you need—how are you managing with words and speaking when you're tired?",
            "Have the community physiotherapists or speech therapists been in touch yet?",
            "How is your husband Tariq holding up with helping you around the house?"
        ]
    else:
        return [
            f"Hello, {patient.name}. Could you tell me a little bit about what brought you in today?",
            "What is your biggest concern or difficulty right now?",
            "What are your main goals for our conversation today?"
        ]

def format_duration(seconds: int) -> str:
    """Formats seconds into MM:SS string."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"
