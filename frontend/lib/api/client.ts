// /**
//  * Base API Client
//  * Feature: 003-frontend-integration
//  *
//  * Centralized HTTP client with automatic token injection and error handling
//  */

// import { getEnvVar, HttpMethod, HttpStatus } from '@/types';
// import { createApiError, logError } from '@/lib/utils/errors';

// /**
//  * Get API base URL from environment
//  */
// function getApiBaseUrl(): string {
//   try {
//     return getEnvVar('NEXT_PUBLIC_API_URL');
//   } catch (error) {
//     logError('API Client', error);
//     return 'http://localhost:8000'; // Fallback for development
//   }
// }

// /**
//  * API Client class with fetch wrapper
//  */
// class ApiClientClass {
//   private baseURL: string;
//   private token: string | null = null;

//   constructor() {
//     this.baseURL = getApiBaseUrl();
//   }

//   /**
//    * Set authentication token
//    */
//   setToken(token: string | null): void {
//     this.token = token;
//   }

//   /**
//    * Get current token
//    */
//   getToken(): string | null {
//     return this.token;
//   }

//   /**
//    * Make HTTP request
//    */
//   private async request<T>(
//     endpoint: string,
//     options: {
//       method: HttpMethod;
//       body?: unknown;
//       headers?: Record<string, string>;
//       requiresAuth?: boolean;
//     }
//   ): Promise<T> {
//     const { method, body, headers = {}, requiresAuth = true } = options;

//     // Build URL
//     const url = `${this.baseURL}${endpoint}`;

//     // Build headers
//     const requestHeaders: Record<string, string> = {
//       'Content-Type': 'application/json',
//       ...headers,
//     };

//     // Add authorization header if token exists and auth is required
//     if (requiresAuth && this.token) {
//       requestHeaders['Authorization'] = `Bearer ${this.token}`;
//     }

//     // Build request options
//     const requestOptions: RequestInit = {
//       method,
//       headers: requestHeaders,
//       body: body ? JSON.stringify(body) : undefined,
//     };

//     try {
//       // Make request
//       const response = await fetch(url, requestOptions);

//       // Handle successful responses
//       if (response.ok) {
//         // Handle 204 No Content
//         if (response.status === HttpStatus.NO_CONTENT) {
//           return {} as T;
//         }

//         // Parse JSON response
//         const data = await response.json();
//         return data as T;
//       }

//       // Handle error responses
//       let errorData;
//       try {
//         errorData = await response.json();
//       } catch {
//         // If response is not JSON, use status text
//         errorData = { detail: response.statusText };
//       }

//       // Create and throw API error
//       const apiError = createApiError(
//         response.status,
//         typeof errorData.detail === 'string' ? errorData.detail : undefined,
//         errorData.detail
//       );

//       logError('API Request', {
//         url,
//         method,
//         status: response.status,
//         error: errorData,
//       });

//       throw apiError;
//     } catch (error) {
//       // Network errors or other exceptions
//       if (error && typeof error === 'object' && 'status' in error) {
//         // Already an API error, re-throw
//         throw error;
//       }

//       // Network error
//       logError('API Request', { url, method, error });
//       throw createApiError(0, 'Network error. Please check your connection.');
//     }
//   }

//   /**
//    * GET request
//    */
//   async get<T>(endpoint: string, requiresAuth = true): Promise<T> {
//     return this.request<T>(endpoint, {
//       method: 'GET',
//       requiresAuth,
//     });
//   }

//   /**
//    * POST request
//    */
//   async post<T>(endpoint: string, data?: unknown, requiresAuth = true): Promise<T> {
//     return this.request<T>(endpoint, {
//       method: 'POST',
//       body: data,
//       requiresAuth,
//     });
//   }

//   /**
//    * PUT request
//    */
//   async put<T>(endpoint: string, data?: unknown, requiresAuth = true): Promise<T> {
//     return this.request<T>(endpoint, {
//       method: 'PUT',
//       body: data,
//       requiresAuth,
//     });
//   }

//   /**
//    * DELETE request
//    */
//   async delete<T>(endpoint: string, requiresAuth = true): Promise<T> {
//     return this.request<T>(endpoint, {
//       method: 'DELETE',
//       requiresAuth,
//     });
//   }
// }

// // Export singleton instance
// export const apiClient = new ApiClientClass();








/**
 * Base API Client
 * Feature: 003-frontend-integration
 *
 * Centralized HTTP client with automatic token injection and error handling
 */

import { getEnvVar, HttpMethod, HttpStatus } from '@/types';
import { createApiError, logError } from '@/lib/utils/errors';

/**
 * Get API base URL from environment
 * Lazy-loaded to avoid initialization errors
 */
function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    console.error('NEXT_PUBLIC_API_URL is not defined, using fallback');
    return 'http://localhost:8001'; // Fallback for development
  }
  return url;
}

/**
 * API Client class with fetch wrapper
 */
class ApiClientClass {
  private token: string | null = null;

  /**
   * Get base URL (lazy-loaded)
   */
  private getBaseURL(): string {
    return getApiBaseUrl();
  }

  setToken(token: string | null): void {
    this.token = token;
    console.log('[API Client] Token updated:', token ? `${token.substring(0, 20)}...` : 'null');
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: {
      method: HttpMethod;
      body?: unknown;
      headers?: Record<string, string>;
      requiresAuth?: boolean;
    }
  ): Promise<T> {
    const { method, body, headers = {}, requiresAuth = true } = options;

    const url = `${this.getBaseURL()}${endpoint}`;

    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    if (requiresAuth && this.token) {
      requestHeaders['Authorization'] = `Bearer ${this.token}`;
    }

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
    };

    try {
      const response = await fetch(url, requestOptions);

      if (response.ok) {
        if (response.status === HttpStatus.NO_CONTENT) {
          return {} as T;
        }
        return (await response.json()) as T;
      }

      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }

      const errorMessage = typeof errorData.detail === 'string'
        ? errorData.detail
        : 'Request failed';

      console.error('[API Request Failed]', {
        url,
        method,
        status: response.status,
        message: errorMessage,
        details: errorData,
        hasToken: !!this.token,
        authRequired: requiresAuth,
      });

      // Handle 401 Unauthorized - token is invalid or missing
      if (response.status === 401) {
        // Clear token from API client
        this.setToken(null);

        // Note: The calling code should handle 401 by redirecting to signin
        // We can't import useRouter here as this is not a React component
      }

      throw createApiError(response.status, errorMessage);
    } catch (error) {
      if (error && typeof error === 'object' && 'status' in error) {
        throw error;
      }

      console.error('[API Network Error]', {
        url,
        method,
        error: error instanceof Error ? error.message : String(error),
      });
      throw createApiError(0, 'Network error. Please check your connection.');
    }
  }

  async get<T>(endpoint: string, requiresAuth = true): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', requiresAuth });
  }

  async post<T>(endpoint: string, data?: unknown, requiresAuth = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data,
      requiresAuth,
    });
  }

  async put<T>(endpoint: string, data?: unknown, requiresAuth = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data,
      requiresAuth,
    });
  }

  async delete<T>(endpoint: string, requiresAuth = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      requiresAuth,
    });
  }

  async patch<T>(endpoint: string, data?: unknown, requiresAuth = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data,
      requiresAuth,
    });
  }
}

export const apiClient = new ApiClientClass();
