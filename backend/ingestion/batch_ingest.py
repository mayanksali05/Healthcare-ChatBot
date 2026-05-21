import os
import json

from ingestion.process_article import process_article


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LINKS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "article_links.json"
)


with open(LINKS_PATH, "r", encoding="utf-8") as file:

    articles = json.load(file)


for article in articles:

    try:

        process_article(
            url=article["url"],
            source=article["source"],
            category=article["category"]
        )

    except Exception as e:

        print(f"\nFailed: {article['url']}")

        print(e)