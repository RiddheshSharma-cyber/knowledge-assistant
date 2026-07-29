"""
Main entry point for Knowledge Assistant FastAPI Backend.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Initialize FastAPI App
app = FastAPI(
    title="Knowledge Assistant API",
    description="Backend service for RAG document question answering",
    version="1.0.0",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="healthy")
    message: str = Field(..., example="Knowledge Assistant API is running")


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to Knowledge Assistant API Version 1"}


@app.get(
    "/api/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
def health_check():
    return HealthCheckResponse(
        status="healthy",
        message="Knowledge Assistant API is running",
    )