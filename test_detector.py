#!/usr/bin/env python
"""Test YOLO detector initialization"""

import sys
sys.path.insert(0, '/content/c:/Users/Vanshaj Sharma/OneDrive/Desktop/local-problem-reporter')

from backend.app.services.yolo_detector import get_detector
from backend.app.services.dynamic_categorizer import DynamicIssueCategor

print("\n=== Testing YOLO Detector ===")
print(f"Python path: {sys.path[0]}")

try:
    detector = get_detector()
    print(f"✓ Detector initialized: {detector is not None}")
    print(f"✓ Model loaded: {detector.model is not None if detector else False}")
    if detector and detector.model:
        print(f"✓ YOLO detector is READY and WORKING!")
    else:
        print(f"✗ YOLO detector model is None")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing Dynamic Categorizer ===")
try:
    # Test with sample objects
    sample_objects = [
        {'class': 'rock', 'confidence': 0.95, 'bbox': [10, 20, 100, 200]},
        {'class': 'water', 'confidence': 0.87, 'bbox': [50, 60, 400, 500]},
    ]
    result = DynamicIssueCategor.categorize_detection(sample_objects)
    print(f"✓ Categorization test passed")
    print(f"  Primary issue: {result['primary_issue']['category'] if result['primary_issue'] else 'None'}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== Test Complete ===\n")
