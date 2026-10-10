import React, { useState, useEffect } from 'react';
import { Plus, FolderPlus } from 'lucide-react';
import { api } from '../api/client';
import ProjectCard from '../components/ProjectCard';
import CreateProjectModal from '../components/CreateProjectModal';

export default function ProjectListPage({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await api.getProjects();
      setProjects(data.items || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (newProjectData) => {
    await api.createProject(newProjectData);
    fetchProjects();
  };

  const handleDeleteProject = async (projectId) => {
    try {
      await api.deleteProject(projectId);
      fetchProjects();
    } catch (err) {
      alert(`Error deleting project: ${err.message}`);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">SRS Projects</h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Select a project to inspect requirements, quality scores, and issues.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={18} />
          New Project
        </button>
      </div>

      {loading && <p style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>Loading projects...</p>}
      {error && <p style={{ color: '#ef4444', textAlign: 'center', padding: '40px' }}>Error: {error}</p>}

      {!loading && !error && projects.length === 0 && (
        <div className="empty-state">
          <FolderPlus size={48} color="#64748b" style={{ marginBottom: '16px' }} />
          <h3>No Projects Found</h3>
          <p>Create your first project to start managing software requirements.</p>
        </div>
      )}

      {!loading && !error && projects.length > 0 && (
        <div className="projects-grid">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onSelect={onSelectProject}
              onDelete={handleDeleteProject}
            />
          ))}
        </div>
      )}

      <CreateProjectModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreate={handleCreateProject}
      />
    </div>
  );
}
