'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AuthForm from '@/components/auth/AuthForm';
import { signup } from '@/lib/api/auth';
import { getErrorMessage, getValidationErrors } from '@/lib/utils/errors';
import { SignupFormData } from '@/types';

/**
 * Signup Page
 * User registration page
 */
export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: SignupFormData) => {
    setLoading(true);
    setError(null);

    try {
      await signup(data.email, data.password);

      // Success - redirect to signin with success message
      router.push('/signin?message=Account created successfully. Please sign in.');
    } catch (err) {
      // Handle validation errors
      const validationErrors = getValidationErrors(err);
      if (Object.keys(validationErrors).length > 0) {
        // Show first validation error
        const firstError = Object.values(validationErrors)[0];
        setError(firstError);
      } else {
        // Show generic error message
        setError(getErrorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-6 sm:space-y-8">
        {/* Header */}
        <div>
          <h2 className="mt-2 sm:mt-6 text-center text-2xl sm:text-3xl font-bold tracking-tight text-black">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-700">
            Already have an account?{' '}
            <Link
              href="/signin"
              className="font-semibold text-blue-600 hover:text-blue-700 underline"
            >
              Sign in
            </Link>
          </p>
        </div>

        {/* Signup Form */}
        <div className="bg-white py-6 sm:py-8 px-4 shadow-lg rounded-lg sm:px-10 border border-gray-200">
          <AuthForm
            mode="signup"
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        </div>
      </div>
    </div>
  );
}
