import React, { useState } from 'react';
import { X, Upload, FileText, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';

export default function ImportRequirementsModal({ isOpen, onClose, projectId, onImportSuccess }) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'file'
  const [rawText, setRawText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Step 2 Preview State
  const [step, setStep] = useState(1); // 1: Input, 2: Preview
  const [candidateItems, setCandidateItems] = useState([]);

  if (!isOpen) return null;

  const resetModal = () => {
    setStep(1);
    setRawText('');
    setSelectedFile(null);
    setCandidateItems([]);
    setError(null);
    setLoading(false);
    onClose();
  };

  const handleExtractPreview = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let res;
      if (activeTab === 'text') {
        if (!rawText.trim()) throw new Error('Please paste SRS text to import.');
        res = await api.importText(projectId, rawText);
      } else {
        if (!selectedFile) throw new Error('Please select a .txt, .docx, or .pdf file.');
        res = await api.importFile(projectId, selectedFile);
      }

      if (!res.items || res.items.length === 0) {
        throw new Error('No requirement statements could be extracted from the input.');
      }

      setCandidateItems(res.items);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (index, newText) => {
    const updated = [...candidateItems];
    updated[index].text = newText;
    setCandidateItems(updated);
  };

  const handleTypeChange = (index, newType) => {
    const updated = [...candidateItems];
    updated[index].type = newType;
    setCandidateItems(updated);
  };

  const handleDeleteCandidate = (index) => {
    setCandidateItems(candidateItems.filter((_, i) => i !== index));
  };

  const handleConfirmImport = async () => {
    if (candidateItems.length === 0) return;
    setLoading(true);
    setError(null);

    try {
      await api.batchCreateRequirements(projectId, candidateItems);
      onImportSuccess();
      resetModal();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={resetModal}>
      <div className="modal-card" style={{ maxWidth: step === 2 ? '780px' : '540px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>
              {step === 1 ? 'Import SRS Document' : `Preview Extracted Requirements (${candidateItems.length})`}
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              {step === 1
                ? 'Paste raw text or upload a document (.txt, .docx, .pdf).'
                : 'Review, edit, or remove extracted requirement statements before saving.'}
            </p>
          </div>
          <button onClick={resetModal} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#f87171', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {step === 1 ? (
          <div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
              <button
                className={`nav-link-btn ${activeTab === 'text' ? 'active' : ''}`}
                style={{ borderColor: activeTab === 'text' ? '#3b82f6' : '#334155', color: activeTab === 'text' ? '#fff' : '#94a3b8' }}
                onClick={() => setActiveTab('text')}
              >
                Paste Text
              </button>
              <button
                className={`nav-link-btn ${activeTab === 'file' ? 'active' : ''}`}
                style={{ borderColor: activeTab === 'file' ? '#3b82f6' : '#334155', color: activeTab === 'file' ? '#fff' : '#94a3b8' }}
                onClick={() => setActiveTab('file')}
              >
                Upload File
              </button>
            </div>

            {activeTab === 'text' ? (
              <div className="form-group">
                <label className="form-label">Raw SRS Text</label>
                <textarea
                  className="form-textarea"
                  style={{ minHeight: '160px' }}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste numbered lists, bullet points, or SRS paragraph statements here..."
                />
              </div>
            ) : (
              <div className="form-group">
                <label className="form-label">Select Document (.txt, .docx, .pdf up to 5MB)</label>
                <div
                  style={{ border: '2px dashed #334155', borderRadius: '8px', padding: '32px', textAlign: 'center', backgroundColor: '#0f172a', cursor: 'pointer' }}
                  onClick={() => document.getElementById('file-input').click()}
                >
                  <Upload size={36} color="#3b82f6" style={{ marginBottom: '8px' }} />
                  <p style={{ fontSize: '0.95rem', color: '#e2e8f0' }}>
                    {selectedFile ? selectedFile.name : 'Click or drag file here'}
                  </p>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Supports TXT, DOCX, and PDF</span>
                  <input
                    id="file-input"
                    type="file"
                    accept=".txt,.docx,.pdf"
                    style={{ display: 'none' }}
                    onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                  />
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button className="btn-secondary" onClick={resetModal}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleExtractPreview} disabled={loading}>
                {loading ? 'Processing...' : 'Preview Extracted Requirements →'}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ maxHeight: '380px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
              {candidateItems.map((item, index) => (
                <div key={index} style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#3b82f6', fontWeight: 600 }}>
                      {item.req_code} {item.source_reference && <span style={{ color: '#64748b', fontWeight: 400 }}>({item.source_reference})</span>}
                    </span>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <select
                        className="form-select"
                        style={{ padding: '2px 8px', fontSize: '0.8rem', width: 'auto' }}
                        value={item.type}
                        onChange={(e) => handleTypeChange(index, e.target.value)}
                      >
                        <option value="UNCLASSIFIED">UNCLASSIFIED</option>
                        <option value="FUNCTIONAL">FUNCTIONAL</option>
                        <option value="NON_FUNCTIONAL">NON_FUNCTIONAL</option>
                      </select>
                      <button
                        onClick={() => handleDeleteCandidate(index)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}
                        title="Remove requirement"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <textarea
                    className="form-textarea"
                    style={{ minHeight: '50px', fontSize: '0.9rem' }}
                    value={item.text}
                    onChange={(e) => handleTextChange(index, e.target.value)}
                  />
                </div>
              ))}
            </div>

            <div className="modal-actions" style={{ justifyContent: 'space-between' }}>
              <button className="btn-secondary" onClick={() => setStep(1)}>
                ← Back
              </button>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button className="btn-secondary" onClick={resetModal}>
                  Cancel
                </button>
                <button className="btn-primary" onClick={handleConfirmImport} disabled={loading || candidateItems.length === 0}>
                  {loading ? 'Saving...' : `Confirm & Import ${candidateItems.length} Requirements`}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
