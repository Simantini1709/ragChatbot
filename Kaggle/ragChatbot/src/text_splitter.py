from typing import List
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)
from langchain.schema import Document


class TextSplitter:
    """Splits documents into chunks based on their type"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Standard text splitter for general content
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

        # Markdown-specific splitter (preserves headers)
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

        # JSON splitter (similar to text but with JSON-friendly separators)
        self.json_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["},\n", "\n", ", ", " ", ""]
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks based on their type

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects with metadata
        """
        all_chunks = []
        global_chunk_counter = 0  # Global counter for unique IDs

        for doc_idx, doc in enumerate(documents):
            doc_type = doc.metadata.get('doc_type', 'other')

            # Route to appropriate chunking method
            if doc_type == 'markdown':
                chunks = self._chunk_markdown(doc)
            elif doc_type == 'pdf':
                chunks = self._chunk_pdf(doc)
            elif doc_type == 'json':
                chunks = self._chunk_json(doc)
            else:
                chunks = self.text_splitter.split_documents([doc])

            # Add chunk metadata with GLOBALLY UNIQUE IDs
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                # Create globally unique chunk_id using source path + counter
                source = doc.metadata.get('source', f'unknown_{doc_idx}')
                # Use hash of source path to make ID shorter but still unique
                import hashlib
                source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
                chunk.metadata['chunk_id'] = f"chunk_{source_hash}_{i}_{global_chunk_counter}"
                chunk.metadata['total_chunks'] = len(chunks)
                global_chunk_counter += 1

            all_chunks.extend(chunks)

        print(f"Split {len(documents)} documents into {len(all_chunks)} chunks")
        print(f"Created {global_chunk_counter} globally unique chunk IDs")
        return all_chunks

    def _chunk_markdown(self, doc: Document) -> List[Document]:
        """
        Split markdown while preserving header structure

        Args:
            doc: Markdown Document to chunk

        Returns:
            List of chunked Documents
        """
        try:
            # First split by headers
            md_chunks = self.markdown_splitter.split_text(doc.page_content)

            # Then apply recursive splitting if chunks are too large
            final_chunks = []
            for md_chunk in md_chunks:
                # Create document from markdown chunk
                temp_doc = Document(
                    page_content=md_chunk.page_content,
                    metadata={**doc.metadata, **md_chunk.metadata}
                )

                # If chunk is too large, split further
                if len(md_chunk.page_content) > self.chunk_size:
                    sub_chunks = self.text_splitter.split_documents([temp_doc])
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(temp_doc)

            return final_chunks if final_chunks else [doc]

        except Exception as e:
            print(f"Warning: Markdown splitting failed ({e}), using standard splitter")
            return self.text_splitter.split_documents([doc])

    def _chunk_pdf(self, doc: Document) -> List[Document]:
        """
        Split PDF content using standard text splitter

        Args:
            doc: PDF Document to chunk

        Returns:
            List of chunked Documents
        """
        return self.text_splitter.split_documents([doc])

    def _chunk_json(self, doc: Document) -> List[Document]:
        """
        Split JSON content using JSON-aware splitter

        Args:
            doc: JSON Document to chunk

        Returns:
            List of chunked Documents
        """
        return self.json_splitter.split_documents([doc])
