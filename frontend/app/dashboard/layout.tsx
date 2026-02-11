'use client';

import { ReactNode } from 'react';
import { useRequireAuth } from '@/lib/auth/hooks';

/**
 * Dashboard Layout
 * Protected layout that requires authentication
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading } = useRequireAuth();

  // Show loading state
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (redirect handled by hook)
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {children}
    </div>
  );
}
