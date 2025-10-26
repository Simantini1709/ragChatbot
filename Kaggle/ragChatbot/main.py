"""
Main entry point for RAG Chatbot
Two modes: 1) Ingest documents, 2) Use chatbot
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.llm_chain import LLMChain
from src.chatbot import RAGChatbot
from config import config


def ingest_documents():
    """
    Ingest documents: Load → Chunk → Embed → Store in Pinecone
    Run this ONCE to set up your vector database
    """
    print("\n" + "="*60)
    print("DOCUMENT INGESTION PIPELINE")
    print("="*60 + "\n")

    # Step 1: Validate configuration
    print("Step 1: Validating configuration...")
    try:
        config.validate()
        config.display()
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease create a .env file with required API keys.")
        print("See .env.example for reference.")
        return

    # Step 2: Load documents
    print("\nStep 2: Loading documents...")
    loader = DocumentLoader(
        blog_path=str(config.BLOG_PATH),
        help_path=str(config.HELP_PATH),
        pdf_path=str(config.PDF_PATH),
        json_path=str(config.JSON_PATH)
    )

    try:
        documents = loader.load_all()
    except Exception as e:
        print(f"\n❌ Error loading documents: {e}")
        return

    if not documents:
        print("\n❌ No documents loaded!")
        return

    # Step 3: Chunk documents
    print("\nStep 3: Chunking documents...")
    splitter = TextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )

    try:
        chunks = splitter.chunk_documents(documents)
    except Exception as e:
        print(f"\n❌ Error chunking documents: {e}")
        return

    if not chunks:
        print("\n❌ No chunks created!")
        return

    # Step 4: Initialize embedding manager
    print("\nStep 4: Initializing embedding manager...")
    try:
        embedding_mgr = EmbeddingManager()
    except Exception as e:
        print(f"\n❌ Error initializing embeddings: {e}")
        return

    # Step 5: Create embeddings
    print("\nStep 5: Creating embeddings (this may take a few minutes)...")
    try:
        texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_mgr.embed_texts(texts)
    except Exception as e:
        print(f"\n❌ Error creating embeddings: {e}")
        return

    # Step 6: Initialize Pinecone
    print("\nStep 6: Initializing Pinecone...")
    try:
        vector_store = VectorStore()
        vector_store.create_index(
            dimension=embedding_mgr.get_embedding_dimension()
        )
    except Exception as e:
        print(f"\n❌ Error initializing Pinecone: {e}")
        return

    # Step 7: Upload to Pinecone
    print("\nStep 7: Uploading embeddings to Pinecone...")
    try:
        metadatas = [chunk.metadata for chunk in chunks]
        vector_store.upsert_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
    except Exception as e:
        print(f"\n❌ Error uploading to Pinecone: {e}")
        return

    # Step 8: Verify
    print("\nStep 8: Verifying upload...")
    stats = vector_store.get_stats()
    print(f"\n✓ Ingestion complete!")
    print(f"  - Total vectors in Pinecone: {stats['total_vectors']}")
    print(f"  - Dimension: {stats['dimension']}")
    print(f"  - Index fullness: {stats['index_fullness']:.2%}")

    print("\n" + "="*60)
    print("SUCCESS! You can now run: python main.py chat")
    print("="*60 + "\n")


def start_chatbot():
    """
    Start the RAG chatbot
    Requires documents to be ingested first
    """
    print("\n" + "="*60)
    print("STARTING RAG CHATBOT")
    print("="*60 + "\n")

    # Step 1: Validate configuration
    print("Validating configuration...")
    try:
        config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        return

    # Step 2: Initialize components
    print("Initializing components...")

    try:
        # Embedding manager
        embedding_mgr = EmbeddingManager()

        # Vector store
        vector_store = VectorStore()
        vector_store.create_index()  # Connects to existing index

        # Retriever
        retriever = Retriever(embedding_mgr, vector_store)

        # LLM Chain
        llm_chain = LLMChain()

        # Chatbot
        chatbot = RAGChatbot(retriever, llm_chain)

    except Exception as e:
        print(f"\n❌ Error initializing chatbot: {e}")
        print("\nMake sure you've run document ingestion first:")
        print("  python main.py ingest")
        return

    # Step 3: Start interactive mode
    print("\n✓ All components initialized!")
    chatbot.interactive_mode()


def test_chatbot():
    """
    Test the chatbot with sample questions
    """
    print("\n" + "="*60)
    print("TESTING RAG CHATBOT")
    print("="*60 + "\n")

    # Initialize
    print("Initializing chatbot...")
    try:
        embedding_mgr = EmbeddingManager()
        vector_store = VectorStore()
        vector_store.create_index()
        retriever = Retriever(embedding_mgr, vector_store)
        llm_chain = LLMChain()
        chatbot = RAGChatbot(retriever, llm_chain)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've run: python main.py ingest")
        return

    # Test questions
    test_questions = [
        "How do I create word clouds in Protobi?",
        "What are the chart types available?",
        "How do I handle outliers in my data?"
    ]

    print("\n✓ Chatbot initialized! Running tests...\n")

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}/{len(test_questions)}: {question}")
        print(f"{'='*60}\n")

        try:
            answer = chatbot.ask(question)
            print(f"\n✓ Test {i} completed\n")
        except Exception as e:
            print(f"\n❌ Error in test {i}: {e}\n")

    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60 + "\n")


def show_stats():
    """
    Show Pinecone index statistics
    """
    print("\n" + "="*60)
    print("PINECONE INDEX STATISTICS")
    print("="*60 + "\n")

    try:
        vector_store = VectorStore()
        vector_store.create_index()
        stats = vector_store.get_stats()

        print(f"Index Name: {config.PINECONE_INDEX_NAME}")
        print(f"Total Vectors: {stats['total_vectors']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Index Fullness: {stats['index_fullness']:.2%}")
        print(f"Free Tier Limit: 100,000 vectors")
        print(f"Remaining Capacity: {100000 - stats['total_vectors']:,} vectors")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure Pinecone is set up and documents are ingested.")

    print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("RAG CHATBOT - USAGE")
        print("="*60)
        print("\nAvailable Commands:")
        print("  python main.py ingest    - Ingest documents (run ONCE to set up)")
        print("  python main.py chat      - Start interactive chatbot")
        print("  python main.py test      - Test with sample questions")
        print("  python main.py stats     - Show Pinecone index statistics")
        print("\nFirst Time Setup:")
        print("  1. Create .env file (see .env.example)")
        print("  2. Run: python main.py ingest")
        print("  3. Run: python main.py chat")
        print("="*60 + "\n")
        return

    mode = sys.argv[1].lower()

    if mode == "ingest":
        ingest_documents()
    elif mode == "chat":
        start_chatbot()
    elif mode == "test":
        test_chatbot()
    elif mode == "stats":
        show_stats()
    else:
        print(f"\n❌ Unknown mode: {mode}")
        print("\nAvailable modes: ingest, chat, test, stats")
        print("Run 'python main.py' for usage instructions.\n")


if __name__ == "__main__":
    main()
