import axios from 'axios'

// Create axios instance with default configuration
export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management
export const tokenManager = {
  getAccessToken: () => localStorage.getItem('access_token'),
  getRefreshToken: () => localStorage.getItem('refresh_token'),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  },
  clearTokens: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = tokenManager.getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data
        tokenManager.setTokens(access_token, newRefreshToken)

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, redirect to login
        tokenManager.clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API types
export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
  subscription_type?: string
}

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface Project {
  id: number
  name: string
  description?: string
  status: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface ProjectWithStats extends Project {
  stats: {
    total_tasks: number
    completed_tasks: number
    total_data_collected: number
    total_reports: number
  }
}

export interface SearchTask {
  id: number
  project_id: number
  query: string
  status: string
  progress: number
  created_at: string
  completed_at?: string
}

export interface AnalysisResult {
  id: number
  project_id: number
  analysis_type: string
  result_data: any
  created_at: string
}

// API functions
export const authAPI = {
  login: (data: LoginData): Promise<AuthResponse> =>
    api.post('/auth/login', data).then(res => res.data),
  
  register: (data: RegisterData): Promise<AuthResponse> =>
    api.post('/auth/register', data).then(res => res.data),
  
  getCurrentUser: (): Promise<User> =>
    api.get('/auth/me').then(res => res.data),
  
  logout: (): Promise<void> =>
    api.post('/auth/logout').then(res => res.data),
}

export const projectsAPI = {
  getProjects: (params?: { skip?: number; limit?: number; status?: string }): Promise<ProjectWithStats[]> =>
    api.get('/projects', { params }).then(res => res.data),
  
  getProject: (id: number): Promise<ProjectWithStats> =>
    api.get(`/projects/${id}`).then(res => res.data),
  
  createProject: (data: { name: string; description?: string; status?: string }): Promise<Project> =>
    api.post('/projects', data).then(res => res.data),
  
  updateProject: (id: number, data: Partial<Project>): Promise<Project> =>
    api.put(`/projects/${id}`, data).then(res => res.data),
  
  deleteProject: (id: number): Promise<void> =>
    api.delete(`/projects/${id}`).then(res => res.data),
}

export const searchAPI = {
  createSearchTask: (data: { project_id: number; query: string; sources: string[] }): Promise<SearchTask> =>
    api.post('/search', data).then(res => res.data),
  
  getSearchTasks: (projectId: number): Promise<SearchTask[]> =>
    api.get(`/search/project/${projectId}`).then(res => res.data),
  
  getSearchTask: (id: number): Promise<SearchTask> =>
    api.get(`/search/${id}`).then(res => res.data),
}

export const analysisAPI = {
  getAnalysis: (projectId: number, analysisType?: string): Promise<AnalysisResult[]> =>
    api.get(`/analysis/project/${projectId}`, { params: { analysis_type: analysisType } }).then(res => res.data),
  
  createAnalysis: (data: { project_id: number; analysis_type: string }): Promise<AnalysisResult> =>
    api.post('/analysis', data).then(res => res.data),
}

export const reportsAPI = {
  generateReport: (data: { project_id: number; report_type: string; format: string }): Promise<{ task_id: string }> =>
    api.post('/reports/generate', data).then(res => res.data),
  
  getReportStatus: (taskId: string): Promise<{ status: string; file_path?: string }> =>
    api.get(`/reports/status/${taskId}`).then(res => res.data),
  
  downloadReport: (filePath: string): Promise<Blob> =>
    api.get(`/reports/download`, { params: { file_path: filePath }, responseType: 'blob' }).then(res => res.data),
}