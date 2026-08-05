import React from 'react';
import DocumentUpload from './components/DocumentUpload';
import QAInterface from './components/QAInterface';
import './App.css';

function App() {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem', fontFamily: 'sans-serif' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1>RAG Knowledge Assistant</h1>
        <p style={{ color: '#666' }}>Upload PDFs, store embeddings in ChromaDB, and query with grounded citations.</p>
      </header>

      <main>
        <DocumentUpload />
        <QAInterface />
      </main>
    </div>
  );
}

export default App;