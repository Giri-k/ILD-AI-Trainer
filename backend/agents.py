"""
LLM Agents for the ILD Diagnostic Trainer.
- PatientAgent: Simulates the patient responding to doctor questions
- HintAgent: Provides next-best-step hints
- JudgeAgent: Evaluates the doctor's overall diagnostic performance
- VisionAgent: Analyzes HRCT images using GPT-4 Vision
"""

import os
import json
import base64
from pathlib import Path
from openai import OpenAI

_client = None
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _chat(system_prompt: str, messages: list[dict], temperature: float = 0.3) -> str:
    """Helper to call OpenAI chat completion."""
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=temperature,
        max_tokens=2000,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# PATIENT AGENT
# ---------------------------------------------------------------------------

PATIENT_SYSTEM_PROMPT = """You are a simulated patient in a medical training scenario for interstitial lung disease (ILD).

You must respond ONLY based on the case details provided below. You are role-playing as the patient described in the case.

CRITICAL RULES:
1. Only reveal information that the doctor specifically asks about. Do not volunteer extra details.
2. Respond in first person as the patient would - use plain, patient-appropriate language.
3. If the doctor asks about something not covered in the case details, provide a realistic "normal" or "negative" response consistent with the case.
4. NEVER reveal the diagnosis or hint at it. You are the patient - you don't know your diagnosis.
5. NEVER provide test results - those come from the system when a test is ordered.
6. If asked about physical exam findings, describe your symptoms but let the system provide clinical exam findings.
7. Keep responses concise (2-5 sentences typically).
8. If the doctor asks overly broad questions like "tell me everything", ask them to be more specific.

CASE DETAILS:
{case_details}
"""


def patient_respond(case: dict, conversation_history: list[dict], doctor_question: str) -> str:
    """Generate patient response to a doctor's question."""
    case_details = json.dumps(case["full_case_details"], indent=2)
    system = PATIENT_SYSTEM_PROMPT.format(case_details=case_details)

    messages = []
    for msg in conversation_history[-10:]:  # Keep last 10 messages for context
        if msg["role"] in ("doctor", "user"):
            messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] in ("patient", "assistant"):
            messages.append({"role": "assistant", "content": msg["content"]})

    messages.append({"role": "user", "content": doctor_question})

    return _chat(system, messages)


# ---------------------------------------------------------------------------
# PHYSICAL EXAM AGENT
# ---------------------------------------------------------------------------

EXAM_SYSTEM_PROMPT = """You are a clinical examination simulator for a medical training scenario.

When the doctor asks to perform a physical examination or specific exam maneuvers, provide the relevant clinical findings from the case data below. Present findings in a clinical, objective format as they would appear in medical documentation.

If the doctor asks to examine something not covered in the case data, provide a normal/unremarkable finding consistent with the case.

CASE PHYSICAL EXAM AND TEST DATA:
{case_details}

Respond with clinical findings ONLY. Do not interpret results or suggest diagnoses."""


def perform_exam(case: dict, exam_request: str) -> str:
    """Simulate a physical examination finding."""
    case_details = json.dumps({
        "physical_exam": case["full_case_details"]["physical_exam"],
        "vitals": case["full_case_details"]["physical_exam"].get("vitals", ""),
    }, indent=2)
    system = EXAM_SYSTEM_PROMPT.format(case_details=case_details)
    messages = [{"role": "user", "content": f"The doctor requests: {exam_request}"}]
    return _chat(system, messages)


# ---------------------------------------------------------------------------
# TEST RESULT AGENT
# ---------------------------------------------------------------------------

TEST_RESULT_PROMPT = """You are a clinical laboratory/imaging result system for a medical training scenario.

When a test is ordered, provide the result from the case data if available. If the exact test is not in the case data, generate a realistic result that is CONSISTENT with the case and would NOT be diagnostic on its own.

CASE TEST RESULTS:
{test_results}

CASE DIAGNOSIS (for generating consistent synthetic results): {diagnosis}

Rules:
1. If the test is in the case data, return the EXACT result from the data.
2. If the test is NOT in the data, generate a plausible result consistent with the diagnosis.
3. Present results in standard clinical laboratory format.
4. Do NOT interpret results or suggest diagnoses.
5. Do NOT reveal whether the result is real or synthetic."""


