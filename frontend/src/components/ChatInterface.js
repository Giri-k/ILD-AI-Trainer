import React, { useState, useRef, useEffect } from "react";
import { askQuestion, orderTest, requestHint, submitDiagnosis } from "../api";

export default function ChatInterface({ session, onDiagnosisComplete }) {
  const [messages, setMessages] = useState(session.messages || []);
  const [inputText, setInputText] = useState("");
  const [mode, setMode] = useState("question"); // question | test | diagnose
  const [loading, setLoading] = useState(false);
  const [totalCost, setTotalCost] = useState(session.initial_cost || 300);
  const [testsOrdered, setTestsOrdered] = useState([]);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [questionsCount, setQuestionsCount] = useState(0);
  const [diagnosisText, setDiagnosisText] = useState("");
  const [reasoningText, setReasoningText] = useState("");
  const [showDiagnoseForm, setShowDiagnoseForm] = useState(false);
  const [isDiagnosed, setIsDiagnosed] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading, mode]);

  const addMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSend = async () => {
    if (!inputText.trim() || loading || isDiagnosed) return;
    const text = inputText.trim();
    setInputText("");
    setLoading(true);

    try {
      if (mode === "question") {
        const res = await askQuestion(session.session_id, text);
        addMessage(res.doctor_message);
        addMessage(res.response_message);
        setTotalCost(res.total_cost);
        setQuestionsCount((c) => c + 1);
      } else if (mode === "test") {
        const res = await orderTest(session.session_id, text);
        addMessage(res.order_message);
        addMessage(res.result_message);
        setTotalCost(res.total_cost);
        setTestsOrdered(res.tests_ordered);
      }
    } catch (err) {
      addMessage({
        role: "system",
        content: `Error: ${err.message}. Please try again.`,
      });
    }
    setLoading(false);
  };

  const handleHint = async () => {
    if (loading || isDiagnosed) return;
    setLoading(true);
    try {
      const res = await requestHint(session.session_id);
      addMessage(res.hint_message);
      setHintsUsed(res.hints_used);
    } catch (err) {
      addMessage({
        role: "system",
        content: `Error getting hint: ${err.message}`,
      });
    }
    setLoading(false);
  };

  const handleDiagnose = async () => {
    if (!diagnosisText.trim() || loading) return;
    setLoading(true);
    try {
      const res = await submitDiagnosis(
        session.session_id,
        diagnosisText.trim(),
        reasoningText.trim()
      );
      addMessage(res.diagnosis_message);
      setIsDiagnosed(true);
      setTotalCost(res.total_cost);

      // Delay before showing report
      setTimeout(() => {
        onDiagnosisComplete({
          ...res.evaluation,
          submitted_diagnosis: diagnosisText.trim(),
          total_cost: res.total_cost,
          tests_ordered: testsOrdered,
          hints_used: hintsUsed,
          questions_asked: questionsCount,
        });
      }, 2000);
    } catch (err) {
      addMessage({
        role: "system",
        content: `Error: ${err.message}`,
      });
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessage = (msg, idx) => {
    const roleClass = `message message-${msg.role}`;
    const labels = {
      doctor: "You (Doctor)",
      patient: "Patient",
      system: "System",
      test_result: "Lab / Imaging Result",
      hint: "Hint",
    };

    return (
      <div key={idx} className={roleClass}>
        <span className="message-label">{labels[msg.role] || msg.role}</span>
        <div className="message-bubble">
          {msg.content.split("\n").map((line, i) => {
            // Simple bold rendering for **text**
            const parts = line.split(/\*\*(.*?)\*\*/g);
            return (
              <div key={i}>
                {parts.map((part, j) =>
                  j % 2 === 1 ? <strong key={j}>{part}</strong> : part
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-layout">
      <div className="chat-main">
        {/* Messages */}
        <div className="chat-messages">
          {messages.map(renderMessage)}
          {loading && (
            <div className="message message-system">
              <span className="message-label">System</span>
              <div className="message-bubble">
                <div className="loading-dots">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {!isDiagnosed && (
          <div className="chat-input-area">
            {!showDiagnoseForm ? (
              <>
                <div className="input-mode-tabs">
                  <button
                    className={`tab-btn ${mode === "question" ? "active" : ""}`}
                    onClick={() => setMode("question")}
                  >
                    Ask Patient / Examine
                  </button>
                  <button
                    className={`tab-btn ${mode === "test" ? "active" : ""}`}
                    onClick={() => setMode("test")}
                  >
                    Order Test
                  </button>
                  <button
                    className="tab-btn"
                    style={{ marginLeft: "auto" }}
                    onClick={() => setShowDiagnoseForm(true)}
                  >
                    Submit Diagnosis
                  </button>
                </div>
                <div className="input-row">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                      mode === "question"
                        ? "Ask a question or request physical exam (e.g., 'What does your cough sound like?', 'Listen to lungs')"
                        : "Order a test (e.g., 'HRCT Chest', 'Pulmonary Function Tests', 'ANA')"
                    }
                    disabled={loading}
                  />
                  <button
                    className="btn btn-primary"
                    onClick={handleSend}
                    disabled={loading || !inputText.trim()}
                  >
                    {mode === "question" ? "Ask" : "Order"}
                  </button>
                </div>
              </>
            ) : (
              <div className="diagnosis-form">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <label>Submit Your Final Diagnosis</label>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => setShowDiagnoseForm(false)}
                  >
                    Cancel
                  </button>
                </div>
                <input
                  type="text"
                  placeholder="Your diagnosis (e.g., Idiopathic Pulmonary Fibrosis)"
                  value={diagnosisText}
                  onChange={(e) => setDiagnosisText(e.target.value)}
                  disabled={loading}
                />
                <textarea
                  placeholder="Your clinical reasoning (what led you to this diagnosis)..."
                  value={reasoningText}
                  onChange={(e) => setReasoningText(e.target.value)}
                  disabled={loading}
                />
                <button
                  className="btn btn-success"
                  onClick={handleDiagnose}
                  disabled={loading || !diagnosisText.trim()}
                >
                  {loading ? "Evaluating..." : "Confirm Diagnosis"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="chat-sidebar">
        {/* Cost Tracker */}
        <div className="sidebar-card">
          <h3>&#x1F4B0; Cost Tracker</h3>
          <div className="cost-total">${totalCost.toFixed(2)}</div>
          <div className="cost-breakdown">
            Total diagnostic cost incurred
          </div>
        </div>

        {/* Session Stats */}
        <div className="sidebar-card">
          <h3>&#x1F4CA; Session Stats</h3>
          <div className="stat-row">
            <span className="stat-label">Questions asked</span>
            <span className="stat-value">{questionsCount}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Tests ordered</span>
            <span className="stat-value">{testsOrdered.length}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Hints used</span>
            <span className="stat-value">{hintsUsed}</span>
          </div>
        </div>

        {/* Tests Ordered */}
        {testsOrdered.length > 0 && (
          <div className="sidebar-card">
            <h3>&#x1F9EA; Tests Ordered</h3>
            <div className="test-list">
              {testsOrdered.map((t, i) => (
                <div key={i} className="test-item">
                  <span className="test-item-name">{t.name}</span>
                  <span className="test-item-cost">${t.cost.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        {!isDiagnosed && (
          <div className="sidebar-card">
            <h3>&#x1F6E0; Actions</h3>
            <div className="sidebar-actions">
              <button
                className="btn btn-hint btn-sm"
                onClick={handleHint}
                disabled={loading}
              >
                &#x1F4A1; Get Hint (-15 pts)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
