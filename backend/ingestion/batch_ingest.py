"""Ingest the curated article registry into the vector store.

Built to stay usable as the registry grows:

  * scraping runs concurrently (network bound), while embedding and the
    Chroma writes stay on the main thread - the embedding model and the
    collection are not thread safe
  * already-ingested articles are skipped, so an interrupted run resumes
    instead of starting over
  * failures are collected and written to a report rather than aborting the
    whole run

Usage (from the backend directory):

    python -m ingestion.batch_ingest
    python -m ingestion.batch_ingest --category "Heart Health"
    python -m ingestion.batch_ingest --force --workers 12
    python -m ingestion.batch_ingest --reset      # clear old chunks first
"""

import os
import json
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed

from ingestion.links import load_links, category_counts, LINKS_PATH
from rag.vector_store import collection
from ingestion.process_article import (
    MIN_CONTENT_CHARS,
    fetch_article,
    is_ingested,
    remove_article,
    store_article,
)


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REPORT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "ingest_report.json"
)

DEFAULT_WORKERS = 8


def parse_args():

    parser = argparse.ArgumentParser(
        description="Ingest curated health articles into the vector store."
    )

    parser.add_argument(
        "--category",
        help="Only ingest one category (see ingestion/categories.py)"
    )

    parser.add_argument(
        "--source",
        help="Only ingest articles from one source, e.g. \"Healthline\""
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Only ingest the first N articles (useful for a smoke test)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Concurrent scrapers (default {DEFAULT_WORKERS})"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest articles that are already stored"
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Delete every chunk in the collection before ingesting. Needed "
            "once to clear chunks written by older ingest scripts, which used "
            "a different id scheme and would otherwise linger as duplicates."
        )
    )

    return parser.parse_args()


def reset_collection():
    """Remove all stored chunks. Destructive, so it is opt-in via --reset."""

    stored = collection.get(include=[])

    if not stored["ids"]:

        print("Collection already empty.")

        return

    collection.delete(ids=stored["ids"])

    print(f"Cleared {len(stored['ids'])} existing chunks.")


def scrape_all(articles, workers):
    """Fetch every article concurrently. Yields (article, result, error).

    Each worker thread builds its own session inside the scraper, so nothing
    HTTP-related is shared across threads.
    """

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = {
            executor.submit(fetch_article, article["url"]): article
            for article in articles
        }

        for future in as_completed(futures):

            article = futures[future]

            try:

                yield article, future.result(), None

            except Exception as error:

                yield article, None, str(error)


def main():

    args = parse_args()

    articles = load_links(
        category=args.category,
        source=args.source,
        limit=args.limit
    )

    print(f"\nRegistry: {len(articles)} articles from {LINKS_PATH}")

    if args.reset:

        reset_collection()

    if not args.force and not args.reset:

        pending = [a for a in articles if not is_ingested(a["id"])]

        skipped = len(articles) - len(pending)

        if skipped:

            print(f"Already ingested (skipping): {skipped}")

    else:

        pending = articles

    if not pending:

        print("\nNothing to do.")

        return

    print(f"Ingesting: {len(pending)} articles with {args.workers} workers\n")

    ingested = []

    low_content = []

    failed = []

    done = 0

    for article, result, error in scrape_all(pending, args.workers):

        done += 1

        label = f"[{done}/{len(pending)}]"

        if error:

            failed.append({**article, "error": error})

            print(f"{label} FAILED   {article['url']}\n          {error}")

            continue

        if result is None:

            low_content.append(article)

            print(f"{label} SKIPPED  under {MIN_CONTENT_CHARS} chars: {article['url']}")

            continue

        # Embedding and the Chroma write happen here, on the main thread.
        remove_article(article["id"])

        chunk_count = store_article(
            article_id=article["id"],
            title=result["title"],
            content=result["content"],
            source=article["source"],
            category=article["category"],
            url=article["url"]
        )

        ingested.append({
            **article,
            "characters": len(result["content"]),
            "chunks": chunk_count
        })

        print(
            f"{label} OK       {len(result['content']):>6} chars, "
            f"{chunk_count:>3} chunks  {article['category']} - {result['title'][:52]}"
        )

    summarise(articles, ingested, low_content, failed)


def summarise(articles, ingested, low_content, failed):

    total_chunks = sum(a["chunks"] for a in ingested)

    print("\n" + "-" * 62)

    print(f"Ingested:     {len(ingested)}")

    print(f"Low content:  {len(low_content)}")

    print(f"Failed:       {len(failed)}")

    print(f"Total chunks: {total_chunks}")

    if ingested:

        characters = sorted(a["characters"] for a in ingested)

        print(f"Chars/article min {characters[0]} median {characters[len(characters) // 2]} max {characters[-1]}")

        print("\nPer category:\n")

        for name, count in category_counts(ingested).items():

            print(f"  {name:<24} {count}")

    if failed:

        print("\nFailures:\n")

        for item in failed:

            print(f"  {item['url']}\n    {item['error']}")

    report = {
        "registry_total": len(articles),
        "ingested": len(ingested),
        "low_content": len(low_content),
        "failed": len(failed),
        "total_chunks": total_chunks,
        "min_content_chars": MIN_CONTENT_CHARS,
        "low_content_urls": [a["url"] for a in low_content],
        "failures": [{"url": a["url"], "error": a["error"]} for a in failed],
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as file:

        json.dump(report, file, indent=2)

    print(f"\nReport written to {REPORT_PATH}")


if __name__ == "__main__":

    main()
