const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.error || payload?.message || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

export function runExperiment(userInput, sessionId = null) {
  return request('/api/experiment', {
    method: 'POST',
    body: JSON.stringify({
      user_input: userInput,
      ...(sessionId ? { session_id: sessionId } : {})
    })
  });
}

export function getStatus() {
  return request('/api/status');
}

export function getReactions() {
  return request('/api/reactions');
}
