"""
Quick script to check Pinecone index status
"""
from src.vector_store import VectorStore

try:
    print("Initializing VectorStore...")
    vector_store = VectorStore()

    print("\nConnecting to index...")
    vector_store.create_index()

    print("\nGetting index stats...")
    stats = vector_store.get_stats()

    print("\n" + "="*50)
    print("PINECONE INDEX STATUS")
    print("="*50)
    print(f"Index Name: {vector_store.index_name}")
    print(f"Total Vectors: {stats['total_vectors']}")
    print(f"Dimension: {stats['dimension']}")
    print(f"Index Fullness: {stats.get('index_fullness', 'N/A')}")
    print("="*50)

    if stats['total_vectors'] == 0:
        print("\n⚠️  WARNING: Index is empty! You need to run the ingestion script first.")
        print("   Run: python main.py")
    else:
        print("\n✓ Index is ready to use!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Index doesn't exist - run ingestion script (main.py)")
    print("2. API key is incorrect")
    print("3. Network connection issue")
