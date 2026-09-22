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

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2400);
}

function analyzeMessage() {
  const text = messageInput.value.trim();
  const normalized = text.toLowerCase();
  const intent = intentRules.find((rule) => rule.words.some((word) => normalized.includes(word))) || {
    name: 'General inquiry',
    code: 'general_inquiry'
  };
  const matchedRisk = escalationTerms.filter((term) => normalized.includes(term));
  const shouldEscalate = matchedRisk.length > 0;

  intentValue.textContent = intent.name;
  intentCode.textContent = intent.code;
  confidenceBadge.textContent = `${text.length > 20 ? (shouldEscalate ? 82 : 87) : 61}% confidence`;
  actionValue.textContent = shouldEscalate ? 'Escalate to human' : 'Auto-handle';
  actionReason.textContent = shouldEscalate
    ? `High-risk term detected: ${matchedRisk.join(', ')}. A specialist should review this case.`
    : 'Routine support request with no high-risk terms detected.';
  actionIcon.textContent = shouldEscalate ? '!' : '✓';
  actionIcon.classList.toggle('escalate', shouldEscalate);

  if (shouldEscalate) {
    replyValue.textContent = 'Thanks for letting us know. To protect your account, a specialist will review this issue securely. Please do not share passwords, verification codes, or full payment details here.';
  } else if (intent.code === 'billing_refund') {
    replyValue.textContent = 'Hi there, we can help review that charge. Please check your purchase history and reply with the date and amount of the duplicate charge. For your security, do not share full payment details here.';
  } else if (intent.code === 'account_access') {
    replyValue.textContent = 'Hi there, we can help you regain access. Please visit iforgot.apple.com and follow the account recovery steps. Reply here if you get stuck and we’ll take a closer look.';
  } else if (intent.code === 'repair_warranty') {
    replyValue.textContent = 'Hi there, we can help arrange the next step. Please check your coverage at checkcoverage.apple.com, then choose an Apple Store or Apple Authorized Service Provider for an inspection.';
  } else {
    replyValue.textContent = 'Hi there, we can help with that. Please check Settings for the relevant device status and make sure your iPhone is updated to the latest iOS version. If the issue continues, reply here and we’ll take a closer look with you.';
  }

  showToast(shouldEscalate ? 'Escalation recommendation updated' : 'Analysis recommendation updated');
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

loadEscalations().catch(() => {});
