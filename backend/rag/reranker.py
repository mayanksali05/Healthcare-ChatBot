from sentence_transformers import CrossEncoder

# Load reranker model
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_documents(query, documents):

    pairs = [
        [query, doc]
        for doc in documents
    ]

    scores = reranker.predict(pairs)

    ranked_results = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_results