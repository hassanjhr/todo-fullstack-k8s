'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthContextValue } from '@/types';
import { signin as signinApi, signup as signupApi } from '@/lib/api/auth';
import { saveToken, getToken, saveUser, getUser, clearAuthData } from './token';
import { apiClient } from '@/lib/api/client';

/**
 * Auth Context
 * Provides authentication state and actions throughout the app
 */
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Auth Provider Component
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  /**
   * Load token and user from localStorage on mount
   */
  const loadToken = () => {
    console.log('[Auth Context] Loading token from localStorage...');
    const storedToken = getToken();
    const storedUser = getUser();

    if (storedToken && storedUser) {
      console.log('[Auth Context] Token found, setting in API client');
      setToken(storedToken);
      setUser(storedUser);
      apiClient.setToken(storedToken);
    } else {
      console.log('[Auth Context] No token found in localStorage');
    }

    setLoading(false);
  };

  /**
   * Sign up a new user
   */
  const signup = async (email: string, password: string) => {
    await signupApi(email, password);
    // Note: signup doesn't return token, user must signin after
  };

  /**
   * Sign in an existing user
   */
  const signin = async (email: string, password: string) => {
    console.log('[Auth Context] Signing in...');
    const response = await signinApi(email, password);

    console.log('[Auth Context] Signin successful, saving token and user');

    // Save token and user to localStorage
    saveToken(response.token);
    saveUser(response.user);

    // Update state
    setToken(response.token);
    setUser(response.user);

    // CRITICAL: Set token in API client so all subsequent requests include it
    console.log('[Auth Context] Setting token in API client');
    apiClient.setToken(response.token);

    console.log('[Auth Context] Token set, user authenticated');
  };

  /**
   * Sign out the current user
   *
   * JWT-based auth is stateless, so signout is purely client-side:
   * 1. Clear token and user from localStorage
   * 2. Clear token from API client
   * 3. Update React state
   * 4. Redirect to signin page
   */
  const signout = () => {
    console.log('[Auth Context] Signing out (client-side only)...');

    // Clear authentication data from localStorage
    clearAuthData();

    // Clear React state
    setToken(null);
    setUser(null);

    // Clear token from API client (important!)
    apiClient.setToken(null);

    console.log('[Auth Context] Signout complete, redirecting to signin');

    // Redirect to signin page
    router.push('/signin');
  };

  /**
   * Load token on mount
   */
  useEffect(() => {
    loadToken();
  }, []);

  const value: AuthContextValue = {
    user,
    token,
    loading,
    signin,
    signup,
    signout,
    loadToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
