import openai
import os
from typing import List, Optional
from dotenv import load_dotenv
from .vector_store import VectorStore

load_dotenv()

class ChatService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self._openai_client = None
        self.conversations = {}  # Store conversation history
    
    @property
    def openai_client(self):
        """Lazy initialization of OpenAI client"""
        if self._openai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self._openai_client = openai.OpenAI(api_key=api_key)
        return self._openai_client
    
    def get_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context from vector store"""
        results = self.vector_store.search(query, k=k)
        context_chunks = [chunk for chunk, _ in results]
        return "\n\n".join(context_chunks)
    
    def get_response(self, user_message: str, conversation_id: Optional[str] = None) -> dict:
        """
        Generate response using RAG with OpenAI API
        
        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with response, conversation_id, and sources
        """
        # Get relevant context
        context = self.get_context(user_message, k=3)
        
        # Create system prompt
        system_prompt = """You are a helpful assistant that answers questions about life insurance based on the provided handbook. 
Use the context from the handbook to provide accurate and helpful answers. 
If the context doesn't contain relevant information, say so politely.
Always cite information from the handbook when available."""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Context from Life Insurance Handbook:\n\n{context}\n\n\nUser Question: {user_message}"
            }
        ]
        
        # Add conversation history if available
        if conversation_id and conversation_id in self.conversations:
            history = self.conversations[conversation_id]
            # Add history before the current message
            messages = [messages[0]] + history + [messages[1]]
        
        # Get response from OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using chat completions API
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            if conversation_id:
                if conversation_id not in self.conversations:
                    self.conversations[conversation_id] = []
                self.conversations[conversation_id].append({"role": "user", "content": user_message})
                self.conversations[conversation_id].append({"role": "assistant", "content": assistant_response})
            
            return {
                "response": assistant_response,
                "conversation_id": conversation_id or "default",
                "sources": [context[:200] + "..." if len(context) > 200 else context]  # Simplified sources
            }
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
