# ILD Diagnostic Trainer

An interactive medical training application for **Interstitial Lung Disease (ILD)** diagnosis, inspired by Microsoft Research's [Sequential Diagnosis with Language Models](https://arxiv.org/abs/2506.22405) paper and the MAI-DxO orchestrator.

Doctors interact with a simulated patient chatbot, ask questions, order tests, and arrive at a diagnosis — all while being evaluated on multiple dimensions including diagnostic accuracy, cost-effectiveness, and clinical reasoning.

## Architecture

```
┌─────────────────────────────────┐
│         React Frontend          │
│  Case Selector → Chat UI → Report │
└──────────┬──────────────────────┘
           │  REST API
┌──────────▼──────────────────────┐
│       FastAPI Backend           │
│  ┌─────────┐ ┌──────────────┐  │
│  │ Patient  │ │   Hint       │  │
│  │  Agent   │ │   Agent      │  │
│  └────┬─────┘ └──────┬───────┘  │
│       │              │          │
│  ┌────▼─────┐ ┌──────▼───────┐  │
│  │ Test     │ │   Judge      │  │
│  │ Result   │ │   Agent      │  │
│  │ Agent    │ │ (Evaluator)  │  │
│  └──────────┘ └──────────────┘  │
│       All powered by OpenAI     │
└─────────────────────────────────┘
```

## Features

- **3 ILD cases** with full ground truth diagnostic pathways:
  - Idiopathic Pulmonary Fibrosis (IPF)
  - Pulmonary Sarcoidosis
  - Chronic Hypersensitivity Pneumonitis (Bird Fancier's Lung)
- **Patient simulation** — LLM role-plays the patient, revealing info only when asked
- **Hint system** — get next-best-step suggestions (with score penalty)
- **Real-time cost tracking** — US healthcare costs for all ordered tests
- **Multi-dimensional evaluation**:
  - Diagnostic Accuracy (1-5 Likert scale)
  - Information Gathering (0-100)
  - Clinical Reasoning (0-100)
  - Cost Effectiveness (0-100)
  - Test Appropriateness (0-100)
  - Hint Penalty

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **OpenAI API key** with access to GPT-4o (or GPT-4o-mini for lower cost)

## Quick Start

### 1. Clone / download the project

```bash
cd ild-dx-trainer
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger documentation.

### 3. Frontend setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The app will open at `http://localhost:3000`.

## Usage Guide

### For the Training Doctor

1. **Select a case** — read the initial presentation and choose one
2. **Ask questions** — type free-text questions to the patient (history, symptoms, exam)
3. **Order tests** — switch to "Order Test" mode and type test names (e.g., "HRCT Chest", "CBC")
4. **Get hints** — click the hint button if stuck (costs 15 points per hint)
5. **Submit diagnosis** — when confident, submit your diagnosis with reasoning
6. **Review evaluation** — see your multi-dimensional score and detailed feedback

### Tips

- Start with a thorough history before ordering tests
- Ask about occupational/environmental exposures early
- Order cheaper, screening tests before expensive imaging
- Use the cost tracker to stay cost-effective
- Physical exam requests work too (e.g., "Listen to the lungs", "Check for clubbing")

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cases` | List available cases |
| GET | `/api/costs` | Get test cost reference |
| POST | `/api/session/start` | Start a new diagnostic session |
| POST | `/api/session/ask` | Ask the patient a question |
| POST | `/api/session/order-test` | Order a diagnostic test |
| POST | `/api/session/hint` | Request a diagnostic hint |
| POST | `/api/session/diagnose` | Submit final diagnosis |
| GET | `/api/session/{id}` | Get session state |

## Configuration

### Using a different OpenAI model

Edit `backend/.env`:

```
OPENAI_MODEL=gpt-4o-mini    # Cheaper alternative
OPENAI_MODEL=gpt-4o         # Default, best quality
OPENAI_MODEL=o3-mini        # Reasoning model
```

### Changing the API URL for frontend

If the backend runs on a different host/port:

```bash
REACT_APP_API_URL=http://your-server:8000 npm start
```

## Adding New Cases

Add new case objects to `backend/cases.py` following the existing structure:

```python
{
    "id": "ild_004",
    "title": "...",
    "difficulty": "easy|moderate|hard",
    "initial_presentation": "...",
    "full_case_details": { ... },
    "ground_truth_diagnosis": "...",
    "ideal_diagnostic_pathway": [ ... ],
    "differential_diagnoses": [ ... ],
    "key_distinguishing_features": { ... }
}
```

## Inspired By

- [Sequential Diagnosis with Language Models](https://arxiv.org/abs/2506.22405) — Nori, Daswani, Kelly et al., Microsoft AI, 2025
- [Open-MAI-Dx-Orchestrator](https://github.com/The-Swarm-Corporation/Open-MAI-Dx-Orchestrator) — Open source implementation by The Swarm Corporation

## License

MIT
