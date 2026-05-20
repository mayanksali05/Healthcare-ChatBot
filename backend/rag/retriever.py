from rag.embeddings import generate_embedding
from rag.vector_store import collection


def retrieve_context(query, n_results=2):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n".join(documents)

    return {
        "context": context,
        "sources": metadatas
    }