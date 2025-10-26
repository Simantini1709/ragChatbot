"""
Quick script to inspect chunks in Pinecone
"""

import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore
from config import config

# Initialize vector store
vector_store = VectorStore()
vector_store.create_index()

# Get stats
stats = vector_store.get_stats()
print("\n" + "="*60)
print("PINECONE INDEX STATISTICS")
print("="*60)
print(f"Total Vectors: {stats['total_vectors']}")
print(f"Dimension: {stats['dimension']}")
print(f"Index Fullness: {stats['index_fullness']:.2%}")
print("="*60 + "\n")

# Fetch a few random vectors to see what they look like
print("Fetching sample chunks to inspect...\n")

# Query with a sample embedding (all zeros just to get some results)
import random
sample_query = [0.0] * 1536  # Dummy query

results = vector_store.search(
    query_embedding=sample_query,
    top_k=3,
    include_metadata=True
)

print("="*60)
print("SAMPLE CHUNKS FROM YOUR DATABASE")
print("="*60 + "\n")

for i, match in enumerate(results, 1):
    print(f"{'='*60}")
    print(f"CHUNK {i}")
    print(f"{'='*60}")
    print(f"ID: {match['id']}")
    print(f"Score: {match['score']:.4f}")
    print(f"\nMetadata:")
    metadata = match['metadata']
    print(f"  - Source: {metadata.get('source', 'N/A')}")
    print(f"  - Doc Type: {metadata.get('doc_type', 'N/A')}")
    print(f"  - Category: {metadata.get('category', 'N/A')}")
    print(f"  - Chunk Index: {metadata.get('chunk_index', 'N/A')}")
    print(f"  - Total Chunks: {metadata.get('total_chunks', 'N/A')}")

    print(f"\nContent Preview (first 300 chars):")
    print(f"  {match['text'][:300]}...")
    print()

print("="*60)
print("These are the chunks Claude uses to answer questions!")
print("="*60 + "\n")
