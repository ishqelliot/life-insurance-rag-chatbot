import pypdf
from typing import List
import tiktoken

class PDFProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize PDF processor with token-based chunking.
        
        Args:
            chunk_size: Number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Used by text-embedding-3-small
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into token-based chunks with overlap.
        """
        # Encode text to tokens
        tokens = self.encoding.encode(text)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk tokens
            chunk_tokens = tokens[start:end]
            
            # Decode tokens back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text.strip())
            
            # Move start position with overlap
            start += self.chunk_size - self.chunk_overlap
            
            # If we're at the end, break
            if end >= len(tokens):
                break
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Process PDF: extract text and chunk it.
        
        Returns:
            List of text chunks
        """
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            raise ValueError("No text extracted from PDF")
        
        chunks = self.chunk_text(text)
        
        return chunks
