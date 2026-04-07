import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const LocationMarker = ({ onLocationSelect, selectedLocation }) => {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onLocationSelect({
        latitude: lat.toFixed(6),
        longitude: lng.toFixed(6)
      });
    },
  });

  return selectedLocation ? (
    <Marker position={[selectedLocation.latitude, selectedLocation.longitude]}>
      <Popup>
        <div>
          <strong>Selected Location</strong>
          <br />
          Lat: {selectedLocation.latitude}
          <br />
          Lon: {selectedLocation.longitude}
        </div>
      </Popup>
    </Marker>
  ) : null;
};

const LocationPickerMap = ({ onSelect, initialLocation, searchQuery }) => {
  const [selectedLocation, setSelectedLocation] = useState(initialLocation || null);
  const [center, setCenter] = useState([40.7128, -74.0060]); // Default: New York
  const [mapKey, setMapKey] = useState(0);

  // Update center when searchQuery changes (user types location)
  useEffect(() => {
    if (searchQuery && searchQuery.length > 3) {
      // Try to geocode the search query
      const geocodeLocation = async () => {
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(searchQuery)}&format=json&limit=1`
          );
          const data = await response.json();
          if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);
            setCenter([lat, lon]);
            setMapKey(prev => prev + 1); // Force map re-render to center on new location
          }
        } catch (err) {
          console.log('Geocoding error:', err);
        }
      };
      geocodeLocation();
    }
  }, [searchQuery]);

  useEffect(() => {
    // Try to get user's current location on first load
    if (navigator.geolocation && !initialLocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setCenter([latitude, longitude]);
          setSelectedLocation({
            latitude: latitude.toFixed(6),
            longitude: longitude.toFixed(6)
          });
        },
        (error) => {
          console.log('Geolocation error:', error);
        }
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    onSelect(location);
  };

  return (
    <div style={{ width: '100%', borderRadius: '8px', overflow: 'hidden', border: '2px solid #ddd' }}>
      <MapContainer
        key={mapKey}
        center={center}
        zoom={13}
        style={{ height: '350px', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <LocationMarker
          onLocationSelect={handleLocationSelect}
          selectedLocation={selectedLocation}
        />
      </MapContainer>
      <div style={{ padding: '10px', background: '#f9f9f9', fontSize: '0.85em', color: '#666' }}>
        💡 <strong>Tip:</strong> Click on the map to mark the exact location of the issue
      </div>
    </div>
  );
};

export default LocationPickerMap;
