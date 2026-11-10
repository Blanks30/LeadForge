/**
 * LeadForge Centralized API Client
 * Interfaces with FastAPI backend with error handling and fallback detection.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errorMsg;
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }
    return await res.json();
  } catch (error) {
    console.error(`API request failed [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // Service health
  getHealth: () => request('/health'),

  // ICP endpoints
  getIcp: () => request('/icp'),
  updateIcp: (payload) => request('/icp', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Prospect endpoints
  getProspects: (params = {}) => {
    const query = new URLSearchParams();
    if (params.minScore !== undefined && params.minScore !== null && params.minScore !== '') {
      query.append('min_score', params.minScore);
    }
    if (params.status) {
      query.append('status', params.status);
    }
    if (params.search) {
      query.append('search', params.search);
    }
    const qs = query.toString();
    return request(`/prospects${qs ? `?${qs}` : ''}`);
  },

  seedProspects: () => request('/prospects/seed', { method: 'POST' }),

  createProspect: (payload) => request('/prospects', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  getProspectDetail: (id) => request(`/prospects/${id}`),

  researchProspect: (id) => request(`/prospects/${id}/research`, { method: 'POST' }),

  generateOutreachDraft: (id, options = {}) => request(`/prospects/${id}/draft`, {
    method: 'POST',
    body: JSON.stringify(options),
  }),

  // Tavily General-Purpose Web Search
  searchWeb: (query, maxResults = 8) => request('/search', {
    method: 'POST',
    body: JSON.stringify({ query, max_results: maxResults }),
  }),

  // CSV Export URL
  getExportUrl: () => `${API_BASE_URL}/export/csv`,
};
