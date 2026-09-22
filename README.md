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