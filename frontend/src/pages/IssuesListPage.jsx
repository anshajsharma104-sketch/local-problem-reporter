import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';


function IssuesListPage() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userUpvotes, setUserUpvotes] = useState(new Set()); // Track upvoted issues
  const [filters, setFilters] = useState({
    priority: '',
    status: '',
    issue_type: ''
  });

  useEffect(() => {
    fetchIssues();
  }, [filters]);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.status) params.append('status', filters.status);
      if (filters.issue_type) params.append('issue_type', filters.issue_type);

      const response = await axios.get(`/api/issues/all?${params}`);
      setIssues(response.data);
      setError('');
      
      // Check which issues user has upvoted
      checkUserUpvotes(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error loading issues';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const checkUserUpvotes = async (issues) => {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    const upvotedIssues = new Set();
    
    for (const issue of issues) {
      try {
        const response = await axios.get(`/api/issues/${issue.id}/has-upvoted`, {
          params: { token, vote_type: 'priority' }
        });
        if (response.data.has_upvoted) {
          upvotedIssues.add(issue.id);
        }
      } catch (err) {
        // Ignore errors when checking upvotes
      }
    }
    
    setUserUpvotes(upvotedIssues);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUpvote = async (issueId) => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please login to upvote');
        return;
      }

      const response = await axios.post(`/api/issues/${issueId}/upvote`, {}, {
        params: { token, vote_type: 'priority' }
      });
      
      // Add to upvoted set
      setUserUpvotes(prev => new Set(prev).add(issueId));
      
      // Refresh issues
      fetchIssues();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error upvoting issue';
      setError(errorMessage);
    }
  };

  const getPriorityIcon = (level) => {
    switch (level) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      case 'low':
        return '🟢';
      default:
        return '⚪';
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      road_damage: '🛣️',
      garbage: '♻️',
      water_leak: '💧',
      traffic: '🚗',
      construction: '🏗️',
      landslide: '⛰️',
      other: '❓'
    };
    return icons[type] || '❓';
  };

  return (
    <div className="issues-list-page">
      <h1 style={{ marginBottom: '2rem' }}>🗂️ Reported Issues</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Filters */}
      <div style={{
        background: 'white',
        padding: '1.5rem',
        borderRadius: '12px',
        marginBottom: '2rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        <div>
          <label className="filter-label">Priority Level</label>
          <select
            name="priority"
            value={filters.priority}
            onChange={handleFilterChange}
          >
            <option value="">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div>
          <label className="filter-label">Status</label>
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">All Status</option>
            <option value="reported">Reported</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div>
          <label className="filter-label">Issue Type</label>
          <select
            name="issue_type"
            value={filters.issue_type}
            onChange={handleFilterChange}
          >
            <option value="">All Types</option>
            <option value="road_damage">Road Damage</option>
            <option value="garbage">Garbage/Litter</option>
            <option value="water_leak">Water Leak</option>
            <option value="traffic">Traffic</option>
            <option value="construction">Construction</option>
            <option value="landslide">Landslide</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading issues...</p>
        </div>
      ) : issues.length === 0 ? (
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          color: '#999'
        }}>
          <p>No issues found. Be the first to report one!</p>
          <Link to="/report" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Report an Issue
          </Link>
        </div>
      ) : (
        <div className="issues-container">
          {issues.map(issue => (
            <div key={issue.id} className="issue-card">
              <div className="issue-card-header">
                <div className="issue-card-title">
                  {getTypeIcon(issue.issue_type)} {issue.title}
                </div>
                <span className="issue-type-badge">{issue.issue_type}</span>
              </div>

              {issue.image_path && (
                <div style={{
                  width: '100%',
                  maxHeight: '200px',
                  overflow: 'hidden',
                  borderRadius: '8px',
                  marginBottom: '1rem'
                }}>
                  <img 
                    src={issue.image_path} 
                    alt="Issue" 
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
                    }}
                  />
                </div>
              )}

              <div className="issue-card-body">
                <div className="issue-priority">
                  {getPriorityIcon(issue.priority_level)}
                  <span>{issue.priority_level.charAt(0).toUpperCase() + issue.priority_level.slice(1)}</span>
                </div>

                <span className={`issue-status status-${issue.status}`}>
                  {issue.status.charAt(0).toUpperCase() + issue.status.slice(1)}
                </span>

                <p style={{ color: '#666', marginBottom: '1rem', fontSize: '0.9rem' }}>
                  Reported: {new Date(issue.created_at).toLocaleDateString()}
                </p>

                <div style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
                  <p><strong>Priority Score:</strong> {issue.priority_score.toFixed(1)}/100</p>
                </div>

                <div className="upvote-section">
                  <button
                    onClick={() => handleUpvote(issue.id)}
                    className="upvote-btn"
                    disabled={userUpvotes.has(issue.id)}
                    style={{
                      opacity: userUpvotes.has(issue.id) ? 0.5 : 1,
                      cursor: userUpvotes.has(issue.id) ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {userUpvotes.has(issue.id) ? '✓ Priority Vote Added' : '🚀 Help Prioritize'} ({issue.upvotes})
                  </button>
                  <Link
                    to={`/issue/${issue.id}`}
                    style={{
                      marginLeft: 'auto',
                      color: '#667eea',
                      textDecoration: 'none',
                      fontWeight: '500'
                    }}
                  >
                    View Details →
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .filter-label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #333;
        }

        select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 1rem;
        }

        select:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
      `}</style>
    </div>
  );
}

export default IssuesListPage;
