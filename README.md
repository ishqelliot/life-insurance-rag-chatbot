# Life Insurance RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built to answer questions about the Life Insurance Handbook published by IRDA (Insurance Regulatory and Development Authority of India).

## Tech Stack

- **Backend**: FastAPI
- **PDF Processing**: pypdf
- **Chunking**: Token-based chunks with overlap (using tiktoken)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: FAISS (local)
- **Chat Generation**: OpenAI Chat Completions API (gpt-4o-mini)
- **Frontend**: React with TypeScript

## Features

- Extract and process PDF content using pypdf
- Token-based text chunking with configurable overlap
- Generate embeddings using OpenAI's embedding model
- Store and search embeddings using FAISS vector database
- Chat interface with conversation history
- Modern React UI with modal chat interface

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

6. Ensure the PDF file is available:
   - The PDF should be in the project root directory: `Life Insurance Handbook (English).pdf`
   - Or in the Downloads folder (the code will try to find it there)

7. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Start both the backend and frontend servers (see Setup Instructions above)

2. Open your browser and navigate to `http://localhost:3000`

3. Click the "Open Chat" button to open the chat modal

4. The system will automatically initialize the vector store on first load (this may take a minute as it processes the PDF and generates embeddings)

5. Once initialized, you can start asking questions about life insurance based on the handbook

## API Endpoints

### GET `/health`
Check the health status of the API and whether the vector store is loaded.

### POST `/initialize`
Initialize the vector store by processing the PDF and creating embeddings. This is called automatically by the frontend on first load.

### POST `/chat`
Send a chat message and get a response.

**Request Body:**
```json
{
  "message": "What is term insurance?",
  "conversation_id": "optional_conversation_id"
}
```

**Response:**
```json
{
  "response": "Term insurance is a type of life insurance...",
  "conversation_id": "conv_1234567890",
  "sources": ["..."]
}
```

## Project Structure

```
life-insurance-rag-chatbot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── pdf_processor.py    # PDF extraction and chunking
│   │   ├── vector_store.py     # FAISS vector database operations
│   │   └── chat_service.py     # Chat service with OpenAI
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── components/
│   │   │   ├── ChatModal.tsx  # Chat modal component
│   │   │   └── ChatModal.css  # Chat modal styles
│   │   └── ...
│   └── package.json
├── Life Insurance Handbook (English).pdf
└── README.md
```

## Configuration

### Backend Configuration

You can modify chunking parameters in `backend/services/pdf_processor.py`:
- `chunk_size`: Number of tokens per chunk (default: 500)
- `chunk_overlap`: Number of overlapping tokens between chunks (default: 50)

### Frontend Configuration

The API base URL can be changed in `frontend/src/components/ChatModal.tsx`:
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## Notes

- The first initialization may take some time as it processes the entire PDF and generates embeddings
- Make sure you have sufficient OpenAI API credits
- The vector store is stored in memory and needs to be reinitialized when the server restarts
- For production use, consider persisting the FAISS index to disk

## Troubleshooting

1. **PDF not found error**: Ensure the PDF file is in the project root directory or update the path in `main.py`

2. **OpenAI API errors**: Check that your API key is correctly set in the `.env` file

3. **CORS errors**: Ensure the backend CORS settings in `main.py` match your frontend URL

4. **Port already in use**: Change the port in the uvicorn command or update the frontend API URL

## License

This project is for educational purposes.
