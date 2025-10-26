"""
View ALL chunks from the XTANDI PDF
"""

import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore
from src.embedding_manager import EmbeddingManager

# Initialize
vector_store = VectorStore()
vector_store.create_index()
embedding_mgr = EmbeddingManager()

# Search specifically for PDF chunks with "S1" "S2" etc
queries = [
    "S1 Are you affiliated",
    "S2 screener question",
    "S3 screener question",
    "S4 screener question",
    "S5 screener question"
]

for query in queries:
    print("="*60)
    print(f"QUERY: {query}")
    print("="*60)

    query_emb = embedding_mgr.embed_text(query)
    results = vector_store.search(
        query_embedding=query_emb,
        top_k=3,
        include_metadata=True
    )

    for i, result in enumerate(results, 1):
        source = result['metadata'].get('source', '').split('/')[-1]
        if 'XTANDI' in source or 'pdf' in result['metadata'].get('doc_type', ''):
            print(f"\nRANK {i} - Score: {result['score']:.4f}")
            print(f"Source: {source}")
            print(f"Content (first 400 chars):")
            print(result['text'][:400])
            print("...")
    print("\n")

# Also do a direct content search
print("\n" + "="*60)
print("SEARCHING FOR: 'primary medical specialty'")
print("="*60)
query_emb = embedding_mgr.embed_text("primary medical specialty")
results = vector_store.search(
    query_embedding=query_emb,
    top_k=5,
    include_metadata=True
)

for i, result in enumerate(results, 1):
    source = result['metadata'].get('source', '').split('/')[-1]
    print(f"\nRANK {i} - Score: {result['score']:.4f} - {source}")
    if 'Q1Q3' in result['text'] or 'specialty' in result['text'].lower():
        print("Content snippet:")
        # Find and print the part with Q1Q3
        text = result['text']
        idx = text.lower().find('q1q3')
        if idx >= 0:
            print(text[max(0, idx-50):min(len(text), idx+500)])
