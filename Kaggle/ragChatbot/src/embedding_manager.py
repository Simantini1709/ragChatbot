from typing import List
from openai import OpenAI
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
class EmbeddingManager:
    def __init__(self, model=None):
        # Validate API key first
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.model = model or config.EMBEDDING_MODEL
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        print(f"Initialized EmbeddingManager with model: {self.model}")
    def embed_text(self,text):
        try:
            response=self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding :{e}")
            raise
    def embed_texts(self, texts, batch_size=200):
        """
        Create embeddings for multiple texts in batches

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts per API call (default: 200)

        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                # Progress feedback
                if (i + batch_size) % 1000 == 0 or (i + batch_size) >= total:
                    print(f"Embedded {min(i + batch_size, total)}/{total} chunks...")

            except Exception as e:
                print(f"Error processing batch {i}-{i+batch_size}: {e}")
                raise

        print(f"✓ Created {len(embeddings)} embeddings successfully")
        return embeddings
    def get_embedding_dimension(self):
        dimensions={
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536 
        }
        return dimensions.get(self.model,1536)