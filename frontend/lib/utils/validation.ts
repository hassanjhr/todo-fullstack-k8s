/**
 * Form Validation Utilities
 * Feature: 003-frontend-integration
 *
 * Client-side validation helpers for forms
 */

/**
 * Email validation regex (RFC 5322 simplified)
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validation result
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate email format
 */
export function validateEmail(email: string): ValidationResult {
  if (!email || email.trim() === '') {
    return {
      isValid: false,
      error: 'Email is required',
    };
  }

  if (!EMAIL_REGEX.test(email)) {
    return {
      isValid: false,
      error: 'Please enter a valid email address',
    };
  }

  return { isValid: true };
}

/**
 * Validate password requirements
 */
export function validatePassword(password: string): ValidationResult {
  if (!password || password.trim() === '') {
    return {
      isValid: false,
      error: 'Password is required',
    };
  }

  if (password.length < 8) {
    return {
      isValid: false,
      error: 'Password must be at least 8 characters long',
    };
  }

  return { isValid: true };
}

/**
 * Validate password confirmation matches
 */
export function validatePasswordConfirmation(
  password: string,
  confirmPassword: string
): ValidationResult {
  if (!confirmPassword || confirmPassword.trim() === '') {
    return {
      isValid: false,
      error: 'Please confirm your password',
    };
  }

  if (password !== confirmPassword) {
    return {
      isValid: false,
      error: 'Passwords do not match',
    };
  }

  return { isValid: true };
}

/**
 * Validate task title
 */
export function validateTaskTitle(title: string): ValidationResult {
  if (!title || title.trim() === '') {
    return {
      isValid: false,
      error: 'Task title is required',
    };
  }

  if (title.length > 200) {
    return {
      isValid: false,
      error: 'Task title is too long (maximum 200 characters)',
    };
  }

  return { isValid: true };
}

/**
 * Validate task description
 */
export function validateTaskDescription(description?: string): ValidationResult {
  if (!description || description.trim() === '') {
    return { isValid: true }; // Description is optional
  }

  if (description.length > 2000) {
    return {
      isValid: false,
      error: 'Description is too long (maximum 2000 characters)',
    };
  }

  return { isValid: true };
}

/**
 * Validate required field
 */
export function validateRequired(value: string, fieldName: string): ValidationResult {
  if (!value || value.trim() === '') {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  return { isValid: true };
}

/**
 * Sanitize user input to prevent XSS
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Validate signup form data
 */
export function validateSignupForm(data: {
  email: string;
  password: string;
  confirmPassword: string;
}): Record<string, string> {
  const errors: Record<string, string> = {};

  const emailValidation = validateEmail(data.email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error!;
  }

  const passwordValidation = validatePassword(data.password);
  if (!passwordValidation.isValid) {
    errors.password = passwordValidation.error!;
  }

  const confirmValidation = validatePasswordConfirmation(
    data.password,
    data.confirmPassword
  );
  if (!confirmValidation.isValid) {
    errors.confirmPassword = confirmValidation.error!;
  }

  return errors;
}

/**
 * Validate signin form data
 */
export function validateSigninForm(data: {
  email: string;
  password: string;
}): Record<string, string> {
  const errors: Record<string, string> = {};

  const emailValidation = validateEmail(data.email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error!;
  }

  const passwordValidation = validateRequired(data.password, 'Password');
  if (!passwordValidation.isValid) {
    errors.password = passwordValidation.error!;
  }

  return errors;
}

/**
 * Validate task form data
 */
export function validateTaskForm(data: { title: string; description?: string }): Record<string, string> {
  const errors: Record<string, string> = {};

  const titleValidation = validateTaskTitle(data.title);
  if (!titleValidation.isValid) {
    errors.title = titleValidation.error!;
  }

  const descriptionValidation = validateTaskDescription(data.description);
  if (!descriptionValidation.isValid) {
    errors.description = descriptionValidation.error!;
  }

  return errors;
}
