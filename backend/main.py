from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn
from pathlib import Path

from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStore
from services.chat_service import ChatService

app = FastAPI(title="Life Insurance RAG Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
vector_store = VectorStore()
chat_service = ChatService(vector_store)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str] = []

class HealthResponse(BaseModel):
    status: str
    vector_db_loaded: bool

@app.get("/")
async def root():
    return {"message": "Life Insurance RAG Chatbot API"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        vector_db_loaded=vector_store.is_loaded()
    )

@app.post("/initialize")
async def initialize():
    """Initialize the vector store with the PDF"""
    try:
        # Try multiple possible locations for the PDF
        possible_paths = [
            Path(__file__).parent.parent / "Life Insurance Handbook (English).pdf",
            Path("/Users/kanishksankpal/Downloads/Life Insurance Handbook (English).pdf"),
        ]
        
        pdf_path = None
        for path in possible_paths:
            if path.exists():
                pdf_path = path
                break
        
        if not pdf_path:
            return JSONResponse(
                status_code=404,
                content={"error": "PDF file not found. Please ensure the PDF is in the project root or Downloads folder."}
            )
        
        # Process PDF
        chunks = pdf_processor.process_pdf(str(pdf_path))
        
        # Create embeddings and store in FAISS
        vector_store.initialize(chunks)
        
        return {"status": "initialized", "chunks_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Handle chat messages with RAG"""
    try:
        if not vector_store.is_loaded():
            raise HTTPException(
                status_code=400,
                detail="Vector store not initialized. Please call /initialize first."
            )
        
        response = chat_service.get_response(message.message, message.conversation_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
