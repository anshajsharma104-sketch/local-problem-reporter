import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const LocationDisplay = ({ issue }) => {
  const [addressData, setAddressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAddress = async () => {
      try {
        const response = await axios.get(`/api/issues/${issue.id}/address`);
        setAddressData(response.data);
      } catch (err) {
        console.error('Error fetching address:', err);
        setError('Could not fetch address');
        // Set fallback data
        setAddressData({
          location_description: issue.location_description,
          street_address: `Lat: ${issue.latitude?.toFixed(4)}, Lon: ${issue.longitude?.toFixed(4)}`,
          latitude: issue.latitude,
          longitude: issue.longitude
        });
      } finally {
        setLoading(false);
      }
    };

    if (issue?.id) {
      fetchAddress();
    }
    // Using issue.id only to avoid unnecessary re-fetches when other issue properties change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [issue?.id]);

  if (loading) {
    return <div style={{ padding: '20px', color: '#666' }}>Loading location...</div>;
  }

  if (!addressData || !issue.latitude || !issue.longitude) {
    return <div style={{ padding: '20px', color: '#999' }}>Location not available</div>;
  }

  return (
    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
      <h3 style={{ marginTop: 0, color: '#333' }}>📍 Location Details</h3>
      
      {/* User's location description */}
      {addressData.location_description && (
        <div style={{ marginBottom: '12px' }}>
          <strong>Reporter Description:</strong>
          <p style={{ margin: '5px 0 0 0', color: '#555' }}>{addressData.location_description}</p>
        </div>
      )}

      {/* Street address (from reverse geocoding) */}
      {addressData.street_address && (
        <div style={{ marginBottom: '12px' }}>
          <strong>Street Address:</strong>
          <p style={{ margin: '5px 0 0 0', color: '#555' }}>{addressData.street_address}</p>
        </div>
      )}

      {/* Coordinates */}
      <div style={{ marginBottom: '12px', fontSize: '0.9em' }}>
        <strong>Coordinates:</strong>
        <p style={{ margin: '5px 0 0 0', color: '#999' }}>
          {addressData.latitude?.toFixed(4)}°N, {addressData.longitude?.toFixed(4)}°E
        </p>
      </div>

      {/* Interactive Map */}
      <div style={{ marginTop: '15px', borderRadius: '6px', overflow: 'hidden', border: '1px solid #ddd' }}>
        <MapContainer
          center={[addressData.latitude, addressData.longitude]}
          zoom={16}
          style={{ height: '300px', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <Marker position={[addressData.latitude, addressData.longitude]}>
            <Popup>
              <div>
                <strong>{issue.issue_type?.replace('_', ' ').toUpperCase()}</strong>
                <br />
                {addressData.street_address}
                <br />
                <em style={{ fontSize: '0.85em' }}>Priority: {issue.priority_level}</em>
              </div>
            </Popup>
          </Marker>
        </MapContainer>
      </div>

      {error && <div style={{ marginTop: '10px', color: '#d32f2f', fontSize: '0.9em' }}>⚠️ {error}</div>}
    </div>
  );
};

export default LocationDisplay;
