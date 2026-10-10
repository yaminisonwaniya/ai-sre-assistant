import React from 'react';
import { Layers } from 'lucide-react';

export default function Navbar({ activeProject, onBack }) {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <Layers className="w-6 h-6 text-blue-500" size={24} color="#3b82f6" />
        <span>SRE Assistant</span>
      </div>
      {activeProject && (
        <button onClick={onBack} className="nav-link-btn">
          ← Back to Projects
        </button>
      )}
    </header>
  );
}
