'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/context';
import { Task, UpdateTaskData, TaskFilters } from '@/types';
import { getTasks, createTask, updateTask, deleteTask } from '@/lib/api/tasks';
import { handleApiError } from '@/lib/utils/errors';
import TaskForm from '@/components/tasks/TaskForm';
import TaskList from '@/components/tasks/TaskList';
import TaskFilter from '@/components/tasks/TaskFilter';

const DEFAULT_FILTERS: TaskFilters = { sort_by: 'created_at', sort_order: 'desc' };

export default function DashboardPage() {
  const { user, signout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TaskFilters>(DEFAULT_FILTERS);
  const [searchQuery, setSearchQuery] = useState('');
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch when filters change
  useEffect(() => {
    fetchTasks(filters);
  }, [filters]);

  // Debounce search input
  useEffect(() => {
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
    searchDebounceRef.current = setTimeout(() => {
      setFilters((prev) => ({ ...prev, q: searchQuery || undefined, cursor: undefined }));
    }, 300);
    return () => { if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current); };
  }, [searchQuery]);

  const fetchTasks = async (f: TaskFilters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getTasks(f);
      setTasks(response.tasks);
      setHasMore(response.has_more);
      setNextCursor(response.next_cursor ?? undefined);
    } catch (err) {
      const errorResult = handleApiError(err);
      setError(errorResult.message);
      if (errorResult.shouldRedirect) signout();
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = async () => {
    if (!nextCursor || loadingMore) return;
    setLoadingMore(true);
    try {
      const response = await getTasks({ ...filters, cursor: nextCursor });
      setTasks((prev) => [...prev, ...response.tasks]);
      setHasMore(response.has_more);
      setNextCursor(response.next_cursor ?? undefined);
    } catch {
      // Silently fail on pagination error
    } finally {
      setLoadingMore(false);
    }
  };

  const handleFilterChange = (newFilters: TaskFilters) => {
    // Reset cursor on filter change (new result set)
    setFilters({ ...newFilters, cursor: undefined });
  };

  const handleCreateTask = async (data: { title: string; description?: string; priority: string; tags: string[] }) => {
    setCreateLoading(true);
    setCreateError(null);
    try {
      const newTask = await createTask(data);
      setTasks((prev) => [newTask, ...prev]);
    } catch (err) {
      const errorResult = handleApiError(err);
      setCreateError(errorResult.message);
      if (errorResult.shouldRedirect) signout();
      throw err;
    } finally {
      setCreateLoading(false);
    }
  };

  const handleUpdateTask = async (id: string, data: UpdateTaskData) => {
    const previousTasks = [...tasks];
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, ...data, updated_at: new Date().toISOString() } : task
      )
    );
    try {
      const updatedTask = await updateTask(id, data);
      setTasks((prev) => prev.map((task) => (task.id === id ? updatedTask : task)));
    } catch (err) {
      setTasks(previousTasks);
      const errorResult = handleApiError(err);
      alert(errorResult.message);
      if (errorResult.shouldRedirect) signout();
      throw err;
    }
  };

  const handleDeleteTask = async (id: string) => {
    const previousTasks = [...tasks];
    setTasks((prev) => prev.filter((task) => task.id !== id));
    try {
      await deleteTask(id);
    } catch (err) {
      setTasks(previousTasks);
      const errorResult = handleApiError(err);
      alert(errorResult.message);
      if (errorResult.shouldRedirect) signout();
      throw err;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b-2 border-blue-600">
        <div className="mx-auto max-w-7xl px-3 py-3 sm:px-6 sm:py-6 lg:px-8 flex justify-between items-center gap-2">
          <h1 className="text-xl sm:text-3xl font-bold tracking-tight text-black truncate">My Tasks</h1>
          <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
            <button
              onClick={() => router.push('/dashboard/chat')}
              className="rounded-md bg-green-600 px-2.5 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 shadow-sm transition-colors"
            >
              AI Chat
            </button>
            <span className="text-sm text-black font-medium hidden sm:inline truncate max-w-[150px]">{user?.email}</span>
            <button
              onClick={signout}
              className="rounded-md bg-blue-600 px-2.5 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 shadow-sm transition-colors"
              aria-label="Sign out"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-3 py-4 sm:px-6 sm:py-8 lg:px-8">
        <div className="space-y-4 sm:space-y-6">
          {/* Task Creation Form */}
          <div className="bg-white shadow-md sm:rounded-lg p-4 sm:p-6 border border-gray-200">
            <h2 className="text-base sm:text-lg font-semibold text-black mb-3 sm:mb-4">Create New Task</h2>
            <TaskForm onSubmit={handleCreateTask} loading={createLoading} error={createError} />
          </div>

          {/* Search + Filter */}
          <div className="space-y-2">
            {/* Search bar */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-gray-300 pl-9 pr-8 py-2 text-sm bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <svg className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
              </svg>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-2 text-gray-400 hover:text-gray-600 text-lg leading-none"
                >
                  ×
                </button>
              )}
            </div>
            <TaskFilter filters={filters} onChange={handleFilterChange} />
          </div>

          {/* Task List */}
          <div className="bg-white shadow-md sm:rounded-lg p-4 sm:p-6 border border-gray-200">
            <h2 className="text-base sm:text-lg font-semibold text-black mb-3 sm:mb-4">
              Your Tasks ({tasks.length})
            </h2>
            <TaskList
              tasks={tasks}
              loading={loading}
              error={error}
              hasMore={hasMore}
              loadingMore={loadingMore}
              onUpdate={handleUpdateTask}
              onDelete={handleDeleteTask}
              onLoadMore={handleLoadMore}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
