import React from 'react';
import { FolderGit2, FileText, Trash2 } from 'lucide-react';

export default function ProjectCard({ project, onSelect, onDelete }) {
  return (
    <div className="project-card" onClick={() => onSelect(project)}>
      <div className="project-card-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <h3 className="project-name">{project.name}</h3>
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(`Delete project "${project.name}"?`)) {
                  onDelete(project.id);
                }
              }}
              style={{ background: 'none', border: 'none', color: '#64748b', padding: '4px' }}
              title="Delete Project"
            >
              <Trash2 size={16} color="#64748b" />
            </button>
          )}
        </div>
        <p className="project-desc">{project.description || 'No description provided.'}</p>
      </div>
      <div className="project-footer">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <FileText size={16} />
          {project.requirement_count || 0} Requirements
        </span>
        <span>ID: {project.id}</span>
      </div>
    </div>
  );
}
