"""Evaluate majority-class and TF-IDF intent baselines on the golden set."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score
from sklearn.pipeline import Pipeline


REQUIRED_LABELS = {"intent", "escalate"}


def load_labeled(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED_LABELS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing label columns: {sorted(missing)}")
    frame["intent"] = frame["intent"].fillna("").astype(str).str.strip()
    frame["escalate"] = frame["escalate"].fillna("").astype(str).str.strip().str.lower()
    if (frame["intent"] == "").any() or (frame["escalate"] == "").any():
        raise ValueError("Golden labels are incomplete. Fill intent and escalate manually before evaluating.")
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=Path("data/golden_eval.csv"))
    args = parser.parse_args()
    frame = load_labeled(args.golden)
    split = max(1, int(len(frame) * 0.8))
    train, test = frame.iloc[:split], frame.iloc[split:]
    majority_intent = train["intent"].mode().iloc[0]
    majority_predictions = [majority_intent] * len(test)
    print("MAJORITY INTENT BASELINE")
    print(classification_report(test["intent"], majority_predictions, zero_division=0))

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(train["customer_text"].astype(str), train["intent"])
    tfidf_predictions = model.predict(test["customer_text"].astype(str))
    print("TF-IDF + LOGISTIC REGRESSION")
    print(classification_report(test["intent"], tfidf_predictions, zero_division=0))
    print("TF-IDF CONFUSION MATRIX")
    print(confusion_matrix(test["intent"], tfidf_predictions, labels=sorted(frame["intent"].unique())))

    actual_escalation = test["escalate"].isin(["true", "1", "yes"])
    baseline_escalation = test["baseline_escalate"].astype(bool) if "baseline_escalate" in test else pd.Series(False, index=test.index)
    print("ESCALATION BASELINE")
    print(f"precision={precision_score(actual_escalation, baseline_escalation, zero_division=0):.3f}")
    print(f"recall={recall_score(actual_escalation, baseline_escalation, zero_division=0):.3f}")


if __name__ == "__main__":
    main()
