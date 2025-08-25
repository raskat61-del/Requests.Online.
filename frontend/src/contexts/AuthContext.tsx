import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { authAPI, tokenManager, User, LoginData, RegisterData } from '../lib/api'
import { toast } from 'react-toastify'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    !!tokenManager.getAccessToken()
  )
  const queryClient = useQueryClient()

  // Get current user query
  const {
    data: user,
    isLoading,
    error,
  } = useQuery(
    'currentUser',
    authAPI.getCurrentUser,
    {
      enabled: isAuthenticated,
      retry: false,
      onError: () => {
        // If fetching user fails, clear tokens and set as unauthenticated
        tokenManager.clearTokens()
        setIsAuthenticated(false)
      },
    }
  )

  // Login mutation
  const loginMutation = useMutation(authAPI.login, {
    onSuccess: (data) => {
      tokenManager.setTokens(data.access_token, data.refresh_token)
      setIsAuthenticated(true)
      queryClient.setQueryData('currentUser', data.user)
      toast.success('Successfully logged in!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
    },
  })

  // Register mutation
  const registerMutation = useMutation(authAPI.register, {
    onSuccess: (data) => {
      tokenManager.setTokens(data.access_token, data.refresh_token)
      setIsAuthenticated(true)
      queryClient.setQueryData('currentUser', data.user)
      toast.success('Successfully registered!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
    },
  })

  // Logout mutation
  const logoutMutation = useMutation(authAPI.logout, {
    onSettled: () => {
      tokenManager.clearTokens()
      setIsAuthenticated(false)
      queryClient.clear()
      toast.success('Successfully logged out')
    },
  })

  const login = async (data: LoginData) => {
    await loginMutation.mutateAsync(data)
  }

  const register = async (data: RegisterData) => {
    await registerMutation.mutateAsync(data)
  }

  const logout = () => {
    logoutMutation.mutate()
  }

  // Effect to check authentication status on mount
  useEffect(() => {
    const token = tokenManager.getAccessToken()
    if (token && !isAuthenticated) {
      setIsAuthenticated(true)
    } else if (!token && isAuthenticated) {
      setIsAuthenticated(false)
    }
  }, [isAuthenticated])

  // Effect to handle authentication errors
  useEffect(() => {
    if (error && isAuthenticated) {
      tokenManager.clearTokens()
      setIsAuthenticated(false)
    }
  }, [error, isAuthenticated])

  const value: AuthContextType = {
    user: user || null,
    isLoading: isLoading || loginMutation.isLoading || registerMutation.isLoading,
    isAuthenticated,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}