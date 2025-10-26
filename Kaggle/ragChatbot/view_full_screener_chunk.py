"""
View the FULL content of the screener chunk
"""

import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore
from src.embedding_manager import EmbeddingManager

# Initialize
vector_store = VectorStore()
vector_store.create_index()
embedding_mgr = EmbeddingManager()

# Search for the screener chunk
query_emb = embedding_mgr.embed_text("S1 screener affiliated FDA")
results = vector_store.search(
    query_embedding=query_emb,
    top_k=3,
    include_metadata=True
)

print("="*60)
print("FULL SCREENER CHUNK CONTENT")
print("="*60)

for result in results:
    source = result['metadata'].get('source', '')
    if 'XTANDI' in source:
        print(f"\nChunk ID: {result['id']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {source.split('/')[-1]}")
        print(f"Chunk {int(result['metadata'].get('chunk_index', 0))+1} of {int(result['metadata'].get('total_chunks', 0))}")
        print(f"\nFull content length: {len(result['text'])} characters")
        print("\n" + "="*60)
        print("FULL TEXT:")
        print("="*60)
        print(result['text'])
        print("\n" + "="*60)

        # Check what questions are in this chunk
        text = result['text']
        questions_found = []
        for q in ['S1.', 'S2.', 'S3.', 'S4.', 'S5.', 'Q1Q3.', 'Q1Q4.', 'Q1Q5.', 'Q1Q6.']:
            if q in text:
                questions_found.append(q)

        print(f"\nQuestions found in this chunk: {', '.join(questions_found)}")
        print("="*60)
        break
