from rag.vector_store import collection
from rag.embeddings import generate_embedding

query = "high protein vegetarian foods"

query_embedding = generate_embedding(query)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

print(results)