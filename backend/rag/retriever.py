from rag.embeddings import generate_embedding
from rag.vector_store import collection
from rag.reranker import rerank_documents
from rag.keyword_search import build_bm25, search_bm25


# --- Tunable retrieval settings ---
SEMANTIC_N = 5             # candidates pulled from vector (semantic) search
KEYWORD_N = 5              # candidates pulled from BM25 (keyword) search
DISTANCE_THRESHOLD = 0.5   # semantic safety gate: keep chunks with cosine distance below this
TOP_K_FINAL = 2            # chunks kept after reranking the merged candidate pool


# --- BM25 index over the full chunk corpus ---
# Built lazily on the first query from the current collection contents and
# cached in memory. NOTE: after re-running ingestion, call refresh_bm25_index()
# or restart the server so the keyword index picks up the new chunks.
_bm25_index = None
_corpus_documents = []
_corpus_metadata = {}


def _load_bm25_index():
    global _bm25_index, _corpus_documents, _corpus_metadata

    if _bm25_index is not None:
        return

    data = collection.get(include=["documents", "metadatas"])

    _corpus_documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []

    # Map each chunk back to its metadata for source attribution.
    _corpus_metadata = {
        doc: metadata
        for doc, metadata in zip(_corpus_documents, metadatas)
    }

    # BM25Okapi divides by the average document length, so it needs a
    # non-empty corpus. Leave the index as None on an empty collection.
    if _corpus_documents:
        _bm25_index = build_bm25(_corpus_documents)


def refresh_bm25_index():
    """Force the BM25 index to rebuild on the next query (call after ingestion)."""
    global _bm25_index
    _bm25_index = None


def retrieve_context(query, n_results=SEMANTIC_N, threshold=DISTANCE_THRESHOLD):

    # --- 1. Semantic search (vector similarity) ---
    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Maps every candidate chunk (semantic + keyword) back to its metadata.
    doc_to_metadata = {}

    # Semantic safety gate: only keep chunks that are close enough.
    semantic_documents = []

    for doc, metadata, distance in zip(documents, metadatas, distances):

        if distance < threshold:

            semantic_documents.append(doc)

            doc_to_metadata[doc] = metadata

    # If semantic search found no trusted grounding, do NOT answer. This
    # preserves the "not enough trusted information" behaviour: BM25 alone
    # must never let the bot respond to an otherwise ungrounded query.
    if not semantic_documents:

        return {
            "context": "",
            "sources": []
        }

    # --- 2. Keyword search (BM25) for additional recall ---
    _load_bm25_index()

    keyword_documents = []

    if _bm25_index is not None:

        bm25_results = search_bm25(
            query,
            _corpus_documents,
            _bm25_index,
            top_k=KEYWORD_N
        )

        # Only admit chunks with real keyword overlap (score > 0).
        for doc, score in bm25_results:

            if score > 0:

                keyword_documents.append(doc)

                doc_to_metadata.setdefault(doc, _corpus_metadata.get(doc))

    # --- 3. Merge candidate pools (dedupe, preserve order) ---
    candidate_documents = list(
        dict.fromkeys(semantic_documents + keyword_documents)
    )

    # --- 4. Rerank the merged pool; the cross-encoder is the final judge ---
    ranked_results = rerank_documents(query, candidate_documents)

    top_documents = [
        doc
        for doc, score in ranked_results[:TOP_K_FINAL]
    ]

    context = "\n".join(top_documents)

    # --- 5. Sources for the chunks actually used, deduped by title ---
    unique_sources = []

    seen_titles = set()

    for doc in top_documents:

        metadata = doc_to_metadata.get(doc)

        if not metadata:
            continue

        title = metadata.get("title")

        if title not in seen_titles:

            unique_sources.append(metadata)

            seen_titles.add(title)

    return {
        "context": context,
        "sources": unique_sources
    }