def get_test_result(case: dict, test_name: str) -> tuple[str, list[str]]:
    """Return test results - vision analysis for HRCT with images, or text from case data.
    
    Returns:
        tuple: (result_text, image_paths) where image_paths is empty list if no images
    """
    # Check if this is an HRCT test and if images are available
    test_lower = test_name.lower()
    is_hrct = "hrct" in test_lower or "high resolution ct" in test_lower or "high-resolution ct" in test_lower
    
    hrct_images = case["full_case_details"].get("hrct_images", [])
    
    print(f"DEBUG: Test name: {test_name}")
    print(f"DEBUG: Is HRCT: {is_hrct}")
    print(f"DEBUG: HRCT images found: {hrct_images}")
    
    # Use vision analysis if HRCT test and images available
    if is_hrct and hrct_images:
        print(f"DEBUG: Attempting vision analysis with {len(hrct_images)} images")
        vision_result = analyze_hrct_images(hrct_images, case["ground_truth_diagnosis"])
        if vision_result:
            print(f"DEBUG: Vision analysis successful, returning {len(hrct_images)} images")
            return vision_result, hrct_images
        else:
            print("DEBUG: Vision analysis returned None, falling back to text")
    
    # Fall back to text-based results
    print("DEBUG: Using text-based results")
    test_results = json.dumps(case["full_case_details"]["test_results"], indent=2)
    system = TEST_RESULT_PROMPT.format(
        test_results=test_results,
        diagnosis=case["ground_truth_diagnosis"]
    )
    messages = [{"role": "user", "content": f"The doctor has ordered: {test_name}. Provide the result."}]
    return _chat(system, messages, temperature=0.2), []


# ---------------------------------------------------------------------------
# VISION-BASED HRCT ANALYSIS AGENT
# ---------------------------------------------------------------------------

