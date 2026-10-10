const API_BASE = '/api/v1';

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  // Projects
  getProjects: () => fetchJSON(`${API_BASE}/projects`),
  getProject: (id) => fetchJSON(`${API_BASE}/projects/${id}`),
  createProject: (data) =>
    fetchJSON(`${API_BASE}/projects`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteProject: (id) =>
    fetchJSON(`${API_BASE}/projects/${id}`, {
      method: 'DELETE',
    }),

  // Requirements
  getProjectRequirements: (projectId, params = {}) => {
    const query = new URLSearchParams();
    if (params.req_type) query.append('req_type', params.req_type);
    if (params.status) query.append('status', params.status);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return fetchJSON(`${API_BASE}/projects/${projectId}/requirements${queryString}`);
  },
  createRequirement: (projectId, data) =>
    fetchJSON(`${API_BASE}/projects/${projectId}/requirements`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteRequirement: (id) =>
    fetchJSON(`${API_BASE}/requirements/${id}`, {
      method: 'DELETE',
    }),

  // Phase 2: Imports
  importText: (projectId, text) =>
    fetchJSON(`${API_BASE}/projects/${projectId}/requirements/import-text`, {
      method: 'POST',
      body: JSON.stringify({ text, preview: true }),
    }),

  importFile: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(
      `${API_BASE}/projects/${projectId}/requirements/import?preview=true`,
      {
        method: 'POST',
        body: formData,
      }
    );
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }
    return response.json();
  },

  batchCreateRequirements: (projectId, requirements) =>
    fetchJSON(`${API_BASE}/projects/${projectId}/requirements/batch`, {
      method: 'POST',
      body: JSON.stringify({ requirements }),
    }),

  // Phase 3A/3B: Quality Analysis
  analyzeRequirement: (reqId) =>
    fetchJSON(`${API_BASE}/requirements/${reqId}/analyze`, {
      method: 'POST',
    }),

  analyzeProject: (projectId) =>
    fetchJSON(`${API_BASE}/projects/${projectId}/analyze`, {
      method: 'POST',
    }),
};
