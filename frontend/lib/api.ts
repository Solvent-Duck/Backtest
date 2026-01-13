/**
 * API client configuration
 */
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token interceptor (TODO: implement when auth is ready)
apiClient.interceptors.request.use((config) => {
  // const token = getAuthToken();
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

export default apiClient;
