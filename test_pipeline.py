#!/usr/bin/env python
"""Test image analysis pipeline end-to-end"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.ai_detector import AIIssueDetector
from backend.app.services.simple_analyzer import SimpleImageAnalyzer

# Create a test image (simple colored square)
from PIL import Image
import numpy as np

print("\n=== Creating test image ===")
# Create a simple test image
img_array = np.ones((200, 200, 3), dtype=np.uint8)
img_array[:100, :100] = [50, 50, 50]  # Dark area (like pothole)
img_array[100:, :100] = [100, 200, 100]  # Green area
img_array[:100, 100:] = [50, 100, 200]  # Blue area (water)
img_array[100:, 100:] = [100, 100, 100]  # Gray area

img = Image.fromarray(img_array)
test_image_path = "test_image.jpg"
img.save(test_image_path)
print(f"✓ Test image saved: {test_image_path}")

print("\n=== Testing SimpleImageAnalyzer ===")
analyzer = SimpleImageAnalyzer()
print(f"Analyzer initialized: {analyzer is not None}")
print(f"Infrastructure detector: {analyzer.detector is not None}")

print("\nAnalyzing test image...")
issue_type, confidence, features = analyzer.analyze_image(test_image_path)
print(f"Result: {issue_type} (confidence: {confidence:.2f})")
print(f"Features: {features}")

print("\n=== Testing AIIssueDetector ===")
detector = AIIssueDetector()
print("\nDetecting issue type...")
issue_type, confidence, detected_objects = detector.detect_issue_type(test_image_path)
print(f"Result: {issue_type} (confidence: {confidence:.2f})")
print(f"Detected objects: {detected_objects}")

# Clean up
os.remove(test_image_path)
print("\n✓ Test complete")
