"""
PDF Extraction and Text Chunking Engine for Knowledge Assistant.
"""

from typing import Any, Dict, List
from pypdf import PdfReader
import io


def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Reads PDF bytes and extracts text page-by-page with associated metadata.
    
    Args:
        pdf_bytes (bytes): The raw byte data of the uploaded PDF file.
        filename (str): The name of the original PDF file.
        
    Returns:
        List[Dict[str, Any]]: List of pages with 'page_number' and raw 'text'.
    """
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    extracted_pages = []

    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Clean up excessive blank spaces and carriage returns
        text = text.strip()
        
        if text:  # Ignore completely blank pages
            extracted_pages.append({
                "page_number": page_index + 1,
                "text": text,
                "source": filename
            })

    return extracted_pages


def create_chunks(
    pages_data: List[Dict[str, Any]], 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Splits page texts into overlapping chunks while preserving source metadata.
    
    Args:
        pages_data (List[Dict[str, Any]]): Extracted pages from extract_text_from_pdf.
        chunk_size (int): Max number of characters per chunk.
        chunk_overlap (int): Number of overlapping characters between consecutive chunks.
        
    Returns:
        List[Dict[str, Any]]: Clean chunks ready for vector embeddings.
    """
    chunks = []
    global_chunk_id = 0

    for page in pages_data:
        text = page["text"]
        page_num = page["page_number"]
        source = page["source"]

        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": f"{source}_p{page_num}_c{global_chunk_id}",
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "page_number": page_num,
                    "character_count": len(chunk_text)
                }
            })

            global_chunk_id += 1
            
            # Move the window forward by (chunk_size - chunk_overlap)
            start += (chunk_size - chunk_overlap)
            
            # Avoid infinite loop if overlap >= size
            if chunk_overlap >= chunk_size:
                break

    return chunks