HRCT_VISION_PROMPT = """You are an expert radiologist analyzing HRCT chest images for interstitial lung disease (ILD) diagnosis.

Analyze the provided HRCT images and provide a detailed radiological report following standard clinical format.

CRITICAL INSTRUCTIONS:
1. Describe what you observe in the images objectively
2. Note the distribution (upper/mid/lower zones, peripheral/central, bilateral/unilateral)
3. Identify key patterns: reticular opacities, ground-glass opacities, honeycombing, traction bronchiectasis, nodules, consolidation, air trapping, mosaic attenuation
4. Comment on pleural changes, lymphadenopathy, and other relevant findings
5. Suggest the most likely radiological pattern (UIP, NSIP, OP, HP, etc.) based on imaging
6. DO NOT provide a definitive diagnosis - only describe imaging findings and patterns
7. Use standard radiological terminology
8. Format as a clinical radiology report

Provide your analysis in this format:

TECHNIQUE: High-resolution CT chest

FINDINGS:
[Detailed description of findings organized by anatomical distribution]

IMPRESSION:
[Summary of key findings and radiological pattern]"""


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_hrct_images(image_paths: list[str], case_diagnosis: str = None) -> str:
    """Analyze HRCT images using GPT-4 Vision."""
    if not image_paths:
        print("DEBUG Vision: No image paths provided")
        return None
    
    print(f"DEBUG Vision: Starting analysis with {len(image_paths)} image paths")
    
    # Prepare image content for the API
    content = [
        {
            "type": "text",
            "text": "Analyze these HRCT chest images and provide a detailed radiological report."
        }
    ]
    
    # Add all images
    for image_path in image_paths:
        try:
            print(f"DEBUG Vision: Checking image path: {image_path}")
            
            # Convert relative path to absolute if needed
            img_path = Path(image_path)
            if not img_path.is_absolute():
                # Try relative to the agents.py file location
                img_path = Path(__file__).parent / image_path.replace("backend/", "")
                print(f"DEBUG Vision: Converted to absolute path: {img_path}")
            
            # Check if file exists
            if not img_path.exists():
                print(f"DEBUG Vision: File does not exist: {img_path}")
                continue
            
            print(f"DEBUG Vision: Encoding image: {img_path}")
            base64_image = encode_image_to_base64(str(img_path))
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high"
                }
            })
            print(f"DEBUG Vision: Successfully encoded image: {image_path}")
        except Exception as e:
            print(f"DEBUG Vision: Error encoding image {image_path}: {e}")
            continue
    
    print(f"DEBUG Vision: Content has {len(content)} items (1 text + {len(content)-1} images)")
    
    if len(content) == 1:  # Only text, no images loaded
        print("DEBUG Vision: No images were successfully loaded")
        return None
    
    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o",  # Use gpt-4o for vision
            messages=[
                {"role": "system", "content": HRCT_VISION_PROMPT},
                {"role": "user", "content": content}
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in vision analysis: {e}")
        return None


# ---------------------------------------------------------------------------
# HINT AGENT
# ---------------------------------------------------------------------------

HINT_SYSTEM_PROMPT = """You are a medical education hint system for an ILD diagnostic training program.

Based on the current state of the diagnostic workup, suggest the SINGLE next best action the doctor should take. This could be a specific question to ask, a test to order, or a recommendation to diagnose.

IDEAL DIAGNOSTIC PATHWAY:
{pathway}

CURRENT STATE:
- All questions asked so far ({num_questions} total): {questions_asked}
- All tests ordered so far ({num_tests} total): {tests_ordered}
- Current step in ideal pathway: {current_step}

CRITICAL RULES:
1. Carefully review ALL questions asked and ALL tests ordered above.
2. Do NOT suggest any question, topic, or test that has already been asked or ordered — even if phrased differently.
3. Suggest only ONE genuinely NEW next action (question or test) that has NOT yet been covered.
4. If history-taking is sufficiently complete, suggest a test. If key tests are done, suggest diagnosing.
5. Briefly explain WHY this is the recommended next step (1-2 sentences).
6. Do NOT reveal the diagnosis.
7. Reference the clinical reasoning behind the suggestion.
8. Format as: "SUGGESTED ACTION: [action]\\nREASONING: [why]"
"""


def get_hint(case: dict, questions_asked: list[str], tests_ordered: list[str]) -> str:
    """Provide a hint for the next best diagnostic step."""
    pathway = json.dumps(case["ideal_diagnostic_pathway"], indent=2)

    # Determine current step based on progress
    current_step = 1
    for i, step in enumerate(case["ideal_diagnostic_pathway"]):
        if step["action"] == "test":
            tests_in_step = step.get("ideal_tests", [])
            if any(t.lower() in [to.lower() for to in tests_ordered] for t in tests_in_step):
                current_step = i + 2
        elif step["action"] == "history":
            if len(questions_asked) >= (i + 1) * 2:
                current_step = i + 2

    system = HINT_SYSTEM_PROMPT.format(
        pathway=pathway,
        questions_asked=json.dumps(questions_asked, indent=2),  # ALL questions, not just last 5
        num_questions=len(questions_asked),
        tests_ordered=json.dumps(tests_ordered, indent=2),
        num_tests=len(tests_ordered),
        current_step=current_step
    )
    messages = [{"role": "user", "content": "What should the doctor do next?"}]
    return _chat(system, messages)


# ---------------------------------------------------------------------------
# JUDGE AGENT
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """You are a medical education evaluator assessing a doctor's diagnostic performance on an ILD case.

GROUND TRUTH DIAGNOSIS: {ground_truth}

IDEAL DIAGNOSTIC PATHWAY:
{ideal_pathway}

DIFFERENTIAL DIAGNOSES FOR THIS CASE:
{differentials}

KEY DISTINGUISHING FEATURES:
{key_features}

DOCTOR'S DIAGNOSTIC JOURNEY:
- Questions asked: {questions}
- Tests ordered: {tests}
- Total cost incurred: ${total_cost}
- Hints used: {hints_used}
- Final diagnosis submitted: {submitted_diagnosis}
- Doctor's reasoning: {reasoning}

EVALUATE the doctor's performance across these dimensions. Respond in valid JSON format ONLY (no markdown, no backticks):

{{
    "diagnostic_accuracy": <1-5 Likert score per rubric below>,
    "diagnostic_accuracy_explanation": "<explanation>",
    "information_gathering": <0-100 score>,
    "information_gathering_explanation": "<explanation>",
    "cost_effectiveness": <0-100 score>,
    "cost_effectiveness_explanation": "<explanation>",
    "clinical_reasoning": <0-100 score>,
    "clinical_reasoning_explanation": "<explanation>",
    "test_appropriateness": <0-100 score>,
    "test_appropriateness_explanation": "<explanation>",
    "overall_feedback": "<2-3 paragraph constructive feedback>",
    "missed_questions": ["<important questions not asked>"],
    "unnecessary_tests": ["<tests ordered that were low-yield>"],
    "missed_tests": ["<critical tests not ordered>"]
}}

DIAGNOSTIC ACCURACY RUBRIC:
5 = Clinically identical to reference or strictly more specific. Perfect.
4 = Core disease correctly identified, minor qualifier missing. Management unchanged.
3 = Correct general category but major error in etiology, site, or specificity.
2 = Shares superficial features only. Fundamentally misdirects workup.
1 = Completely incorrect. No meaningful overlap.
"""


def evaluate_performance(
    case: dict,
    questions_asked: list[str],
    tests_ordered: list[dict],
    total_cost: float,
    hints_used: int,
    submitted_diagnosis: str,
    reasoning: str
) -> dict:
    """Evaluate the doctor's overall diagnostic performance."""
    test_names = [t["name"] for t in tests_ordered]

    system = JUDGE_SYSTEM_PROMPT.format(
        ground_truth=case["ground_truth_diagnosis"],
        ideal_pathway=json.dumps(case["ideal_diagnostic_pathway"], indent=2),
        differentials=json.dumps(case["differential_diagnoses"]),
        key_features=json.dumps(case.get("key_distinguishing_features", {}), indent=2),
        questions=json.dumps(questions_asked),
        tests=json.dumps(test_names),
        total_cost=f"{total_cost:.2f}",
        hints_used=hints_used,
        submitted_diagnosis=submitted_diagnosis,
        reasoning=reasoning
    )

    messages = [{"role": "user", "content": "Evaluate the doctor's performance."}]
    response = _chat(system, messages, temperature=0.1)

    try:
        # Clean response - remove markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {
            "diagnostic_accuracy": 1,
            "diagnostic_accuracy_explanation": "Error parsing evaluation",
            "information_gathering": 50,
            "information_gathering_explanation": "Error parsing evaluation",
            "cost_effectiveness": 50,
            "cost_effectiveness_explanation": "Error parsing evaluation",
            "clinical_reasoning": 50,
            "clinical_reasoning_explanation": "Error parsing evaluation",
            "test_appropriateness": 50,
            "test_appropriateness_explanation": "Error parsing evaluation",
            "overall_feedback": f"Raw evaluation: {response[:500]}",
            "missed_questions": [],
            "unnecessary_tests": [],
            "missed_tests": []
        }

    # Calculate hint penalty
    hint_penalty = max(0, 100 - (hints_used * 15))

    # Calculate overall score
    weights = {
        "diagnostic_accuracy": 0.30,
        "information_gathering": 0.20,
        "cost_effectiveness": 0.15,
        "clinical_reasoning": 0.20,
        "test_appropriateness": 0.10,
        "hint_penalty": 0.05
    }

    accuracy_normalized = (result.get("diagnostic_accuracy", 1) / 5) * 100
    overall = (
        accuracy_normalized * weights["diagnostic_accuracy"] +
        result.get("information_gathering", 50) * weights["information_gathering"] +
        result.get("cost_effectiveness", 50) * weights["cost_effectiveness"] +
        result.get("clinical_reasoning", 50) * weights["clinical_reasoning"] +
        result.get("test_appropriateness", 50) * weights["test_appropriateness"] +
        hint_penalty * weights["hint_penalty"]
    )

    return {
        "overall_score": round(overall, 1),
        "diagnostic_accuracy": result.get("diagnostic_accuracy", 1),
        "diagnostic_accuracy_explanation": result.get("diagnostic_accuracy_explanation", ""),
        "information_gathering": result.get("information_gathering", 50),
        "information_gathering_explanation": result.get("information_gathering_explanation", ""),
        "cost_effectiveness": result.get("cost_effectiveness", 50),
        "cost_effectiveness_explanation": result.get("cost_effectiveness_explanation", ""),
        "clinical_reasoning": result.get("clinical_reasoning", 50),
        "clinical_reasoning_explanation": result.get("clinical_reasoning_explanation", ""),
        "test_appropriateness": result.get("test_appropriateness", 50),
        "test_appropriateness_explanation": result.get("test_appropriateness_explanation", ""),
        "hint_penalty": hint_penalty,
        "overall_feedback": result.get("overall_feedback", ""),
        "missed_questions": result.get("missed_questions", []),
        "unnecessary_tests": result.get("unnecessary_tests", []),
        "missed_tests": result.get("missed_tests", []),
        "ground_truth": case["ground_truth_diagnosis"]
    }
