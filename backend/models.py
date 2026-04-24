"""Pydantic models for the ILD Diagnostic Trainer API."""

from pydantic import BaseModel
from typing import Optional


class StartSessionRequest(BaseModel):
    case_id: str


class AskQuestionRequest(BaseModel):
    session_id: str
    question: str


class OrderTestRequest(BaseModel):
    session_id: str
    test_name: str


class DiagnoseRequest(BaseModel):
    session_id: str
    diagnosis: str
    reasoning: str = ""


class HintRequest(BaseModel):
    session_id: str


class ChatMessage(BaseModel):
    role: str  # "doctor", "patient", "system", "hint", "test_result"
    content: str
    cost: Optional[float] = None
    test_name: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    case_id: str
    case_title: str
    initial_presentation: str
    messages: list[ChatMessage]
    tests_ordered: list[dict]
    total_cost: float
    hints_used: int
    questions_asked: int
    visit_count: int
    is_diagnosed: bool
    diagnosis: Optional[str] = None
    evaluation: Optional[dict] = None


class EvaluationResult(BaseModel):
    overall_score: float  # 0-100
    diagnostic_accuracy: int  # 1-5 Likert scale
    information_gathering: float  # 0-100
    cost_effectiveness: float  # 0-100
    clinical_reasoning: float  # 0-100
    hint_penalty: float  # 0-100 (100 = no hints used)
    test_appropriateness: float  # 0-100
    diagnosis: str
    ground_truth: str
    feedback: str
    detailed_breakdown: dict
