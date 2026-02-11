'use client';

import { useState, FormEvent } from 'react';
import { SigninFormData, SignupFormData } from '@/types';
import { validateSigninForm, validateSignupForm } from '@/lib/utils/validation';

/**
 * AuthForm Component
 * Reusable form for both signup and signin
 */
type AuthFormProps = {
  mode: 'signin';
  onSubmit: (data: SigninFormData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
} | {
  mode: 'signup';
  onSubmit: (data: SignupFormData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
};

function EyeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );
}

function EyeSlashIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
    </svg>
  );
}

export default function AuthForm({ mode, onSubmit, loading = false, error = null }: AuthFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const isSignup = mode === 'signup';

  // Clear validation error when user starts typing
  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (validationErrors.email) {
      setValidationErrors((prev) => {
        const { email, ...rest } = prev;
        return rest;
      });
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (validationErrors.password) {
      setValidationErrors((prev) => {
        const { password, ...rest } = prev;
        return rest;
      });
    }
  };

  const handleConfirmPasswordChange = (value: string) => {
    setConfirmPassword(value);
    if (validationErrors.confirmPassword) {
      setValidationErrors((prev) => {
        const { confirmPassword, ...rest } = prev;
        return rest;
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Clear previous validation errors
    setValidationErrors({});

    // Validate form data
    const formData = isSignup
      ? { email, password, confirmPassword }
      : { email, password };

    const errors = isSignup
      ? validateSignupForm(formData as SignupFormData)
      : validateSigninForm(formData as SigninFormData);

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    // Submit form
    try {
      if (isSignup) {
        await onSubmit(formData as SignupFormData);
      } else {
        await onSubmit(formData as SigninFormData);
      }
    } catch (err) {
      // Error handling is done by parent component
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 sm:space-y-6">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-black">
          Email address
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => handleEmailChange(e.target.value)}
          placeholder="Enter your email"
          className={`mt-1 block w-full rounded-md border px-3 py-2 shadow-sm !text-black bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base ${
            validationErrors.email
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          disabled={loading}
          aria-invalid={!!validationErrors.email}
          aria-describedby={validationErrors.email ? 'email-error' : undefined}
        />
        {validationErrors.email && (
          <p id="email-error" className="mt-1 text-sm text-red-600">
            {validationErrors.email}
          </p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-black">
          Password
        </label>
        <div className="mt-1 relative">
          <input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete={isSignup ? 'new-password' : 'current-password'}
            required
            value={password}
            onChange={(e) => handlePasswordChange(e.target.value)}
            placeholder="Enter your password"
            className={`block w-full rounded-md border px-3 py-2 pr-10 shadow-sm !text-black bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base ${
              validationErrors.password
                ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                : 'border-gray-300'
            }`}
            disabled={loading}
            aria-invalid={!!validationErrors.password}
            aria-describedby={validationErrors.password ? 'password-error' : undefined}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? (
              <EyeSlashIcon className="h-5 w-5" />
            ) : (
              <EyeIcon className="h-5 w-5" />
            )}
          </button>
        </div>
        {validationErrors.password && (
          <p id="password-error" className="mt-1 text-sm text-red-600">
            {validationErrors.password}
          </p>
        )}
        {isSignup && !validationErrors.password && (
          <p className="mt-1 text-xs sm:text-sm text-gray-500">
            Password must be at least 8 characters long
          </p>
        )}
      </div>

      {/* Confirm Password Field (Signup only) */}
      {isSignup && (
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-black">
            Confirm Password
          </label>
          <div className="mt-1 relative">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(e) => handleConfirmPasswordChange(e.target.value)}
              placeholder="Confirm your password"
              className={`block w-full rounded-md border px-3 py-2 pr-10 shadow-sm !text-black bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base ${
                validationErrors.confirmPassword
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300'
              }`}
              disabled={loading}
              aria-invalid={!!validationErrors.confirmPassword}
              aria-describedby={validationErrors.confirmPassword ? 'confirm-password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
              aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
            >
              {showConfirmPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>
          {validationErrors.confirmPassword && (
            <p id="confirm-password-error" className="mt-1 text-sm text-red-600">
              {validationErrors.confirmPassword}
            </p>
          )}
        </div>
      )}

      {/* API Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-3 sm:p-4" role="alert">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <span className="flex items-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            {isSignup ? 'Creating account...' : 'Signing in...'}
          </span>
        ) : (
          <span>{isSignup ? 'Create account' : 'Sign in'}</span>
        )}
      </button>
    </form>
  );
}
