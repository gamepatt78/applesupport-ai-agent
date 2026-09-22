const form = document.querySelector('#support-form');
const input = document.querySelector('#support-message');
const resultSection = document.querySelector('#result-section');
const resultIntent = document.querySelector('#result-intent');
const resultReason = document.querySelector('#result-reason');
const resultReply = document.querySelector('#result-reply');
const resultAction = document.querySelector('#result-action');
const resultActionCopy = document.querySelector('#result-action-copy');
const nextIcon = document.querySelector('#next-icon');
const supportLink = document.querySelector('#support-link');
const storeLink = document.querySelector('.store-link');
const toast = document.querySelector('#toast');

const labels = {
  account_access: 'Apple ID and account access',
  billing_refund: 'Billing and subscriptions',
  device_setup: 'Device setup',
  software_troubleshooting: 'Software troubleshooting',
  repair_warranty: 'Repairs and warranty',
  order_delivery: 'Orders and delivery',
  store_support: 'Apple Store support',
  general_inquiry: 'General support question'
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2400);
}

function fallbackAnalyze(message) {
  const text = message.toLowerCase();
  const rules = [
    ['account_access', ['password', 'login', 'locked', 'apple id', 'icloud', 'account']],
    ['billing_refund', ['charge', 'charged', 'billing', 'refund', 'payment', 'subscription']],
    ['device_setup', ['setup', 'activate', 'activation', 'restore', 'backup', 'transfer']],
    ['software_troubleshooting', ['ios', 'update', 'app', 'crash', 'bug', 'not working', 'error', 'battery']],
    ['repair_warranty', ['repair', 'broken', 'screen', 'warranty', 'replacement']],
    ['order_delivery', ['order', 'ship', 'shipping', 'delivery', 'tracking']],
    ['store_support', ['store', 'genius', 'appointment', 'visit']]
  ];
  const match = rules.find(([, words]) => words.some((word) => text.includes(word)));
  const intent = match ? match[0] : 'general_inquiry';
  const risks = ['fraud', 'hacked', 'lawyer', 'lawsuit', 'legal', 'threat', 'stolen', 'chargeback'];
  const matchedRisk = risks.filter((risk) => text.includes(risk));
  const escalate = matchedRisk.length > 0;
  return {
    intent,
    escalate,
    reason: escalate ? `high-risk term: ${matchedRisk.join(', ')}` : 'browser-only guidance; no high-risk term detected',
    reply: escalate
      ? 'A specialist should review this securely. Please do not share passwords, verification codes, or full payment details here.'
      : 'Please check Apple Support for the recommended steps. If the issue continues, visit an Apple Store or contact a specialist.'
  };
}

async function analyze(message) {
  if (!message.trim()) {
    input.focus();
    showToast('Tell us what is happening first');
    return;
  }
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    if (!response.ok) throw new Error('API unavailable');
    return response.json();
  } catch (error) {
    return fallbackAnalyze(message);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submit = form.querySelector('button');
  submit.disabled = true;
  submit.textContent = 'Searching...';
  try {
    const result = await analyze(input.value);
    resultIntent.textContent = labels[result.intent] || result.intent;
    resultReason.textContent = result.reason;
    resultReply.textContent = result.reply;
    const escalated = result.escalate;
    resultAction.textContent = escalated ? 'Talk to a specialist' : 'Try these steps first';
    resultActionCopy.textContent = escalated
      ? 'This issue is better handled by a person who can securely review your account.'
      : 'Start with self-service support. If the issue continues, an Apple specialist can help.';
    nextIcon.textContent = escalated ? '!' : '✓';
    nextIcon.classList.toggle('warn', escalated);
    if (result.intent === 'account_access') {
      supportLink.href = 'https://iforgot.apple.com/';
      supportLink.textContent = 'Recover Apple Account ↗';
    } else if (result.intent === 'repair_warranty') {
      supportLink.href = 'https://support.apple.com/repair';
      supportLink.textContent = 'Start a repair ↗';
    } else {
      supportLink.href = 'https://support.apple.com/';
      supportLink.textContent = 'Apple Support ↗';
    }
    storeLink.href = 'https://www.apple.com/retail/';
    storeLink.textContent = 'Visit an Apple Store ↗';
    resultSection.hidden = false;
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (result.reason.startsWith('browser-only')) {
      showToast('Browser guidance shown; database saving requires the Flask app');
    }
  } finally {
    submit.disabled = false;
    submit.textContent = 'Search';
  }
});

document.querySelectorAll('[data-question]').forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.question;
    input.focus();
    form.requestSubmit();
  });
});

document.querySelector('#close-result').addEventListener('click', () => {
  resultSection.hidden = true;
});
