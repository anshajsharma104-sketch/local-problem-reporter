"""
Dynamic issue categorization based on detected objects.
Instead of rigid categories, intelligently categorize any detected objects.
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DynamicIssueCategor:
    """Categorize detected objects into infrastructure issues with priority."""
    
    # Mapping of detected objects to issue types and priorities
    OBJECT_CATEGORY_MAP = {
        # Road damage
        'pothole': {'category': 'pothole', 'priority': 7, 'severity': 'high'},
        'crater': {'category': 'pothole', 'priority': 8, 'severity': 'critical'},
        'hole': {'category': 'road_damage', 'priority': 6, 'severity': 'high'},
        'broken_pavement': {'category': 'road_damage', 'priority': 6, 'severity': 'high'},
        'asphalt_damage': {'category': 'road_damage', 'priority': 5, 'severity': 'medium'},
        'crack': {'category': 'road_damage', 'priority': 4, 'severity': 'medium'},
        
        # Water/Flooding
        'water': {'category': 'flooding', 'priority': 10, 'severity': 'critical'},
        'flood': {'category': 'flooding', 'priority': 10, 'severity': 'critical'},
        'puddle': {'category': 'water_accumulation', 'priority': 4, 'severity': 'low'},
        'stagnant_water': {'category': 'water_accumulation', 'priority': 4, 'severity': 'low'},
        'muddy_water': {'category': 'flooding', 'priority': 7, 'severity': 'high'},
        'sewage': {'category': 'sewage_overflow', 'priority': 10, 'severity': 'critical'},
        'dirty_water': {'category': 'sewage_overflow', 'priority': 10, 'severity': 'critical'},
        
        # Obstacles/Blocking
        'rock': {'category': 'road_obstruction', 'priority': 8, 'severity': 'critical'},
        'boulder': {'category': 'road_obstruction', 'priority': 8, 'severity': 'critical'},
        'debris': {'category': 'road_obstruction', 'priority': 8, 'severity': 'critical'},
        'rubble': {'category': 'structural_collapse', 'priority': 9, 'severity': 'critical'},
        'fallen_structure': {'category': 'structural_collapse', 'priority': 9, 'severity': 'critical'},
        'barrier': {'category': 'construction_hazard', 'priority': 3, 'severity': 'low'},
        'cone': {'category': 'construction_hazard', 'priority': 2, 'severity': 'low'},
        
        # Vegetation
        'tree': {'category': 'vegetation_overgrowth', 'priority': 3, 'severity': 'low'},
        'fallen_tree': {'category': 'road_obstruction', 'priority': 9, 'severity': 'critical'},
        'uprooted_tree': {'category': 'road_obstruction', 'priority': 9, 'severity': 'critical'},
        'vegetation': {'category': 'vegetation_overgrowth', 'priority': 2, 'severity': 'low'},
        'dense_vegetation': {'category': 'vegetation_overgrowth', 'priority': 3, 'severity': 'low'},
        'grass': {'category': 'vegetation_overgrowth', 'priority': 1, 'severity': 'low'},
        'branches': {'category': 'vegetation_hazard', 'priority': 4, 'severity': 'medium'},
        
        # Electrical
        'power_line': {'category': 'electrical_hazard', 'priority': 10, 'severity': 'critical'},
        'downed_wire': {'category': 'electrical_hazard', 'priority': 10, 'severity': 'critical'},
        'exposed_wire': {'category': 'electrical_hazard', 'priority': 10, 'severity': 'critical'},
        'electrical_pole': {'category': 'utility_hazard', 'priority': 6, 'severity': 'medium'},
        'transformer': {'category': 'electrical_hazard', 'priority': 8, 'severity': 'high'},
        'cable': {'category': 'electrical_hazard', 'priority': 7, 'severity': 'high'},
        
        # Utilities
        'manhole': {'category': 'manhole_hazard', 'priority': 8, 'severity': 'high'},
        'open_manhole': {'category': 'manhole_hazard', 'priority': 9, 'severity': 'critical'},
        'drain': {'category': 'drainage_problem', 'priority': 4, 'severity': 'medium'},
        'clogged_drain': {'category': 'drainage_problem', 'priority': 5, 'severity': 'medium'},
        'water_pipe': {'category': 'water_leak', 'priority': 5, 'severity': 'medium'},
        'leaking_pipe': {'category': 'water_leak', 'priority': 6, 'severity': 'high'},
        
        # Construction/Structures
        'construction_equipment': {'category': 'active_construction', 'priority': 1, 'severity': 'low'},
        'crane': {'category': 'active_construction', 'priority': 1, 'severity': 'low'},
        'incomplete_building': {'category': 'construction_site', 'priority': 2, 'severity': 'low'},
        'damaged_building': {'category': 'structural_collapse', 'priority': 9, 'severity': 'critical'},
        'collapsed_wall': {'category': 'structural_collapse', 'priority': 9, 'severity': 'critical'},
        'cracked_wall': {'category': 'structural_damage', 'priority': 6, 'severity': 'high'},
        'damaged_foundation': {'category': 'structural_damage', 'priority': 7, 'severity': 'high'},
        'broken_concrete': {'category': 'road_damage', 'priority': 5, 'severity': 'medium'},
        
        # Pollution/Environmental
        'trash': {'category': 'trash_pollution', 'priority': 2, 'severity': 'low'},
        'garbage': {'category': 'trash_pollution', 'priority': 3, 'severity': 'low'},
        'waste': {'category': 'illegal_dumping', 'priority': 4, 'severity': 'medium'},
        'pollution': {'category': 'environmental_hazard', 'priority': 5, 'severity': 'medium'},
        'dust': {'category': 'dust_pollution', 'priority': 2, 'severity': 'low'},
        'smoke': {'category': 'air_pollution', 'priority': 5, 'severity': 'medium'},
        
        # Lighting
        'broken_light': {'category': 'dark_unlit_area', 'priority': 3, 'severity': 'low'},
        'dark_area': {'category': 'dark_unlit_area', 'priority': 3, 'severity': 'low'},
        'streetlight': {'category': 'lighting_hazard', 'priority': 2, 'severity': 'low'},
        
        # Vehicles/Encroachment
        'car': {'category': 'vehicle_obstruction', 'priority': 1, 'severity': 'low'},
        'truck': {'category': 'vehicle_obstruction', 'priority': 1, 'severity': 'low'},
        'bus': {'category': 'vehicle_obstruction', 'priority': 1, 'severity': 'low'},
        'motorcycle': {'category': 'vehicle_obstruction', 'priority': 1, 'severity': 'low'},
        'encroachment': {'category': 'illegal_encroachment', 'priority': 2, 'severity': 'low'},
        'illegal_structure': {'category': 'illegal_encroachment', 'priority': 3, 'severity': 'medium'},
        
        # People/Safety
        'person': {'category': 'safety_hazard', 'priority': 0, 'severity': 'none'},
        'crowd': {'category': 'safety_hazard', 'priority': 0, 'severity': 'none'},
    }
    
    PRIORITY_NAMES = {
        10: '🔴 CRITICAL - Life threatening',
        9: '🔴 CRITICAL - Severe damage',
        8: '🟠 HIGH - Significant hazard',
        7: '🟠 HIGH - Dangerous condition',
        6: '🟠 HIGH - Major issue',
        5: '🟡 MEDIUM - Needs attention',
        4: '🟡 MEDIUM - Noticeable problem',
        3: '🟢 LOW - Minor issue',
        2: '🟢 LOW - Cosmetic issue',
        1: '⚪ MINIMAL - Monitoring',
        0: '⚪ INFO - No hazard',
    }
    
    @staticmethod
    def categorize_detection(detected_objects: List[Dict]) -> Dict:
        """
        Categorize detected objects into infrastructure issues.
        
        Args:
            detected_objects: List of YOLO detections with class names
            
        Returns:
            Dictionary with categorized issues and priorities
        """
        if not detected_objects:
            return {
                'primary_issue': None,
                'secondary_issues': [],
                'critical_issues': [],
                'all_issues': [],
                'max_priority': 0
            }
        
        issues = []
        critical_issues = []
        
        # Categorize each detected object
        for obj in detected_objects:
            class_name = obj.get('class', 'unknown').lower()
            confidence = obj.get('confidence', 0.0)
            
            # Try exact match first, then partial match
            category_info = DynamicIssueCategor.OBJECT_CATEGORY_MAP.get(class_name)
            
            if not category_info:
                # Try partial matching
                category_info = DynamicIssueCategor._partial_match(class_name)
            
            if not category_info:
                # Default categorization for unknown objects
                category_info = DynamicIssueCategor._infer_category(class_name)
            
            issue = {
                'detected_object': class_name,
                'category': category_info['category'],
                'priority': category_info['priority'],
                'severity': category_info['severity'],
                'confidence': confidence,
                'priority_name': DynamicIssueCategor.PRIORITY_NAMES.get(
                    category_info['priority'],
                    'UNKNOWN'
                ),
                'bbox': obj.get('bbox', [])
            }
            
            issues.append(issue)
            
            # Track critical issues
            if category_info['priority'] >= 8:
                critical_issues.append(issue)
        
        # Sort by priority (HIGHEST first)
        issues_sorted = sorted(issues, key=lambda x: x['priority'], reverse=True)
        critical_issues_sorted = sorted(critical_issues, key=lambda x: x['priority'], reverse=True)
        
        # Primary issue = highest priority
        primary_issue = issues_sorted[0] if issues_sorted else None
        
        # Secondary issues = rest
        secondary_issues = issues_sorted[1:] if len(issues_sorted) > 1 else []
        
        # Calculate overall priority
        max_priority = max([i['priority'] for i in issues_sorted], default=0)
        
        return {
            'primary_issue': primary_issue,
            'secondary_issues': secondary_issues,
            'critical_issues': critical_issues_sorted,
            'all_issues': issues_sorted,
            'max_priority': max_priority,
            'object_count': len(detected_objects),
            'critical_count': len(critical_issues_sorted)
        }
    
    @staticmethod
    def _partial_match(class_name: str) -> Dict | None:
        """Try to match partial class names."""
        for key, value in DynamicIssueCategor.OBJECT_CATEGORY_MAP.items():
            if key in class_name or class_name in key:
                return value
        return None
    
    @staticmethod
    def _infer_category(class_name: str) -> Dict:
        """Infer category for unknown objects based on keywords."""
        keywords_high = ['danger', 'hazard', 'critical', 'emergency', 'severe', 'major', 'collapse', 'fallen']
        keywords_medium = ['damage', 'broken', 'problem', 'issue', 'blocked', 'clogged']
        keywords_low = ['minor', 'small', 'crack', 'dust']
        
        class_lower = class_name.lower()
        
        # Check for high priority keywords
        if any(kw in class_lower for kw in keywords_high):
            return {'category': class_name, 'priority': 8, 'severity': 'critical'}
        
        # Check for medium priority keywords
        if any(kw in class_lower for kw in keywords_medium):
            return {'category': class_name, 'priority': 5, 'severity': 'medium'}
        
        # Check for low priority keywords
        if any(kw in class_lower for kw in keywords_low):
            return {'category': class_name, 'priority': 2, 'severity': 'low'}
        
        # Default: unknown object = low priority
        return {'category': class_name, 'priority': 1, 'severity': 'low'}
