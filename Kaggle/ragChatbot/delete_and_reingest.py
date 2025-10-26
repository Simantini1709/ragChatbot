"""
Delete all vectors and re-ingest with fixed chunk IDs
"""

import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore
from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from src.embedding_manager import EmbeddingManager
from config import config

print("=" * 60)
print("STEP 1: INITIALIZING VECTOR STORE")
print("=" * 60)

# Initialize vector store
vector_store = VectorStore()
vector_store.create_index()

# Check if there are any vectors to delete
stats = vector_store.get_stats()
if stats['total_vectors'] > 0:
    print(f"\nDeleting {stats['total_vectors']} existing vectors...")
    vector_store.delete_all()
else:
    print(f"\nIndex is already empty (0 vectors). Skipping deletion.")

print("\n" + "=" * 60)
print("STEP 2: LOADING DOCUMENTS")
print("=" * 60)

# Load documents
loader = DocumentLoader(
    blog_path=config.BLOG_PATH,
    help_path=config.HELP_PATH,
    pdf_path=config.PDF_PATH,
    json_path=config.JSON_PATH
)
documents = loader.load_all()

print("\n" + "=" * 60)
print("STEP 3: CHUNKING DOCUMENTS")
print("=" * 60)

# Chunk documents with NEW globally unique IDs
splitter = TextSplitter()
chunks = splitter.chunk_documents(documents)

print("\n" + "=" * 60)
print("STEP 4: CREATING EMBEDDINGS")
print("=" * 60)

# Create embeddings
embedding_mgr = EmbeddingManager()
texts = [chunk.page_content for chunk in chunks]
embeddings = embedding_mgr.embed_texts(texts)

print("\n" + "=" * 60)
print("STEP 5: UPLOADING TO PINECONE")
print("=" * 60)

# Upload to Pinecone
metadatas = [chunk.metadata for chunk in chunks]
vector_store.upsert_documents(texts, embeddings, metadatas)

print("\n" + "=" * 60)
print("STEP 6: VERIFICATION")
print("=" * 60)

# Verify final count
stats = vector_store.get_stats()
print(f"\n✓ Total vectors in index: {stats['total_vectors']}")
print(f"✓ Expected vectors: {len(chunks)}")

if stats['total_vectors'] == len(chunks):
    print("\n🎉 SUCCESS! All documents uploaded without data loss!")
else:
    print(f"\n⚠️  WARNING: Expected {len(chunks)} but got {stats['total_vectors']}")

print("=" * 60)
