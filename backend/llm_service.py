"""
LLM Abstraction Service for Knowledge Assistant.
Supports dynamic model selection and seamless provider switching (Gemini / Ollama).
"""

import os
import json
import urllib.request
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "latest").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")


def format_prompt(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved context chunks into a strict, grounded RAG prompt.
    """
    context_str = ""
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get("metadata", {}).get("source", "Unknown")
        page = chunk.get("metadata", {}).get("page_number", "N/A")
        context_str += f"\n--- Context Chunk {i} [Source: {source}, Page: {page}] ---\n"
        context_str += chunk.get("text", "").strip() + "\n"

    prompt = f"""You are a precise, grounded AI Knowledge Assistant.
Answer the user's question relying strictly on the context chunks provided below.

RULES:
1. Do NOT make up information or use outside knowledge not explicitly supported by the context.
2. If the context does not contain enough information to answer the question, state:
   "I cannot find the answer in the uploaded documents."
3. Always cite the exact source document and page number in your answer using inline citations like (Source: filename.pdf, Page X).

Context:
{context_str}

User Question: {question}

Grounded Answer:"""
    return prompt


def generate_answer(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Routes the prompt to the configured LLM provider (Gemini or Ollama).
    """
    prompt = format_prompt(question, context_chunks)

    if LLM_PROVIDER == "gemini":
        return _call_gemini(prompt)
    elif LLM_PROVIDER == "ollama":
        return _call_ollama(prompt)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. Use 'gemini' or 'ollama'.")


def _get_latest_flash_model(client: genai.Client) -> str:
    """
    Queries the Gemini API to find the highest-version Flash model available to the account.
    """
    try:
        models = list(client.models.list())
        flash_models = []

        for m in models:
            model_id = m.name.replace("models/", "")
            # Filter standard text generation flash models (excluding preview/TTS/image variants)
            if "flash" in model_id and not any(sub in model_id for sub in ["image", "tts", "audio", "live", "preview"]):
                flash_models.append(model_id)

        if flash_models:
            # Sort descending to grab the newest available version (e.g. 2.5 > 2.0 > 1.5)
            flash_models.sort(reverse=True)
            return flash_models[0]
    except Exception:
        pass

    return "gemini-2.0-flash"


def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        raise ValueError("GEMINI_API_KEY is missing or invalid in backend/.env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Automatically fetch the latest available model if configured as 'latest'
    if GEMINI_MODEL in ["latest", "auto", ""]:
        target_model = _get_latest_flash_model(client)
    else:
        target_model = GEMINI_MODEL

    response = client.models.generate_content(
        model=target_model,
        contents=prompt,
    )
    return response.text.strip()


def _call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to local Ollama server at {OLLAMA_URL}: {str(e)}")