const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export async function checkServerHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error("Health check failed");
    return await res.json();
  } catch (err) {
    return { status: "offline", error: err.message };
  }
}

export async function submitReviewTask(payload) {
  const res = await fetch(`${API_BASE}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Unknown server error" }));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  return await res.json();
}

export async function validateDeterministically(code, language) {
  const res = await fetch(`${API_BASE}/validate-only`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language })
  });
  if (!res.ok) throw new Error("Validation check failed");
  return await res.json();
}

export async function fetchReviewHistory() {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error("Failed to load history");
  return await res.json();
}

export async function fetchReportById(taskId) {
  const res = await fetch(`${API_BASE}/report/${taskId}`);
  if (!res.ok) throw new Error("Report not found");
  return await res.json();
}

export async function fetchReportMarkdown(taskId) {
  const res = await fetch(`${API_BASE}/export/${taskId}/markdown`);
  if (!res.ok) throw new Error("Export failed");
  return await res.text();
}
