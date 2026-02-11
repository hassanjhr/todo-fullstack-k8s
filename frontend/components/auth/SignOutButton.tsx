'use client';

import { useAuth } from '@/lib/auth/context';

/**
 * SignOutButton Component
 * Button to sign out the current user
 */
export default function SignOutButton() {
  const { signout } = useAuth();

  return (
    <button
      onClick={signout}
      className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
    >
      Sign out
    </button>
  );
}
