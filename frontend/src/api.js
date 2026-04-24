const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export function getCases() {
  return request("/api/cases");
}

export function getCosts() {
  return request("/api/costs");
}

export function startSession(caseId) {
  return request("/api/session/start", {
    method: "POST",
    body: JSON.stringify({ case_id: caseId }),
  });
}

export function askQuestion(sessionId, question) {
  return request("/api/session/ask", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, question }),
  });
}

export function orderTest(sessionId, testName) {
  return request("/api/session/order-test", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, test_name: testName }),
  });
}

export function requestHint(sessionId) {
  return request("/api/session/hint", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export function submitDiagnosis(sessionId, diagnosis, reasoning) {
  return request("/api/session/diagnose", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, diagnosis, reasoning }),
  });
}

export function getSession(sessionId) {
  return request(`/api/session/${sessionId}`);
}
