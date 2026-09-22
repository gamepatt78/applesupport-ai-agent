"""Small X API v2 client for recent AppleSupport mentions."""

from __future__ import annotations

import os

import requests


X_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


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
    response.raise_for_status()
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
