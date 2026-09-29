# CareSim AI – Agentic Virtual Patient Simulation Platform

**CareSim AI** is an AI-powered healthcare education and clinical simulation platform where healthcare students and practitioners can interact with realistic fictional virtual patients, conduct clinical history-taking, identify latent safety risks, formulate person-centred care plans, and receive structured educational rubric feedback.

The platform employs a bounded agentic AI architecture with specialized agents operating with clear scope isolation, powered by the **Groq API** with an automatic, deterministic **Demo Mode** fallback.

---

## ⚠️ Healthcare Simulation & Educational Notice

> **Educational Simulation Tool Only:**  
> CareSim AI is designed solely for educational simulation, communication practice, and clinical reasoning training. It is **NOT** a medical device, clinical decision support system, diagnostic tool, or a substitute for qualified professional clinical supervision.
> 
> All patient profiles, records, scenarios, and data are entirely fictional.
> In the event of a real-world medical emergency, immediately contact your local emergency services (e.g., 911 / 999 / 112).

---

## 🏛️ Agentic AI Architecture

The system implements a bounded agentic workflow coordinating specialized agents:

```
                  ┌─────────────────────────────────┐
                  │       Learner (Streamlit)       │
                  └───────────────┬─────────────────┘
                                  │
                                  ▼
                  ┌─────────────────────────────────┐
                  │        Agent Orchestrator       │
                  └──────┬───────────────┬──────────┘
                         │               │
        ┌────────────────▼───┐       ┌───▼────────────────┐
        │   Virtual Patient  │       │  Evaluation Agent  │
        │        Agent       │       │  (Separate Rubric) │
        └────────────────────┘       └────────────────────┘
                         │                     ▲
                         ▼                     │
                  ┌────────────────────────────┴────┐
                  │    SQLite Persistence Layer     │
                  │   (Messages, Notes, Care Plans) │
                  └─────────────────────────────────┘
                                  ▲
                                  │
                  ┌───────────────┴─────────────────┐
                  │  Scenario Authoring Agent (AI)  │
                  │   (Draft -> Educator Approval)  │
                  └─────────────────────────────────┘
```

1. **Virtual Patient Agent (`agents/patient_agent.py`):**
   - Roleplays as the selected fictional patient in the first person.
   - Preserves patient persona, emotional state, dialect, and communication style.
   - Reveals latent/hidden clinical details (e.g., unreported falls, medication side effects, grief, unmanaged pain) progressively in response to targeted, empathetic questions.
   - Never reveals the hidden rubric or acts as a medical doctor.

2. **Assessment and Care Plan Evaluation Agent (`agents/evaluation_agent.py`):**
   - Completely isolated from the consultation phase; only invoked after learner submits their assessment and care plan.
   - Evaluates 6 weighted educational criteria: *Communication (15%)*, *Information Gathering (20%)*, *Holistic Assessment (15%)*, *Risk Identification (20%)*, *Clinical Reasoning (15%)*, and *Person-Centred Care (15%)*.
   - Identifies specific strengths, omissions, latent missed areas, and suggested learning activities.
   - Outputs validated structured JSON with educational feedback scores.

3. **Patient Scenario Authoring Agent (`agents/scenario_agent.py`):**
   - Generates draft fictional patient profiles from educator specifications.
   - Performs clinical consistency and safety checks.
   - Stores new profiles as `DRAFT` until explicitly validated and approved by a human clinical educator.

4. **Agent Orchestrator (`agents/orchestrator.py`):**
   - Coordinates workflow transitions, context passing, state management, and database updates.

---

## 📚 Virtual Patient Library (5 Core Scenarios)

CareSim AI includes five pre-seeded, clinically sound fictional scenarios:

1. **Margaret Dawson (82, Female) – Frailty and Fall Risk:**
   - *Setting:* Community / Home Visit
   - *Core Focus:* Multifactorial fall assessment, postural hypotension, polypharmacy (antihypertensives + OTC sleep aids), living hazards, and preserving home independence.
