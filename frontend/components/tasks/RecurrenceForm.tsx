'use client';

import { useState } from 'react';

interface RecurrenceFormProps {
  value: string;
  onChange: (rule: string) => void;
}

type Frequency = 'NONE' | 'DAILY' | 'WEEKDAYS' | 'WEEKLY' | 'MONTHLY' | 'CUSTOM';

const DAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
const DAY_LABELS: Record<string, string> = {
  MO: 'Mon', TU: 'Tue', WE: 'Wed', TH: 'Thu', FR: 'Fri', SA: 'Sat', SU: 'Sun',
};

function buildRRule(
  freq: Frequency,
  selectedDays: string[],
  monthDay: string,
  customRule: string,
): string {
  if (freq === 'NONE') return '';
  if (freq === 'DAILY') return 'FREQ=DAILY';
  if (freq === 'WEEKDAYS') return 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR';
  if (freq === 'WEEKLY') {
    const days = selectedDays.length ? selectedDays.join(',') : 'MO';
    return `FREQ=WEEKLY;BYDAY=${days}`;
  }
  if (freq === 'MONTHLY') {
    const day = parseInt(monthDay, 10);
    if (!isNaN(day) && day >= 1 && day <= 31) {
      return `FREQ=MONTHLY;BYMONTHDAY=${day}`;
    }
    return 'FREQ=MONTHLY';
  }
  if (freq === 'CUSTOM') return customRule;
  return '';
}

function describeRRule(rule: string): string {
  if (!rule) return 'No recurrence';
  if (rule === 'FREQ=DAILY') return 'Daily';
  if (rule === 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR') return 'Every weekday';
  if (rule.startsWith('FREQ=WEEKLY;BYDAY=')) {
    const days = rule.replace('FREQ=WEEKLY;BYDAY=', '').split(',').map((d) => DAY_LABELS[d] || d);
    return `Weekly on ${days.join(', ')}`;
  }
  if (rule.startsWith('FREQ=MONTHLY')) {
    const match = rule.match(/BYMONTHDAY=(\d+)/);
    return match ? `Monthly on the ${match[1]}th` : 'Monthly';
  }
  return rule;
}

export default function RecurrenceForm({ value, onChange }: RecurrenceFormProps) {
  const [freq, setFreq] = useState<Frequency>(() => {
    if (!value) return 'NONE';
    if (value === 'FREQ=DAILY') return 'DAILY';
    if (value.includes('BYDAY=MO,TU,WE,TH,FR')) return 'WEEKDAYS';
    if (value.startsWith('FREQ=WEEKLY')) return 'WEEKLY';
    if (value.startsWith('FREQ=MONTHLY')) return 'MONTHLY';
    return 'CUSTOM';
  });
  const [selectedDays, setSelectedDays] = useState<string[]>(['MO']);
  const [monthDay, setMonthDay] = useState('1');
  const [customRule, setCustomRule] = useState(value || '');

  const handleFreqChange = (newFreq: Frequency) => {
    setFreq(newFreq);
    const rule = buildRRule(newFreq, selectedDays, monthDay, customRule);
    onChange(rule);
  };

  const toggleDay = (day: string) => {
    const next = selectedDays.includes(day)
      ? selectedDays.filter((d) => d !== day)
      : [...selectedDays, day];
    setSelectedDays(next);
    onChange(buildRRule('WEEKLY', next, monthDay, customRule));
  };

  const handleMonthDayChange = (val: string) => {
    setMonthDay(val);
    onChange(buildRRule('MONTHLY', selectedDays, val, customRule));
  };

  const handleCustomChange = (val: string) => {
    setCustomRule(val);
    onChange(val);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Recurrence</label>

      {/* Frequency selector */}
      <div className="flex flex-wrap gap-1.5">
        {(['NONE', 'DAILY', 'WEEKDAYS', 'WEEKLY', 'MONTHLY', 'CUSTOM'] as Frequency[]).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => handleFreqChange(f)}
            className={`px-2.5 py-1 text-xs rounded border transition-colors ${
              freq === f
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
            }`}
          >
            {f === 'NONE' ? 'None' : f.charAt(0) + f.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {/* Weekly day picker */}
      {freq === 'WEEKLY' && (
        <div className="flex gap-1">
          {DAYS.map((day) => (
            <button
              key={day}
              type="button"
              onClick={() => toggleDay(day)}
              className={`w-8 h-8 text-xs rounded-full border transition-colors ${
                selectedDays.includes(day)
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
              }`}
            >
              {DAY_LABELS[day].charAt(0)}
            </button>
          ))}
        </div>
      )}

      {/* Monthly day input */}
      {freq === 'MONTHLY' && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-600">Day of month:</span>
          <input
            type="number"
            min="1"
            max="31"
            value={monthDay}
            onChange={(e) => handleMonthDayChange(e.target.value)}
            className="w-16 text-xs border border-gray-300 rounded px-2 py-1 bg-white text-black"
          />
        </div>
      )}

      {/* Custom RRULE input */}
      {freq === 'CUSTOM' && (
        <input
          type="text"
          placeholder="e.g. FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE"
          value={customRule}
          onChange={(e) => handleCustomChange(e.target.value)}
          className="block w-full text-xs border border-gray-300 rounded px-3 py-1.5 bg-white text-black placeholder-gray-400 focus:ring-1 focus:ring-blue-500"
        />
      )}

      {/* Preview */}
      {value && (
        <p className="text-xs text-gray-500">Preview: {describeRRule(value)}</p>
      )}
    </div>
  );
}
