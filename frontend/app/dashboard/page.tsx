'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/context';
import { Task, UpdateTaskData } from '@/types';
import { getTasks, createTask, updateTask, deleteTask } from '@/lib/api/tasks';
import { getErrorMessage, handleApiError } from '@/lib/utils/errors';
import TaskForm from '@/components/tasks/TaskForm';
import TaskList from '@/components/tasks/TaskList';

/**
 * Dashboard Page
 * Main application page for task management
 */
export default function DashboardPage() {
  const { user, signout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  /**
   * Fetch tasks on mount
   */
  useEffect(() => {
    fetchTasks();
  }, []);

  /**
   * Fetch all tasks
   */
  const fetchTasks = async () => {
    setLoading(true);
    setError(null);

    try {
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      const errorResult = handleApiError(err);
      setError(errorResult.message);

      // Redirect if unauthorized
      if (errorResult.shouldRedirect) {
        signout();
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new task
   */
  const handleCreateTask = async (data: { title: string }) => {
    setCreateLoading(true);
    setCreateError(null);

    try {
      const newTask = await createTask(data);
      // Add to list immediately (optimistic update)
      setTasks((prev) => [newTask, ...prev]);
    } catch (err) {
      const errorResult = handleApiError(err);
      setCreateError(errorResult.message);

      // Redirect if unauthorized
      if (errorResult.shouldRedirect) {
        signout();
      }

      throw err; // Re-throw to prevent form reset
    } finally {
      setCreateLoading(false);
    }
  };

  /**
   * Update a task
   */
  const handleUpdateTask = async (id: string, data: UpdateTaskData) => {
    // Optimistic update
    const previousTasks = [...tasks];
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, ...data, updated_at: new Date().toISOString() } : task
      )
    );

    try {
      const updatedTask = await updateTask(id, data);
      // Update with server response
      setTasks((prev) => prev.map((task) => (task.id === id ? updatedTask : task)));
    } catch (err) {
      // Revert on error
      setTasks(previousTasks);

      const errorResult = handleApiError(err);
      alert(errorResult.message); // Simple error display for now

      // Redirect if unauthorized
      if (errorResult.shouldRedirect) {
        signout();
      }

      throw err;
    }
  };

  /**
   * Delete a task
   */
  const handleDeleteTask = async (id: string) => {
    // Optimistic update
    const previousTasks = [...tasks];
    setTasks((prev) => prev.filter((task) => task.id !== id));

    try {
      await deleteTask(id);
    } catch (err) {
      // Revert on error
      setTasks(previousTasks);

      const errorResult = handleApiError(err);
      alert(errorResult.message); // Simple error display for now

      // Redirect if unauthorized
      if (errorResult.shouldRedirect) {
        signout();
      }

      throw err;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b-2 border-blue-600">
        <div className="mx-auto max-w-7xl px-3 py-3 sm:px-6 sm:py-6 lg:px-8 flex justify-between items-center gap-2">
          <h1 className="text-xl sm:text-3xl font-bold tracking-tight text-black truncate">
            My Tasks
          </h1>
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
            <h2 className="text-base sm:text-lg font-semibold text-black mb-3 sm:mb-4">
              Create New Task
            </h2>
            <TaskForm
              onSubmit={handleCreateTask}
              loading={createLoading}
              error={createError}
            />
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
              onUpdate={handleUpdateTask}
              onDelete={handleDeleteTask}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
