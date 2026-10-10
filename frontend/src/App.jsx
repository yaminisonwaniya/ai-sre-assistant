import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ProjectListPage from './pages/ProjectListPage';
import ProjectDetailPage from './pages/ProjectDetailPage';

export default function App() {
  const [selectedProject, setSelectedProject] = useState(null);

  return (
    <div className="app-container">
      <Navbar
        activeProject={selectedProject}
        onBack={() => setSelectedProject(null)}
      />
      <main>
        {selectedProject ? (
          <ProjectDetailPage project={selectedProject} />
        ) : (
          <ProjectListPage onSelectProject={(proj) => setSelectedProject(proj)} />
        )}
      </main>
    </div>
  );
}
