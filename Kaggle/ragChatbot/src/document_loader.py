from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from pathlib import Path
from typing import List
from langchain.schema import Document
import json


class DocumentLoader:
    """Simple document loader with generic JSON handling"""
    
    def __init__(self, blog_path: str, help_path: str, pdf_path: str, json_path: str):
        self.BLOG = blog_path
        self.HELP = help_path
        self.PDF = pdf_path
        self.JSON = json_path
        self.content = []
    
    def load_markdown(self):
        """Load markdown files"""
        blog_loader = DirectoryLoader(self.BLOG, glob="**/*.md", loader_cls=TextLoader)
        blog_docs = blog_loader.load()

        help_loader = DirectoryLoader(self.HELP, glob="**/*.md", loader_cls=TextLoader)
        help_docs = help_loader.load()

        # Add doc_type metadata to all markdown documents
        for doc in blog_docs:
            doc.metadata['doc_type'] = 'markdown'
            doc.metadata['category'] = 'blog'

        for doc in help_docs:
            doc.metadata['doc_type'] = 'markdown'
            doc.metadata['category'] = 'help'

        return blog_docs, help_docs
    
    def load_pdf(self):
        """Load PDF files"""
        pdf_files = list(Path(self.PDF).glob("*.pdf"))
        pdf_docs = []

        for files in pdf_files:
            loader = PyPDFLoader(str(files))
            docs = loader.load()
            # Add doc_type metadata
            for doc in docs:
                doc.metadata['doc_type'] = 'pdf'
                doc.metadata['filename'] = files.name
            pdf_docs.extend(docs)

        return pdf_docs
    
    def load_json(self):
        """Load JSON files simple and generic"""
        json_files = list(Path(self.JSON).glob("*.json"))
        json_docs = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert entire JSON to string - simple and works for any structure
                content = json.dumps(data, indent=2)
                
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': str(json_file),
                        'filename': json_file.name,
                        'doc_type': 'json'
                    }
                )
                json_docs.append(doc)
                
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")
        
        return json_docs
    
    def load_all(self):
        """Load all documents"""
        blog_docs, help_docs = self.load_markdown()
        pdf_docs = self.load_pdf()
        json_docs = self.load_json()
        
        self.content = blog_docs + help_docs + pdf_docs + json_docs
        
        print(f"Loaded {len(blog_docs)} blog files")
        print(f"Loaded {len(help_docs)} help files")
        print(f"Loaded {len(pdf_docs)} PDF pages")
        print(f"Loaded {len(json_docs)} JSON files")
        print(f"Total: {len(self.content)} documents")
        
        return self.content

