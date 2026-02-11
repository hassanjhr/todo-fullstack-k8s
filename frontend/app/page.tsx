'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

/**
 * Landing Page
 * Shows welcome screen with Sign In / Sign Up options
 * Redirects authenticated users to dashboard
 */
export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user has token in localStorage
    const token = localStorage.getItem('auth_token');

    if (token) {
      // User is authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // User is not authenticated, show landing page
      setIsLoading(false);
    }
  }, [router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show landing page with Sign In / Sign Up options
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 px-4 py-8 sm:py-4">
      <div className="w-full max-w-md text-center">
        {/* App Logo/Icon */}
        <div className="mb-6 sm:mb-8">
          <div className="mx-auto flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-full bg-blue-600 text-white shadow-xl border-4 border-white">
            <svg
              className="h-8 w-8 sm:h-10 sm:w-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>
        </div>

        {/* Hero Text */}
        <h1 className="mb-3 sm:mb-4 text-3xl sm:text-4xl font-bold text-black">
          Todo App
        </h1>
        <p className="mb-6 sm:mb-8 text-base sm:text-lg text-gray-700">
          Organize your tasks and boost your productivity
        </p>

        {/* Action Buttons */}
        <div className="space-y-3 sm:space-y-4">
          <Link
            href="/signin"
            className="block w-full rounded-lg bg-blue-600 px-6 py-2.5 sm:py-3 text-center font-semibold text-white shadow-lg transition-all hover:bg-blue-700 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="Sign in to your account"
          >
            Sign In
          </Link>

          <Link
            href="/signup"
            className="block w-full rounded-lg border-2 border-blue-600 bg-white px-6 py-2.5 sm:py-3 text-center font-semibold text-blue-600 shadow-lg transition-all hover:bg-blue-50 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="Create a new account"
          >
            Sign Up
          </Link>
        </div>

        {/* Features */}
        <div className="mt-8 sm:mt-12 space-y-2.5 sm:space-y-3 text-sm text-gray-700">
          <div className="flex items-center justify-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Create and manage tasks</span>
          </div>
          <div className="flex items-center justify-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Track completion status</span>
          </div>
          <div className="flex items-center justify-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Secure and private</span>
          </div>
        </div>
      </div>
    </div>
  );
}
