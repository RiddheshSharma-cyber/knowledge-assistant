import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/documents/ingest', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const searchDocuments = async (queryText, topK = 6) => {
  const response = await apiClient.post('/api/documents/search', {
    query_text: queryText,
    top_k: topK,
  });
  return response.data;
};

// Ensure askQuestion is exported here
export const askQuestion = async (question, topK = 6) => {
  const response = await apiClient.post('/api/qa/query', {
    question: question,
    top_k: topK,
  });
  return response.data;
};