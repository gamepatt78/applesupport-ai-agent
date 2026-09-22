"""Small X API v2 client for recent AppleSupport mentions."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests


X_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


class XAPIError(RuntimeError):
    """Safe, non-secret description of an upstream X API failure."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(message)


def fetch_kaggle_applesupport_sample(path: Path, max_results: int = 10) -> list[dict]:
    """Return historical AppleSupport examples when live X data is unavailable."""
    frame = pd.read_csv(
        path,
        usecols=["tweet_id", "customer_text", "created_at", "historical_reply"],
        nrows=10000,
    ).dropna(subset=["customer_text"])
    sample = frame.head(max(1, min(int(max_results), 100)))
    return [
        {
            "id": str(row.tweet_id),
            "text": str(row.customer_text),
            "created_at": str(row.created_at),
            "historical_reply": str(row.historical_reply),
            "source": "historical_kaggle",
        }
        for row in sample.itertuples()
    ]


def fetch_recent_applesupport_tweets(max_results: int = 10) -> list[dict]:
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        raise RuntimeError("X_BEARER_TOKEN is not configured")

    bounded_results = max(10, min(int(max_results), 100))
    response = requests.get(
        X_SEARCH_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "query": "(@AppleSupport OR to:AppleSupport) -is:retweet lang:en",
            "max_results": bounded_results,
            "tweet.fields": "created_at,author_id,conversation_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name",
        },
        timeout=20,
    )
    if not response.ok:
        try:
            error_payload = response.json()
            message = error_payload.get("detail") or error_payload.get("title") or "X API rejected the request"
        except ValueError:
            message = "X API rejected the request"
        raise XAPIError(response.status_code, str(message)[:240])
    payload = response.json()
    users = {user["id"]: user for user in payload.get("includes", {}).get("users", [])}

    tweets = []
    for tweet in payload.get("data", []):
        author = users.get(tweet.get("author_id"), {})
        tweets.append({
            "id": tweet["id"],
            "text": tweet["text"],
            "created_at": tweet.get("created_at"),
            "conversation_id": tweet.get("conversation_id"),
            "author": author.get("username", tweet.get("author_id")),
            "author_name": author.get("name"),
            "public_metrics": tweet.get("public_metrics", {}),
        })
    return tweets
