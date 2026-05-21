from rag.embeddings import generate_embedding
from rag.vector_store import collection
from rag.reranker import rerank_documents


def retrieve_context(query, n_results=5, threshold=0.5):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    # Distance filtering
    filtered_documents = []

    filtered_sources = []

    for doc, metadata, distance in zip(documents, metadatas, distances):

        if distance < threshold:

            filtered_documents.append(doc)

            filtered_sources.append(metadata)

    # No relevant retrievals
    if not filtered_documents:

        return {
            "context": "",
            "sources": []
        }

    # Rerank retrieved chunks
    ranked_results = rerank_documents(
        query,
        filtered_documents
    )

    # Take top 2 reranked chunks
    top_documents = [
        doc
        for doc, score in ranked_results[:2]
    ]

    context = "\n".join(top_documents)

    # Deduplicate sources
    unique_sources = []

    seen_titles = set()

    for source in filtered_sources:

        title = source["title"]

        if title not in seen_titles:

            unique_sources.append(source)

            seen_titles.add(title)

    return {
        "context": context,
        "sources": unique_sources
    }