'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AuthForm from '@/components/auth/AuthForm';
import { useAuth } from '@/lib/auth/context';
import { getErrorMessage, getValidationErrors } from '@/lib/utils/errors';
import { SigninFormData } from '@/types';

/**
 * Signin Content Component
 * Handles the signin logic and uses useSearchParams
 */
function SigninContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signin, user, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && user) {
      router.push('/dashboard');
    }
  }, [user, authLoading, router]);

  // Check for success message from signup
  useEffect(() => {
    const message = searchParams.get('message');
    if (message) {
      setSuccessMessage(message);
    }
  }, [searchParams]);

  const handleSubmit = async (data: SigninFormData) => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await signin(data.email, data.password);

      // Success - redirect to dashboard
      router.push('/dashboard');
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

  // Show loading while checking auth status
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent" aria-label="Loading"></div>
          <p className="mt-4 text-black font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if already authenticated (will redirect)
  if (user) {
    return null;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-6 sm:space-y-8">
        {/* Header */}
        <div>
          <h2 className="mt-2 sm:mt-6 text-center text-2xl sm:text-3xl font-bold tracking-tight text-black">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-700">
            Don't have an account?{' '}
            <Link
              href="/signup"
              className="font-semibold text-blue-600 hover:text-blue-700 underline"
            >
              Sign up
            </Link>
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="rounded-md bg-green-50 border border-green-200 p-4" role="alert">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-sm font-medium text-green-800">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Signin Form */}
        <div className="bg-white py-6 sm:py-8 px-4 shadow-lg rounded-lg sm:px-10 border border-gray-200">
          <AuthForm
            mode="signin"
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Signin Page
 * User authentication page with Suspense boundary
 */
export default function SigninPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-white">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent" aria-label="Loading"></div>
            <p className="mt-4 text-black font-medium">Loading...</p>
          </div>
        </div>
      }
    >
      <SigninContent />
    </Suspense>
  );
}
