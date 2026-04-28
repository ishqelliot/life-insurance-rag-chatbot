import faiss
import numpy as np
from typing import List, Tuple
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.embedding_dim = 1536  # text-embedding-3-small dimension
        self._openai_client = None
        self._loaded = False
    
    @property
    def openai_client(self):
        """Lazy initialization of OpenAI client"""
        if self._openai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self._openai_client = openai.OpenAI(api_key=api_key)
        return self._openai_client
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings from OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings).astype('float32')
        except Exception as e:
            raise Exception(f"Error getting embeddings: {str(e)}")
    
    def initialize(self, chunks: List[str]):
        """Initialize FAISS index with chunks"""
        if not chunks:
            raise ValueError("No chunks provided")
        
        self.chunks = chunks
        
        # Get embeddings for all chunks
        print(f"Getting embeddings for {len(chunks)} chunks...")
        embeddings = self.get_embeddings(chunks)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        self._loaded = True
        print(f"Vector store initialized with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for similar chunks
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of tuples (chunk_text, distance)
        """
        if not self._loaded:
            raise ValueError("Vector store not initialized")
        
        # Get query embedding
        query_embedding = self.get_embeddings([query])
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        # Get relevant chunks
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        return results
    
    def is_loaded(self) -> bool:
        """Check if vector store is loaded"""
        return self._loaded
