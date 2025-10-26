"""
Configuration management for RAG Chatbot
Loads settings from environment variables with sensible defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the RAG chatbot"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-chatbot-index")

    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")

    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retrieval Configuration
    TOP_K = int(os.getenv("TOP_K", "5"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

    # Data Paths
    BASE_DIR = Path(__file__).parent
    BLOG_PATH = BASE_DIR / os.getenv("BLOG_PATH", "data/markdown/markdowns-cleaned/topics/blog")
    HELP_PATH = BASE_DIR / os.getenv("HELP_PATH", "data/markdown/markdowns-cleaned/topics/help")
    PDF_PATH = BASE_DIR / os.getenv("PDF_PATH", "data/pdf")
    JSON_PATH = BASE_DIR / os.getenv("JSON_PATH", "data/json")

    # Pinecone Configuration
    PINECONE_DIMENSION = 1536  # For text-embedding-3-small
    PINECONE_METRIC = "cosine"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")
        if not cls.PINECONE_API_KEY:
            errors.append("PINECONE_API_KEY is required")

        # Check if data paths exist
        for path_name, path in [
            ("BLOG_PATH", cls.BLOG_PATH),
            ("HELP_PATH", cls.HELP_PATH),
            ("PDF_PATH", cls.PDF_PATH),
            ("JSON_PATH", cls.JSON_PATH)
        ]:
            if not path.exists():
                errors.append(f"{path_name} does not exist: {path}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)"""
        print("\n" + "="*60)
        print("RAG Chatbot Configuration")
        print("="*60)
        print(f"OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not set'}")
        print(f"Anthropic API Key: {'✓ Set' if cls.ANTHROPIC_API_KEY else '✗ Not set'}")
        print(f"Pinecone API Key: {'✓ Set' if cls.PINECONE_API_KEY else '✗ Not set'}")
        print(f"Pinecone Index: {cls.PINECONE_INDEX_NAME}")
        print("-"*60)
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"Top K Results: {cls.TOP_K}")
        print(f"Temperature: {cls.TEMPERATURE}")
        print("-"*60)
        print(f"Blog Path: {cls.BLOG_PATH}")
        print(f"Help Path: {cls.HELP_PATH}")
        print(f"PDF Path: {cls.PDF_PATH}")
        print(f"JSON Path: {cls.JSON_PATH}")
        print("="*60 + "\n")


# Create a singleton instance
config = Config()
