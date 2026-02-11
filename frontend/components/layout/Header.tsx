import { User } from '@/types';

/**
 * Header Component
 * App header with user info and signout button
 */
interface HeaderProps {
  user: User;
  onSignout: () => void;
}

export default function Header({ user, onSignout }: HeaderProps) {
  return (
    <header className="bg-white shadow-md border-b-2 border-blue-600">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-black">
              My Tasks
            </h1>
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            <span className="text-sm text-black font-medium truncate max-w-[200px]" title={user.email}>
              {user.email}
            </span>
            <button
              onClick={onSignout}
              className="rounded-md bg-blue-600 px-3 py-1.5 sm:px-4 sm:py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors shadow-sm"
              aria-label="Sign out"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
