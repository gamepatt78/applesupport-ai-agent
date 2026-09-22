"""Build a reproducible AppleSupport data slice and golden-set template."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


INTENT_KEYWORDS = {
    "account_access": ("password", "login", "locked", "apple id", "icloud", "account"),
    "billing_refund": ("charge", "charged", "billing", "refund", "payment", "subscription"),
    "device_setup": ("setup", "activate", "activation", "restore", "backup", "transfer"),
    "software_troubleshooting": ("ios", "update", "app", "crash", "bug", "not working", "error"),
    "repair_warranty": ("repair", "broken", "screen", "battery", "warranty", "replacement"),
    "order_delivery": ("order", "ship", "shipping", "delivery", "tracking"),
    "store_support": ("store", "genius", "appointment", "visit"),
}

ESCALATION_TERMS = (
    "fraud",
    "hacked",
    "lawyer",
    "lawsuit",
    "legal",
    "threat",
    "stolen",
    "chargeback",
)


def classify_baseline(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text).lower()).strip()
    scores = {
        intent: sum(keyword in normalized for keyword in keywords)
        for intent, keywords in INTENT_KEYWORDS.items()
    }
    strongest_intent = max(scores, key=scores.get)
    if scores[strongest_intent] > 0:
        return strongest_intent
    return "general_inquiry"


def escalation_baseline(text: str) -> tuple[bool, str]:
    normalized = str(text).lower()
    matches = [term for term in ESCALATION_TERMS if term in normalized]
    if matches:
        return True, "high-risk term: " + ", ".join(matches)
    return False, "no high-risk term detected"


def load_apple_support(path: Path) -> pd.DataFrame:
    columns = [
        "tweet_id",
        "author_id",
        "inbound",
        "created_at",
        "text",
        "response_tweet_id",
        "in_response_to_tweet_id",
    ]
    frame = pd.read_csv(path, usecols=columns)
    frame["author_id"] = frame["author_id"].astype(str)
    frame = frame.dropna(subset=["text"]).drop_duplicates(subset=["tweet_id"])
    return frame


def build_pairs(frame: pd.DataFrame) -> pd.DataFrame:
    replies = frame[frame["author_id"].str.lower().eq("applesupport")].copy()
    replies["customer_tweet_id"] = replies["in_response_to_tweet_id"]
    replies = replies[["customer_tweet_id", "text"]].rename(columns={"text": "historical_reply"})

    linked_customer_ids = set(replies["customer_tweet_id"].dropna())
    inbound = frame[
        frame["inbound"].astype(bool) & frame["tweet_id"].isin(linked_customer_ids)
    ].copy()
    inbound = inbound.rename(columns={"text": "customer_text"})
    result = inbound.merge(replies, left_on="tweet_id", right_on="customer_tweet_id", how="left")
    result["baseline_intent"] = result["customer_text"].map(classify_baseline)
    escalation_results = result["customer_text"].map(escalation_baseline)
    result["baseline_escalate"] = escalation_results.map(lambda item: item[0])
    result["baseline_escalation_reason"] = escalation_results.map(lambda item: item[1])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--golden", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=2000)
    parser.add_argument("--golden-size", type=int, default=200)
    args = parser.parse_args()

    frame = load_apple_support(args.input)
    pairs = build_pairs(frame).head(args.sample_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(args.output, index=False)

    golden = pairs.sample(min(args.golden_size, len(pairs)), random_state=42).copy()
    golden["intent"] = ""
    golden["escalate"] = ""
    golden["label_notes"] = ""
    golden.to_csv(args.golden, index=False)

    paired = int(pairs["historical_reply"].notna().sum())
    print(f"AppleSupport inbound examples: {len(pairs)}")
    print(f"Examples with historical replies: {paired}")
    print(f"Golden labelling sheet: {len(golden)} rows -> {args.golden}")


if __name__ == "__main__":
    main()