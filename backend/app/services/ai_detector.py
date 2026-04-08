from typing import Tuple, List, Dict
from .simple_analyzer import SimpleImageAnalyzer


class AIIssueDetector:
    def __init__(self):
        """Initialize AI detector with basic CSV-based analysis only"""
        self.analyzer = SimpleImageAnalyzer()
        print("✓ Initialized basic detector: CSV-based rules only")
        print("⚠️  Advanced AI/ML features disabled for deployment compatibility")

    def detect_issue_type(self, image_path: str) -> Tuple[str, float, List[str]]:
        """
        Detect issue type using basic CSV rules only
        """
        try:
            return self.analyzer.analyze_image(image_path)
        except Exception as e:
            print(f"Error in detection: {e}")
            return "other", 0.3, []

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model": "CSV-based Rule System",
            "status": "active",
            "rules_count": len(self.analyzer.rules) if hasattr(self.analyzer, 'rules') else 0,
            "detection_method": "Color threshold matching",
            "categories": [
                "road_damage",
                "garbage",
                "water_leak",
                "traffic",
                "construction",
                "landslide",
            ]
        }
