"""
Hybrid Image Analyzer: YOLOv5 Object Detection + Color Analysis
- YOLOv5 detects WHAT objects are in the image (rocks, vehicles, people, etc)
- Color analysis detects PATTERNS (water, dark holes, vegetation coverage)
- Combined confidence scoring for accurate issue detection
"""

from PIL import Image
import numpy as np
from typing import Tuple, List, Dict
import csv
import os
import torch
import yolov5


class SimpleImageAnalyzer:
    """Hybrid analyzer combining YOLOv5 + color analysis"""
    
    # YOLOv5 class names for issue detection
    OBJECT_CLASSES = {
        'person': 'people_on_road',
        'car': 'vehicle',
        'truck': 'vehicle',
        'motorcycle': 'vehicle',
        'bicycle': 'vehicle',
        'bus': 'vehicle',
        'dog': 'animal',
        'cat': 'animal',
        'horse': 'animal',
        'cow': 'animal',
        'bird': 'animal',
        'potted plant': 'vegetation',
        'plant': 'vegetation',
        'backpack': 'trash',
        'handbag': 'trash',
        'suitcase': 'trash',
        'bottle': 'trash',
        'cup': 'trash',
        'fork': 'trash',
        'knife': 'trash',
        'spoon': 'trash',
    }
    
    def __init__(self):
        """Initialize YOLOv5 model + CSV rules"""
        self.model = None
        self.rules = []
        self.detected_objects = {}
        self._load_yolov5_model()
        self._load_csv_rules()
    
    def _load_yolov5_model(self):
        """Load YOLOv5 nano model for object detection"""
        try:
            print("🔄 Loading YOLOv5 model...")
            self.model = yolov5.load('yolov5n')  # nano = fastest
            self.model.conf = 0.40  # Confidence threshold
            self.model.iou = 0.45   # NMS IOU threshold
            print("✓ YOLOv5 model loaded - ready to detect objects")
        except Exception as e:
            print(f"⚠️  Warning: YOLOv5 load failed: {e}")
            self.model = None
    
    def _load_csv_rules(self):
        """Load color-based detection rules from CSV"""
        csv_path = os.path.join(os.path.dirname(__file__), '../../data/detection_rules.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.rules.append({
                        'issue_type': row['issue_type'],
                        'context_keywords': [kw.strip() for kw in row['context_keywords'].split(',')],
                        'color_requirements': row['color_requirements'],
                        'confidence_boost': float(row['confidence_boost']),
                        'description': row['description'],
                    })
            print(f"✓ Loaded {len(self.rules)} color-based detection rules")
        except Exception as e:
            print(f"Warning: Could not load CSV rules: {e}")
            self.rules = []
    
    @staticmethod
    def analyze_image(image_path: str) -> Tuple[str, float, List[str]]:
        """Main analysis function - combines YOLOv5 + color analysis"""
        analyzer = SimpleImageAnalyzer()
        return analyzer._analyze_image_hybrid(image_path)
    
    def _analyze_image_hybrid(self, image_path: str) -> Tuple[str, float, List[str]]:
        """Hybrid analysis: YOLOv5 objects + color patterns"""
        try:
            # Load image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_array = np.array(image)
            
            # Phase 1: Detect objects with YOLOv5
            yolov5_detections = self._detect_objects_yolov5(image)
            print(f"🎯 YOLOv5 detected: {yolov5_detections}")
            
            # Phase 2: Analyze color patterns
            color_metrics = self._extract_color_metrics(img_array)
            color_detections = self._detect_from_colors(color_metrics, image_path)
            print(f"🎨 Color analysis detected: {color_detections}")
            
            # Phase 3: Combine results (prioritize water + objects)
            final_issue, final_confidence = self._combine_detections(
                yolov5_detections, 
                color_detections, 
                color_metrics
            )
            
            return final_issue, final_confidence, [final_issue]
        
        except Exception as e:
            print(f"Error in analysis: {e}")
            return "other", 0.25, []
    
    def _detect_objects_yolov5(self, image: Image) -> Dict[str, int]:
        """Detect objects using YOLOv5 - returns object counts"""
        detected = {}
        
        if self.model is None:
            return detected
        
        try:
            # Run YOLOv5 detection
            results = self.model(image, size=640)
            predictions = results.pandas().xyxy[0]
            
            if len(predictions) > 0:
                # Count objects by class
                for class_name in predictions['name'].unique():
                    count = len(predictions[predictions['name'] == class_name])
                    detected[class_name] = count
                    print(f"  → {class_name}: {count}")
            
            self.detected_objects = detected
        except Exception as e:
            print(f"YOLOv5 error: {e}")
        
        return detected
    
    def _detect_from_colors(self, color_metrics: dict, image_path: str) -> Dict[str, float]:
        """Detect issues from color patterns - returns issue -> confidence"""
        detections = {}
        location_context = os.path.basename(os.path.dirname(image_path)).lower()
        
        # Check each CSV rule
        for rule in self.rules:
            if not self._check_color_requirements(rule['color_requirements'], color_metrics):
                continue
            
            coverage = self._calculate_coverage(rule['issue_type'], color_metrics)
            if coverage < 0.05:  # Need >5% coverage
                continue
            
            confidence = 0.4 + (coverage * 0.5) + rule['confidence_boost']
            detections[rule['issue_type']] = min(0.85, confidence)
        
        return detections
    
    def _combine_detections(self, 
                           yolov5_detections: Dict[str, int],
                           color_detections: Dict[str, float],
                           color_metrics: dict) -> Tuple[str, float]:
        """Intelligently combine YOLOv5 + color results"""
        
        # PRIORITY 1: Water always wins (>20% blue)
        if color_metrics.get('blue_ratio', 0) > 0.20:
            water_issues = [k for k in color_detections if 'flood' in k or 'water' in k]
            if water_issues:
                best_water = max(water_issues, key=lambda x: color_detections[x])
                return best_water, min(0.95, color_detections[best_water] + 0.15)
        
        # PRIORITY 2: Objects detected by YOLOv5
        if yolov5_detections:
            # Check for rocks/debris blocking road
            if 'rock' in yolov5_detections or 'brick' in yolov5_detections:
                # Disambiguate: if water high, it's water; if potholes detected, combine
                if color_metrics.get('dark_ratio', 0) > 0.40:
                    return 'critical_pothole', 0.80
                return 'trash_pollution', 0.70
            
            # Trees/vegetation detected by YOLOv5
            if 'tree' in yolov5_detections or 'plant' in yolov5_detections:
                # If water also detected, it's water (trees in water)
                if color_metrics.get('blue_ratio', 0) > 0.15:
                    return 'severe_flooding', 0.82
                # Otherwise it's vegetation
                return 'severe_vegetation', 0.75
            
            # Vehicles blocking road
            if 'car' in yolov5_detections or 'truck' in yolov5_detections or 'motorcycle' in yolov5_detections:
                return 'vehicle', 0.80
            
            # People on road
            if 'person' in yolov5_detections:
                return 'people_on_road', 0.65
            
            # Trash/debris
            if any(k in yolov5_detections for k in ['bottle', 'cup', 'backpack', 'handbag']):
                return 'trash_pollution', 0.70
            
            # Animals on road
            if any(k in yolov5_detections for k in ['dog', 'cat', 'cow', 'horse']):
                return 'animal_on_road', 0.65
        
        # PRIORITY 3: Color patterns (when no YOLOv5 detection)
        if color_detections:
            best_color_issue = max(color_detections.items(), key=lambda x: x[1])
            return best_color_issue[0], best_color_issue[1]
        
        # PRIORITY 4: Fallback
        return 'other', 0.30
    
    @staticmethod
    def _extract_color_metrics(img_array: np.ndarray) -> dict:
        """Extract color metrics from image"""
        metrics = {}
        
        r = img_array[:, :, 0].astype(float)
        g = img_array[:, :, 1].astype(float)
        b = img_array[:, :, 2].astype(float)
        
        total = img_array.shape[0] * img_array.shape[1]
        
        # Blue (water)
        blue_px = np.sum((b > r + 20) & (b > g + 20))
        metrics['blue_ratio'] = blue_px / total
        
        # Dark (potholes, shadows, damage)
        dark_px = np.sum((r < 100) & (g < 100) & (b < 100))
        metrics['dark_ratio'] = dark_px / total
        
        # Brown (asphalt, dirt)
        brown_px = np.sum((r > 100) & (r < 180) & (g > 80) & (g < 150) & (b < 100))
        metrics['brown_ratio'] = brown_px / total
        
        # Green (vegetation)
        green_px = np.sum((g > r + 20) & (g > b + 20))
        metrics['green_ratio'] = green_px / total
        
        # Gray (concrete, construction)
        gray_px = np.sum((np.abs(r - g) < 30) & (np.abs(r - b) < 30) & 
                        (r > 80) & (r < 200))
        metrics['gray_ratio'] = gray_px / total
        
        # Red (warnings, vehicles)
        red_px = np.sum((r > g + 30) & (r > b + 30))
        metrics['red_ratio'] = red_px / total
        
        # Dust/sand
        dust_px = np.sum((r > 150) & (g > 130) & (b < 120))
        metrics['dust_ratio'] = dust_px / total
        
        return metrics
    
    @staticmethod
    def _calculate_coverage(issue_type: str, metrics: dict) -> float:
        """Calculate coverage % for each issue type"""
        if 'flood' in issue_type or 'water' in issue_type:
            return metrics.get('blue_ratio', 0)
        elif 'pothole' in issue_type:
            return min(metrics.get('dark_ratio', 0) * 0.65, 0.45)
        elif 'vegetation' in issue_type:
            return metrics.get('green_ratio', 0)
        elif 'construction' in issue_type:
            return min(metrics.get('gray_ratio', 0) * 0.6, 0.35)
        elif 'dust' in issue_type or 'trash' in issue_type:
            return min(metrics.get('dust_ratio', 0) * 0.6, 0.40)
        elif 'electrical' in issue_type:
            return min(metrics.get('red_ratio', 0) * 0.55, 0.35)
        else:
            return 0.08
    
    @staticmethod
    def _check_color_requirements(color_reqs: str, metrics: dict) -> bool:
        """Evaluate color requirement expressions"""
        if not color_reqs or 'multicolor' in color_reqs:
            return True
        
        # AND logic
        if '&' in color_reqs:
            for cond in color_reqs.split('&'):
                if not SimpleImageAnalyzer._eval_cond(cond.strip(), metrics):
                    return False
            return True
        
        # OR logic
        elif '|' in color_reqs:
            for cond in color_reqs.split('|'):
                if SimpleImageAnalyzer._eval_cond(cond.strip(), metrics):
                    return True
            return False
        
        else:
            return SimpleImageAnalyzer._eval_cond(color_reqs.strip(), metrics)
    
    @staticmethod
    def _eval_cond(cond: str, metrics: dict) -> bool:
        """Evaluate single condition like 'blue_ratio>0.25'"""
        try:
            if '>' in cond:
                metric, val = cond.split('>')
                return metrics.get(metric.strip(), 0) > float(val.strip())
            elif '<' in cond:
                metric, val = cond.split('<')
                return metrics.get(metric.strip(), 0) < float(val.strip())
            elif '>=' in cond:
                metric, val = cond.split('>=')
                return metrics.get(metric.strip(), 0) >= float(val.strip())
            elif '<=' in cond:
                metric, val = cond.split('<=')
                return metrics.get(metric.strip(), 0) <= float(val.strip())
        except:
            pass
        return False
    
    def _fallback_classification(self, metrics: dict) -> Tuple[str, float]:
        """Fallback when nothing detected"""
        # Check dominant color
        if metrics.get('blue_ratio', 0) > 0.25:
            return 'flood', 0.50
        elif metrics.get('green_ratio', 0) > 0.40:
            return 'vegetation', 0.45
        elif metrics.get('dark_ratio', 0) > 0.35:
            return 'pothole', 0.48
        else:
            return 'other', 0.30
