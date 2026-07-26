from rank_bm25 import BM25Okapi


def build_bm25(documents):

    tokenized_docs = [
        doc.lower().split()
        for doc in documents
    ]

    return BM25Okapi(tokenized_docs)


def search_bm25(query, documents, bm25, top_k=5):

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]