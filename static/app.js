const messageInput = document.querySelector('#customer-message');
const characterCount = document.querySelector('#character-count');
const intentValue = document.querySelector('#intent-value');
const intentCode = document.querySelector('#intent-code');
const actionValue = document.querySelector('#action-value');
const actionReason = document.querySelector('#action-reason');
const actionIcon = document.querySelector('#action-icon');
const replyValue = document.querySelector('#reply-value');
const confidenceBadge = document.querySelector('#confidence-badge');
const toast = document.querySelector('#toast');
const customerNames = [
  ['Maya Chen', '@maya_chen'],
  ['Alex Morgan', '@alex_morgan'],
  ['Sofia Patel', '@sofia_patel'],
  ['Noah Williams', '@noah_williams'],
  ['Emma Laurent', '@emma_laurent'],
  ['Liam Carter', '@liam_carter']
];

const intentRules = [
  { name: 'Account access', code: 'account_access', words: ['password', 'login', 'locked', 'apple id', 'icloud', 'account'] },
  { name: 'Billing and refund', code: 'billing_refund', words: ['charge', 'charged', 'billing', 'refund', 'payment', 'subscription'] },
  { name: 'Device setup', code: 'device_setup', words: ['setup', 'activate', 'activation', 'restore', 'backup', 'transfer'] },
  { name: 'Software troubleshooting', code: 'software_troubleshooting', words: ['ios', 'update', 'app', 'crash', 'bug', 'not working', 'error', 'battery'] },
  { name: 'Repair and warranty', code: 'repair_warranty', words: ['repair', 'broken', 'screen', 'battery', 'warranty', 'replacement'] },
  { name: 'Order and delivery', code: 'order_delivery', words: ['order', 'ship', 'shipping', 'delivery', 'tracking'] },
  { name: 'Store support', code: 'store_support', words: ['store', 'genius', 'appointment', 'visit'] }
];

const escalationTerms = ['fraud', 'hacked', 'lawyer', 'lawsuit', 'legal', 'threat', 'stolen', 'chargeback'];

function updateCount() {
  characterCount.textContent = `${messageInput.value.length} / 500`;
}

function setRandomCustomer() {
  const [name, handle] = customerNames[Math.floor(Math.random() * customerNames.length)];
  const initials = name.split(' ').map((part) => part[0]).join('');
  document.querySelector('#customer-avatar').textContent = initials;
  document.querySelector('#customer-name').textContent = name;
  document.querySelector('#customer-handle').textContent = `${handle} · just now`;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2400);
}

async function analyzeMessage() {
  const text = messageInput.value.trim();
  if (!text) {
    showToast('Enter a customer message first');
    return;
  }
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    if (!response.ok) throw new Error('API request failed');
    const result = await response.json();
    const shouldEscalate = result.escalate;

    intentValue.textContent = result.intent.replaceAll('_', ' ');
    intentCode.textContent = result.intent;
    confidenceBadge.textContent = `${shouldEscalate ? 82 : 87}% confidence`;
    actionValue.textContent = shouldEscalate ? 'Escalate to human' : 'Auto-handle';
    actionReason.textContent = result.reason;
    actionIcon.textContent = shouldEscalate ? '!' : '✓';
    actionIcon.classList.toggle('escalate', shouldEscalate);
    replyValue.textContent = result.reply;
    await loadEscalations();
    showToast(shouldEscalate ? 'Saved and added to escalation queue' : 'Saved to interaction history');
  } catch (error) {
    showToast('API unavailable. Start Flask with: python app.py');
  }
}

messageInput.addEventListener('input', updateCount);
document.querySelector('#analyze-button').addEventListener('click', analyzeMessage);
document.querySelector('#clear-message').addEventListener('click', () => {
  messageInput.value = '';
  updateCount();
  messageInput.focus();
});

document.querySelectorAll('.suggestion').forEach((button) => {
  button.addEventListener('click', () => {
    messageInput.value = button.dataset.message;
    updateCount();
    analyzeMessage();
  });
});

document.querySelector('#copy-reply').addEventListener('click', async () => {
  await navigator.clipboard.writeText(replyValue.textContent);
  showToast('Draft reply copied');
});
document.querySelector('#edit-reply').addEventListener('click', () => {
  replyValue.contentEditable = 'true';
  replyValue.focus();
  showToast('Draft is editable');
});
document.querySelector('#approve-reply').addEventListener('click', () => showToast('Reply approved for sending'));

updateCount();
setRandomCustomer();

async function loadEscalations() {
  const response = await fetch('/api/escalations?limit=5');
  if (!response.ok) return;
  const data = await response.json();
  const count = document.querySelector('#queue-count');
  const container = document.querySelector('#escalation-queue-items');
  count.textContent = String(data.escalations.length).padStart(2, '0');
  if (!data.escalations.length) return;
  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
  container.innerHTML = data.escalations.map((item, index) => `
    <div class="queue-item">
      <div class="queue-avatar ${['red', 'blue', 'purple'][index % 3]}">${item.intent.slice(0, 2).toUpperCase()}</div>
      <div><strong>${escapeHtml(item.customer_message.slice(0, 42))}${item.customer_message.length > 42 ? '...' : ''}</strong><span>${escapeHtml(item.escalation_reason)}</span></div>
      <span class="queue-arrow">→</span>
    </div>`).join('');
}

async function loadMetrics() {
  const response = await fetch('/api/metrics');
  if (!response.ok) return;
  const metrics = await response.json();
  document.querySelector('#metric-handled').textContent = metrics.handled_today;
  document.querySelector('#metric-escalation').textContent = `${metrics.escalation_rate}%`;
  document.querySelector('#metric-escalated').textContent = `${metrics.escalated_today} escalations today`;
  document.querySelector('#metric-confidence').textContent = `${metrics.baseline_confidence}%`;
}

loadEscalations().catch(() => {});
loadMetrics().catch(() => {});
