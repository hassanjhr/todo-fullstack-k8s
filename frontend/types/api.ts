/**
 * API Response Type Definitions
 * Feature: 003-frontend-integration
 */

export interface ApiResponse<T> {
  data: T;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: ValidationError[];
}

export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  detail: string | ValidationError[];
}

export function hasValidationErrors(error: ErrorResponse): error is { detail: ValidationError[] } {
  return Array.isArray(error.detail);
}
