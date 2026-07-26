"""Loader for the curated article registry (data/raw/article_links.json).

Validates the registry before any network work happens, so a typo in a
category or a duplicated URL fails fast instead of halfway through a
150-article ingest run.
"""

import os
import json

from ingestion.categories import validate


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LINKS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "article_links.json"
)


REQUIRED_FIELDS = ["url", "source", "category"]


def load_links(path=LINKS_PATH, category=None, source=None, limit=None):

    with open(path, "r", encoding="utf-8") as file:

        entries = json.load(file)

    articles = []

    seen_urls = set()

    seen_ids = set()

    for position, entry in enumerate(entries):

        for field in REQUIRED_FIELDS:

            if not entry.get(field):

                raise ValueError(
                    f"Entry {position} in {os.path.basename(path)} "
                    f"is missing required field: {field}"
                )

        validate(entry["category"])

        url = entry["url"].strip()

        # Only fetch over TLS - the registry must never downgrade to plain HTTP.
        if not url.startswith("https://"):

            raise ValueError(f"Entry {position} must use https: {url}")

        if url in seen_urls:

            raise ValueError(f"Duplicate url in registry: {url}")

        seen_urls.add(url)

        # id is optional in the file; fall back to the url so downstream
        # chunk ids stay stable and unique either way.
        article_id = entry.get("id") or url

        if article_id in seen_ids:

            raise ValueError(f"Duplicate id in registry: {article_id}")

        seen_ids.add(article_id)

        articles.append({
            "id": article_id,
            "url": url,
            "source": entry["source"],
            "category": entry["category"],
            "title": entry.get("title", "")
        })

    if category:

        articles = [a for a in articles if a["category"] == category]

    if source:

        articles = [a for a in articles if a["source"] == source]

    if limit:

        articles = articles[:limit]

    return articles


def category_counts(articles):

    counts = {}

    for article in articles:

        counts[article["category"]] = counts.get(article["category"], 0) + 1

    return counts


if __name__ == "__main__":

    articles = load_links()

    print(f"\nRegistry OK: {len(articles)} articles")

    print(f"Sources: {len(set(a['source'] for a in articles))}")

    print("\nPer category:\n")

    for name, count in category_counts(articles).items():

        print(f"  {name:<24} {count}")
