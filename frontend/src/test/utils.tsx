import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { AuthProvider } from '../contexts/AuthContext'

// Mock user data for testing
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  subscription_type: 'free',
}

export const mockProject = {
  id: 1,
  name: 'Test Project',
  description: 'A test project',
  status: 'active',
  user_id: 1,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  stats: {
    total_tasks: 5,
    completed_tasks: 3,
    total_data_collected: 100,
    total_reports: 2,
  },
}

// Mock API responses
export const mockApiResponses = {
  auth: {
    login: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer',
      user: mockUser,
    },
    currentUser: mockUser,
  },
  projects: {
    list: [mockProject],
    single: mockProject,
    create: mockProject,
    update: mockProject,
  },
  search: {
    create: {
      id: 1,
      project_id: 1,
      query: 'test query',
      status: 'pending',
      progress: 0,
      created_at: '2023-01-01T00:00:00Z',
    },
  },
  analysis: {
    results: [
      {
        id: 1,
        project_id: 1,
        analysis_type: 'sentiment',
        result_data: {
          total_analyzed: 100,
          average_score: 0.2,
          sentiment_distribution: {
            positive: { count: 40, percentage: 40 },
            negative: { count: 35, percentage: 35 },
            neutral: { count: 25, percentage: 25 },
          },
        },
        created_at: '2023-01-01T00:00:00Z',
      },
    ],
  },
}

// Create a test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

// Mock auth context values
export const mockAuthContextValue = {
  user: mockUser,
  isLoading: false,
  isAuthenticated: true,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
}

export const mockUnauthenticatedContextValue = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
}

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[]
  authContextValue?: typeof mockAuthContextValue
  queryClient?: QueryClient
}

export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const {
    initialEntries = ['/'],
    authContextValue = mockAuthContextValue,
    queryClient = createTestQueryClient(),
    ...renderOptions
  } = options

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider value={authContextValue as any}>
            {children}
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Helper function to render without authentication
export function renderWithoutAuth(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  return renderWithProviders(ui, {
    ...options,
    authContextValue: mockUnauthenticatedContextValue,
  })
}

// Helper function to render with specific route
export function renderWithRoute(
  ui: ReactElement,
  route: string,
  options: CustomRenderOptions = {}
) {
  return renderWithProviders(ui, {
    ...options,
    initialEntries: [route],
  })
}

// Mock API module
export const mockApi = {
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
    logout: vi.fn(),
  },
  projectsAPI: {
    getProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
  },
  searchAPI: {
    createSearchTask: vi.fn(),
    getSearchTasks: vi.fn(),
    getSearchTask: vi.fn(),
  },
  analysisAPI: {
    getAnalysis: vi.fn(),
    createAnalysis: vi.fn(),
  },
  reportsAPI: {
    generateReport: vi.fn(),
    getReportStatus: vi.fn(),
    downloadReport: vi.fn(),
  },
}

// Helper to wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

// Helper to mock successful API responses
export function mockSuccessfulApiCalls() {
  mockApi.authAPI.getCurrentUser.mockResolvedValue(mockUser)
  mockApi.projectsAPI.getProjects.mockResolvedValue([mockProject])
  mockApi.projectsAPI.getProject.mockResolvedValue(mockProject)
  mockApi.projectsAPI.createProject.mockResolvedValue(mockProject)
  mockApi.projectsAPI.updateProject.mockResolvedValue(mockProject)
  mockApi.projectsAPI.deleteProject.mockResolvedValue(undefined)
}

// Helper to mock API errors
export function mockApiErrors() {
  const error = new Error('API Error')
  mockApi.authAPI.login.mockRejectedValue(error)
  mockApi.projectsAPI.getProjects.mockRejectedValue(error)
  mockApi.projectsAPI.createProject.mockRejectedValue(error)
}

// Helper to create mock form events
export function createMockFormEvent(values: Record<string, string>) {
  return {
    preventDefault: vi.fn(),
    target: {
      elements: Object.entries(values).reduce((acc, [name, value]) => {
        acc[name] = { value }
        return acc
      }, {} as Record<string, { value: string }>),
    },
  } as any
}

// Helper to simulate user interactions
export const userInteractions = {
  fillForm: (getByLabelText: any, values: Record<string, string>) => {
    Object.entries(values).forEach(([label, value]) => {
      const input = getByLabelText(new RegExp(label, 'i'))
      input.value = value
    })
  },
}

// Custom matchers for testing
export const customMatchers = {
  toHaveValidationError: (received: HTMLElement, expected: string) => {
    const errorElement = received.querySelector('[role="alert"], .error, .text-red-600')
    const hasError = errorElement && errorElement.textContent?.includes(expected)
    
    return {
      message: () =>
        hasError
          ? `Expected element not to have validation error "${expected}"`
          : `Expected element to have validation error "${expected}"`,
      pass: !!hasError,
    }
  },
}

// Export everything for easy imports
export * from '@testing-library/react'
export * from '@testing-library/user-event'
export { vi } from 'vitest'