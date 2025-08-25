import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { AuthProvider, useAuth } from '../contexts/AuthContext'
import { mockApiResponses, mockApi } from '../test/utils'

// Mock the API module
vi.mock('../lib/api', () => mockApi)

describe('AuthContext', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, cacheTime: 0 },
        mutations: { retry: false },
      },
    })
    
    // Reset all mocks
    vi.clearAllMocks()
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    })
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  )

  it('should provide initial auth state when not authenticated', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.isLoading).toBe(false)
  })

  it('should authenticate user on successful login', async () => {
    const loginResponse = mockApiResponses.auth.login
    mockApi.authAPI.login.mockResolvedValue(loginResponse)
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await result.current.login({
      email: 'test@example.com',
      password: 'password123',
    })

    await waitFor(() => {
      expect(result.current.user).toEqual(loginResponse.user)
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(mockApi.authAPI.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    })
  })

  it('should handle login error', async () => {
    const errorMessage = 'Invalid credentials'
    mockApi.authAPI.login.mockRejectedValue(new Error(errorMessage))
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await expect(
      result.current.login({
        email: 'test@example.com',
        password: 'wrongpassword',
      })
    ).rejects.toThrow(errorMessage)

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('should register user successfully', async () => {
    const registerResponse = mockApiResponses.auth.login
    mockApi.authAPI.register.mockResolvedValue(registerResponse)
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await result.current.register({
      email: 'newuser@example.com',
      password: 'password123',
      full_name: 'New User',
    })

    await waitFor(() => {
      expect(result.current.user).toEqual(registerResponse.user)
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(mockApi.authAPI.register).toHaveBeenCalledWith({
      email: 'newuser@example.com',
      password: 'password123',
      full_name: 'New User',
    })
  })

  it('should handle registration error', async () => {
    const errorMessage = 'Email already exists'
    mockApi.authAPI.register.mockRejectedValue(new Error(errorMessage))
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await expect(
      result.current.register({
        email: 'existing@example.com',
        password: 'password123',
        full_name: 'Existing User',
      })
    ).rejects.toThrow(errorMessage)

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('should logout user successfully', async () => {
    // First login
    const loginResponse = mockApiResponses.auth.login
    mockApi.authAPI.login.mockResolvedValue(loginResponse)
    mockApi.authAPI.logout.mockResolvedValue(undefined)
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await result.current.login({
      email: 'test@example.com',
      password: 'password123',
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Then logout
    result.current.logout()

    await waitFor(() => {
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    expect(mockApi.authAPI.logout).toHaveBeenCalled()
  })

  it('should fetch current user when token exists', async () => {
    const currentUser = mockApiResponses.auth.currentUser
    mockApi.authAPI.getCurrentUser.mockResolvedValue(currentUser)
    
    // Mock localStorage to return a token
    vi.mocked(window.localStorage.getItem).mockReturnValue('mock-token')
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.user).toEqual(currentUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(mockApi.authAPI.getCurrentUser).toHaveBeenCalled()
  })

  it('should handle getCurrentUser error and logout', async () => {
    mockApi.authAPI.getCurrentUser.mockRejectedValue(new Error('Unauthorized'))
    
    // Mock localStorage to return a token
    vi.mocked(window.localStorage.getItem).mockReturnValue('mock-token')
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    // Should clear tokens on error
    expect(window.localStorage.removeItem).toHaveBeenCalled()
  })

  it('should set loading state during authentication operations', async () => {
    let resolveLogin: (value: any) => void
    const loginPromise = new Promise(resolve => {
      resolveLogin = resolve
    })
    mockApi.authAPI.login.mockReturnValue(loginPromise)
    
    const { result } = renderHook(() => useAuth(), { wrapper })

    // Start login
    const loginCall = result.current.login({
      email: 'test@example.com',
      password: 'password123',
    })

    // Should be loading
    expect(result.current.isLoading).toBe(true)

    // Resolve login
    resolveLogin!(mockApiResponses.auth.login)
    await loginCall

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
  })

  it('should throw error when useAuth is used outside AuthProvider', () => {
    expect(() => {
      renderHook(() => useAuth())
    }).toThrow('useAuth must be used within an AuthProvider')
  })

  it('should handle token refresh on API calls', async () => {
    // This would be tested with the actual API interceptors
    // For now, we just test that the context provides the expected interface
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(typeof result.current.login).toBe('function')
    expect(typeof result.current.register).toBe('function')
    expect(typeof result.current.logout).toBe('function')
    expect(typeof result.current.isLoading).toBe('boolean')
    expect(typeof result.current.isAuthenticated).toBe('boolean')
  })
})