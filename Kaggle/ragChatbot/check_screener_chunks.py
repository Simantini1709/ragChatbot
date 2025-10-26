"""
Check all chunks from the PDF that contain screener questions
"""

import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore

# Initialize
vector_store = VectorStore()
vector_store.create_index()

# Search for all chunks from the XTANDI PDF
print("="*60)
print("SEARCHING FOR ALL CHUNKS FROM ZS_XTANDI_ATU.pdf")
print("="*60 + "\n")

# Use a dummy query to get samples, then filter
import random
sample_query = [0.0] * 1536

# Get more results to find PDF chunks
results = vector_store.search(
    query_embedding=sample_query,
    top_k=100,
    include_metadata=True
)

# Filter for only XTANDI PDF chunks
pdf_chunks = [r for r in results if 'XTANDI' in r['metadata'].get('source', '')]

print(f"Found {len(pdf_chunks)} chunks from XTANDI PDF\n")

# Look specifically for screener-related chunks
screener_chunks = []
for chunk in pdf_chunks:
    text = chunk['text'].lower()
    if 'screener' in text or 's1.' in text or 's2.' in text or 's3.' in text or 's4.' in text or 's5.' in text:
        screener_chunks.append(chunk)

print(f"Found {len(screener_chunks)} chunks mentioning screener questions\n")

# Display these chunks
for i, chunk in enumerate(screener_chunks[:5], 1):
    print("="*60)
    print(f"CHUNK {i}")
    print("="*60)
    print(f"ID: {chunk['id']}")
    print(f"Chunk Index: {int(chunk['metadata'].get('chunk_index', 0))+1} of {int(chunk['metadata'].get('total_chunks', 0))}")
    print(f"\nFull Content:")
    print(chunk['text'])
    print("\n")
