import React from 'react';
import { Trash2, AlertTriangle } from 'lucide-react';
import { QualityScoreBadge, SeverityBadge } from './QualityBadge';

export default function RequirementCard({ requirement, onSelect, onDelete }) {
  const getTypeBadgeClass = (type) => {
    switch (type) {
      case 'FUNCTIONAL': return 'badge-functional';
      case 'NON_FUNCTIONAL': return 'badge-non-functional';
      default: return 'badge-unclassified';
    }
  };

  const highestSeverity = requirement.issues?.reduce((acc, issue) => {
    const sevOrder = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
    const currentOrder = sevOrder[issue.severity?.toUpperCase()] || 0;
    const maxOrder = sevOrder[acc] || 0;
    return currentOrder > maxOrder ? issue.severity.toUpperCase() : acc;
  }, null);

  return (
    <div className="req-card" onClick={() => onSelect && onSelect(requirement)} style={{ cursor: 'pointer' }}>
      <div className="req-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="req-code">{requirement.req_code}</span>
          <QualityScoreBadge score={requirement.quality_score} />
        </div>
        <div className="req-badges" style={{ alignItems: 'center' }}>
          <span className={`badge ${getTypeBadgeClass(requirement.type)}`}>
            {requirement.type}
          </span>

          {highestSeverity && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={14} color="#f59e0b" />
              <SeverityBadge severity={highestSeverity} />
            </div>
          )}

          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(requirement.id);
              }}
              style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: '8px' }}
              title="Delete Requirement"
            >
              <Trash2 size={16} color="#64748b" />
            </button>
          )}
        </div>
      </div>

      <p className="req-text" style={{ marginTop: '8px' }}>{requirement.text}</p>

      <div className="req-meta" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
        <span>Subtype: {requirement.subtype || 'GENERAL'}</span>
        <span>
          {requirement.issues ? requirement.issues.length : 0} Quality Issue(s)
        </span>
      </div>
    </div>
  );
}
