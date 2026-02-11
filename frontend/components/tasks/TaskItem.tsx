'use client';

import { useState } from 'react';
import { Task, UpdateTaskData } from '@/types';

/**
 * TaskItem Component
 * Individual task item with edit, toggle completion, and delete functionality
 */
interface TaskItemProps {
  task: Task;
  onUpdate: (data: UpdateTaskData) => Promise<void>;
  onDelete: () => Promise<void>;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title || '');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showCompletionNotification, setShowCompletionNotification] = useState(false);

  const handleToggleComplete = async () => {
    const willBeCompleted = !task.is_completed;
    setIsUpdating(true);
    try {
      await onUpdate({ is_completed: willBeCompleted });
      // Show completion notification only when marking as completed
      if (willBeCompleted) {
        setShowCompletionNotification(true);
        // Auto-hide after 3 seconds
        setTimeout(() => {
          setShowCompletionNotification(false);
        }, 3000);
      }
    } catch (error) {
      // Error handled by parent
    } finally {
      setIsUpdating(false);
    }
  };

  const handleSaveEdit = async () => {
    if (editTitle.trim() === '') {
      return;
    }

    if (editTitle === task.title) {
      setIsEditing(false);
      return;
    }

    setIsUpdating(true);
    try {
      await onUpdate({ title: editTitle });
      setIsEditing(false);
    } catch (error) {
      // Revert on error
      setEditTitle(task.title);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete();
      setShowDeleteConfirm(false);
    } catch (error) {
      // Error handled by parent
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div className="p-3 sm:p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
      <div className="flex items-start sm:items-center gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggleComplete}
          disabled={isUpdating || isDeleting}
          className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50 cursor-pointer mt-0.5 sm:mt-0 flex-shrink-0"
          aria-label={`Mark "${task.title}" as ${task.is_completed ? 'incomplete' : 'complete'}`}
        />

        {/* Task Title */}
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <input
              type="text"
              value={editTitle || ''}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSaveEdit();
                } else if (e.key === 'Escape') {
                  handleCancelEdit();
                }
              }}
              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white !text-black placeholder-gray-400 text-sm"
              disabled={isUpdating}
              autoFocus
            />
          ) : (
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <p
                  className={`text-sm font-medium break-words ${
                    task.is_completed ? 'line-through text-gray-500' : 'text-gray-900'
                  }`}
                >
                  {task.title}
                </p>
                {task.is_completed && (
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    ✓ Done
                  </span>
                )}
              </div>
              {task.description && (
                <p
                  className={`text-xs mt-1 break-words ${
                    task.is_completed ? 'line-through text-gray-400' : 'text-gray-600'
                  }`}
                >
                  {task.description}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Actions - visible on sm+ screens */}
        <div className="hidden sm:flex items-center gap-2 flex-shrink-0">
          {isEditing ? (
            <>
              <button
                onClick={handleSaveEdit}
                disabled={isUpdating}
                className="text-sm text-green-600 hover:text-green-700 disabled:opacity-50"
                aria-label="Save changes"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                disabled={isUpdating}
                className="text-sm text-gray-600 hover:text-gray-700 disabled:opacity-50"
                aria-label="Cancel editing"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                disabled={isUpdating || isDeleting}
                className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
                aria-label={`Edit "${task.title}"`}
              >
                Edit
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                disabled={isUpdating || isDeleting}
                className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
                aria-label={`Delete "${task.title}"`}
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {/* Actions - mobile row below content */}
      <div className="flex sm:hidden items-center gap-3 mt-2 ml-8">
        {isEditing ? (
          <>
            <button
              onClick={handleSaveEdit}
              disabled={isUpdating}
              className="text-xs font-medium text-green-600 hover:text-green-700 disabled:opacity-50"
              aria-label="Save changes"
            >
              Save
            </button>
            <button
              onClick={handleCancelEdit}
              disabled={isUpdating}
              className="text-xs font-medium text-gray-600 hover:text-gray-700 disabled:opacity-50"
              aria-label="Cancel editing"
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setIsEditing(true)}
              disabled={isUpdating || isDeleting}
              className="text-xs font-medium text-blue-600 hover:text-blue-700 disabled:opacity-50"
              aria-label={`Edit "${task.title}"`}
            >
              Edit
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isUpdating || isDeleting}
              className="text-xs font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
              aria-label={`Delete "${task.title}"`}
            >
              Delete
            </button>
          </>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Delete Task</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to delete "{task.title}"? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Completion Notification */}
      {showCompletionNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
            <div className="flex items-center justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 text-center mb-2">Task Completed! 🎉</h3>
            <p className="text-sm text-gray-600 text-center mb-4">
              Your task, <span className="font-semibold">"{task.title}"</span>, is completed.
            </p>
            <div className="flex justify-center">
              <button
                onClick={() => setShowCompletionNotification(false)}
                className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors"
              >
                Great!
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
