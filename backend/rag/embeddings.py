from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def generate_embedding(text):
    embedding = embedding_model.encode(text)

    return embedding.tolist()