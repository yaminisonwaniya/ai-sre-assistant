import React, { useState } from 'react';
import { X, AlertTriangle, CheckCircle2, RotateCw, BookOpen } from 'lucide-react';
import { QualityScoreBadge, SeverityBadge } from './QualityBadge';
import { api } from '../api/client';

export default function RequirementDetailDrawer({ requirement, isOpen, onClose, onRequirementUpdated }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen || !requirement) return null;

  const handleReAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const updated = await api.analyzeRequirement(requirement.id);
      if (onRequirementUpdated) onRequirementUpdated(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  // Highlight trigger words in requirement text statement
  const renderHighlightedText = () => {
    const text = requirement.text;
    const issues = requirement.issues || [];
    if (issues.length === 0) return <span>{text}</span>;

    const triggers = issues
      .map((i) => i.trigger_text)
      .filter((t) => t && t.trim().length > 0);

    if (triggers.length === 0) return <span>{text}</span>;

    // Create regex matching any trigger text
    const pattern = new RegExp(`(${triggers.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
    const parts = text.split(pattern);

    return (
      <span>
        {parts.map((part, index) => {
          const isMatched = triggers.some((t) => t.toLowerCase() === part.toLowerCase());
          if (isMatched) {
            return (
              <mark
                key={index}
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.3)',
                  color: '#fca5a5',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  fontWeight: 600,
                  borderBottom: '2px solid #ef4444',
                }}
              >
                {part}
              </mark>
            );
          }
          return part;
        })}
      </span>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-card"
        style={{
          maxWidth: '680px',
          height: '100vh',
          maxHeight: '100vh',
          borderRadius: 0,
          position: 'fixed',
          right: 0,
          top: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <span className="req-code">{requirement.req_code}</span>
              <QualityScoreBadge score={requirement.quality_score} />
            </div>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              Type: {requirement.type} | Subtype: {requirement.subtype || 'GENERAL'}
            </span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#f87171', padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '0.85rem' }}>
            Error: {error}
          </div>
        )}

        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
          {/* Statement View with Highlighted Trigger Words */}
          <div style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
            <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase' }}>
              Requirement Statement (Highlighted Issues)
            </h4>
            <p style={{ fontSize: '1rem', lineHeight: '1.6', color: '#f8fafc' }}>
              {renderHighlightedText()}
            </p>
          </div>

          {/* Quality Issues List */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={18} color="#f59e0b" />
                Detected Quality Issues ({requirement.issues ? requirement.issues.length : 0})
              </h4>
              <button
                className="btn-secondary"
                style={{ padding: '4px 12px', fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                onClick={handleReAnalyze}
                disabled={analyzing}
              >
                <RotateCw size={14} className={analyzing ? 'animate-spin' : ''} />
                {analyzing ? 'Analyzing...' : 'Re-Analyze'}
              </button>
            </div>

            {(!requirement.issues || requirement.issues.length === 0) ? (
              <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', borderRadius: '8px', padding: '20px', textAlign: 'center', color: '#34d399' }}>
                <CheckCircle2 size={32} style={{ marginBottom: '8px' }} />
                <p style={{ fontWeight: 600 }}>No Quality Flaws Detected</p>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Compliant with ISO/IEC/IEEE 29148 characteristics.</span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {requirement.issues.map((issue) => (
                  <div key={issue.id || Math.random()} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontWeight: 600, color: '#60a5fa', fontSize: '0.9rem' }}>
                        {issue.category}
                      </span>
                      <SeverityBadge severity={issue.severity} />
                    </div>
                    {issue.trigger_text && (
                      <p style={{ fontSize: '0.85rem', color: '#f87171', marginBottom: '6px', fontFamily: 'var(--font-mono)' }}>
                        Trigger: "{issue.trigger_text}"
                      </p>
                    )}
                    <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '8px', lineHeight: 1.5 }}>
                      {issue.explanation}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#94a3b8', borderTop: '1px dashed #334155', paddingTop: '8px' }}>
                      <BookOpen size={14} />
                      <span>{issue.standard_reference || 'ISO/IEC/IEEE 29148:2018'}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="modal-actions" style={{ marginTop: '16px' }}>
          <button className="btn-secondary" onClick={onClose} style={{ width: '100%' }}>
            Close Detail Drawer
          </button>
        </div>
      </div>
    </div>
  );
}
