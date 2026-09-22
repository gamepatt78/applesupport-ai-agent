# AppleSupport AI Agent

A reproducible customer-support agent built for the Hiver SDE take-home assignment. The system classifies AppleSupport customer messages, retrieves similar historical replies, drafts a grounded response, and decides whether the case should be auto-handled or escalated.

**Live application:** https://applesupport-ai-agent.onrender.com/

**Customer support view:** https://applesupport-ai-agent.onrender.com/support

**Assignment report:** [REPORT.md](REPORT.md)

## Public URLs

| Resource | URL |
| --- | --- |
| Dashboard | https://applesupport-ai-agent.onrender.com/ |
| Customer support view | https://applesupport-ai-agent.onrender.com/support |
| Database viewer | https://applesupport-ai-agent.onrender.com/database |
| Interaction history | https://applesupport-ai-agent.onrender.com/history |
| Metrics viewer | https://applesupport-ai-agent.onrender.com/metrics |
| Escalation viewer | https://applesupport-ai-agent.onrender.com/escalations |
| Analyze API | https://applesupport-ai-agent.onrender.com/api/analyze |
| History API | https://applesupport-ai-agent.onrender.com/api/history |
| Metrics API | https://applesupport-ai-agent.onrender.com/api/metrics |
| Escalations API | https://applesupport-ai-agent.onrender.com/api/escalations |
| GitHub repository | https://github.com/gamepatt78/applesupport-ai-agent |
| Report PDF | [AppleSupport_AI_Agent_Report.pdf](AppleSupport_AI_Agent_Report.pdf) |

## What the agent does

1. Receives a customer-support message.
2. Assigns a broad intent such as `account_access`, `billing_refund`, or `software_troubleshooting`.
3. Checks for high-risk signals such as fraud, hacking, legal threats, stolen devices, and chargebacks.
4. Retrieves three similar historical AppleSupport conversations using TF-IDF cosine similarity.
5. Produces a reply grounded in the best historical response, or a privacy-safe escalation message.
6. Stores the message, decision, reason, reply, evidence, and timestamp in Render PostgreSQL in production, with SQLite as the local fallback.

Example:

```text
Message: Someone hacked my Apple account.
Intent: account_access
Decision: Escalate to human
Reason: high-risk term: hacked
```

## Architecture

```text
Customer browser
      |
      v
Flask website and API
      |
      +--> Intent and escalation baseline
      +--> TF-IDF historical-reply retrieval
      +--> Grounded response generator
      +--> PostgreSQL interaction log (SQLite locally)
      |
      v
Dashboard metrics and escalation queue
```

### Main components

- `app.py`: Flask routes, API orchestration, response generation, and public entry point.
- `src/pipeline.py`: transparent intent and escalation baselines.
- `src/agent.py`: TF-IDF retrieval and grounded response generation.
- `src/database.py`: PostgreSQL/SQLite schema and interaction-history queries.
- `src/evaluate.py`: majority-class and TF-IDF evaluation harness.
- `templates/`: dashboard and customer-facing HTML.
- `static/`: CSS and browser JavaScript.
- `data/apple_support_sample.csv`: AppleSupport development sample with historical replies.
- `data/golden_eval.csv`: 200-row manually labelled evaluation template.
- `LABELING_GUIDE.md`: annotation instructions.
- `JUDGE_RUBRIC.md`: reply-quality and judge-human agreement rubric.
- `REPORT.md`: assignment report and decision log.

## Run locally

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open the local dashboard:

```text
http://127.0.0.1:5000/
```

Open the customer support page:

```text
http://127.0.0.1:5000/support
```

Open the read-only database viewer:

```text
http://127.0.0.1:5000/database
```

On Windows, `python app.py` is the simplest local start command. Render uses `gunicorn app:app` in production.

## API

### Analyze a message

```http
POST /api/analyze
Content-Type: application/json
```

```json
{"message":"My Apple ID is locked"}
```

The response contains `id`, `intent`, `escalate`, `reason`, `reply`, and retrieved `evidence`.

PowerShell example:

```powershell
$body = @{ message = "My Apple ID is locked" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/analyze" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### Inspect stored data

```text
GET /api/history?limit=20
GET /api/escalations?limit=20
GET /api/metrics
```

The same data is available in a readable browser view at `/database`.

The app uses Render PostgreSQL when the server environment contains `DATABASE_URL`. Without that variable, local development falls back to `data/support.db` using SQLite. The local database is ignored by Git because it contains runtime data.

To connect Render PostgreSQL, copy the database's **Internal Database URL** into the web service environment as `DATABASE_URL`, then save and redeploy. Do not commit or share this URL because it contains credentials. After redeployment, `/api/metrics` reports `database: postgresql` and new records appear in the Render database.

## Rebuild the data slice

The expected source is the Customer Support on Twitter CSV with columns including `tweet_id`, `author_id`, `inbound`, `text`, `response_tweet_id`, and `in_response_to_tweet_id`.

```powershell
python -m src.pipeline `
  --input dataset/twcs/twcs.csv `
  --output data/apple_support_sample.csv `
  --golden data/golden_eval.csv `
  --sample-size 2000 `
  --golden-size 200
```

The command filters AppleSupport conversations, pairs inbound messages with historical replies, and creates a 200-row golden-set template.

## Evaluation

First label the 200 examples in `data/golden_eval.csv`. Fill in:

- `intent`: one of the labels below
- `escalate`: `true` or `false`
- `label_notes`: short reasoning for ambiguous cases

Read [LABELING_GUIDE.md](LABELING_GUIDE.md) before annotating. Then run:

```powershell
python -m src.evaluate --golden data/golden_eval.csv
```

The harness compares:

- A trivial majority-class intent baseline
- A TF-IDF plus Logistic Regression intent classifier
- The escalation baseline using explicit risk terms

It reports classification output, macro-F1, escalation precision, escalation recall, and a confusion matrix. It refuses to report results while labels are incomplete.

For reply quality, use [JUDGE_RUBRIC.md](JUDGE_RUBRIC.md) to score correctness, grounding, actionability, privacy, and tone. Compare the LLM judge with independent human scores on the same examples and report agreement.

## Intent taxonomy

- `account_access`
- `billing_refund`
- `device_setup`
- `software_troubleshooting`
- `repair_warranty`
- `order_delivery`
- `store_support`
- `general_inquiry`
- `other`

## Deployment

The Flask application is deployed on Render as a Web Service with PostgreSQL persistence:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
```

Render environment variable:

```text
DATABASE_URL=<Render PostgreSQL Internal Database URL>
```

GitHub Actions validates the Python code and can trigger an optional Render deploy hook. GitHub Pages can host a static customer-page artifact, but it cannot run Flask, the API, or the database.

## Scope and limitations

This is an evaluation-focused prototype. It does not send messages to Apple, authenticate users, process payments, or claim to resolve accounts automatically. Keyword rules and the retrieval generator are intentionally transparent; measured quality depends on completing the human-labelled golden set.

## License and data note

The source Customer Support on Twitter dataset is not redistributed by this repository. Follow the dataset's terms and cite any external resources used in a final submission.
