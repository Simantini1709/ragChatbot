"""
Example: Search for relevant chunks using a real query
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

# Test query
query = "How do I create word clouds in Protobi?"
print("\n" + "="*60)
print(f"SEARCHING FOR: '{query}'")
print("="*60 + "\n")

# Create embedding for the query
print("1. Converting query to embedding...")
query_embedding = embedding_mgr.embed_text(query)
print(f"   ✓ Created 1536-dimensional vector\n")

# Search Pinecone
print("2. Searching Pinecone for top 5 relevant chunks...")
results = vector_store.search(
    query_embedding=query_embedding,
    top_k=5,
    include_metadata=True
)
print(f"   ✓ Found {len(results)} matching chunks\n")

# Display results
print("="*60)
print("TOP 5 MOST RELEVANT CHUNKS")
print("="*60 + "\n")

for i, match in enumerate(results, 1):
    print(f"{'─'*60}")
    print(f"RANK {i} - Relevance Score: {match['score']:.4f}")
    print(f"{'─'*60}")

    metadata = match['metadata']
    source = metadata.get('source', 'Unknown')
    filename = source.split('/')[-1] if '/' in source else source

    print(f"📄 Source: {filename}")
    print(f"📁 Category: {metadata.get('category', 'N/A')}")
    print(f"📑 Type: {metadata.get('doc_type', 'N/A')}")
    print(f"🔢 Chunk: {int(metadata.get('chunk_index', 0))+1} of {int(metadata.get('total_chunks', 0))}")

    print(f"\n📝 Content:")
    print(f"{match['text'][:400]}...")
    print()

print("="*60)
print("These chunks would be sent to Claude to generate an answer!")
print("="*60 + "\n")
