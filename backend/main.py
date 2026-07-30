"""
Main entry point for Knowledge Assistant FastAPI Backend.
"""

from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pdf_processor import extract_text_from_pdf, create_chunks
from vector_store import add_chunks_to_vectorstore, query_vectorstore

app = FastAPI(
    title="Knowledge Assistant API",
    description="Backend service for RAG document question answering",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Schemas
class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="healthy")
    message: str = Field(..., example="Knowledge Assistant API is running")


class IngestResponse(BaseModel):
    filename: str
    total_pages: int
    total_chunks: int
    indexed_chunks: int


class QueryRequest(BaseModel):
    question: str = Field(..., example="What is the main topic of the document?")
    top_k: int = Field(default=3, ge=1, le=10)


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    distance: float


class QueryResponse(BaseModel):
    question: str
    results: List[SearchResult]


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to Knowledge Assistant API Version 1"}


@app.get("/api/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
def health_check():
    return HealthCheckResponse(
        status="healthy",
        message="Knowledge Assistant API is running",
    )


@app.post("/api/documents/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to extract text, chunk it, and store vectors into ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    try:
        content = await file.read()
        pages = extract_text_from_pdf(content, file.filename)
        
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract readable text from the uploaded PDF."
            )

        chunks = create_chunks(pages, chunk_size=1000, chunk_overlap=200)
        indexed_count = add_chunks_to_vectorstore(chunks)

        return IngestResponse(
            filename=file.filename,
            total_pages=len(pages),
            total_chunks=len(chunks),
            indexed_chunks=indexed_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the PDF: {str(e)}"
        )


@app.post("/api/documents/search", response_model=QueryResponse, status_code=status.HTTP_200_OK)
def search_documents(request: QueryRequest):
    """
    Perform semantic vector similarity search across ingested documents.
    """
    try:
        results = query_vectorstore(request.question, n_results=request.top_k)
        return QueryResponse(
            question=request.question,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )