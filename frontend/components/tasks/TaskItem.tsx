'use client';

import { useState } from 'react';
import { Task, UpdateTaskData } from '@/types';

// Priority badge styling
const PRIORITY_STYLES: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
};

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
                {/* Priority badge */}
                {task.priority && (
                  <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${PRIORITY_STYLES[task.priority] ?? PRIORITY_STYLES.medium}`}>
                    {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                  </span>
                )}
                {/* Overdue indicator */}
                {task.is_overdue && (
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-700">
                    Overdue
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
              {/* Tag chips */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1.5">
                  {task.tags.map((tag) => (
                    <span key={tag} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 border border-blue-200">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              {/* Due date */}
              {task.due_date && (
                <p className={`text-xs mt-1 flex items-center gap-1 ${task.is_overdue ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
                  {task.is_overdue && (
                    <svg className="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  )}
                  Due: {new Date(task.due_date).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
                </p>
              )}
              {/* Recurrence badge */}
              {task.recurrence_rule && (
                <span className="inline-flex items-center gap-0.5 mt-1 text-xs text-purple-600">
                  ↻ {task.recurrence_rule.startsWith('FREQ=DAILY') ? 'Daily'
                    : task.recurrence_rule.includes('WEEKDAYS') ? 'Weekdays'
                    : task.recurrence_rule.startsWith('FREQ=WEEKLY') ? 'Weekly'
                    : task.recurrence_rule.startsWith('FREQ=MONTHLY') ? 'Monthly'
                    : 'Recurring'}
                  {task.is_paused && ' (paused)'}
                </span>
              )}
              {/* Reminder count badge */}
              {task.reminders && task.reminders.length > 0 && (
                <span className="inline-flex items-center gap-0.5 mt-1 text-xs text-gray-500">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {task.reminders.length} reminder{task.reminders.length > 1 ? 's' : ''}
                </span>
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
              {/* Pause/resume for recurring tasks */}
              {task.recurrence_rule && (
                <button
                  onClick={() => onUpdate({ is_paused: !task.is_paused })}
                  disabled={isUpdating || isDeleting}
                  className="text-sm text-purple-600 hover:text-purple-700 disabled:opacity-50"
                  aria-label={task.is_paused ? 'Resume recurrence' : 'Pause recurrence'}
                >
                  {task.is_paused ? 'Resume' : 'Pause'}
                </button>
              )}
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
            {task.recurrence_rule && (
              <div className="mb-4 p-3 bg-purple-50 rounded-md border border-purple-200">
                <p className="text-xs font-medium text-purple-800 mb-2">This is a recurring task</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => { handleDelete(); }}
                    className="flex-1 px-3 py-1.5 text-xs font-medium text-white bg-purple-600 rounded hover:bg-purple-700"
                  >
                    This task only
                  </button>
                  <button
                    onClick={() => { onUpdate({ is_paused: true }); setShowDeleteConfirm(false); }}
                    className="flex-1 px-3 py-1.5 text-xs font-medium text-purple-700 bg-white border border-purple-300 rounded hover:bg-purple-50"
                  >
                    All future tasks
                  </button>
                </div>
              </div>
            )}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              {!task.recurrence_rule && (
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
                >
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </button>
              )}
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
