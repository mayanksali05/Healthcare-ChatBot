from rag.reranker import rerank_documents


query = "protein foods"

documents = [
    "Bananas contain potassium and fiber.",
    "Lentils and tofu are high protein vegetarian foods.",
    "Drinking water supports hydration."
]


results = rerank_documents(query, documents)


for doc, score in results:

    print("\nDOCUMENT:\n")

    print(doc)

    print("\nSCORE:\n")

    print(score)