2. **Arthur Chen (68, Male) – Complex Long-Term Conditions:**
   - *Setting:* Primary Care Outpatient Clinic
   - *Core Focus:* Type 2 Diabetes, CKD Stage 3a, nocturnal neuropathic burning, metformin GI intolerance, hidden toe blister, and diabetes burnout.
3. **Liam O'Connor (34, Male) – Mental Health and Social Isolation:**
   - *Setting:* Community Mental Health / Primary Care
   - *Core Focus:* Major reactive depression, unresolved bereavement, passive suicidal ideation screening, alcohol coping, eviction notice, and protective anchors (pet cat).
4. **Eleanor Vance (74, Female) – End-of-Life and Palliative Care Communication:**
   - *Setting:* Hospice Day Care / Palliative Unit
   - *Core Focus:* Metastatic lung cancer, breakthrough bone pain, opioid addiction fears, caregiver fatigue (daughter Sarah), advance care planning (DNACPR / ReSPECT).
5. **Fatima Al-Mansoor (59, Female) – Integrated Care Coordination:**
   - *Setting:* Intermediate Care / Home Rehabilitation
   - *Core Focus:* Post-ischemic MCA stroke, mild expressive aphasia, delayed community PT/SLT referrals, husband caregiver strain, and multilingual communication.

---

## 💻 Local Setup on Ubuntu & VS Code

### Prerequisites
- Ubuntu 20.04+ or 22.04+
- Python 3.11 (or compatible Python 3.10+)
- Visual Studio Code

### Step-by-Step Installation

1. **Verify Python Installation:**
   ```bash
   python3 --version
   ```

2. **Clone or Open Project in VS Code:**
   ```bash
   cd CareSim-AI
   code .
   ```

3. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` in VS Code and set your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   CARESIM_DEMO_MODE=false
   ```
   *(Note: If you do not have a Groq API key yet, the application automatically runs in **Demo Mode** with realistic, deterministic simulated patient responses).*

6. **Initialize the SQLite Database & Run Tests:**
   ```bash
   python3 tests/run_tests.py
   ```

7. **Launch the Streamlit Application:**
   ```bash
   streamlit run app.py
   ```

8. **Open in Browser:**
   Navigate to `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment

1. **Push to GitHub:**
   Ensure `.env` and `.db` are not committed (handled automatically by `.gitignore`):
   ```bash
   git init
   git add .
   git commit -m "Initial commit of CareSim AI platform"
   git branch -M main
   git remote add origin https://github.com/your-username/caresim-ai.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Sign in with GitHub.
   - Click **New app** and select your repository, branch (`main`), and entry point (`app.py`).

3. **Configure Secrets:**
   In the Streamlit Cloud App Settings under **Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

4. **Persistence Note:**
   Streamlit Cloud uses ephemeral container storage. While SQLite works seamlessly for single-session lifecycles, for production multi-tenant persistent storage across container restarts, point `CARESIM_DB_PATH` to an external database adapter or hosted PostgreSQL service.

---

## 🧪 Automated Testing

Run the full automated test suite with standard `unittest` or `pytest`:

```bash
# Using Python Standard Library runner (zero external dependencies required)
python3 tests/run_tests.py

# Or using pytest (if installed)
pytest tests/ -v
```

The automated test suite verifies:
- Database schema creation and scenario auto-seeding
- Virtual patient multi-turn conversational consistency
- Progressive disclosure of hidden facts
- Learner clinical assessment and care plan persistence
- AI-powered evaluation rubric calculation
- Markdown clinical report generation
- Safe API credentials handling and Demo Mode failovers

---

## 🔒 Security & Safeguards

- **Server-Side API Key Management:** `GROQ_API_KEY` is loaded exclusively server-side via environment variables or Streamlit secrets and is never exposed in client payloads, logs, or reports.
- **Progressive Fact Disclosure:** Confidential hidden facts and rubric scoring keys are withheld from the patient chat prompt context.
- **Safety Flags:** Learners can flag inaccurate or unsafe AI responses directly in the UI.
- **Emergency Protocols:** Automated triggers remind users of real-world emergency protocols if emergency terminology is detected.
