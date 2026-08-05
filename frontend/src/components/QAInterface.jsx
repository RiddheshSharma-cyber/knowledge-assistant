import React, { useState } from 'react';
import { askQuestion } from '../api';

export default function QAInterface() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [qaResult, setQaResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await askQuestion(question);
      setQaResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate answer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>2. Ask Questions</h2>
      <form onSubmit={handleAsk}>
        <input
          type="text"
          placeholder="Ask something about your uploaded documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={!question.trim() || loading}>
          {loading ? 'Searching & Generating...' : 'Ask AI'}
        </button>
      </form>

      {error && <p className="status-error">{error}</p>}

      {qaResult && (
        <div className="answer-box">
          <h3>Grounded Answer</h3>
          <p className="answer-text">{qaResult.answer}</p>

          {qaResult.sources && qaResult.sources.length > 0 && (
            <div className="sources-section">
              <h4>Source Citations</h4>
              <div className="sources-list">
                {qaResult.sources.map((src, index) => (
                  <div key={index} className="source-card">
                    <span className="source-badge">
                      📄 {src.source} (Page {src.page_number})
                    </span>
                    <p className="source-snippet">"{src.snippet}"</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}