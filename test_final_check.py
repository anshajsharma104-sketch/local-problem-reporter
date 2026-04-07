import requests
from PIL import Image
import numpy as np
import io

# Create a test image with water
img_array = np.full((300, 400, 3), [50, 100, 200], dtype=np.uint8)  # All water-like blue
img = Image.fromarray(img_array)
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

files = {'file': ('test_final.jpg', img_bytes, 'image/jpeg')}
data = {
    'title': 'Final Test - Water Flooding',
    'description': 'Checking detected objects in response',
    'latitude': 40.7128,
    'longitude': -74.0060,
    'location_description': 'Test',
    'issue_type': 'auto'
}

response = requests.post('http://localhost:8000/api/issues/upload', files=files, data=data)
result = response.json()

print("=" * 60)
print("RESPONSE FIELDS CHECK")
print("=" * 60)
print(f"\nAPI Response includes these fields:")
for key in result.keys():
    print(f"  - {key}")

print(f"\n{'✓' if 'ai_detected_objects' not in result else '✗'} ai_detected_objects in response: {'ai_detected_objects' in result}")
if 'ai_detected_objects' in result:
    print(f"  Value: {result['ai_detected_objects'][:100]}...")  # Show first 100 chars
else:
    print(f"  (Hidden from API response - good!)")

print(f"\n✅ Issue Detection Summary:")
print(f"   Type: {result['issue_type']}")
print(f"   Confidence: {(result['ai_confidence'] * 100):.1f}%")
print(f"   Priority: {result['priority_level'].upper()}")
print(f"   Score: {result['priority_score']:.1f}/100")
