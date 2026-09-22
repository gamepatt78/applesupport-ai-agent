# AppleSupport AI Agent

This project builds a small, reproducible support-agent prototype for the Hiver SDE take-home assignment.

See [REPORT.md](REPORT.md) for the assignment report, baseline plan, failure analysis, misleading-headline section, and decision log.

## How it works

1. A user enters a customer-support message in the website.
2. The browser sends it as JSON to `POST /api/analyze`.
3. Flask classifies the intent and checks for escalation-risk terms.
4. Flask creates a draft AppleSupport-style reply.
5. The message, intent, decision, reason, reply, and timestamp are saved in SQLite at `data/support.db`.
6. The dashboard refreshes `/api/metrics` and `/api/escalations` to show live database results.

Example:

```text
Input: Someone hacked my Apple account.
Intent: account_access
Action: Escalate to human
Reason: high-risk term: hacked
```

The main implementation files are `app.py` for Flask routes, `src/pipeline.py` for the baseline logic, `src/database.py` for SQLite, `templates/` for HTML, and `static/` for CSS and JavaScript.

Use [LABELING_GUIDE.md](LABELING_GUIDE.md) to label the golden set before running the evaluation harness.

### Component-by-component flow

#### 1. Customer website

The customer opens `/support` and enters a support question. The page is built with HTML in `templates/support.html`, styling in `static/support.css`, and browser interactions in `static/support.js`.

#### 2. API request

When the customer clicks **Search**, JavaScript sends the message to the Flask API:

```http
POST /api/analyze
Content-Type: application/json
```

Example request:

```json
{"message":"My Apple ID is locked"}
```

#### 3. Intent classification

`src/pipeline.py` checks the message against the AppleSupport intent vocabulary. It returns labels such as `account_access`, `billing_refund`, `repair_warranty`, or `software_troubleshooting`. Messages without a matching phrase use `general_inquiry`.

#### 4. Escalation decision

The same module checks for high-risk terms such as `fraud`, `hacked`, `legal`, `stolen`, and `chargeback`. A match produces `escalate: true` and a reason. Otherwise, the request is marked for `auto-handle`.

#### 5. Draft reply

`src/agent.py` retrieves the three most similar historical customer messages with TF-IDF cosine similarity. The best historical AppleSupport reply is included as evidence for the draft. High-risk messages receive a privacy-safe response asking for human review rather than account details or passwords.

#### 6. Database storage

`src/database.py` saves every successful analysis in the SQLite database `data/support.db`. Each row includes the original message, intent, escalation decision, reason, draft reply, and UTC timestamp. The database file is local and excluded from Git.

#### 7. Dashboard updates

The agent dashboard at `/` loads live information from:

- `GET /api/metrics`: today's analyzed count, escalation count, escalation rate, and baseline confidence.
- `GET /api/escalations`: recent high-risk messages for the Needs attention queue.
- `GET /api/history`: recent analysis records.

After a new message is analyzed, the dashboard refreshes the queue so an escalation appears immediately.

#### 8. Public deployment

The Flask API is deployed on Render with:

```text
Build: pip install -r requirements.txt
Start: gunicorn app:app
```

The live application is available at `https://applesupport-ai-agent.onrender.com/`. GitHub Pages can host only the static customer page; it cannot run Flask, the API, or SQLite. The GitHub Actions workflows in `.github/workflows/` validate the code and prepare the static Pages deployment.

## Current scope

- Filter the Customer Support on Twitter dataset to `AppleSupport`.
- Pair incoming customer tweets with Apple's historical reply when the dataset provides a reply link.
- Produce a 200-example labelling sheet for the golden evaluation set.
- Use transparent keyword rules for an initial intent and escalation baseline.

The first version intentionally avoids an API key and heavy model downloads. It creates a trustworthy data slice first; retrieval, LLM drafting, and evaluation can be added on top of this slice.

## Run

From this folder:

```powershell
python -m src.pipeline --input dataset/twcs/twcs.csv --output data/apple_support_sample.csv --golden data/golden_eval.csv --sample-size 2000 --golden-size 200
```

The command writes:

- `data/apple_support_sample.csv`: AppleSupport inbound messages paired with historical replies where available.
- `data/golden_eval.csv`: 200 stratified-by-availability examples with blank labels for manual annotation.

## Run the app

Install dependencies and start the Flask website:

```powershell
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. The app provides message classification, escalation recommendations, and draft replies through the Flask API.

## Database

The Flask app automatically creates a local SQLite database at `data/support.db`. Every successful `/api/analyze` request stores the customer message, intent, escalation decision, reason, draft reply, and UTC timestamp. View recent records with `GET /api/history?limit=20`.

## Deploy with CI/CD

This repository includes [render.yaml](render.yaml) and a GitHub Actions workflow at [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

1. Create a Render Web Service from this GitHub repository.
2. In Render, create a deploy hook for the service.
3. Add the hook URL in GitHub under `Settings > Secrets and variables > Actions` as `RENDER_DEPLOY_HOOK_URL`.
4. Push to `main`. GitHub Actions will install dependencies, validate the Python files, and trigger the Render deployment.

The Render deployment is optional; without the secret, CI passes and reports that deployment was skipped. The GitHub Pages workflow is manual because GitHub Pages must first be enabled under `Settings > Pages > Source: GitHub Actions`.

For each golden example, fill in `intent`, `escalate`, and `label_notes`. Keep the original text and IDs unchanged.

## Suggested intent labels

Use these labels consistently while annotating:

- `account_access`
- `billing_refund`
- `device_setup`
- `software_troubleshooting`
- `repair_warranty`
- `order_delivery`
- `store_support`
- `general_inquiry`
- `other`

## Dataset

The expected input is the Kaggle Customer Support on Twitter CSV, whose columns include `tweet_id`, `author_id`, `inbound`, `text`, `response_tweet_id`, and `in_response_to_tweet_id`. The dataset is not copied or redistributed by this project.

## Next evaluation steps

1. Manually label 150-250 examples.
2. Add TF-IDF and majority-class baselines.
3. Add retrieval of similar historical AppleSupport replies.
4. Add a grounded response generator and escalation policy.
5. Report macro F1, escalation precision/recall, reply quality, failure cases, and judge-human agreement.

## Evaluation commands

After manually filling `intent` and `escalate` in `data/golden_eval.csv`, run:

```powershell
python -m src.evaluate --golden data/golden_eval.csv
```

The harness compares a majority-class intent baseline with TF-IDF plus logistic regression, then reports macro-F1 classification output and escalation precision/recall. It exits before scoring when labels are incomplete so no unsupported headline number is produced.