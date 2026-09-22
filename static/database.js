const elements = {
  database: document.querySelector('#database-name'),
  handled: document.querySelector('#handled-count'),
  escalated: document.querySelector('#escalated-count'),
  rate: document.querySelector('#escalation-rate'),
  count: document.querySelector('#record-count'),
  state: document.querySelector('#table-state'),
  table: document.querySelector('#records-table'),
  body: document.querySelector('#records-body')
};

const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));

async function loadDatabase() {
  elements.state.textContent = 'Loading database records...';
  elements.table.hidden = true;
  const [metricsResponse, historyResponse] = await Promise.all([fetch('/api/metrics'), fetch('/api/history?limit=200')]);
  if (!metricsResponse.ok || !historyResponse.ok) throw new Error('Database API unavailable');
  const metrics = await metricsResponse.json();
  const history = await historyResponse.json();
  elements.database.textContent = metrics.database || 'Connected';
  elements.handled.textContent = metrics.handled_today;
  elements.escalated.textContent = metrics.escalated_today;
  elements.rate.textContent = `${metrics.escalation_rate}%`;
  elements.count.textContent = `${history.interactions.length} records`;
  if (!history.interactions.length) { elements.state.textContent = 'No interactions have been saved yet.'; return; }
  elements.body.innerHTML = history.interactions.map((item) => {
    const escalated = Boolean(item.escalated);
    return `<tr><td>${item.id}</td><td>${escapeHtml(item.customer_message)}</td><td>${escapeHtml(item.intent)}</td><td class="${escalated ? 'escalate' : 'handle'}">${escalated ? 'Escalate' : 'Auto-handle'}</td><td>${escapeHtml(item.escalation_reason)}</td><td>${escapeHtml(item.created_at)}</td></tr>`;
  }).join('');
  elements.state.textContent = '';
  elements.table.hidden = false;
}

document.querySelector('#refresh').addEventListener('click', () => loadDatabase().catch(() => { elements.state.textContent = 'Unable to load database records. Check the server logs.'; }));
loadDatabase().catch(() => { elements.database.textContent = 'Unavailable'; elements.state.textContent = 'Unable to load database records. Check the server logs.'; });