# AppleSupport AI Agent

This project builds a small, reproducible support-agent prototype for the Hiver SDE take-home assignment.

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