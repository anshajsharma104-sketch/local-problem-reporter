import React, { useState, useRef } from 'react';
import axios from 'axios';
import LocationPickerMap from '../components/LocationPickerMap';


function ReportPage() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    latitude: '',
    longitude: '',
    location_description: '',
    issue_type: 'auto'
  });

  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  const [showMapPicker, setShowMapPicker] = useState(false);
  const fileInputRef = useRef(null);

  const issueTypes = [    { value: 'auto', label: '🤖 Auto-Detect (AI Analysis)' },    { value: 'road_damage', label: '🛣️ Road Damage (Pothole, Crack)' },
    { value: 'garbage', label: '🗑️ Garbage (Litter, Trash)' },
    { value: 'water_leak', label: '💧 Water Leak (Puddle, Drainage)' },
    { value: 'traffic', label: '🚗 Traffic Issue (Congestion, Signal)' },
    { value: 'construction', label: '🏗️ Construction (Blocked Road)' },
    { value: 'landslide', label: '⛰️ Landslide (Erosion, Collapse)' },
    { value: 'other', label: '📌 Other' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLocationSearch = async (query) => {
    if (query.length < 3) {
      setLocationSuggestions([]);
      return;
    }

    try {
      const response = await axios.get(`https://nominatim.openstreetmap.org/search`, {
        params: {
          q: query,
          format: 'json',
          limit: 5
        }
      });
      setLocationSuggestions(response.data || []);
      setShowLocationSuggestions(true);
    } catch (err) {
      console.error('Error fetching location suggestions:', err);
      setLocationSuggestions([]);
    }
  };

  const handleLocationSelect = (suggestion) => {
    setFormData(prev => ({
      ...prev,
      latitude: parseFloat(suggestion.lat),
      longitude: parseFloat(suggestion.lon),
      location_description: suggestion.display_name
    }));
    setShowLocationSuggestions(false);
    setLocationSuggestions([]);
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6)
          }));
        },
        () => {
          setError('Unable to get your location. Please enable location services.');
        }
      );
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (!image) {
      setError('Please select an image');
      return;
    }

    if (!formData.title.trim()) {
      setError('Please enter a title');
      return;
    }

    if (!formData.latitude || !formData.longitude) {
      setError('Please provide location coordinates');
      return;
    }

    setLoading(true);

    try {
      const form = new FormData();
      form.append('file', image);
      form.append('title', formData.title);
      form.append('description', formData.description);
      form.append('latitude', parseFloat(formData.latitude));
      form.append('longitude', parseFloat(formData.longitude));
      form.append('location_description', formData.location_description);
      form.append('issue_type', formData.issue_type);

      console.log('Submitting form data:', {
        title: formData.title,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        description: formData.description,
        location_description: formData.location_description
      });

      const response = await axios.post('/api/issues/upload', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setAiResult(response.data);
      const confidenceText = response.data.ai_confidence > 0.3 ? 
        ` | 🎯 Detected: ${response.data.issue_type} (${(response.data.ai_confidence * 100).toFixed(0)}% confident)` : 
        '';
      setSuccess(`✓ Issue reported successfully! ID: ${response.data.id}${confidenceText}`);

      // Reset form (keep issue_type as 'auto' - don't change until user manually selects)
      setTimeout(() => {
        setFormData({
          title: '',
          description: '',
          latitude: '',
          longitude: '',
          location_description: '',
          issue_type: 'auto'
        });
        setImage(null);
        setPreview(null);
        setAiResult(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 2000);
    } catch (err) {
      console.error('Error submitting issue:', err.response?.data || err.message);
      let errorMessage = 'Error submitting issue';
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => e.msg || e.message || JSON.stringify(e)).join('; ');
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else {
          errorMessage = JSON.stringify(err.response.data.detail);
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-page">
      <div className="report-form">
        <h2>📝 Report an Issue</h2>
        <p style={{ marginBottom: '2rem', color: '#666' }}>
          Upload an image and describe the problem. Our AI will categorize it and calculate priority.
        </p>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          {/* Title */}
          <div className="form-group">
            <label htmlFor="title">Issue Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="e.g., Large pothole on Main Street"
              required
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Provide additional details about the issue..."
            />
          </div>

          {/* Image Upload */}
          <div className="form-group">
            <label htmlFor="image">Upload Image *</label>
            <input
              ref={fileInputRef}
              type="file"
              id="image"
              accept="image/*"
              onChange={handleImageSelect}
              required
            />
          </div>

          {preview && (
            <div className="image-preview">
              <img src={preview} alt="Preview" />
            </div>
          )}

          {/* Issue Type Selector */}
          <div className="form-group">
            <label htmlFor="issue_type">Issue Type *</label>
            <select
              id="issue_type"
              name="issue_type"
              value={formData.issue_type}
              onChange={handleInputChange}
              required
            >
              {issueTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <p style={{ marginTop: '0.5rem', fontSize: '0.85em', color: '#999' }}>
              📌 Select the category that best describes this issue
            </p>
          </div>

          {/* Location */}
          <div className="form-group">
            <label>📍 Location</label>
            <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={handleGetLocation}
                className="btn btn-secondary"
              >
                📍 Get My Location
              </button>
              <button
                type="button"
                onClick={() => setShowMapPicker(!showMapPicker)}
                className="btn btn-secondary"
              >
                {showMapPicker ? '✓ Close Map' : '🗺️ Pick on Map'}
              </button>
            </div>

            {/* Map Picker */}
            {showMapPicker && (
              <div style={{ marginBottom: '1.5rem' }}>
                <LocationPickerMap
                  onSelect={(location) => {
                    setFormData(prev => ({
                      ...prev,
                      latitude: location.latitude,
                      longitude: location.longitude
                    }));
                  }}
                  initialLocation={formData.latitude && formData.longitude ? {
                    latitude: parseFloat(formData.latitude),
                    longitude: parseFloat(formData.longitude)
                  } : null}
                  searchQuery={formData.location_description}
                />
              </div>
            )}
          </div>

          {/* Latitude */}
          <div className="form-group">
            <label htmlFor="latitude">Latitude *</label>
            <input
              type="number"
              id="latitude"
              name="latitude"
              step="0.000001"
              value={formData.latitude}
              onChange={handleInputChange}
              placeholder="e.g., 40.7128"
              required
            />
          </div>

          {/* Longitude */}
          <div className="form-group">
            <label htmlFor="longitude">Longitude *</label>
            <input
              type="number"
              id="longitude"
              name="longitude"
              step="0.000001"
              value={formData.longitude}
              onChange={handleInputChange}
              placeholder="e.g., -74.0060"
              required
            />
          </div>

          {/* Location Description with Search */}
          <div className="form-group">
            <label htmlFor="location_description">Location Description (with search)</label>
            <input
              type="text"
              id="location_description"
              name="location_description"
              value={formData.location_description}
              onChange={(e) => {
                const value = e.target.value;
                setFormData(prev => ({
                  ...prev,
                  location_description: value
                }));
                handleLocationSearch(value);
              }}
              placeholder="Search for a place or address..."
              autoComplete="off"
            />
            {showLocationSuggestions && locationSuggestions.length > 0 && (
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '4px',
                maxHeight: '200px',
                overflowY: 'auto',
                marginTop: '0.5rem',
                backgroundColor: '#fff'
              }}>
                {locationSuggestions.map((suggestion, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleLocationSelect(suggestion)}
                    style={{
                      padding: '0.75rem',
                      borderBottom: idx < locationSuggestions.length - 1 ? '1px solid #eee' : 'none',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                    onMouseLeave={(e) => e.target.style.background = 'transparent'}
                  >
                    {suggestion.display_name}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Result */}
          {aiResult && (
            <div className="ai-detection-result">
              <h4>🤖 AI Analysis Result</h4>
              <p><strong>Issue Type:</strong>
                <span className="detection-badge">{aiResult.issue_type}</span>
              </p>
              <p><strong>Confidence:</strong> {(aiResult.ai_confidence * 100).toFixed(1)}%</p>
              <p><strong>Priority Level:</strong>
                <span className={`priority-${aiResult.priority_level}`} style={{ marginLeft: '0.5rem', fontWeight: 'bold' }}>
                  {aiResult.priority_level.toUpperCase()}
                </span>
              </p>
              <p><strong>Priority Score:</strong> {aiResult.priority_score.toFixed(1)}/100</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span> Processing...
              </>
            ) : (
              '🚀 Submit Issue'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ReportPage;
