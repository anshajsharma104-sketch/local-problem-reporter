import requests
from PIL import Image
import numpy as np
import io

# Create a simple test image
img_array = np.full((200, 200, 3), 128, dtype=np.uint8)
img = Image.fromarray(img_array)
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Upload with issue_type="other" to test that case
files = {'file': ('test_other.jpg', img_bytes, 'image/jpeg')}
data = {
    'title': 'Test Other Type',
    'description': 'Testing other type confidence',
    'latitude': 40.7128,
    'longitude': -74.0060,
    'location_description': 'Test',
    'issue_type': 'other'  # This is the case that was showing 0%
}

response = requests.post('http://localhost:8000/api/issues/upload', files=files, data=data)
result = response.json()
print(f"Issue type: {result['issue_type']}")
print(f"AI Confidence: {result['ai_confidence']}")
print(f"As percentage: {(result['ai_confidence'] * 100):.1f}%")
print(f"\n✓ Test passed - confidence is not 0%!" if result['ai_confidence'] > 0 else "\n✗ Still showing 0%!")
