import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';


ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);


function DashboardPage() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/analytics/dashboard');
      setDashboardData(response.data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error loading dashboard';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="alert alert-error">
        <p>{error || 'Error loading dashboard'}</p>
        <button onClick={fetchDashboardData} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  // Prepare data for charts
  const priorityLabels = Object.keys(dashboardData.priority_distribution || {});
  const priorityValues = Object.values(dashboardData.priority_distribution || {});

  const typeLabels = Object.keys(dashboardData.issue_types || {});
  const typeValues = Object.values(dashboardData.issue_types || {});

  const statusLabels = Object.keys(dashboardData.status_distribution || {});
  const statusValues = Object.values(dashboardData.status_distribution || {});

  const priorityColors = {
    critical: '#e74c3c',
    high: '#e67e22',
    medium: '#f39c12',
    low: '#27ae60'
  };

  const typeColors = [
    '#667eea',
    '#764ba2',
    '#f093fb',
    '#4facfe',
    '#43e97b',
    '#fa709a',
    '#fee140'
  ];

  const statusColors = {
    reported: '#3498db',
    investigating: '#f39c12',
    resolved: '#27ae60'
  };

  return (
    <div className="dashboard-page">
      <h1 style={{ marginBottom: '2rem' }}>📊 Authority Dashboard</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card critical">
          <h3>Critical Issues</h3>
          <div className="number">{dashboardData.critical_issues}</div>
        </div>
        <div className="stat-card high">
          <h3>High Priority</h3>
          <div className="number">{dashboardData.high_issues}</div>
        </div>
        <div className="stat-card">
          <h3>Medium Priority</h3>
          <div className="number">{dashboardData.medium_issues}</div>
        </div>
        <div className="stat-card">
          <h3>Low Priority</h3>
          <div className="number">{dashboardData.low_issues}</div>
        </div>
        <div className="stat-card resolved">
          <h3>Resolved Issues</h3>
          <div className="number">{dashboardData.resolved_issues}</div>
        </div>
        <div className="stat-card">
          <h3>Pending Issues</h3>
          <div className="number">{dashboardData.pending_issues}</div>
        </div>
        <div className="stat-card">
          <h3>Total Issues</h3>
          <div className="number">{dashboardData.total_issues}</div>
        </div>
        <div className="stat-card">
          <h3>Resolution Rate</h3>
          <div className="number">
            {dashboardData.total_issues > 0
              ? ((dashboardData.resolved_issues / dashboardData.total_issues) * 100).toFixed(1)
              : 0}%
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
        {/* Priority Distribution */}
        <div className="chart-container">
          <h3>Issues by Priority Level</h3>
          <Pie
            data={{
              labels: priorityLabels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
              datasets: [{
                data: priorityValues,
                backgroundColor: priorityLabels.map(l => priorityColors[l] || '#999'),
                borderColor: '#fff',
                borderWidth: 2
              }]
            }}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom'
                }
              }
            }}
          />
        </div>

        {/* Type Distribution */}
        <div className="chart-container">
          <h3>Issues by Type</h3>
          <Bar
            data={{
              labels: typeLabels.map(t => t.replace(/_/g, ' ')),
              datasets: [{
                label: 'Count',
                data: typeValues,
                backgroundColor: typeColors,
                borderColor: '#fff',
                borderWidth: 1
              }]
            }}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: {
                legend: {
                  display: false
                }
              }
            }}
          />
        </div>
      </div>

      {/* Status Distribution */}
      <div className="chart-container" style={{ marginBottom: '2rem' }}>
        <h3>Issues by Status</h3>
        <Bar
          data={{
            labels: statusLabels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
            datasets: [{
              label: 'Count',
              data: statusValues,
              backgroundColor: statusLabels.map(s => statusColors[s] || '#999'),
              borderColor: '#fff',
              borderWidth: 1
            }]
          }}
          options={{
            responsive: true,
            plugins: {
              legend: {
                display: false
              }
            }
          }}
        />
      </div>

      {/* Recent Issues */}
      <div className="chart-container">
        <h3>Recent Issues</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Upvotes</th>
                <th>Reported</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.recent_issues?.map(issue => (
                <tr key={issue.id}>
                  <td>#{issue.id}</td>
                  <td>{issue.title}</td>
                  <td>{issue.issue_type}</td>
                  <td>
                    <span style={{
                      fontWeight: '600',
                      color: {
                        'critical': '#e74c3c',
                        'high': '#e67e22',
                        'medium': '#f39c12',
                        'low': '#27ae60'
                      }[issue.priority_level]
                    }}>
                      {issue.priority_level}
                    </span>
                  </td>
                  <td>
                    <span className={`issue-status status-${issue.status}`}>
                      {issue.status}
                    </span>
                  </td>
                  <td>{issue.upvotes}</td>
                  <td>{new Date(issue.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Locations */}
      {dashboardData.top_locations && dashboardData.top_locations.length > 0 && (
        <div className="chart-container" style={{ marginTop: '2rem' }}>
          <h3>Top Locations by Issue Count</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Issue Count</th>
                <th>Average Priority</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.top_locations.map((loc, idx) => (
                <tr key={idx}>
                  <td>{loc.location}</td>
                  <td><strong>{loc.issue_count}</strong></td>
                  <td>{loc.avg_priority.toFixed(1)}/100</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          onClick={fetchDashboardData}
          className="btn btn-primary"
        >
          🔄 Refresh Dashboard
        </button>
        <a
          href="/api/analytics/export/csv"
          className="btn btn-secondary"
          download
        >
          📥 Export as CSV
        </a>
      </div>
    </div>
  );
}

export default DashboardPage;
