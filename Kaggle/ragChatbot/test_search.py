"""
Test search for screener questions to verify data retrieval
"""

import sys
sys.path.insert(0, 'src')

from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from config import config

# Initialize
embedding_mgr = EmbeddingManager()
vector_store = VectorStore()
vector_store.create_index()

# Test query about screener questions
query = "screener question"
print("\n" + "="*60)
print(f"SEARCHING FOR: '{query}'")
print("="*60 + "\n")

# Create embedding for the query
query_embedding = embedding_mgr.embed_text(query)

# Search Pinecone with different top_k values to see more results
print("Searching with top_k=10 to see more chunks...\n")
results = vector_store.search(
    query_embedding=query_embedding,
    top_k=10,
    include_metadata=True
)

print(f"Found {len(results)} matching chunks\n")

# Display results
for i, match in enumerate(results, 1):
    print(f"{'='*60}")
    print(f"RANK {i} - Score: {match['score']:.4f}")
    print(f"{'='*60}")

    metadata = match['metadata']
    print(f"Source: {metadata.get('source', 'Unknown')}")
    print(f"Doc Type: {metadata.get('doc_type', 'N/A')}")
    print(f"Chunk ID: {match['id']}")
    print(f"Chunk: {int(metadata.get('chunk_index', 0))+1} of {int(metadata.get('total_chunks', 0))}")

    print(f"\nContent (first 500 chars):")
    print(match['text'][:500])
    print("\n")

# Now let's search for specific screener questions
print("\n" + "="*60)
print("SEARCHING FOR: 'S1 S2 S3 S4 S5 screener'")
print("="*60 + "\n")

query2 = "S1 S2 S3 S4 S5 screener questions"
query_embedding2 = embedding_mgr.embed_text(query2)

results2 = vector_store.search(
    query_embedding=query_embedding2,
    top_k=10,
    include_metadata=True
)

print(f"Found {len(results2)} matching chunks\n")

for i, match in enumerate(results2, 1):
    print(f"RANK {i} - Score: {match['score']:.4f}")
    print(f"Source: {match['metadata'].get('source', 'Unknown').split('/')[-1]}")
    print(f"Content preview: {match['text'][:200]}...")
    print()
