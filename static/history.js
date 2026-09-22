const state = document.querySelector('#state');
const table = document.querySelector('#history');
const rows = document.querySelector('#rows');
const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));

async function loadHistory() {
  state.textContent = 'Loading history...';
  table.hidden = true;
  const response = await fetch('/api/history?limit=200');
  if (!response.ok) throw new Error('History unavailable');
  const data = await response.json();
  if (!data.interactions.length) { state.textContent = 'No interaction records yet.'; return; }
  rows.innerHTML = data.interactions.map((item) => {
    const escalated = Boolean(item.escalated);
    return `<tr><td>${item.id}</td><td>${escapeHtml(item.customer_message)}</td><td>${escapeHtml(item.intent)}</td><td class="${escalated ? 'escalate' : 'handle'}">${escalated ? 'Escalate' : 'Auto-handle'}</td><td>${escapeHtml(item.escalation_reason)}</td><td>${escapeHtml(item.draft_reply)}</td><td>${escapeHtml(item.created_at)}</td></tr>`;
  }).join('');
  state.textContent = '';
  table.hidden = false;
}

document.querySelector('#refresh').addEventListener('click', () => loadHistory().catch(() => { state.textContent = 'Unable to load history from the database.'; }));
loadHistory().catch(() => { state.textContent = 'Unable to load history from the database.'; });