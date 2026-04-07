import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';


function ResolvedIssuesPage() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userUpvotes, setUserUpvotes] = useState(new Set());

  useEffect(() => {
    fetchResolvedIssues();
  }, []);

  const fetchResolvedIssues = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/issues/resolved/list');
      setIssues(response.data);
      setError('');
      
      // Check which issues user has upvoted
      checkUserUpvotes(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error loading resolved issues';
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
          params: { token, vote_type: 'satisfaction' }
        });
        if (response.data.has_upvoted) {
          upvotedIssues.add(issue.id);
        }
      } catch (err) {
        // Ignore errors
      }
    }
    
    setUserUpvotes(upvotedIssues);
  };

  const handleUpvote = async (issueId) => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please login to vote');
        return;
      }

      await axios.post(`/api/issues/${issueId}/upvote`, {}, {
        params: { token, vote_type: 'satisfaction' }
      });
      
      // Add to voted set
      setUserUpvotes(prev => new Set(prev).add(issueId));
      
      // Refresh issues
      fetchResolvedIssues();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error voting';
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
      <h1 style={{ marginBottom: '0.5rem' }}>✅ Resolved Issues</h1>
      <p style={{ marginBottom: '2rem', color: '#666' }}>
        Issues that have been resolved by authorities. Upvote to confirm your satisfaction!
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading resolved issues...</p>
        </div>
      ) : issues.length === 0 ? (
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          color: '#999'
        }}>
          <p>No resolved issues yet.</p>
          <Link to="/issues" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            View Open Issues
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
                  ✓ {issue.status.charAt(0).toUpperCase() + issue.status.slice(1)}
                </span>

                <p style={{ color: '#666', marginBottom: '1rem', fontSize: '0.9rem' }}>
                  Resolved: {new Date(issue.created_at).toLocaleDateString()}
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
                      background: userUpvotes.has(issue.id) ? '#95a5a6' : '#27ae60',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      cursor: userUpvotes.has(issue.id) ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      opacity: userUpvotes.has(issue.id) ? 0.7 : 1
                    }}
                  >
                    {userUpvotes.has(issue.id) ? '✓ Satisfied' : '👍 Satisfied'} ({issue.satisfaction_votes || 0})
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
    </div>
  );
}

export default ResolvedIssuesPage;
