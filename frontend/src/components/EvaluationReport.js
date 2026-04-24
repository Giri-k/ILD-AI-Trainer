import React from "react";

function ScoreBar({ value, max = 100 }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const level = pct >= 70 ? "high" : pct >= 40 ? "medium" : "low";
  return (
    <div className="score-bar-container">
      <div className="score-bar" style={{ width: `${pct}%` }} data-level={level}>
        <div className={`score-bar ${level}`} style={{ width: "100%", height: "100%" }} />
      </div>
    </div>
  );
}

export default function EvaluationReport({ evaluation, onReset }) {
  const overall = evaluation.overall_score || 0;
  const scoreClass =
    overall >= 80 ? "score-excellent" :
    overall >= 60 ? "score-good" :
    overall >= 40 ? "score-fair" : "score-poor";

  const scoreLabel =
    overall >= 80 ? "Excellent" :
    overall >= 60 ? "Good" :
    overall >= 40 ? "Needs Improvement" : "Poor";

  const dimensions = [
    {
      label: "Diagnostic Accuracy",
      value: (evaluation.diagnostic_accuracy / 5) * 100,
      display: `${evaluation.diagnostic_accuracy}/5`,
      explanation: evaluation.diagnostic_accuracy_explanation,
    },
    {
      label: "Information Gathering",
      value: evaluation.information_gathering,
      display: `${evaluation.information_gathering}/100`,
      explanation: evaluation.information_gathering_explanation,
    },
    {
      label: "Clinical Reasoning",
      value: evaluation.clinical_reasoning,
      display: `${evaluation.clinical_reasoning}/100`,
      explanation: evaluation.clinical_reasoning_explanation,
    },
    {
      label: "Cost Effectiveness",
      value: evaluation.cost_effectiveness,
      display: `${evaluation.cost_effectiveness}/100`,
      explanation: evaluation.cost_effectiveness_explanation,
    },
    {
      label: "Test Appropriateness",
      value: evaluation.test_appropriateness,
      display: `${evaluation.test_appropriateness}/100`,
      explanation: evaluation.test_appropriateness_explanation,
    },
    {
      label: "Hint Penalty",
      value: evaluation.hint_penalty,
      display: `${evaluation.hint_penalty}/100`,
      explanation: evaluation.hints_used
        ? `Used ${evaluation.hints_used} hint(s). Each hint deducts 15 points.`
        : "No hints used. Full marks!",
    },
  ];

  return (
    <div className="eval-report">
      {/* Header with overall score */}
      <div className="eval-header">
        <h2>Diagnostic Performance Evaluation</h2>
        <div className={`eval-score-big ${scoreClass}`}>{overall.toFixed(0)}</div>
        <div style={{ fontSize: "18px", color: "#64748b", marginBottom: "8px" }}>
          {scoreLabel}
        </div>

        {/* Diagnosis comparison */}
        <div className="eval-diagnosis-compare">
          <div className="eval-diag-card eval-diag-yours">
            <label>Your Diagnosis</label>
            <p>{evaluation.submitted_diagnosis}</p>
          </div>
          <div className="eval-diag-card eval-diag-correct">
            <label>Correct Diagnosis</label>
            <p>{evaluation.ground_truth}</p>
          </div>
        </div>

        {/* Quick stats */}
        <div style={{
          display: "flex", justifyContent: "center", gap: "32px",
          fontSize: "14px", color: "#64748b"
        }}>
          <span>Questions: {evaluation.questions_asked}</span>
          <span>Tests: {evaluation.tests_ordered?.length || 0}</span>
          <span>Cost: ${evaluation.total_cost?.toFixed(2)}</span>
          <span>Hints: {evaluation.hints_used}</span>
        </div>
      </div>

      {/* Dimension scores */}
      <div className="eval-grid">
        {dimensions.map((d, i) => (
          <div key={i} className="eval-dimension">
            <h4>{d.label}</h4>
            <ScoreBar value={d.value} />
            <div className="score-value">{d.display}</div>
            {d.explanation && (
              <div className="explanation">{d.explanation}</div>
            )}
          </div>
        ))}
      </div>

      {/* Feedback lists */}
      <div className="eval-lists">
        <div className="eval-list-card missed">
          <h4>Important Questions Missed</h4>
          <ul>
            {(evaluation.missed_questions || []).length > 0
              ? evaluation.missed_questions.map((q, i) => <li key={i}>{q}</li>)
              : <li style={{ color: "#16a34a" }}>None - good job!</li>
            }
          </ul>
        </div>
        <div className="eval-list-card unnecessary">
          <h4>Unnecessary Tests Ordered</h4>
          <ul>
            {(evaluation.unnecessary_tests || []).length > 0
              ? evaluation.unnecessary_tests.map((t, i) => <li key={i}>{t}</li>)
              : <li style={{ color: "#16a34a" }}>None - efficient workup!</li>
            }
          </ul>
        </div>
        <div className="eval-list-card missed-tests">
          <h4>Critical Tests Not Ordered</h4>
          <ul>
            {(evaluation.missed_tests || []).length > 0
              ? evaluation.missed_tests.map((t, i) => <li key={i}>{t}</li>)
              : <li style={{ color: "#16a34a" }}>None - thorough workup!</li>
            }
          </ul>
        </div>
      </div>

      {/* Overall feedback */}
      <div className="eval-feedback">
        <h3>Detailed Feedback</h3>
        {(evaluation.overall_feedback || "").split("\n").map((p, i) =>
          p.trim() ? <p key={i}>{p}</p> : null
        )}
      </div>

      {/* Actions */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <button className="btn btn-primary" onClick={onReset} style={{ padding: "14px 32px", fontSize: "16px" }}>
          Try Another Case
        </button>
      </div>
    </div>
  );
}
