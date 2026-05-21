import os
import json

from ingestion.scraper import scrape_article
from ingestion.chunker import chunk_text

from rag.embeddings import generate_embedding
from rag.vector_store import collection


def process_article(url, source, category):

    # Scrape article
    article = scrape_article(url)

    title = article["title"]

    content = article["content"]

    # Validate scraped article
    invalid_titles = [
        "Error Page",
        "Page Not Found",
        "404"
    ]

    if title.strip() in invalid_titles:

        print(f"\nSkipping invalid article: {url}")

        return

    if len(content.strip()) < 300:

        print(f"\nSkipping low-content article: {url}")

        return

    # Split into chunks
    chunks = chunk_text(content)

    for index, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        collection.add(

            ids=[f"{url}_{index}"],

            embeddings=[embedding],

            documents=[chunk],

            metadatas=[{
                "title": title,
                "source": source,
                "category": category,
                "url": url
            }]
        )

    print(f"\nProcessed article: {title}")


if __name__ == "__main__":

    process_article(
        url="https://www.healthline.com/nutrition/11-proven-benefits-of-bananas",
        source="Healthline",
        category="Nutrition"
    )