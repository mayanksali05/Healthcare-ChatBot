import os
import json

from rag.embeddings import generate_embedding
from rag.vector_store import collection

from ingestion.chunker import chunk_text


# Absolute path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "health_articles.json"
)


# Load JSON data
with open(DATA_PATH, "r", encoding="utf-8") as file:
    articles = json.load(file)


chunk_id = 0


for article in articles:

    title = article["title"]

    source = article["source"]

    category = article["category"]

    content = article["content"]

    # Split article into chunks
    chunks = chunk_text(content)


    for chunk in chunks:

        embedding = generate_embedding(chunk)

        collection.add(

            ids=[str(chunk_id)],

            embeddings=[embedding],

            documents=[chunk],

            metadatas=[{
                "title": title,
                "source": source,
                "category": category
            }]
        )

        chunk_id += 1


print("Chunked data stored successfully")