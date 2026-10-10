import React, { useState, useEffect } from 'react';
import { Plus, Upload, FileText, Play, RotateCw, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import RequirementCard from '../components/RequirementCard';
import CreateRequirementModal from '../components/CreateRequirementModal';
import ImportRequirementsModal from '../components/ImportRequirementsModal';
import RequirementDetailDrawer from '../components/RequirementDetailDrawer';
import ProjectAnalyticsCharts from '../components/ProjectAnalyticsCharts';

export default function ProjectDetailPage({ project }) {
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzingProject, setAnalyzingProject] = useState(false);
  const [error, setError] = useState(null);

  // Filters
  const [filterType, setFilterType] = useState('');
  const [filterLabel, setFilterLabel] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');

  // Drawer & Modals
  const [selectedReqForDrawer, setSelectedReqForDrawer] = useState(null);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [importModalOpen, setImportModalOpen] = useState(false);

  const fetchRequirements = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterType) params.req_type = filterType;

      const data = await api.getProjectRequirements(project.id, params);
      setRequirements(data.items || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequirements();
  }, [project.id, filterType]);

  const handleAnalyzeProject = async () => {
    setAnalyzingProject(true);
    setError(null);
    try {
      await api.analyzeProject(project.id);
      await fetchRequirements();
    } catch (err) {
      setError(`Failed to analyze project: ${err.message}`);
    } finally {
      setAnalyzingProject(false);
    }
  };

  const handleCreateRequirement = async (reqData) => {
    await api.createRequirement(project.id, reqData);
    fetchRequirements();
  };

  const handleDeleteRequirement = async (reqId) => {
    if (confirm('Are you sure you want to delete this requirement?')) {
      try {
        await api.deleteRequirement(reqId);
        fetchRequirements();
        if (selectedReqForDrawer?.id === reqId) {
          setSelectedReqForDrawer(null);
        }
      } catch (err) {
        alert(`Error deleting requirement: ${err.message}`);
      }
    }
  };

  const handleRequirementUpdated = (updatedReq) => {
    setRequirements((prev) =>
      prev.map((r) => (r.id === updatedReq.id ? updatedReq : r))
    );
    setSelectedReqForDrawer(updatedReq);
  };

  // Apply frontend client-side filtering for Quality Label & Severity
  const filteredRequirements = requirements.filter((req) => {
    // Quality Label Filter
    if (filterLabel) {
      const score = req.quality_score;
      if (filterLabel === 'GOOD' && score < 80) return false;
      if (filterLabel === 'NEEDS_IMPROVEMENT' && (score < 50 || score >= 80)) return false;
      if (filterLabel === 'POOR' && score >= 50) return false;
    }

    // Severity Filter
    if (filterSeverity) {
      const hasSev = req.issues?.some(
        (issue) => issue.severity?.toUpperCase() === filterSeverity.toUpperCase()
      );
      if (!hasSev) return false;
    }

    return true;
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">{project.name}</h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            {project.description || 'Project Requirements Specification Details'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            className="btn-primary"
            style={{ backgroundColor: '#8b5cf6' }}
            onClick={handleAnalyzeProject}
            disabled={analyzingProject || requirements.length === 0}
          >
            <Play size={18} className={analyzingProject ? 'animate-spin' : ''} />
            {analyzingProject ? 'Analyzing Project...' : 'Analyze Project Quality'}
          </button>
          <button className="btn-secondary" onClick={() => setImportModalOpen(true)}>
            <Upload size={18} />
            Import SRS
          </button>
          <button className="btn-primary" onClick={() => setAddModalOpen(true)}>
            <Plus size={18} />
            Add Requirement
          </button>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#f87171', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Analytics Charts Component */}
      {!loading && requirements.length > 0 && (
        <ProjectAnalyticsCharts requirements={requirements} />
      )}

      {/* Filter Toolbar */}
      <div className="filter-bar">
        <select
          className="select-input"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="">All Requirement Types</option>
          <option value="FUNCTIONAL">Functional</option>
          <option value="NON_FUNCTIONAL">Non-Functional</option>
          <option value="UNCLASSIFIED">Unclassified</option>
        </select>

        <select
          className="select-input"
          value={filterLabel}
          onChange={(e) => setFilterLabel(e.target.value)}
        >
          <option value="">All Quality Labels</option>
          <option value="GOOD">Good (80-100)</option>
          <option value="NEEDS_IMPROVEMENT">Needs Improvement (50-79)</option>
          <option value="POOR">Poor (&lt; 50)</option>
        </select>

        <select
          className="select-input"
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
        >
          <option value="">All Issue Severities</option>
          <option value="CRITICAL">Critical Severity</option>
          <option value="HIGH">High Severity</option>
          <option value="MEDIUM">Medium Severity</option>
          <option value="LOW">Low Severity</option>
        </select>
      </div>

      {loading && <p style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>Loading requirements...</p>}

      {!loading && filteredRequirements.length === 0 && (
        <div className="empty-state">
          <FileText size={48} color="#64748b" style={{ marginBottom: '16px' }} />
          <h3>No Requirements Matching Filter Criteria</h3>
          <p>Try resetting filters or import an SRS document to begin analysis.</p>
        </div>
      )}

      {!loading && filteredRequirements.length > 0 && (
        <div className="requirements-list">
          {filteredRequirements.map((req) => (
            <RequirementCard
              key={req.id}
              requirement={req}
              onSelect={(r) => setSelectedReqForDrawer(r)}
              onDelete={handleDeleteRequirement}
            />
          ))}
        </div>
      )}

      <CreateRequirementModal
        isOpen={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onCreate={handleCreateRequirement}
      />

      <ImportRequirementsModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        projectId={project.id}
        onImportSuccess={fetchRequirements}
      />

      <RequirementDetailDrawer
        isOpen={!!selectedReqForDrawer}
        requirement={selectedReqForDrawer}
        onClose={() => setSelectedReqForDrawer(null)}
        onRequirementUpdated={handleRequirementUpdated}
      />
    </div>
  );
}
