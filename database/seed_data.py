"""
CareSim AI - Seed Data
Contains comprehensive fictional patient scenarios for simulation.
All patient profiles are entirely fictional and designed for educational purposes only.
"""
from typing import List, Dict, Any
from .models import ClinicalReviewStatus

SEED_PATIENTS: List[Dict[str, Any]] = [
    {
        "id": "scenario_frailty_01",
        "name": "Margaret Dawson",
        "age": 82,
        "gender": "Female",
        "category": "Frailty and fall risk",
        "care_setting": "Community / Home Visit",
        "difficulty": "Intermediate",
        "estimated_duration_mins": 15,
        "learning_objectives": [
            "Conduct a multifactorial fall risk assessment in an older adult living alone",
            "Identify intrinsic and environmental risk factors contributing to instability",
            "Explore orthostatic symptoms and polypharmacy implications with empathy",
            "Develop a collaborative, person-centred falls prevention and mobility plan"
        ],
        "presenting_concerns": "Referred by GP for home safety assessment following a fall in the hallway last week. Bruising on left forearm, reluctant to use her walking stick.",
        "medical_history": [
            "Osteoporosis (diagnosed 6 years ago)",
            "Hypertension (15 years)",
            "Osteoarthritis (bilateral knees and hips)",
            "Mild cognitive slowing (age-related, intact capacity)"
        ],
        "current_medications": [
            "Amlodipine 10mg once daily",
            "Bendroflumethiazide 2.5mg once daily (taken in morning)",
            "Alendronic acid 70mg once weekly",
            "Paracetamol 1g as needed for joint pain",
            "Over-the-counter diphenhydramine night-time sleep aid (self-purchased)"
        ],
        "symptoms_and_limitations": [
            "Left knee stiffness and morning crepitus",
            "Unsteadiness when turning around quickly",
            "Difficulty rising from deep armchairs without using both arms",
            "Hesitant gait, touches walls and furniture when moving around house"
        ],
        "living_situation": "Lives alone in a two-storey terraced house. Bedroom is upstairs, bathroom downstairs. Steep stairs without a second handrail. Loose rug in the front hallway.",
        "emotional_state": "Anxious about being placed in a nursing home; fiercely proud and defensive about her independence. Minimizes pain and downplays falls.",
        "communication_style": "Polite, slightly formal, speaks softly. Becomes cautious if she feels the clinician is trying to restrict her freedom or take away her independence.",
        "patient_preferences": [
            "Desperately wants to remain living safely in her own home",
            "Dislikes the look of traditional hospital walking frames ('makes me feel like an invalid')",
            "Enjoys tending to her small garden courtyard and attending church tea on Tuesdays"
        ],
        "hidden_facts": [
            "Has actually fallen three times in the past 6 weeks, not just once. Only reported the last one because her daughter saw the bruise.",
            "Experiences severe lightheadedness and 'fuzzy vision' when standing up quickly after breakfast (orthostatic hypotension caused by combined antihypertensives).",
            "Takes an over-the-counter sedative sleep aid (diphenhydramine) nearly every night, causing grogginess in the morning.",
            "Keeps a loose patterned rug over the hallway tiles because it was an anniversary gift from her late husband."
        ],
        "expected_assessment_areas": [
            "Detailed fall history (frequency, circumstances, loss of consciousness, time spent on floor)",
            "Lying and standing blood pressure assessment (postural hypotension check)",
            "Medication review including OTC drugs and sedative side effects",
            "Home environmental hazards (lighting, footwear, loose rugs, stair handrails)",
            "Mobility, footwear, and balance assessment (e.g. Timed Up and Go)",
            "Osteoporosis fracture risk, bone protection, and emergency alarm availability"
        ],
        "safety_rules": [
            "Do not simulate head trauma, loss of consciousness, or acute fracture unless asked",
            "Refuse immediate care home admission firmly but politely",
            "Express fear of losing autonomy if aggressive interventions are pushed"
        ],
        "clinical_review_status": ClinicalReviewStatus.APPROVED,
        "is_custom": False
    },
    {
        "id": "scenario_chronic_02",
        "name": "Arthur Chen",
        "age": 68,
        "gender": "Male",
        "category": "Complex long-term conditions",
        "care_setting": "Primary Care / Outpatient Clinic",
        "difficulty": "Advanced",
        "estimated_duration_mins": 20,
        "learning_objectives": [
            "Conduct a comprehensive holistic review for multimorbidity (T2DM, CKD, HTN)",
            "Uncover root causes of non-adherence and diabetes distress with motivational interviewing",
            "Identify early peripheral microvascular and renal complications",
            "Formulate a patient-tailored chronic disease management plan"
        ],
        "presenting_concerns": "Attends routine annual chronic disease review. HbA1c elevated at 78 mmol/mol (9.3%). Reports fatigue and 'tingling pins and needles' in both feet at night.",
        "medical_history": [
            "Type 2 Diabetes Mellitus (diagnosed 14 years ago)",
            "Chronic Kidney Disease Stage 3a (eGFR 52 mL/min)",
            "Hypertension (controlled on dual therapy)",
            "Dyslipidemia",
            "Mild non-proliferative diabetic retinopathy"
        ],
        "current_medications": [
            "Metformin 1000mg twice daily with meals",
            "Gliclazide 80mg once daily in morning",
            "Ramipril 5mg once daily",
            "Atorvastatin 20mg at night"
        ],
        "symptoms_and_limitations": [
            "Bilateral burning sensation in soles of feet, worse at bedtime",
            "Generalized mid-afternoon lethargy and reduced stamina",
            "Nocturia 2-3 times per night",
            "Occasional visual blurriness when blood sugar spikes"
        ],
        "living_situation": "Lives with his wife of 42 years in a suburban bungalow. Retired mechanical engineer. Highly analytical mindset, feels ashamed about 'failing' to manage his blood sugar.",
        "emotional_state": "Frustrated, feeling overwhelmed by dietary restrictions and finger-prick checks ('diabetes burnout'). Resigned tone.",
        "communication_style": "Direct, asks logical questions about numbers and test results, but holds back emotional distress until an empathetic, non-judgmental question is asked.",
        "patient_preferences": [
            "Wants to avoid starting daily insulin injections at all costs due to needle anxiety and lifestyle disruption",
            "Values clear quantitative explanations over vague advice like 'eat healthier'",
            "Eager to maintain mobility so he can play with his grandchildren at the park"
        ],
        "hidden_facts": [
            "Frequently skips his evening Metformin dose because it causes severe bloating and loose stools during family dinners.",
            "Has not checked his blood glucose in over 3 weeks because high readings make him feel like a personal failure.",
            "Noticed a small painless blister under his right great toe three days ago from new walking shoes, but hasn't shown anyone.",
            "Wife cooks traditional carbohydrate-heavy meals; he feels guilty asking her to cook separate food just for him."
        ],
        "expected_assessment_areas": [
            "Investigation of medication adherence, side effects, and barriers to compliance",
            "Detailed diabetic foot inspection and sensation testing (monofilament, pulses, blister check)",
            "Evaluation of diabetes burnout and psychological impact of chronic illness",
            "Renal safety review (Metformin dosage adjustment relative to eGFR 52)",
            "Cardiovascular risk factor management and lifestyle support",
            "Hypoglycemia awareness and prevention education"
        ],
        "safety_rules": [
            "Acknowledge the toe blister only if the clinician specifically asks to examine or inspect the feet",
            "Defend wife's cooking lovingly if blamed for poor diet",
            "Show palpable relief if the practitioner offers empathy rather than lecturing"
        ],
        "clinical_review_status": ClinicalReviewStatus.APPROVED,
        "is_custom": False
    },
    {
        "id": "scenario_mental_03",
        "name": "Liam O'Connor",
        "age": 34,
        "gender": "Male",
        "category": "Mental health and social isolation",
        "care_setting": "Community Mental Health / Primary Care",
        "difficulty": "Advanced",
        "estimated_duration_mins": 20,
        "learning_objectives": [
            "Conduct a compassionate mental health assessment and explore depressive symptoms",
            "Execute a thorough, non-judgmental risk assessment (self-harm, suicidal ideation, protective factors)",
            "Identify psychosocial stressors, social isolation, and maladaptive coping mechanisms",
            "Co-create a safety plan and stepped-care therapeutic referral"
        ],
        "presenting_concerns": "Self-presented after being encouraged by an old friend. States: 'I just can't seem to get out of bed or care about anything anymore. Everything feels like walking through wet cement.'",
        "medical_history": [
            "Single previous episode of reactive depression 5 years ago (resolved with brief talking therapy)",
            "No chronic physical illnesses",
            "Occasional tension headaches"
        ],
        "current_medications": [
            "None prescribed currently",
            "Occasional ibuprofen for headaches"
        ],
        "symptoms_and_limitations": [
            "Pervasive low mood and anhedonia for past 4 months",
            "Early morning waking (wakes at 3:30 AM unable to return to sleep)",
            "Weight loss of approx 5kg over 2 months due to loss of appetite",
            "Difficulty concentrating, brain fog, neglecting personal hygiene"
        ],
        "living_situation": "Lives in a rented studio flat alone. Was made redundant from his graphic design job 5 months ago. Estranged from biological parents.",
        "emotional_state": "Despondent, flat affect, tearful when speaking about his late partner who passed away 14 months ago in a road traffic collision. Feels profoundly isolated.",
        "communication_style": "Slow speech rate, pauses often, maintains poor eye contact. Gives short answers initially unless warmth, active listening, and silence are offered.",
        "patient_preferences": [
            "Wants to be listened to as a human being, not reduced to a checklist of psychiatric symptoms",
            "Prefers psychological therapies or support groups over immediate medication, but is open if explained well",
            "Cares deeply about his pet cat, Buster, who is his primary anchor"
        ],
        "hidden_facts": [
            "Drinks 4-5 cans of strong lager every night to numb thoughts and sleep, which has escalated over the last month.",
            "Has experienced passive suicidal thoughts: 'I often think everyone would be better off without me, and I wish I wouldn't wake up.'",
            "No active plan or immediate intent to harm himself, specifically because 'I could never abandon Buster; no one else would feed him.'",
            "Has accumulated mounting utility bills and received a final eviction notice warning two days ago."
        ],
        "expected_assessment_areas": [
            "Detailed assessment of core depressive symptoms (duration, biological features like sleep/appetite)",
            "Direct, sensitive suicide risk inquiry (ideation, intent, plan, access to means, past attempts)",
            "Identification of protective factors (his cat, friend who encouraged visit)",
            "Screening for alcohol and substance misuse as coping strategies",
            "Evaluation of immediate social vulnerability (eviction, debt, food security)",
            "Collaborative safety planning and crisis contact provision"
        ],
        "safety_rules": [
            "Confirm passive suicidal ideation if asked directly, but clearly deny active plan/intent",
            "Highlight his pet cat as a major life anchor",
            "If clinician is dismissive or rushes into prescribing without asking about his grief, become withdrawn"
        ],
        "clinical_review_status": ClinicalReviewStatus.APPROVED,
        "is_custom": False
    },
    {
        "id": "scenario_palliative_04",
        "name": "Eleanor Vance",
        "age": 74,
        "gender": "Female",
        "category": "End-of-life and palliative care communication",
        "care_setting": "Hospice Day Care / Specialist Palliative Unit",
        "difficulty": "Intermediate",
        "estimated_duration_mins": 20,
        "learning_objectives": [
            "Demonstrate sensitive, patient-led communication regarding end-of-life concerns and advance care planning",
            "Explore pain, breakthrough symptoms, and symptom burden with precision",
            "Address patient fears regarding dying, loss of dignity, and family burden",
            "Facilitate advance care planning and preferred place of care/death discussions"
        ],
        "presenting_concerns": "Follow-up consultation to discuss symptom management and future care wishes. Diagnosed with metastatic non-small cell lung cancer 8 months ago, disease progression despite chemotherapy.",
        "medical_history": [
            "Metastatic NSCLC (bone metastases to thoracic spine and ribs)",
            "COPD (Gold Stage 2)",
            "Mild osteoporosis"
        ],
        "current_medications": [
            "Morphine sulfate modified-release (MST Continus) 30mg twice daily",
            "Oramorph (liquid morphine) 10mg as needed for breakthrough pain",
            "Senna and Docusate daily for opioid-induced constipation",
            "Salbutamol inhaler as needed"
        ],
        "symptoms_and_limitations": [
            "Dull constant thoracic back ache with sharp stabbing pain when coughing",
            "Exertional dyspnea walking to the bathroom",
            "Profound cancer-related fatigue (ECOG performance status 2-3)",
            "Dry cough and dry mouth"
        ],
        "living_situation": "Lives at home with her devoted adult daughter Sarah, who has taken unpaid leave from work to act as full-time carer. Close, loving family bond.",
        "emotional_state": "Serene yet emotionally weary. Accepts that her time is limited, but carries heavy guilt about the emotional and physical toll on her daughter.",
        "communication_style": "Gentle, reflective, thoughtful. Values honesty and compassionate directness. Appreciates when clinicians do not beat around the bush.",
        "patient_preferences": [
            "Strong desire to remain comfortable and die peacefully at home in her own bed, looking out at the garden",
            "Wants to avoid invasive medical interventions (CPR, ventilators, ICU admission) if her condition deteriorates",
            "Wishes for clear guidance for her daughter on what to expect during the dying phase"
        ],
        "hidden_facts": [
            "Takes less than half of her prescribed breakthrough morphine because she is terrified of becoming 'addicted' or 'a zombie who can't speak with Sarah'.",
            "Wakes up crying at night with unmanaged pain but refuses to call Sarah into the room because 'Sarah needs her sleep.'",
            "Has not yet documented an Advance Decision to Refuse Treatment (ADRT) or ReSPECT / DNACPR form because she didn't know how to raise it with her daughter without causing distress.",
            "Deep personal wish to live long enough to attend her granddaughter's wedding in 3 months' time, or at least watch a livestream."
        ],
        "expected_assessment_areas": [
            "Detailed pain assessment (OPQRST, neuropathic vs somatic, breakthrough frequency, opioid myths/fears)",
            "Symptom control review (dyspnea, nausea, bowel function, dry mouth)",
            "Psychological and existential exploration (fears, guilt, hopes, milestones)",
            "Advance Care Planning (DNACPR status, preferred place of care, emergency anticipatory medication)",
            "Caregiver support and respite evaluation for daughter Sarah"
        ],
        "safety_rules": [
            "Express fear of opioid addiction/sedation if pain meds are increased without education",
            "Emphasize desire for dignified home-based care without invasive resuscitation",
            "React warmly to holistic reassurance about symptom control"
        ],
        "clinical_review_status": ClinicalReviewStatus.APPROVED,
        "is_custom": False
    },
    {
        "id": "scenario_integrated_05",
        "name": "Fatima Al-Mansoor",
        "age": 59,
        "gender": "Female",
        "category": "Integrated care coordination",
        "care_setting": "Community Rehabilitation / Intermediate Care",
        "difficulty": "Intermediate",
        "estimated_duration_mins": 15,
        "learning_objectives": [
            "Navigate complex multidisciplinary care transitions following an acute medical event",
            "Assess post-stroke functional deficits, mild expressive aphasia, and emotional adjustment",
            "Identify cultural, linguistic, and informal family care dynamics",
            "Design an integrated care coordination plan connecting health, social care, and community assets"
        ],
        "presenting_concerns": "Home assessment 4 weeks following discharge from hyperacute stroke unit after an ischemic left MCA stroke. Right-sided hemiparesis and mild expressive communication difficulty.",
        "medical_history": [
            "Left MCA Ischemic Stroke (4 weeks ago)",
            "Hypertension (10 years)",
            "Atrial Fibrillation (newly diagnosed during stroke admission)",
            "High Cholesterol"
        ],
        "current_medications": [
            "Apixaban 5mg twice daily",
            "Atorvastatin 40mg at night",
            "Lisinopril 10mg once daily"
        ],
        "symptoms_and_limitations": [
            "Right hand weakness (struggles with buttons, keys, cutlery)",
            "Circumlocution and word-finding difficulty when tired or rushed",
            "Mild gait imbalance, uses a single-point stick outdoors",
            "Emotional lability (cries unexpectedly when frustrated with speech)"
        ],
        "living_situation": "Lives in a multigenerational household with her husband Tariq, eldest son, daughter-in-law, and two young grandchildren. Culturally vibrant, supportive environment.",
        "emotional_state": "Determined and proud, but deeply embarrassed when she cannot find words in English. Feels she is burdening her daughter-in-law.",
        "communication_style": "English is her second language (fluent Arabic speaker). Speaks deliberate, clear English, but struggles when spoken to rapidly. Needs extra processing time and patience.",
        "patient_preferences": [
            "Desires to cook traditional meals again for her grandchildren",
            "Prefers community rehabilitation exercises that fit into her daily home routine rather than distant hospital visits",
            "Requests female healthcare professionals for personal care if bathing support is needed"
        ],
        "hidden_facts": [
            "Community physiotherapy and speech therapy visits have not started yet because the discharge referral paperwork got lost between hospital and community trust.",
            "Her husband Tariq has taken on heavy lifting and is experiencing worsening chronic lumbar back strain, which they are hiding.",
            "She misses taking Apixaban occasionally because the blister pack text is too small to read and she confuses morning/night compartments.",
            "Feels isolated from her Arabic-speaking women's social circle at the local community center because she is embarrassed by her arm limp and speech."
        ],
        "expected_assessment_areas": [
            "Multidisciplinary discharge follow-up verification (OT, PT, Speech and Language Therapy)",
            "Medication safety and adherence check for anticoagulation (DOAC dosing, compliance aid)",
            "Functional independence assessment (activities of daily living, cooking safety, upper limb rehab)",
            "Carer strain and caregiver health screening (husband Tariq)",
            "Psychosocial and cultural inclusion (local Arabic community support, stroke recovery groups)",
            "Secondary stroke prevention education and red flags"
        ],
        "safety_rules": [
            "Pause and search for words occasionally to realistically reflect mild expressive aphasia",
            "Reveal the missing community therapy referral only when asked about current services or therapy visits",
            "Express warm appreciation when practitioner speaks clearly and gives adequate time to respond"
        ],
        "clinical_review_status": ClinicalReviewStatus.APPROVED,
        "is_custom": False
    }
]
