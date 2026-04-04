'use client';

import { useState, useEffect } from 'react';
import { TaskFilters } from '@/types';
import { getTags } from '@/lib/api/tags';
import { Tag } from '@/types/tag';

interface TaskFilterProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
}

const PRIORITIES = ['high', 'medium', 'low'] as const;
const STATUS_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'completed', label: 'Completed' },
  { value: 'overdue', label: 'Overdue' },
] as const;
const SORT_OPTIONS = [
  { value: 'created_at', label: 'Created' },
  { value: 'priority', label: 'Priority' },
  { value: 'title', label: 'Title' },
  { value: 'due_date', label: 'Due Date' },
] as const;

export default function TaskFilter({ filters, onChange }: TaskFilterProps) {
  const [open, setOpen] = useState(false);
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);

  useEffect(() => {
    getTags().then(setAvailableTags).catch(() => {});
  }, []);

  const togglePriority = (p: 'high' | 'medium' | 'low') => {
    const current = filters.priority ?? [];
    const next = current.includes(p) ? current.filter((x) => x !== p) : [...current, p];
    onChange({ ...filters, priority: next.length ? next : undefined });
  };

  const toggleTag = (name: string) => {
    const current = filters.tags ?? [];
    const next = current.includes(name) ? current.filter((x) => x !== name) : [...current, name];
    onChange({ ...filters, tags: next.length ? next : undefined });
  };

  const setStatus = (s: TaskFilters['status']) => {
    onChange({ ...filters, status: s });
  };

  const setSortBy = (v: TaskFilters['sort_by']) => {
    onChange({ ...filters, sort_by: v });
  };

  const toggleSortOrder = () => {
    onChange({ ...filters, sort_order: filters.sort_order === 'asc' ? 'desc' : 'asc' });
  };

  const hasActiveFilters =
    (filters.priority?.length ?? 0) > 0 ||
    (filters.tags?.length ?? 0) > 0 ||
    (filters.status && filters.status !== 'all') ||
    filters.sort_by !== 'created_at';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="text-sm font-medium text-gray-700 flex items-center gap-1.5"
        >
          <svg className={`w-4 h-4 transition-transform ${open ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          Filters &amp; Sort
          {hasActiveFilters && (
            <span className="ml-1 px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">active</span>
          )}
        </button>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={() => onChange({ sort_by: 'created_at', sort_order: 'desc' })}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Collapsible panel */}
      {open && (
        <div className="mt-3 space-y-3">
          {/* Status toggles */}
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Status</p>
            <div className="flex flex-wrap gap-1.5">
              {STATUS_OPTIONS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setStatus(value as TaskFilters['status'])}
                  className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
                    (filters.status ?? 'all') === value
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Priority checkboxes */}
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Priority</p>
            <div className="flex gap-2">
              {PRIORITIES.map((p) => (
                <label key={p} className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(filters.priority ?? []).includes(p)}
                    onChange={() => togglePriority(p)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-xs capitalize text-gray-700">{p}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Tag multi-select */}
          {availableTags.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Tags</p>
              <div className="flex flex-wrap gap-1.5">
                {availableTags.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => toggleTag(tag.name)}
                    className={`px-2 py-0.5 rounded-full text-xs border transition-colors ${
                      (filters.tags ?? []).includes(tag.name)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                    }`}
                  >
                    #{tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Sort */}
          <div className="flex items-center gap-3">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Sort by</p>
              <select
                value={filters.sort_by ?? 'created_at'}
                onChange={(e) => setSortBy(e.target.value as TaskFilters['sort_by'])}
                className="text-sm border border-gray-300 rounded px-2 py-1 bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {SORT_OPTIONS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Order</p>
              <button
                type="button"
                onClick={toggleSortOrder}
                className="text-sm border border-gray-300 rounded px-2 py-1 bg-white text-gray-700 hover:bg-gray-50"
              >
                {(filters.sort_order ?? 'desc') === 'desc' ? '↓ Desc' : '↑ Asc'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
