from typing import Tuple, List, Dict
from .simple_analyzer import SimpleImageAnalyzer


class AIIssueDetector:
    def __init__(self):
        """Initialize AI detector with Infrastructure Detection + CSV-based hybrid system"""
        self.analyzer = SimpleImageAnalyzer()
        print("✓ Initialized HYBRID detector: Infrastructure Detection + CSV-based rules")
        if self.analyzer.detector:
            print("✓ Infrastructure detector ACTIVE")
        else:
            print("⚠ Infrastructure detector not available, using color analysis only")
    
    def detect_issue_type(self, image_path: str) -> Tuple[str, float, List[str]]:
        """
        Detect issue type from image using CSV rules and pixel analysis
        
        Returns:
            Tuple of (issue_type, confidence, detected_objects)
        """
        try:
            return self._detect_with_csv_rules(image_path)
        except Exception as e:
            print(f"Error in detection: {e}")
            return "other", 0.3, []

    def _detect_with_csv_rules(self, image_path: str) -> Tuple[str, float, List[str]]:
        """Detect using CSV-based rule system"""
        issue_type, confidence, detected_objects = self.analyzer.analyze_image(image_path)
        print(f"CSV Detection: {issue_type} with confidence {confidence:.2f}")
        return issue_type, confidence, detected_objects

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model": "CSV-based Rule System with Pixel Analysis",
            "status": "active",
            "rules_count": len(self.analyzer.rules),
            "detection_method": "Color threshold matching with AND/OR logic",
            "categories": [
                "flooding_episode",
                "flood",
                "water_leak",
                "drainage_problem",
                "minor_water_stain",
                "vegetation",
                "landslide",
                "dust_pollution",
                "road_damage",
                "pothole",
                "potholes_cluster",
                "construction",
                "collapsed_structure",
                "street_lighting",
                "waste_pollution",
                "electrical_hazard",
                "vehicle_concern",
                "graffiti",
                "sidewalk_damage",
                "manhole_damage",
                "other"
            ]
        }
