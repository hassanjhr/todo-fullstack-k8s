/**
 * TypeScript Type Definitions for Frontend Application
 *
 * Feature: 003-frontend-integration
 * Date: 2026-02-07
 *
 * These types mirror the backend API contracts and provide type safety
 * throughout the frontend application.
 */

// ============================================================================
// User Types
// ============================================================================

/**
 * Represents an authenticated user in the application
 */
export interface User {
  id: number;
  email: string;
}

/**
 * User credentials for authentication
 */
export interface UserCredentials {
  email: string;
  password: string;
}

// ============================================================================
// Task Types
// ============================================================================

/**
 * Represents a todo task owned by a user
 */
export interface Task {
  id: number;
  title: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

/**
 * Data required to create a new task
 */
export interface CreateTaskData {
  title: string;
}

/**
 * Data for updating an existing task (partial update)
 */
export interface UpdateTaskData {
  title?: string;
  completed?: boolean;
}

// ============================================================================
// Authentication Types
// ============================================================================

/**
 * JWT authentication token
 */
export interface AuthToken {
  token: string;
  expiresAt?: number;
}

/**
 * Response from signin endpoint
 */
export interface SigninResponse {
  token: string;
  user: User;
}

/**
 * Response from signup endpoint
 */
export interface SignupResponse {
  message: string;
}

// ============================================================================
// Form Types
// ============================================================================

/**
 * Signup form data (includes confirm password for client-side validation)
 */
export interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

/**
 * Signin form data
 */
export interface SigninFormData {
  email: string;
  password: string;
}

/**
 * Task creation/edit form data
 */
export interface TaskFormData {
  title: string;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Generic successful API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
}

/**
 * API error response
 */
export interface ApiError {
  message: string;
  status: number;
  details?: ValidationError[];
}

/**
 * Validation error from backend (422 responses)
 */
export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

/**
 * Standard error response from backend
 */
export interface ErrorResponse {
  detail: string | ValidationError[];
}

// ============================================================================
// Auth Context Types
// ============================================================================

/**
 * Authentication context state
 */
export interface AuthContextState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

/**
 * Authentication context actions
 */
export interface AuthContextActions {
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  signout: () => void;
  loadToken: () => void;
}

/**
 * Complete auth context value
 */
export interface AuthContextValue extends AuthContextState, AuthContextActions {}

// ============================================================================
// Component Props Types
// ============================================================================

/**
 * Props for AuthForm component
 */
export interface AuthFormProps {
  mode: 'signin' | 'signup';
  onSubmit: (data: SigninFormData | SignupFormData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

/**
 * Props for TaskForm component
 */
export interface TaskFormProps {
  onSubmit: (data: TaskFormData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

/**
 * Props for TaskList component
 */
export interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  error?: string | null;
  onUpdate: (id: number, data: UpdateTaskData) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

/**
 * Props for TaskItem component
 */
export interface TaskItemProps {
  task: Task;
  onUpdate: (data: UpdateTaskData) => Promise<void>;
  onDelete: () => Promise<void>;
}

/**
 * Props for LoadingSpinner component
 */
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Props for ErrorMessage component
 */
export interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

/**
 * Props for Button component
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
  fullWidth?: boolean;
}

/**
 * Props for Header component
 */
export interface HeaderProps {
  user: User;
  onSignout: () => void;
}

/**
 * Props for Container component
 */
export interface ContainerProps {
  children: React.ReactNode;
  className?: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Type guard to check if response is an API error
 */
export function isApiError(response: unknown): response is ApiError {
  return (
    typeof response === 'object' &&
    response !== null &&
    'message' in response &&
    'status' in response
  );
}

/**
 * Type guard to check if data is a Task
 */
export function isTask(data: unknown): data is Task {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'title' in data &&
    'completed' in data &&
    'user_id' in data
  );
}

/**
 * Type guard to check if data is a User
 */
export function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'email' in data
  );
}

/**
 * Type guard to check if error response contains validation errors
 */
export function hasValidationErrors(error: ErrorResponse): error is { detail: ValidationError[] } {
  return Array.isArray(error.detail);
}

// ============================================================================
// HTTP Status Codes
// ============================================================================

/**
 * Common HTTP status codes used in the application
 */
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  UNPROCESSABLE_ENTITY = 422,
  TOO_MANY_REQUESTS = 429,
  INTERNAL_SERVER_ERROR = 500,
  SERVICE_UNAVAILABLE = 503,
}

// ============================================================================
// Environment Variables
// ============================================================================

/**
 * Type-safe environment variable access
 */
export interface EnvironmentVariables {
  NEXT_PUBLIC_API_URL: string;
}

/**
 * Get environment variable with type safety
 */
export function getEnvVar(key: keyof EnvironmentVariables): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Environment variable ${key} is not defined`);
  }
  return value;
}

// ============================================================================
// API Client Types
// ============================================================================

/**
 * HTTP methods supported by API client
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

/**
 * Request options for API client
 */
export interface RequestOptions {
  method: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  token?: string | null;
}

/**
 * API client interface
 */
export interface ApiClient {
  get<T>(endpoint: string): Promise<T>;
  post<T>(endpoint: string, data?: unknown): Promise<T>;
  put<T>(endpoint: string, data?: unknown): Promise<T>;
  delete<T>(endpoint: string): Promise<T>;
}
