from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def generate_embedding(text):
    embedding = embedding_model.encode(text)

    return embedding.tolist()


def generate_embeddings(texts, batch_size=32):
    """Encode many texts in one vectorised pass.

    Ingesting 150 articles means thousands of chunks; encoding them one at a
    time wastes most of the model's throughput.
    """

    if not texts:
        return []

    embeddings = embedding_model.encode(
        texts,
        batch_size=batch_size
    )

    return [embedding.tolist() for embedding in embeddings]