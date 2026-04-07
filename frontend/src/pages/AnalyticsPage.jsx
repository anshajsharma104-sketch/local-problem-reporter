import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';


function AnalyticsPage() {
  const [statsData, setStatsData] = useState(null);
  const [resolutionData, setResolutionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const [statsRes, resRes] = await Promise.all([
        axios.get('/api/analytics/stats/by-type'),
        axios.get('/api/analytics/stats/resolution-rate')
      ]);

      setStatsData(statsRes.data);
      setResolutionData(resRes.data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error loading analytics';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <h1 style={{ marginBottom: '2rem' }}>📈 Detailed Analytics</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Resolution Rate Overview */}
      {resolutionData && (
        <div className="chart-container" style={{ marginBottom: '2rem' }}>
          <h2>Resolution Rate Statistics</h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{
              background: '#f0f4ff',
              padding: '1.5rem',
              borderRadius: '8px',
              border: '2px solid #667eea'
            }}>
              <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>Total Issues</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{resolutionData.total_issues}</p>
            </div>

            <div style={{
              background: '#e8f5e9',
              padding: '1.5rem',
              borderRadius: '8px',
              border: '2px solid #27ae60'
            }}>
              <h4 style={{ color: '#27ae60', marginBottom: '0.5rem' }}>Resolved</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{resolutionData.resolved}</p>
            </div>

            <div style={{
              background: '#fff3e0',
              padding: '1.5rem',
              borderRadius: '8px',
              border: '2px solid #f57c00'
            }}>
              <h4 style={{ color: '#f57c00', marginBottom: '0.5rem' }}>Pending</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{resolutionData.pending}</p>
            </div>

            <div style={{
              background: '#f3e5f5',
              padding: '1.5rem',
              borderRadius: '8px',
              border: '2px solid #7b1fa2'
            }}>
              <h4 style={{ color: '#7b1fa2', marginBottom: '0.5rem' }}>Resolution Rate</h4>
              <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>
                {resolutionData.overall_resolution_rate}%
              </p>
            </div>
          </div>

          <h3 style={{ marginBottom: '1rem' }}>Average Resolution Time</h3>
          <p style={{ fontSize: '1.5rem', color: '#667eea', fontWeight: 'bold' }}>
            {resolutionData.avg_resolution_time_hours}
          </p>
        </div>
      )}

      {/* Resolution Rate by Type */}
      {resolutionData && (
        <div className="chart-container" style={{ marginBottom: '2rem' }}>
          <h2>Resolution Rate by Issue Type</h2>

          <table className="data-table" style={{ marginTop: '1.5rem' }}>
            <thead>
              <tr>
                <th>Issue Type</th>
                <th>Total</th>
                <th>Resolved</th>
                <th>Pending</th>
                <th>Resolution Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(resolutionData.by_type || {}).map(([type, data]) => (
                <tr key={type}>
                  <td style={{ fontWeight: '600' }}>{type.replace(/_/g, ' ')}</td>
                  <td>{data.total}</td>
                  <td style={{ color: '#27ae60', fontWeight: '600' }}>{data.resolved}</td>
                  <td>{data.total - data.resolved}</td>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      background: '#f0f0f0',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '20px',
                      fontWeight: '600',
                      color: data.rate > 50 ? '#27ae60' : '#e67e22'
                    }}>
                      {data.rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Statistics by Issue Type */}
      {statsData && (
        <div className="chart-container">
          <h2>Detailed Statistics by Issue Type</h2>

          <table className="data-table" style={{ marginTop: '1.5rem' }}>
            <thead>
              <tr>
                <th>Issue Type</th>
                <th>Total Count</th>
                <th>Avg Priority</th>
                <th>Resolved</th>
                <th>Pending</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(statsData || {}).map(([type, stats]) => (
                <tr key={type}>
                  <td style={{ fontWeight: '600' }}>{type.replace(/_/g, ' ')}</td>
                  <td>{stats.total}</td>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      background: '#f0f0f0',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '20px',
                      fontWeight: '600'
                    }}>
                      {stats.avg_priority_score}/100
                    </span>
                  </td>
                  <td style={{ color: '#27ae60', fontWeight: '600' }}>{stats.resolved}</td>
                  <td style={{ color: '#e67e22' }}>{stats.pending}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          onClick={fetchAnalyticsData}
          className="btn btn-primary"
        >
          🔄 Refresh Analytics
        </button>
        <a
          href="/api/analytics/export/csv"
          className="btn btn-secondary"
          download
        >
          📥 Export as CSV
        </a>
      </div>

      <style jsx>{`
        .data-table {
          margin-top: 1.5rem;
        }
      `}</style>
    </div>
  );
}

export default AnalyticsPage;
