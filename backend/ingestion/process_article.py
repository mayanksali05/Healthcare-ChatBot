from ingestion.scraper import scrape_article
from ingestion.chunker import chunk_text

from rag.embeddings import generate_embeddings
from rag.vector_store import collection


# The registry guarantees every curated link yields more than 2500 characters
# of article text. Enforcing the same floor here means a page that has been
# rewritten, paywalled or reduced to a stub is skipped instead of polluting
# the knowledge base with a fragment.
MIN_CONTENT_CHARS = 2500

INVALID_TITLES = [
    "Error Page",
    "Page Not Found",
    "404",
    "Access Denied",
]


def chunk_id(article_id, index):

    return f"{article_id}::{index}"


def is_ingested(article_id):
    """True when this article already has chunks stored."""

    existing = collection.get(ids=[chunk_id(article_id, 0)])

    return bool(existing["ids"])


def remove_article(article_id):
    """Drop an article's chunks so a re-ingest cannot leave stale ones behind.

    Needed when a source page gets shorter: upserting alone would overwrite
    chunks 0..n but leave the old n+1.. orphaned in the collection.
    """

    collection.delete(where={"article_id": article_id})


def fetch_article(url, session=None):
    """Scrape and validate one article. Returns None when it is unusable."""

    article = scrape_article(url, session=session)

    title = article["title"].strip()

    content = article["content"].strip()

    if title in INVALID_TITLES:

        return None

    if len(content) < MIN_CONTENT_CHARS:

        return None

    return {
        "title": title,
        "content": content
    }


def store_article(article_id, title, content, source, category, url):
    """Chunk, embed and upsert one article. Returns the chunk count."""

    chunks = chunk_text(content)

    embeddings = generate_embeddings(chunks)

    ids = [chunk_id(article_id, index) for index in range(len(chunks))]

    metadatas = [
        {
            "article_id": article_id,
            "title": title,
            "source": source,
            "category": category,
            "url": url
        }
        for _ in chunks
    ]

    # upsert (not add) keeps re-runs idempotent instead of raising on
    # duplicate ids or silently double-storing the same chunk.
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

    return len(chunks)


def process_article(url, source, category, article_id=None, session=None):

    article_id = article_id or url

    article = fetch_article(url, session=session)

    if article is None:

        print(f"\nSkipping low-content or invalid article: {url}")

        return None

    remove_article(article_id)

    chunk_count = store_article(
        article_id=article_id,
        title=article["title"],
        content=article["content"],
        source=source,
        category=category,
        url=url
    )

    print(f"\nProcessed article: {article['title']} ({chunk_count} chunks)")

    return {
        "id": article_id,
        "title": article["title"],
        "chunks": chunk_count,
        "characters": len(article["content"])
    }


if __name__ == "__main__":

    process_article(
        url="https://www.healthline.com/nutrition/11-proven-benefits-of-bananas",
        source="Healthline",
        category="Nutrition"
    )
