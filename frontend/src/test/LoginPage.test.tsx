import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginPage } from '../pages/LoginPage'
import { 
  renderWithoutAuth, 
  mockUnauthenticatedContextValue,
  mockApiResponses 
} from '../test/utils'

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  }
})

describe('LoginPage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render login form correctly', () => {
    renderWithoutAuth(<LoginPage />)

    expect(screen.getByText('Sign in to Analytics Bot')).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    expect(screen.getByText(/create a new account/i)).toBeInTheDocument()
  })

  it('should show validation errors for empty fields', async () => {
    renderWithoutAuth(<LoginPage />)

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })
  })

  it('should show validation error for invalid email format', async () => {
    renderWithoutAuth(<LoginPage />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'invalid-email')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
    })
  })

  it('should show validation error for short password', async () => {
    renderWithoutAuth(<LoginPage />)

    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(passwordInput, '123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
    })
  })

  it('should toggle password visibility', async () => {
    renderWithoutAuth(<LoginPage />)

    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement
    const toggleButton = screen.getByRole('button', { name: '' }) // Eye icon button

    expect(passwordInput.type).toBe('password')

    await user.click(toggleButton)
    expect(passwordInput.type).toBe('text')

    await user.click(toggleButton)
    expect(passwordInput.type).toBe('password')
  })

  it('should call login function on successful form submission', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
    }

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })

  it('should navigate to dashboard after successful login', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
    }

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
    })
  })

  it('should navigate to return URL after login if provided', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
    }

    // Mock useLocation to return a state with from
    vi.doMock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom')
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useLocation: () => ({ 
          state: { from: { pathname: '/projects' } } 
        }),
        Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
          <a href={to}>{children}</a>
        ),
      }
    })

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/projects', { replace: true })
    })
  })

  it('should handle login error gracefully', async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
    }

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'wrongpassword')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled()
    })

    // Should not navigate on error
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('should show loading state during login', async () => {
    let resolveLogin: () => void
    const loginPromise = new Promise<void>(resolve => {
      resolveLogin = resolve
    })
    const mockLogin = vi.fn().mockReturnValue(loginPromise)
    
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
      isLoading: true,
    }

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    
    // Button should show loading state
    expect(submitButton).toBeDisabled()
    
    // Should show loading spinner instead of text
    expect(screen.queryByText('Sign in')).not.toBeInTheDocument()
  })

  it('should have proper accessibility attributes', () => {
    renderWithoutAuth(<LoginPage />)

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const form = screen.getByRole('form', { name: '' })

    expect(emailInput).toHaveAttribute('type', 'email')
    expect(emailInput).toHaveAttribute('autoComplete', 'email')
    expect(passwordInput).toHaveAttribute('type', 'password')
    expect(passwordInput).toHaveAttribute('autoComplete', 'current-password')
    expect(form).toBeInTheDocument()
  })

  it('should link to registration page', () => {
    renderWithoutAuth(<LoginPage />)

    const registerLink = screen.getByText(/create a new account/i)
    expect(registerLink).toHaveAttribute('href', '/register')
  })

  it('should have forgot password link', () => {
    renderWithoutAuth(<LoginPage />)

    const forgotPasswordLink = screen.getByText(/forgot your password/i)
    expect(forgotPasswordLink).toBeInTheDocument()
  })

  it('should handle form submission with Enter key', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    const authContextValue = {
      ...mockUnauthenticatedContextValue,
      login: mockLogin,
    }

    renderWithoutAuth(<LoginPage />, { authContextValue })

    const emailInput = screen.getByLabelText(/email address/i)
    const passwordInput = screen.getByLabelText(/password/i)

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })
})