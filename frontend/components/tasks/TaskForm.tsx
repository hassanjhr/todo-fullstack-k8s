'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';
import { TaskFormData } from '@/types';
import { validateTaskForm } from '@/lib/utils/validation';
import RecurrenceForm from './RecurrenceForm';

/**
 * TaskForm Component
 * Form for creating new tasks with priority and tags support
 */
interface TaskFormProps {
  onSubmit: (data: TaskFormData & { priority: string; tags: string[] }) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

const TAG_REGEX = /^[a-zA-Z0-9-]+$/;

export default function TaskForm({ onSubmit, loading = false, error = null }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [dueDate, setDueDate] = useState('');
  const [recurrenceRule, setRecurrenceRule] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const addTag = (raw: string) => {
    const name = raw.trim().toLowerCase();
    if (name && TAG_REGEX.test(name) && name.length <= 50 && !tags.includes(name)) {
      setTags((prev) => [...prev, name]);
    }
    setTagInput('');
  };

  const handleTagKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(tagInput);
    } else if (e.key === 'Backspace' && tagInput === '' && tags.length > 0) {
      setTags((prev) => prev.slice(0, -1));
    }
  };

  const removeTag = (name: string) => {
    setTags((prev) => prev.filter((t) => t !== name));
  };

  const handleTitleChange = (value: string) => {
    setTitle(value);
    // Clear title validation error when user starts typing
    if (validationErrors.title) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.title;
        return newErrors;
      });
    }
  };

  const handleDescriptionChange = (value: string) => {
    setDescription(value);
    // Clear description validation error when user starts typing
    if (validationErrors.description) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.description;
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Clear previous validation errors
    setValidationErrors({});

    // Validate form data
    const formData = {
      title,
      description: description.trim() || undefined
    };
    const errors = validateTaskForm(formData);

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    // Submit form
    try {
      await onSubmit({
        ...formData,
        priority,
        tags,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        recurrence_rule: recurrenceRule || undefined,
      });
      // Clear form on success
      setTitle('');
      setDescription('');
      setPriority('medium');
      setTags([]);
      setTagInput('');
      setDueDate('');
      setRecurrenceRule('');
      setValidationErrors({});
    } catch (err) {
      // Error handling is done by parent component
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title Field */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Task Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          name="title"
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
          className={`block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white !text-black placeholder-gray-400 ${
            validationErrors.title
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          disabled={loading}
          aria-invalid={!!validationErrors.title}
          aria-describedby={validationErrors.title ? 'title-error' : undefined}
          maxLength={200}
        />
        {validationErrors.title && (
          <p id="title-error" className="mt-1 text-sm text-red-600">
            {validationErrors.title}
          </p>
        )}
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description <span className="text-gray-500 text-xs">(optional)</span>
        </label>
        <textarea
          id="description"
          name="description"
          rows={3}
          placeholder="Add more details about this task..."
          value={description}
          onChange={(e) => handleDescriptionChange(e.target.value)}
          className={`block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white !text-black placeholder-gray-400 ${
            validationErrors.description
              ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          disabled={loading}
          aria-invalid={!!validationErrors.description}
          aria-describedby={validationErrors.description ? 'description-error' : undefined}
          maxLength={2000}
        />
        <p className="mt-1 text-xs text-gray-500">
          {description.length}/2000 characters
        </p>
        {validationErrors.description && (
          <p id="description-error" className="mt-1 text-sm text-red-600">
            {validationErrors.description}
          </p>
        )}
      </div>

      {/* Due Date Field */}
      <div>
        <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
          Due Date <span className="text-gray-500 text-xs">(optional)</span>
        </label>
        <input
          id="due_date"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={loading}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
        />
      </div>

      {/* Priority Field */}
      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
          Priority
        </label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
          disabled={loading}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
        >
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Tags Field */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
          Tags <span className="text-gray-500 text-xs">(press Enter or comma to add)</span>
        </label>
        <div className="flex flex-wrap gap-1.5 mb-1.5">
          {tags.map((tag) => (
            <span key={tag} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 border border-blue-200">
              #{tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="text-blue-400 hover:text-blue-600 font-bold leading-none"
                aria-label={`Remove tag ${tag}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <input
          id="tags"
          type="text"
          placeholder="e.g. work, urgent"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
          onKeyDown={handleTagKeyDown}
          onBlur={() => { if (tagInput.trim()) addTag(tagInput); }}
          disabled={loading}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white !text-black placeholder-gray-400"
        />
        <p className="mt-1 text-xs text-gray-500">Letters, numbers, and hyphens only. Max 50 chars each.</p>
      </div>

      {/* Recurrence Field */}
      <RecurrenceForm value={recurrenceRule} onChange={setRecurrenceRule} />

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Creating...
            </>
          ) : (
            '+ Add Task'
          )}
        </button>
      </div>

      {/* API Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}
    </form>
  );
}
