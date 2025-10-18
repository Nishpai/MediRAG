import axios from 'axios';

/**
 * API Configuration
 * Base URL for the Flask backend API
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Create axios instance with default configuration
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor for logging (optional)
 */
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      console.error('API Error Response:', error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('API No Response:', error.request);
    } else {
      // Something else happened
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Ask a question to the medical FAQ bot
 * @param {string} query - The user's medical question
 * @returns {Promise<Object>} Response containing answer, sources, confidence, and latency
 */
export const askQuestion = async (query) => {
  try {
    const response = await apiClient.post('/ask', { query });
    return response.data;
  } catch (error) {
    // Handle specific error cases
    if (error.response) {
      // Server returned an error response
      const status = error.response.status;
      const data = error.response.data;

      if (status === 400) {
        throw new Error(data.error || 'Invalid query. Please try again.');
      } else if (status === 503) {
        throw new Error('The service is temporarily unavailable. Please try again later.');
      } else if (status >= 500) {
        throw new Error('Server error. Please try again later.');
      } else {
        throw new Error(data.error || 'An unexpected error occurred.');
      }
    } else if (error.request) {
      // No response received from server
      throw new Error('Unable to connect to the server. Please check your connection and try again.');
    } else {
      // Other errors
      throw new Error('An unexpected error occurred. Please try again.');
    }
  }
};

/**
 * Check server health status
 * @returns {Promise<Object>} Server status and statistics
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    throw new Error('Unable to connect to the server.');
  }
};

/**
 * Rebuild the vector store index
 * @param {string} password - Admin password (optional)
 * @returns {Promise<Object>} Status message
 */
export const rebuildIndex = async (password = '') => {
  try {
    const response = await apiClient.post('/build_index', { password });
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Unauthorized. Invalid password.');
    }
    throw new Error('Failed to rebuild index.');
  }
};

/**
 * Get RAG pipeline statistics
 * @returns {Promise<Object>} Pipeline statistics
 */
export const getStats = async () => {
  try {
    const response = await apiClient.get('/stats');
    return response.data;
  } catch (error) {
    throw new Error('Failed to retrieve statistics.');
  }
};

export default {
  askQuestion,
  checkHealth,
  rebuildIndex,
  getStats,
};
