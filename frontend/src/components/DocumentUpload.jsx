import React, { useState } from 'react';
import { uploadDocument } from '../api';

export default function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF file first.');
      return;
    }

    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      const data = await uploadDocument(file);
      setMessage(`Successfully indexed "${data.filename}" (${data.total_pages} pages,${data.indexed_chunks} chunks).`);
      if (onUploadSuccess) onUploadSuccess(data);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>1. Upload Document</h2>
      <form onSubmit={handleUpload}>
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange} 
          disabled={loading}
        />
        <button type="submit" disabled={!file || loading}>
          {loading ? 'Processing & Vectorizing...' : 'Upload PDF'}
        </button>
      </form>
      {message && <p className="status-success">{message}</p>}
      {error && <p className="status-error">{error}</p>}
    </div>
  );
}