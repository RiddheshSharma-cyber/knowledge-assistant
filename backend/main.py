"""
Main entry point for Knowledge Assistant FastAPI Backend.
"""

from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pdf_processor import extract_text_from_pdf, create_chunks
from vector_store import add_chunks_to_vectorstore, query_vectorstore
from llm_service import generate_answer

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


class QARequest(BaseModel):
    question: str = Field(..., example="What are model manifests in Ollama?")
    top_k: int = Field(default=3, ge=1, le=10)


class SourceCitation(BaseModel):
    source: str
    page_number: int
    snippet: str


class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]


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


@app.post("/api/qa/query", response_model=QAResponse, status_code=status.HTTP_200_OK)
def ask_question(request: QARequest):
    """
    Full RAG Pipeline: Vector Search -> LLM Prompt Construction -> Grounded Answer with Citations.
    """
    try:
        chunks = query_vectorstore(request.question, n_results=request.top_k)
        
        if not chunks:
            return QAResponse(
                question=request.question,
                answer="No relevant document content found in the knowledge base.",
                sources=[]
            )

        answer = generate_answer(request.question, chunks)

        sources = [
            SourceCitation(
                source=chunk["metadata"].get("source", "Unknown"),
                page_number=chunk["metadata"].get("page_number", 0),
                snippet=chunk["text"][:150] + "..."
            )
            for chunk in chunks
        ]

        return QAResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"QA pipeline error: {str(e)}"
        )