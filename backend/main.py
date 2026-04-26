"""
ILD Diagnostic Trainer - FastAPI Backend
A medical training chatbot for interstitial lung disease diagnosis.
"""
from __future__ import annotations

import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models import (
    StartSessionRequest, AskQuestionRequest, OrderTestRequest,
    DiagnoseRequest, HintRequest, ChatMessage
)
from cases import ILD_CASES, list_cases, get_case_by_id, get_test_cost, TEST_COSTS
from agents import patient_respond, perform_exam, get_test_result, get_hint, evaluate_performance

app = FastAPI(
    title="ILD Diagnostic Trainer",
    description="An interactive medical training application for interstitial lung disease diagnosis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
images_dir = Path(__file__).parent / "images"
if images_dir.exists():
    app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")

# In-memory session store
sessions: dict[str, dict] = {}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/cases")
async def get_cases():
    """List all available ILD cases."""
    print("Getting cases...")
    return {"cases": list_cases()}


@app.get("/api/costs")
async def get_costs():
    """Return available test costs for reference."""
    return {"costs": TEST_COSTS}


@app.post("/api/session/start")
async def start_session(req: StartSessionRequest):
    """Start a new diagnostic session for a given case."""
    case = get_case_by_id(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "case_id": req.case_id,
        "case": case,
        "messages": [],
        "conversation_history": [],  # For LLM context
        "tests_ordered": [],
        "questions_asked": [],
        "total_cost": 300.0,  # Initial physician visit cost
        "visit_count": 1,
        "hints_used": 0,
        "is_diagnosed": False,
        "diagnosis": None,
        "evaluation": None,
    }

    # Add initial presentation as first message
    initial_msg = ChatMessage(
        role="system",
        content=f"**Case: {case['title']}**\n\n{case['initial_presentation']}\n\n"
                f"_Initial physician visit cost: $300.00_\n\n"
                f"You may now ask the patient questions, perform physical examination, "
                f"order diagnostic tests, or submit your diagnosis."
    )
    session["messages"].append(initial_msg.model_dump())

    sessions[session_id] = session

    return {
        "session_id": session_id,
        "case_title": case["title"],
        "difficulty": case["difficulty"],
        "initial_presentation": case["initial_presentation"],
        "initial_cost": 300.0,
        "messages": [initial_msg.model_dump()]
    }


@app.post("/api/session/ask")
async def ask_question(req: AskQuestionRequest):
    """Doctor asks the patient a question or requests physical exam."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["is_diagnosed"]:
        raise HTTPException(status_code=400, detail="Diagnosis already submitted")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Add doctor's question to messages
    doc_msg = ChatMessage(role="doctor", content=question)
    session["messages"].append(doc_msg.model_dump())
    session["questions_asked"].append(question)

    # Detect if this is a physical exam request
    exam_keywords = ["examine", "auscult", "palpat", "percuss", "inspect",
                     "listen to", "check vitals", "physical exam", "look at",
                     "lung sounds", "heart sounds", "blood pressure", "oxygen",
                     "spo2", "temperature"]
    is_exam = any(kw in question.lower() for kw in exam_keywords)

    # Add to conversation history for LLM context
    session["conversation_history"].append({"role": "doctor", "content": question})

    if is_exam:
        response = perform_exam(session["case"], question)
        response_msg = ChatMessage(
            role="system",
            content=f"**Physical Examination Finding:**\n{response}"
        )
    else:
        response = patient_respond(
            session["case"],
            session["conversation_history"],
            question
        )
        response_msg = ChatMessage(role="patient", content=response)

    session["messages"].append(response_msg.model_dump())
    session["conversation_history"].append({"role": "patient", "content": response})

    return {
        "doctor_message": doc_msg.model_dump(),
        "response_message": response_msg.model_dump(),
        "total_cost": session["total_cost"]
    }


@app.post("/api/session/order-test")
async def order_test(req: OrderTestRequest):
    """Doctor orders a diagnostic test."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["is_diagnosed"]:
        raise HTTPException(status_code=400, detail="Diagnosis already submitted")

    test_name = req.test_name.strip()
    if not test_name:
        raise HTTPException(status_code=400, detail="Test name cannot be empty")

    # Calculate cost
    cost = get_test_cost(test_name)
    session["total_cost"] += cost

    # Add visit cost if this starts a new round of testing
    # (simplified: every 3 tests = new visit)
    tests_this_session = len(session["tests_ordered"])
    if tests_this_session > 0 and tests_this_session % 3 == 0:
        session["total_cost"] += 300.0
        session["visit_count"] += 1

    # Record the test
    test_record = {"name": test_name, "cost": cost}
    session["tests_ordered"].append(test_record)

    # Add doctor's order message
    order_msg = ChatMessage(
        role="doctor",
        content=f"I'd like to order: **{test_name}**",
        test_name=test_name,
        cost=cost
    )
    session["messages"].append(order_msg.model_dump())

    # Get test result from LLM (now returns tuple with images)
    result, image_paths = get_test_result(session["case"], test_name)
    
    # Convert image paths to URLs accessible by frontend
    image_urls = []
    if image_paths:
        for img_path in image_paths:
            # Convert backend/images/filename.png to /images/filename.png
            filename = Path(img_path).name
            image_urls.append(f"/images/{filename}")
    
    result_msg = ChatMessage(
        role="test_result",
        content=f"**{test_name}** (Cost: ${cost:.2f})\n\n{result}",
        test_name=test_name,
        cost=cost
    )
    session["messages"].append(result_msg.model_dump())

    return {
        "order_message": order_msg.model_dump(),
        "result_message": result_msg.model_dump(),
        "test_cost": cost,
        "total_cost": session["total_cost"],
        "tests_ordered": session["tests_ordered"],
        "images": image_urls  # Add images to response
    }


@app.post("/api/session/hint")
async def request_hint(req: HintRequest):
    """Doctor requests a hint for the next best step."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["is_diagnosed"]:
        raise HTTPException(status_code=400, detail="Diagnosis already submitted")

    session["hints_used"] += 1

    hint = get_hint(
        session["case"],
        session["questions_asked"],
        [t["name"] for t in session["tests_ordered"]]
    )

    hint_msg = ChatMessage(
        role="hint",
        content=f"💡 **Hint #{session['hints_used']}**\n\n{hint}\n\n"
                f"_Note: Each hint reduces your final score by 15 points._"
    )
    session["messages"].append(hint_msg.model_dump())

    return {
        "hint_message": hint_msg.model_dump(),
        "hints_used": session["hints_used"]
    }


@app.post("/api/session/diagnose")
async def submit_diagnosis(req: DiagnoseRequest):
    """Doctor submits their final diagnosis."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["is_diagnosed"]:
        raise HTTPException(status_code=400, detail="Diagnosis already submitted")

    session["is_diagnosed"] = True
    session["diagnosis"] = req.diagnosis

    # Add doctor's diagnosis message
    diag_msg = ChatMessage(
        role="doctor",
        content=f"**Final Diagnosis:** {req.diagnosis}\n\n**Reasoning:** {req.reasoning}"
    )
    session["messages"].append(diag_msg.model_dump())

    # Evaluate performance
    evaluation = evaluate_performance(
        case=session["case"],
        questions_asked=session["questions_asked"],
        tests_ordered=session["tests_ordered"],
        total_cost=session["total_cost"],
        hints_used=session["hints_used"],
        submitted_diagnosis=req.diagnosis,
        reasoning=req.reasoning
    )
    session["evaluation"] = evaluation

    # Add evaluation summary message
    eval_msg = ChatMessage(
        role="system",
        content=(
            f"## Evaluation Complete\n\n"
            f"**Your Diagnosis:** {req.diagnosis}\n"
            f"**Correct Diagnosis:** {session['case']['ground_truth_diagnosis']}\n\n"
            f"**Overall Score: {evaluation['overall_score']}/100**"
        )
    )
    session["messages"].append(eval_msg.model_dump())

    return {
        "diagnosis_message": diag_msg.model_dump(),
        "evaluation": evaluation,
        "ground_truth": session["case"]["ground_truth_diagnosis"],
        "total_cost": session["total_cost"]
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get full session state."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session["session_id"],
        "case_id": session["case_id"],
        "case_title": session["case"]["title"],
        "difficulty": session["case"]["difficulty"],
        "messages": session["messages"],
        "tests_ordered": session["tests_ordered"],
        "total_cost": session["total_cost"],
        "hints_used": session["hints_used"],
        "questions_asked": len(session["questions_asked"]),
        "visit_count": session["visit_count"],
        "is_diagnosed": session["is_diagnosed"],
        "diagnosis": session["diagnosis"],
        "evaluation": session["evaluation"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
