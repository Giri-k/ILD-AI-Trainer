import React, { useState } from "react";
import CaseSelector from "./components/CaseSelector";
import ChatInterface from "./components/ChatInterface";
import EvaluationReport from "./components/EvaluationReport";
import "./App.css";

export default function App() {
  const [view, setView] = useState("select");
  const [session, setSession] = useState(null);
  const [evaluation, setEvaluation] = useState(null);

  const handleCaseStart = (sessionData) => {
    setSession(sessionData);
    setView("chat");
  };

  const handleDiagnosisComplete = (evalData) => {
    setEvaluation(evalData);
    setView("report");
  };

  const handleReset = () => {
    setSession(null);
    setEvaluation(null);
    setView("select");
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon" role="img" aria-label="lungs">&#x1FAC1;</span>
            <div>
              <h1>ILD Diagnostic Trainer</h1>
              <p className="subtitle">Sequential Diagnosis Training for Interstitial Lung Disease</p>
            </div>
          </div>
          {view !== "select" && (
            <button className="btn btn-ghost" onClick={handleReset}>
              &larr; New Case
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        {view === "select" && <CaseSelector onStart={handleCaseStart} />}
        {view === "chat" && session && (
          <ChatInterface
            session={session}
            onDiagnosisComplete={handleDiagnosisComplete}
          />
        )}
        {view === "report" && evaluation && (
          <EvaluationReport
            evaluation={evaluation}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
}
