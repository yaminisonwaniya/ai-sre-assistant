import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

export default function ProjectAnalyticsCharts({ requirements }) {
  if (!requirements || requirements.length === 0) return null;

  // 1. Score Distribution Data
  let goodCount = 0;
  let needsImprovementCount = 0;
  let poorCount = 0;

  // 2. Type Distribution Data
  let functionalCount = 0;
  let nonFunctionalCount = 0;
  let unclassifiedCount = 0;

  // 3. Issues by Category Data
  const issueCategoryCounts = {};

  requirements.forEach((req) => {
    // Quality Score
    const score = req.quality_score;
    if (score >= 80) goodCount++;
    else if (score >= 50) needsImprovementCount++;
    else poorCount++;

    // Type
    if (req.type === 'FUNCTIONAL') functionalCount++;
    else if (req.type === 'NON_FUNCTIONAL') nonFunctionalCount++;
    else unclassifiedCount++;

    // Issues
    if (req.issues && req.issues.length > 0) {
      req.issues.forEach((issue) => {
        const cat = issue.category || 'OTHER';
        issueCategoryCounts[cat] = (issueCategoryCounts[cat] || 0) + 1;
      });
    }
  });

  const scoreData = [
    { name: 'Good (80-100)', count: goodCount, fill: '#10b981' },
    { name: 'Needs Imp. (50-79)', count: needsImprovementCount, fill: '#f59e0b' },
    { name: 'Poor (0-49)', count: poorCount, fill: '#ef4444' },
  ];

  const typeData = [
    { name: 'Functional', value: functionalCount, color: '#3b82f6' },
    { name: 'Non-Functional', value: nonFunctionalCount, color: '#f59e0b' },
    { name: 'Unclassified', value: unclassifiedCount, color: '#94a3b8' },
  ].filter((d) => d.value > 0);

  const categoryData = Object.keys(issueCategoryCounts).map((cat) => ({
    category: cat,
    count: issueCategoryCounts[cat],
  }));

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '24px' }}>
      {/* Chart 1: Quality Score Distribution */}
      <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '16px' }}>
          Quality Score Distribution
        </h4>
        <div style={{ width: '100%', height: '180px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scoreData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {scoreData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: Issues by Category */}
      <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '16px' }}>
          Issues by ISO 29148 Category
        </h4>
        {categoryData.length === 0 ? (
          <p style={{ color: '#94a3b8', fontSize: '0.85rem', textAlign: 'center', paddingTop: '40px' }}>
            No quality issues detected yet. Run Analysis.
          </p>
        ) : (
          <div style={{ width: '100%', height: '180px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical" margin={{ top: 5, right: 15, left: 30, bottom: 5 }}>
                <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis type="category" dataKey="category" stroke="#94a3b8" tick={{ fontSize: 10 }} width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Chart 3: Functional vs Non-Functional */}
      <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '16px' }}>
          Requirement Classification
        </h4>
        <div style={{ width: '100%', height: '180px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={typeData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} innerRadius={35}>
                {typeData.map((entry, index) => (
                  <Cell key={`cell-type-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
              <Legend verticalAlign="bottom" height={36} formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: '11px' }}>{value}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
