# AI Knowledge Assistant (Local RAG System)

An end-to-end Retrieval-Augmented Generation (RAG) platform that processes uploaded PDF documents, indexes text into vector embeddings, and provides grounded answers with source citations using local LLMs.

---

## 🏗️ Architecture Overview

```text
[ User Interface ]  <--->  [ React / Vite Frontend ]
                                   |
                                   | (Axios HTTP Requests)
                                   v
                           [ FastAPI Backend ]
                             /            \
                            /              \
            [ PyMuPDF / Text Chunking ]   [ ChromaDB Vector Store ]
                            \              /
                             \            /
                      [ Local LLM / Ollama Engine ]
```

---

## 🛠️ Tech Stack

* **Frontend**: React, Vite, Axios, Modern CSS3
* **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
* **RAG Pipeline**: LangChain, PyMuPDF (`fitz`), ChromaDB (Vector Database)
* **Inference Engine**: Ollama (Local LLM Execution)

---

## 📂 Project Structure

```text
knowledge-assistant/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── requirements.txt         # Python dependencies
│   └── chroma_db/               # Persistent vector database storage
├── frontend/
│   ├── src/
│   │   ├── api.js              # Axios backend service functions
│   │   ├── components/
│   │   │   ├── DocumentUpload.jsx # PDF upload component
│   │   │   └── QAInterface.jsx    # Question & Citation display component
│   │   ├── App.jsx             # Main React page layout
│   │   └── App.css             # UI styling
│   └── package.json            # Node.js dependencies
├── .env.example                 # Environment variable template
└── README.md                    # System documentation
```

---

## 🚀 Getting Started

### Prerequisites

* **Python**: 3.10 or higher
* **Node.js**: v18 or higher
* **Ollama**: Installed and running locally (`ollama serve`)

---

### 1. Backend Setup

1. Open a terminal and navigate to the `backend/` folder:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend API server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will be live at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

1. Open a second terminal and navigate to the `frontend/` folder:
   ```bash
   cd frontend
   ```

2. Install Node packages:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check endpoint |
| `POST` | `/api/documents/ingest` | Uploads a PDF file, extracts text, chunks content, and stores vectors |
| `POST` | `/api/qa/query` | Accepts user queries, retrieves relevant contexts, and generates grounded answers |

---

## 🧪 Application Workflow

1. **Upload Document**: Select a PDF file in the web UI. The server parses text using PyMuPDF, chunks text, creates vector embeddings, and stores them in ChromaDB.
2. **Ask Questions**: Submit natural language queries in the search box.
3. **Get Grounded Answers**: The system performs top-$K$ cosine similarity retrieval on ChromaDB and returns a synthesized answer complete with page numbers and source text snippets.