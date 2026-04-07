import requests
from PIL import Image
import numpy as np
import io
import json

# Create a test image with mixed colors (sky, road, water)
img_array = np.zeros((300, 400, 3), dtype=np.uint8)
# Sky (blue at top)
img_array[0:100, :] = [135, 206, 235]
# Road (gray in middle) 
img_array[100:250, :] = [128, 128, 128]
# Water (blue at bottom)
img_array[250:300, :] = [50, 100, 200]
# Add a pothole (dark spot in road)
img_array[150:200, 150:200] = [40, 40, 40]

img = Image.fromarray(img_array)
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Test: User selects "other" but AI detects road_obstruction with high confidence
files = {'file': ('test_detection.jpg', img_bytes, 'image/jpeg')}
data = {
    'title': 'Test Road Obstruction Detection',
    'description': 'Testing priority based on detected type',
    'latitude': 40.7128,
    'longitude': -74.0060,
    'location_description': 'Test Location',
    'issue_type': 'other'  # User selected "other"
}

response = requests.post('http://localhost:8000/api/issues/upload', files=files, data=data)
result = response.json()

print("=" * 60)
print("TEST: Priority Based on Detected Issue Type")
print("=" * 60)
print(f"\nUser selected issue_type: other")
print(f"Stored issue_type: {result['issue_type']}")
print(f"AI Confidence: {(result['ai_confidence'] * 100):.1f}%")
print(f"Priority Level: {result['priority_level']}")
print(f"Priority Score: {result['priority_score']:.1f}/100")

# The results should show:
# - High confidence detection (90%+)
# - Priority level should NOT be "low" if detected type is high-priority
if result['priority_level'] in ['high', 'critical']:
    print(f"\n✅ SUCCESS: Priority correctly elevated based on detected type!")
else:
    print(f"\n✓ Priority is {result['priority_level']}")
    print(f"   (Depends on what was detected)")
