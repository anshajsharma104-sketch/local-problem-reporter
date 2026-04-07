"""
YOLO-based object detection for infrastructure issues.
Uses YOLOv8 (ultralytics) to identify objects in images and classify infrastructure problems.
"""

from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import logging
from typing import Dict, List, Tuple
import os

logger = logging.getLogger(__name__)

# Suppress ultralytics telemetry
os.environ['YOLO_VERBOSE'] = '0'


class YOLODetector:
    """Detects infrastructure issues using YOLOv8 object detection."""
    
    def __init__(self, model_name: str = 'yolov8n', confidence: float = 0.45):
        """
        Initialize YOLO detector.
        
        Args:
            model_name: YOLOv8 model to use ('yolov8n', 'yolov8s', 'yolov8m', 'yolov8l')
            confidence: Detection confidence threshold (0-1)
        """
        try:
            logger.info(f"Loading {model_name}...")
            self.model = YOLO(f'{model_name}.pt')
            self.conf = confidence
            logger.info(f"✓ {model_name} model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect(self, image_path: str) -> Dict:
        """
        Detect objects in image using YOLO.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with detected objects and their classifications
        """
        if not self.model:
            logger.warning("YOLO model not loaded, returning empty detections")
            return {'objects': [], 'has_potholes': False, 'has_rocks': False, 'has_vegetation': False}
        
        try:
            # Run detection
            results = self.model(image_path, conf=self.conf, verbose=False)
            
            # Parse results
            detections = self._parse_detections(results)
            
            logger.info(f"YOLO detected: {len(detections['objects'])} objects")
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return {'objects': [], 'has_potholes': False, 'has_rocks': False, 'has_vegetation': False}
    
    def _parse_detections(self, results) -> Dict:
        """
        Parse YOLOv8 results into structured format.
        
        Returns:
            Dictionary with classified detections
        """
        objects = []
        has_potholes = False
        has_rocks = False
        has_vegetation = False
        has_vehicles = False
        has_water = False
        
        try:
            # Extract detections from YOLO results
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = result.names[cls]
                    
                    # Get bbox coordinates
                    bbox_coords = box.xyxy[0].tolist()
                    
                    obj = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': bbox_coords
                    }
                    objects.append(obj)
                    
                    # Classify detected object
                    class_lower = class_name.lower()
                    
                    if class_lower in ['pothole', 'crater', 'hole', 'damage']:
                        has_potholes = True
                        obj['issue_type'] = 'pothole'
                    elif class_lower in ['rock', 'stone', 'debris', 'rubble', 'boulder']:
                        has_rocks = True
                        obj['issue_type'] = 'obstruction'
                    elif class_lower in ['tree', 'plant', 'vegetation', 'bush']:
                        has_vegetation = True
                        obj['issue_type'] = 'vegetation'
                    elif class_lower in ['car', 'truck', 'bus', 'vehicle', 'motorcycle', 'bicycle']:
                        has_vehicles = True
                        obj['issue_type'] = 'parked_vehicle'
                    elif class_lower in ['person', 'people', 'crowd']:
                        obj['issue_type'] = 'people'
                    
        except Exception as e:
            logger.error(f"Error parsing YOLO detections: {e}")
        
        return {
            'objects': objects,
            'has_potholes': has_potholes,
            'has_rocks': has_rocks,
            'has_vegetation': has_vegetation,
            'has_vehicles': has_vehicles,
            'has_water': has_water,
            'object_count': len(objects)
        }
    
    def get_dominant_objects(self, detections: Dict, top_n: int = 3) -> List[Dict]:
        """
        Get the most confident detected objects.
        
        Args:
            detections: Detection results from detect()
            top_n: Number of top objects to return
            
        Returns:
            List of top-confidence objects
        """
        sorted_objects = sorted(
            detections['objects'],
            key=lambda x: x['confidence'],
            reverse=True
        )
        return sorted_objects[:top_n]
    
    def analyze_road_hazards(self, detections: Dict) -> Dict:
        """
        Analyze detected objects for road hazards.
        
        Args:
            detections: Detection results
            
        Returns:
            Dictionary with hazard analysis
        """
        hazard_score = 0
        detected_hazards = []
        
        # Check for blocking objects
        rock_objects = [obj for obj in detections['objects'] if 'rock' in obj.get('class', '').lower()]
        if rock_objects:
            hazard_score += 30
            detected_hazards.append({
                'type': 'rockfall/debris',
                'count': len(rock_objects),
                'severity': 'high' if len(rock_objects) > 2 else 'medium'
            })
        
        # Check for vegetation overgrowth
        veg_objects = [obj for obj in detections['objects'] if 'tree' in obj.get('class', '').lower()]
        if len(veg_objects) > 3:  # Multiple trees = overgrowth concern
            hazard_score += 20
            detected_hazards.append({
                'type': 'vegetation_overgrowth',
                'count': len(veg_objects),
                'severity': 'medium'
            })
        
        # Check for vehicles parked (obstruction)
        vehicle_objects = [obj for obj in detections['objects'] if obj.get('class', '').lower() in ['car', 'truck']]
        if vehicle_objects:
            hazard_score += 10
            detected_hazards.append({
                'type': 'parked_vehicle',
                'count': len(vehicle_objects),
                'severity': 'low'
            })
        
        return {
            'hazard_score': min(hazard_score, 100),
            'hazards': detected_hazards,
            'total_objects': detections['object_count']
        }


# Global detector instance
_detector = None


def get_detector() -> YOLODetector:
    """Get or create global YOLO detector instance."""
    global _detector
    if _detector is None:
        _detector = YOLODetector(model_name='yolov8n', confidence=0.45)
    return _detector
