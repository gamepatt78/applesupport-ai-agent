"""Retrieval and grounded response components for the AppleSupport agent."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.pipeline import classify_baseline, escalation_baseline


class AppleSupportAgent:
    def __init__(self, examples: pd.DataFrame) -> None:
        required = {"customer_text", "historical_reply"}
        missing = required.difference(examples.columns)
        if missing:
            raise ValueError(f"Missing retrieval columns: {sorted(missing)}")
        self.examples = examples.dropna(subset=["customer_text", "historical_reply"]).copy()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=30000)
        self.matrix = self.vectorizer.fit_transform(self.examples["customer_text"].astype(str))

    @classmethod
    def from_csv(cls, path: Path) -> "AppleSupportAgent":
        return cls(pd.read_csv(path, usecols=["customer_text", "historical_reply"], nrows=10000))

    def retrieve(self, message: str, top_k: int = 3) -> list[dict]:
        query = self.vectorizer.transform([message])
        scores = cosine_similarity(query, self.matrix).ravel()
        indices = scores.argsort()[::-1][:top_k]
        return [
            {
                "customer_text": str(self.examples.iloc[index]["customer_text"]),
                "historical_reply": str(self.examples.iloc[index]["historical_reply"]),
                "similarity": round(float(scores[index]), 4),
            }
            for index in indices
        ]

    def analyze(self, message: str) -> dict:
        intent = classify_baseline(message)
        escalate, reason = escalation_baseline(message)
        evidence = self.retrieve(message)
        reply = self._grounded_reply(intent, escalate, evidence)
        return {
            "intent": intent,
            "escalate": escalate,
            "reason": reason,
            "reply": reply,
            "evidence": evidence,
        }

    @staticmethod
    def _grounded_reply(intent: str, escalate: bool, evidence: list[dict]) -> str:
        if escalate:
            return "A specialist should review this securely. Please do not share passwords, verification codes, or full payment details here."
        if intent == "order_delivery":
            return "Please check your order status at https://www.apple.com/shop/order/list for the latest tracking details. Reply with your order number if the delivery status has not updated, and we can help with the next step."
        best_reply = evidence[0]["historical_reply"] if evidence else ""
        if best_reply:
            return f"Based on similar AppleSupport cases: {best_reply}"
        return f"We identified this as {intent.replace('_', ' ')}. Please contact Apple Support for the next step."
