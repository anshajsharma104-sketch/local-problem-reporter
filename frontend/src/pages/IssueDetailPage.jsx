import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import LocationDisplay from '../components/LocationDisplay';


function IssueDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAuthority] = useState(localStorage.getItem('isAuthority') === 'true');
  const [statusUpdate, setStatusUpdate] = useState('');
  const [notes, setNotes] = useState('');
  const [updating, setUpdating] = useState(false);
  const [userHasUpvoted, setUserHasUpvoted] = useState(false);

  useEffect(() => {
    fetchIssueDetail();
  }, [id]);

  const fetchIssueDetail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/issues/${id}`);
      setIssue(response.data);
      setError('');
      
      // Check if user has voted (use appropriate vote type based on status)
      checkUserUpvote(response.data.id, response.data.status);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error loading issue';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const checkUserUpvote = async (issueId, status) => {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
      // Use satisfaction vote for resolved, priority for others
      const voteType = status === 'resolved' ? 'satisfaction' : 'priority';
      const response = await axios.get(`/api/issues/${issueId}/has-upvoted`, {
        params: { token, vote_type: voteType }
      });
      setUserHasUpvoted(response.data.has_upvoted);
    } catch (err) {
      // Ignore errors
    }
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    if (!statusUpdate.trim()) {
      setError('Please select a new status');
      return;
    }

    setUpdating(true);
    try {
      const token = localStorage.getItem('authToken');
      await axios.patch(
        `/api/issues/${id}/status`,
        {},
        {
          params: {
            new_status: statusUpdate,
            notes: notes,
            token: token
          }
        }
      );
      setError('');
      setStatusUpdate('');
      setNotes('');
      fetchIssueDetail();
      alert('✓ Status updated successfully');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error updating status';
      setError(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteIssue = async () => {
    if (window.confirm('Are you sure you want to delete this resolved issue? This action cannot be undone.')) {
      try {
        const token = localStorage.getItem('authToken');
        const userId = localStorage.getItem('userId');
        await axios.delete(
          `/api/issues/${id}/delete`,
          {
            params: {
              user_id: userId,
              token: token
            }
          }
        );
        alert('✓ Issue deleted successfully');
        navigate('/issues');
      } catch (err) {
        const errorMessage = err.response?.data?.detail || 'Error deleting issue';
        setError(errorMessage);
      }
    }
  };

  const handleUpvote = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please login to vote');
        return;
      }

      // Use satisfaction vote for resolved, priority for others
      const voteType = issue.status === 'resolved' ? 'satisfaction' : 'priority';

      await axios.post(`/api/issues/${issue.id}/upvote`, {}, {
        params: { token, vote_type: voteType }
      });
      
      setUserHasUpvoted(true);
      fetchIssueDetail();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Error voting issue';
      setError(errorMessage);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading issue details...</p>
      </div>
    );
  }

  if (!issue) {
    return (
      <div className="alert alert-error">
        <p>{error || 'Issue not found'}</p>
        <button onClick={() => navigate('/issues')} className="btn btn-primary">
          Go Back to Issues
        </button>
      </div>
    );
  }

  const detectedObjects = issue.ai_detected_objects ? JSON.parse(issue.ai_detected_objects) : [];

  return (
    <div className="issue-detail-page">
      <button
        onClick={() => navigate('/issues')}
        style={{
          marginBottom: '1.5rem',
          background: '#f0f0f0',
          border: 'none',
          padding: '0.5rem 1rem',
          borderRadius: '6px',
          cursor: 'pointer'
        }}
      >
        ← Back to Issues
      </button>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="issue-detail">
        <div className="issue-detail-header">
          <h1>{issue.title}</h1>
          <p>{issue.location_description}</p>
        </div>

        <div className="issue-detail-body">
          {/* Main Info */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
            <div>
              <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>Issue Information</h3>

              <div className="detail-row">
                <label>Type:</label>
                <span style={{ fontWeight: '600', color: '#e67e22' }}>{issue.issue_type}</span>
              </div>

              <div className="detail-row">
                <label>Status:</label>
                <span className={`issue-status status-${issue.status}`}>
                  {issue.status.toUpperCase()}
                </span>
              </div>

              <div className="detail-row">
                <label>Priority Level:</label>
                <span style={{ 
                  fontWeight: '600',
                  color: {
                    'critical': '#e74c3c',
                    'high': '#e67e22',
                    'medium': '#f39c12',
                    'low': '#27ae60'
                  }[issue.priority_level]
                }}>
                  {issue.priority_level.toUpperCase()}
                </span>
              </div>

              <div className="detail-row">
                <label>Priority Score:</label>
                <span>{issue.priority_score.toFixed(1)}/100</span>
              </div>

              <div className="detail-row">
                <label>Upvotes:</label>
                <span>{issue.upvotes}</span>
              </div>

              <div className="detail-row">
                <label>Reported:</label>
                <span>{new Date(issue.created_at).toLocaleString()}</span>
              </div>

              {issue.resolved_at && (
                <div className="detail-row">
                  <label>Resolved:</label>
                  <span>{new Date(issue.resolved_at).toLocaleString()}</span>
                </div>
              )}
            </div>

            <div>
              <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>Location & AI Analysis</h3>

              <div className="detail-row">
                <label>Latitude:</label>
                <span>{issue.latitude.toFixed(6)}</span>
              </div>

              <div className="detail-row">
                <label>Longitude:</label>
                <span>{issue.longitude.toFixed(6)}</span>
              </div>

              <div className="detail-row">
                <label>AI Confidence:</label>
                <span>{(issue.ai_confidence * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* Description */}
          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>Description</h3>
            <p style={{ lineHeight: '1.6', color: '#555', whiteSpace: 'pre-wrap' }}>
              {issue.description || 'No description provided'}
            </p>
          </div>

          {/* Image */}
          {issue.image_path && (
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>📷 Uploaded Image</h3>
              <img 
                src={issue.image_path} 
                alt="Issue" 
                style={{
                  maxWidth: '100%',
                  maxHeight: '500px',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0',
                  display: 'block'
                }}
              />
            </div>
          )}

          {/* Location Display with Map */}
          <LocationDisplay issue={issue} />

          {/* Upvote Button */}
          <div style={{ marginBottom: '2rem', borderTop: '1px solid #eee', paddingTop: '1.5rem' }}>
            <button
              onClick={handleUpvote}
              disabled={userHasUpvoted}
              className="btn btn-secondary"
              style={{
                marginRight: '1rem',
                opacity: userHasUpvoted ? 0.6 : 1,
                cursor: userHasUpvoted ? 'not-allowed' : 'pointer'
              }}
            >
              {issue.status === 'resolved' ? (
                userHasUpvoted ? '✓ Satisfied' : '👍 Satisfied'
              ) : (
                userHasUpvoted ? '✓ Priority Vote Added' : '🚀 Help Prioritize'
              )} ({issue.status === 'resolved' ? issue.satisfaction_votes || 0 : issue.upvotes})
            </button>
            <span style={{ color: '#999' }}>
              {issue.status === 'resolved' ? 'Confirm you are satisfied with the solution' : 'Help increase priority of this issue'}
            </span>
          </div>

          {/* Authority Updates & Progress */}
          {issue.updates && issue.updates.length > 0 && (
            <div style={{ marginBottom: '2rem', borderTop: '1px solid #eee', paddingTop: '1.5rem' }}>
              <h3 style={{ marginBottom: '1.5rem', color: '#667eea' }}>📋 Authority Updates</h3>
              <div>
                {issue.updates.map((update, index) => (
                  <div key={update.id} style={{
                    background: '#f9f9f9',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    borderLeft: '4px solid #667eea'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div>
                        <span style={{ 
                          background: '#667eea',
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '4px',
                          fontWeight: 'bold',
                          fontSize: '0.9rem'
                        }}>
                          {update.status_update.toUpperCase()}
                        </span>
                      </div>
                      <span style={{ color: '#999', fontSize: '0.9rem' }}>
                        {new Date(update.created_at).toLocaleString()}
                      </span>
                    </div>
                    {update.notes && (
                      <p style={{ marginTop: '0.75rem', color: '#555', whiteSpace: 'pre-wrap' }}>
                        <strong>Notes:</strong> {update.notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Authority Status Update */}
          {isAuthority && issue.status !== 'resolved' && (
            <div style={{
              background: '#f0f4ff',
              padding: '2rem',
              borderRadius: '12px',
              marginTop: '2rem',
              borderLeft: '4px solid #667eea'
            }}>
              <h3 style={{ marginBottom: '1.5rem', color: '#667eea' }}>Authority Actions</h3>

              <form onSubmit={handleUpdateStatus}>
                <div className="form-group">
                  <label htmlFor="status-update">Update Status</label>
                  <select
                    id="status-update"
                    value={statusUpdate}
                    onChange={(e) => setStatusUpdate(e.target.value)}
                  >
                    <option value="">Select new status...</option>
                    {issue.status === 'reported' && (
                      <option value="investigating">Move to Investigating</option>
                    )}
                    {issue.status === 'investigating' && (
                      <>
                        <option value="reported">Move back to Reported</option>
                        <option value="resolved">Mark as Resolved</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="notes">Notes</label>
                  <textarea
                    id="notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add notes about the action taken..."
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-success"
                  disabled={updating || !statusUpdate}
                >
                  {updating ? 'Updating...' : '✓ Update Status'}
                </button>
              </form>
            </div>
          )}

          {/* Authority Delete Resolved Issue */}
          {isAuthority && issue.status === 'resolved' && (
            <div style={{
              background: '#ffe0e0',
              padding: '2rem',
              borderRadius: '12px',
              marginTop: '2rem',
              borderLeft: '4px solid #e74c3c'
            }}>
              <h3 style={{ marginBottom: '1rem', color: '#c0392b' }}>🗑️ Delete Resolved Issue</h3>
              <p style={{ marginBottom: '1rem', color: '#555' }}>
                Requirements: Issue must have at least 5 user confirmations (upvotes).
              </p>
              <p style={{ marginBottom: '1.5rem', color: issue.upvotes >= 5 ? '#27ae60' : '#e74c3c', fontWeight: '600' }}>
                Current confirmations: {issue.upvotes}/5
              </p>
              <button
                onClick={handleDeleteIssue}
                disabled={issue.upvotes < 5}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: issue.upvotes >= 5 ? '#e74c3c' : '#ccc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: issue.upvotes >= 5 ? 'pointer' : 'not-allowed',
                  fontWeight: '600',
                  opacity: issue.upvotes >= 5 ? 1 : 0.5
                }}
              >
                {issue.upvotes >= 5 ? '🗑️ Delete Issue' : `Need ${5 - issue.upvotes} more upvotes`}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default IssueDetailPage;
