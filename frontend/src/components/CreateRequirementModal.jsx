import React, { useState } from 'react';
import { X } from 'lucide-react';

export default function CreateRequirementModal({ isOpen, onClose, onCreate }) {
  const [text, setText] = useState('');
  const [type, setType] = useState('FUNCTIONAL');
  const [subtype, setSubtype] = useState('GENERAL');
  const [status, setStatus] = useState('DRAFT');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setSubmitting(true);
    try {
      await onCreate({ text, type, subtype, status });
      setText('');
      setType('FUNCTIONAL');
      setSubtype('GENERAL');
      setStatus('DRAFT');
      onClose();
    } catch (err) {
      alert(`Failed to add requirement: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Requirement Statement</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8' }}>
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Requirement Statement *</label>
            <textarea
              className="form-textarea"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. The system shall respond to user login authentication within 2 seconds."
              required
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Type</label>
              <select className="form-select" value={type} onChange={(e) => setType(e.target.value)}>
                <option value="FUNCTIONAL">FUNCTIONAL</option>
                <option value="NON_FUNCTIONAL">NON_FUNCTIONAL</option>
                <option value="UNCLASSIFIED">UNCLASSIFIED</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Subtype</label>
              <input
                type="text"
                className="form-input"
                value={subtype}
                onChange={(e) => setSubtype(e.target.value)}
                placeholder="e.g. SECURITY, PERFORMANCE"
              />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Requirement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
