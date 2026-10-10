import React from 'react';

export function QualityScoreBadge({ score }) {
  if (score === null || score === undefined) return null;

  let bg = 'rgba(16, 185, 129, 0.2)';
  let color = '#34d399';
  let label = 'GOOD';

  if (score < 50) {
    bg = 'rgba(239, 68, 68, 0.2)';
    color = '#f87171';
    label = 'POOR';
  } else if (score < 80) {
    bg = 'rgba(245, 158, 11, 0.2)';
    color = '#fbbf24';
    label = 'NEEDS IMPROVEMENT';
  }

  return (
    <span
      style={{
        backgroundColor: bg,
        color: color,
        padding: '4px 10px',
        borderRadius: '6px',
        fontSize: '0.8rem',
        fontWeight: 600,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
      }}
    >
      Score: {score}% ({label})
    </span>
  );
}

export function SeverityBadge({ severity }) {
  let bg = 'rgba(148, 163, 184, 0.2)';
  let color = '#cbd5e1';

  switch (severity?.toUpperCase()) {
    case 'CRITICAL':
      bg = 'rgba(239, 68, 68, 0.25)';
      color = '#f87171';
      break;
    case 'HIGH':
      bg = 'rgba(249, 115, 22, 0.25)';
      color = '#fb923c';
      break;
    case 'MEDIUM':
      bg = 'rgba(245, 158, 11, 0.25)';
      color = '#fbbf24';
      break;
    case 'LOW':
      bg = 'rgba(59, 130, 246, 0.25)';
      color = '#60a5fa';
      break;
    default:
      break;
  }

  return (
    <span
      style={{
        backgroundColor: bg,
        color: color,
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '0.75rem',
        fontWeight: 600,
        textTransform: 'uppercase',
      }}
    >
      {severity}
    </span>
  );
}
