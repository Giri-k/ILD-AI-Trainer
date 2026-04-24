import React, { useState, useEffect } from "react";
import { getCases, startSession } from "../api";

export default function CaseSelector({ onStart }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCases()
      .then((data) => {
        setCases(data.cases);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleStart = async (caseId) => {
    setStarting(caseId);
    setError(null);
    try {
      const session = await startSession(caseId);
      onStart(session);
    } catch (err) {
      setError(err.message);
      setStarting(null);
    }
  };

  if (loading) {
    return (
      <div className="case-selector" style={{ textAlign: "center", padding: "60px 0" }}>
        <div className="loading-dots"><span></span><span></span><span></span></div>
        <p>Loading cases...</p>
      </div>
    );
  }

  return (
    <div className="case-selector">
      <h2>Select a Clinical Case</h2>
      <p>
        Choose a case below to begin the sequential diagnostic challenge. You will interact
        with a simulated patient, ask questions, order tests, and arrive at a diagnosis.
        Your performance will be evaluated on diagnostic accuracy, cost-effectiveness, and
        clinical reasoning.
      </p>

      {error && (
        <div style={{
          background: "#fef2f2", border: "1px solid #fecaca",
          padding: "12px 16px", borderRadius: "8px", marginBottom: "16px",
          color: "#dc2626", fontSize: "14px"
        }}>
          {error}
        </div>
      )}

      {cases.map((c) => (
        <div
          key={c.id}
          className="case-card"
          onClick={() => !starting && handleStart(c.id)}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
            <h3>{c.title}</h3>
            <span className={`difficulty-badge difficulty-${c.difficulty}`}>
              {c.difficulty}
            </span>
          </div>
          <p>{c.initial_presentation}</p>
          <button
            className="btn btn-primary btn-sm"
            disabled={starting === c.id}
          >
            {starting === c.id ? "Starting..." : "Begin Case"}
          </button>
        </div>
      ))}
    </div>
  );
}
