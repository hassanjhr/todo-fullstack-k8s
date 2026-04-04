'use client';

import { useState } from 'react';
import { Reminder } from '@/types/reminder';
import { createReminder, deleteReminder } from '@/lib/api/reminders';

interface ReminderFormProps {
  taskId: string;
  dueDate: string; // ISO string
  reminders: Reminder[];
  onRemindersChange: (reminders: Reminder[]) => void;
}

const PRESET_OFFSETS = [
  { label: '15 min before', value: 15 },
  { label: '1 hour before', value: 60 },
  { label: '24 hours before', value: 1440 },
];

function formatTriggerAt(triggerAt: string): string {
  try {
    return new Date(triggerAt).toLocaleString();
  } catch {
    return triggerAt;
  }
}

export default function ReminderForm({
  taskId,
  dueDate,
  reminders,
  onRemindersChange,
}: ReminderFormProps) {
  const [adding, setAdding] = useState(false);
  const [customOffset, setCustomOffset] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAdd = async (offsetMinutes: number) => {
    setLoading(true);
    setError(null);
    try {
      const newReminder = await createReminder(taskId, { offset_minutes: offsetMinutes });
      onRemindersChange([...reminders, newReminder]);
      setAdding(false);
      setCustomOffset('');
    } catch {
      setError('Failed to add reminder. Make sure the task has a due date.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (reminderId: string) => {
    setLoading(true);
    try {
      await deleteReminder(taskId, reminderId);
      onRemindersChange(reminders.filter((r) => r.id !== reminderId));
    } catch {
      setError('Failed to delete reminder');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomAdd = () => {
    const val = parseInt(customOffset, 10);
    if (!isNaN(val) && val > 0) {
      handleAdd(val);
    }
  };

  return (
    <div className="mt-3 space-y-2">
      <p className="text-sm font-medium text-gray-700">Reminders</p>

      {/* Existing reminders */}
      {reminders.length > 0 && (
        <ul className="space-y-1">
          {reminders.map((r) => (
            <li key={r.id} className="flex items-center justify-between text-xs bg-gray-50 rounded px-2 py-1.5 border border-gray-200">
              <span className="text-gray-700">
                {r.offset_minutes < 60
                  ? `${r.offset_minutes} min before`
                  : r.offset_minutes < 1440
                  ? `${r.offset_minutes / 60} hr before`
                  : `${r.offset_minutes / 1440} day before`}
                {' '}— {formatTriggerAt(r.trigger_at)}
              </span>
              <button
                type="button"
                onClick={() => handleDelete(r.id)}
                disabled={loading}
                className="text-red-400 hover:text-red-600 font-medium ml-2"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* Add reminder */}
      {!adding ? (
        <button
          type="button"
          onClick={() => setAdding(true)}
          disabled={!dueDate || loading}
          className="text-xs text-blue-600 hover:text-blue-700 disabled:text-gray-400 underline"
        >
          + Add Reminder
        </button>
      ) : (
        <div className="flex flex-wrap gap-1.5 items-center">
          {PRESET_OFFSETS.map(({ label, value }) => (
            <button
              key={value}
              type="button"
              onClick={() => handleAdd(value)}
              disabled={loading}
              className="px-2 py-1 text-xs rounded border border-blue-300 text-blue-700 hover:bg-blue-50 disabled:opacity-50"
            >
              {label}
            </button>
          ))}
          <div className="flex items-center gap-1">
            <input
              type="number"
              min="1"
              placeholder="custom min"
              value={customOffset}
              onChange={(e) => setCustomOffset(e.target.value)}
              className="w-24 text-xs border border-gray-300 rounded px-2 py-1 bg-white text-black"
            />
            <button
              type="button"
              onClick={handleCustomAdd}
              disabled={loading || !customOffset}
              className="px-2 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Add
            </button>
          </div>
          <button
            type="button"
            onClick={() => { setAdding(false); setCustomOffset(''); }}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Cancel
          </button>
        </div>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
