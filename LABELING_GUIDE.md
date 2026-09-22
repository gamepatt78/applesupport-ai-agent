# Golden Set Labeling Guide

Label `data/golden_eval.csv` manually before running the evaluator. The file already contains 200 sampled AppleSupport customer messages.

## Intent labels

Choose exactly one:

- `account_access`: Apple ID, login, password, iCloud, locked or disabled account
- `billing_refund`: charges, subscriptions, payment, refund, purchase history
- `device_setup`: activation, restore, backup, transfer, new-device setup
- `software_troubleshooting`: iOS, app errors, crashes, bugs, update problems
- `repair_warranty`: broken hardware, battery replacement, repair, coverage, warranty
- `order_delivery`: orders, shipment, tracking, delivery, returns
- `store_support`: Apple Store, Genius Bar, appointment, store visit
- `general_inquiry`: informational requests without a more specific issue
- `other`: ambiguous, unreadable, or outside these categories

## Escalation label

Enter `true` when a human should review the case, including fraud, hacked or stolen accounts/devices, legal threats, chargebacks, safety risks, or cases requiring identity verification. Enter `false` for routine informational and troubleshooting requests.

## Labeling process

1. Read only `customer_text` first.
2. Assign one intent and escalation value.
3. Add a short explanation in `label_notes` for ambiguous cases.
4. Review all escalation positives a second time.
5. Keep the original message and tweet IDs unchanged.
6. Run `python -m src.evaluate --golden data/golden_eval.csv` only after all labels are filled.

For reply-quality evaluation, create a second review sheet with columns `message`, `generated_reply`, `correct`, `grounded`, `actionable`, `privacy_safe`, `tone`, and `human_notes`. Use 1/0 scores and compare an LLM judge against the human scores on the same examples.
