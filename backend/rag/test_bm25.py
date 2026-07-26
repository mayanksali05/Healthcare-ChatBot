from rag.keyword_search import (
    build_bm25,
    search_bm25
)

documents = [
    "Bananas contain potassium",
    "Vitamin B12 deficiency can cause fatigue",
    "Protein helps muscle growth"
]

bm25 = build_bm25(documents)

results = search_bm25(
    "vitamin b12",
    documents,
    bm25
)

for doc, score in results:
    print(doc, score)