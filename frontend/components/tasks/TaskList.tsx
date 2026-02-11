'use client';

import { Task, UpdateTaskData } from '@/types';
import TaskItem from './TaskItem';

/**
 * TaskList Component
 * Displays a list of tasks with loading and empty states
 */
interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  error?: string | null;
  onUpdate: (id: string, data: UpdateTaskData) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export default function TaskList({ tasks, loading = false, error = null, onUpdate, onDelete }: TaskListProps) {
  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4" role="alert">
        <p className="text-sm text-red-800">{error}</p>
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-blue-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-black">No tasks yet</h3>
        <p className="mt-1 text-sm text-gray-600">Get started by creating a new task above.</p>
      </div>
    );
  }

  // Task list
  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={(data) => onUpdate(task.id, data)}
          onDelete={() => onDelete(task.id)}
        />
      ))}
    </div>
  );
}
