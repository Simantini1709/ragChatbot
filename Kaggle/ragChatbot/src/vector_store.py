from typing import List, Dict, Any, Tuple
from pinecone import Pinecone, ServerlessSpec
import sys
import os
import time
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

class VectorStore:
    def __init__(self, index_name=None):
        """Initialize Pinecone connection"""
        # Validate pinecone API key
        if not config.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        self.index_name = index_name or config.PINECONE_INDEX_NAME
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = None
        print(f"Initialized Pinecone connection")
    def create_index(self, dimension=None, metric=None):
        """Create or connect to Pinecone index"""
        dimension = dimension or config.PINECONE_DIMENSION
        metric = metric or config.PINECONE_METRIC

        # Check if index already exists in pinecone
        existing_indexes = self.pc.list_indexes()
        index_names = [idx['name'] for idx in existing_indexes]

        if self.index_name in index_names:
            print(f"✓ Index '{self.index_name}' already exists, connecting...")
            self.index = self.pc.Index(self.index_name)
            stats = self.index.describe_index_stats()
            print(f"  - Total vectors: {stats.total_vector_count}")

        else:
            print(f"Creating new index '{self.index_name}'...")
            print(f"  - Dimension: {dimension}")
            print(f"  - Metric: {metric}")

            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,  # Fixed: was self.dimension
                metric=metric,
                spec=ServerlessSpec(
                    cloud=config.PINECONE_CLOUD,
                    region=config.PINECONE_REGION
                )
            )

            print("Waiting for index to be ready...")
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)

            self.index = self.pc.Index(self.index_name)
            print(f"✓ Index '{self.index_name}' created successfully!")

        return self.index
    def upsert_documents(self, texts, embeddings, metadatas, batch_size:int=200):
        """Upload documents to Pinecone"""
        if not self.index:
            raise ValueError("Index not initialised call create_index() first")
        if not (len(texts) == len(embeddings) == len(metadatas)):
            raise ValueError("texts, embeddings, and metadatas must have the same length")

        total_vectors = len(texts)
        print(f"\nUpserting {total_vectors} vectors to Pinecone...")

        # Prepare vectors
        vectors = []
        for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            vector_id = metadata.get('chunk_id', f"doc_{i}")
            metadata_with_text = {**metadata, 'text': text}
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata_with_text
            })

        # Upload in batches
        upserted_count = 0
        for i in tqdm(range(0, len(vectors), batch_size), desc="Uploading to Pinecone"):
            batch = vectors[i:i+batch_size]
            try:
                self.index.upsert(vectors=batch)
                upserted_count += len(batch)
            except Exception as e:
                print(f"\nError upserting batch {i}-{i+batch_size}: {e}")
                raise

        # Print summary (OUTSIDE the loop - this was the bug!)
        print(f"✓ Successfully upserted {upserted_count} vectors")
        time.sleep(2)  # Give Pinecone time to update
        stats = self.index.describe_index_stats()
        print(f"✓ Index now contains {stats.total_vector_count} total vectors")

        return upserted_count
        
    def search(self, query_embedding, top_k=None, filter_dict=None, include_metadata=True):
        """Search for similar vectors in Pinecone"""
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        top_k = top_k or config.TOP_K  # Use parameter or config default

        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata
            )

            # Format results
            matches = []
            for match in results.matches:
                matches.append({
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', '') if include_metadata else '',
                    'metadata': match.metadata if include_metadata else {}
                })

            # Return OUTSIDE the loop (this was the bug!)
            return matches

        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            raise 
    def delete_all(self):
        """Delete all vectors from the index (keeps index structure)"""
        if not self.index:
            raise ValueError("Index not initialized.")

        print(f"⚠️  Deleting all vectors from index '{self.index_name}'...")
        self.index.delete(delete_all=True)
        print("✓ All vectors deleted")

    def delete_index(self):
        """Delete the entire index (use with caution!)"""
        print(f"⚠️  Deleting index '{self.index_name}'...")
        self.pc.delete_index(self.index_name)
        self.index = None
        print("✓ Index deleted")

    def get_stats(self):
        """Get index statistics"""
        if not self.index:
            raise ValueError("Index not initialized.")

        stats = self.index.describe_index_stats()
        return {
            'total_vectors': stats.total_vector_count,
            'dimension': stats.dimension if hasattr(stats, 'dimension') else config.PINECONE_DIMENSION,
            'index_fullness': stats.index_fullness if hasattr(stats, 'index_fullness') else 0
        }
    