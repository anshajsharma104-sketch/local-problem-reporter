import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import LoginPage from './pages/LoginPage';
import ReportPage from './pages/ReportPage';
import DashboardPage from './pages/DashboardPage';
import IssuesListPage from './pages/IssuesListPage';
import IssueDetailPage from './pages/IssueDetailPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ResolvedIssuesPage from './pages/ResolvedIssuesPage';


function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
  const [isAuthority, setIsAuthority] = useState(localStorage.getItem('isAuthority') === 'true');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail'));

  useEffect(() => {
    // Check for token on mount
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
      setIsAuthority(localStorage.getItem('isAuthority') === 'true');
      setUserEmail(localStorage.getItem('userEmail'));
    }
  }, []);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {!authToken ? (
        <LoginPage />
      ) : (
        <div className="App">
          <NavBar 
            isAuthority={isAuthority} 
            userEmail={userEmail}
            onLogout={() => {
              localStorage.removeItem('authToken');
              localStorage.removeItem('userId');
              localStorage.removeItem('userEmail');
              localStorage.removeItem('isAuthority');
              localStorage.removeItem('userRole');
              window.location.href = '/';
            }}
          />

          <main className="main-content">
            <Routes>
              <Route path="/" element={<HomePage isAuthority={isAuthority} />} />
              <Route path="/report" element={<ReportPage />} />
              <Route path="/issues" element={<IssuesListPage />} />
              <Route path="/resolved" element={<ResolvedIssuesPage />} />
              <Route path="/issue/:id" element={<IssueDetailPage />} />
              {isAuthority && (
                <>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                </>
              )}
            </Routes>
          </main>

          <footer className="footer">
            <p>&copy; 2024 Local Problem Reporter. AI-powered infrastructure issue tracking.</p>
          </footer>
        </div>
      )}
    </Router>
  );
}


function NavBar({ isAuthority, userEmail, onLogout }) {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          🚨 <strong>Local Problem Reporter</strong>
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">Home</Link>
          </li>
          <li className="nav-item">
            <Link to="/report" className="nav-link">Report Issue</Link>
          </li>
          <li className="nav-item">
            <Link to="/issues" className="nav-link">View Issues</Link>
          </li>
          <li className="nav-item">
            <Link to="/resolved" className="nav-link">✅ Resolved</Link>
          </li>
          {isAuthority && (
            <>
              <li className="nav-item">
                <Link to="/dashboard" className="nav-link">Dashboard</Link>
              </li>
              <li className="nav-item">
                <Link to="/analytics" className="nav-link">Analytics</Link>
              </li>
            </>
          )}
          <li className="nav-item" style={{ marginLeft: 'auto' }}>
            <span style={{ color: '#667eea', fontWeight: '600', marginRight: '1rem' }}>
              {isAuthority ? '👨‍💼' : '👤'} {userEmail}
            </span>
          </li>
          <li className="nav-item">
            <button 
              onClick={onLogout}
              className="nav-toggle-btn"
              style={{ background: '#e74c3c', color: 'white' }}
            >
              🔓 Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}


function HomePage({ isAuthority }) {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>Local Problem Reporter</h1>
        <p>Report infrastructure issues in your community. AI categorizes, prioritizes, and authorities respond.</p>
        <div className="hero-buttons">
          <Link to="/report" className="btn btn-primary">Report an Issue</Link>
          <Link to="/issues" className="btn btn-secondary">View Issues</Link>
          <Link to="/resolved" className="btn btn-secondary">✅ Resolved Issues</Link>
        </div>
      </div>

      <section className="features">
        <div className="feature-card">
          <h3>📸 Image Recognition</h3>
          <p>Upload photos of issues. Our AI automatically detects and categorizes problems.</p>
        </div>
        <div className="feature-card">
          <h3>📊 Smart Prioritization</h3>
          <p>Issues are automatically prioritized based on severity, location, and community reports.</p>
        </div>
        <div className="feature-card">
          <h3>🗺️ Map-Based Tracking</h3>
          <p>View all reported issues on an interactive map. Track progress in real-time.</p>
        </div>
        <div className="feature-card">
          <h3>👥 Community-Driven</h3>
          <p>Upvote issues to increase priority. Help authorities focus on what matters most.</p>
        </div>
      </section>

      <section className="info">
        <h2>How It Works</h2>
        <ol className="steps">
          <li><strong>Report:</strong> Upload image of road damage, garbage, water leak, etc.</li>
          <li><strong>AI Analyzes:</strong> System detects issue type and severity automatically</li>
          <li><strong>Community Votes:</strong> Others can upvote to increase priority</li>
          <li><strong>Authorities Respond:</strong> Local authorities track and resolve issues</li>
        </ol>
      </section>

      {isAuthority && (
        <section className="authority-action">
          <h2>Authority Tools</h2>
          <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
        </section>
      )}
    </div>
  );
}


export default App;
