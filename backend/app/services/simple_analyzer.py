from PIL import Image
import numpy as np
from typing import Tuple, List
import csv
import os
import logging

# Import infrastructure detector and dynamic categorizer
try:
    from .infrastructure_detector import get_detector
    from .dynamic_categorizer import DynamicIssueCategor
    DETECTOR_AVAILABLE = True
except Exception as e:
    print(f"Warning: Detector not available: {e}")
    DETECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleImageAnalyzer:
    """Hybrid image analysis using Infrastructure Detection + Color-based CSV rules"""
    
    def __init__(self):
        """Load detection rules from CSV file"""
        self.rules = self._load_rules()
        self.detector = None
        if DETECTOR_AVAILABLE:
            try:
                self.detector = get_detector()
            except Exception as e:
                logger.warning(f"Detector initialization failed: {e}")

    
    def _load_rules(self) -> List[dict]:
        """Load detection rules from CSV file"""
        rules = []
        csv_path = os.path.join(os.path.dirname(__file__), '../../data/detection_rules.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rules.append({
                        'issue_type': row['issue_type'],
                        'context_keywords': [kw.strip() for kw in row['context_keywords'].split(',')],
                        'color_requirements': row['color_requirements'],
                        'confidence_boost': float(row['confidence_boost']),
                        'description': row['description'],
                        'examples': row['examples']
                    })
            print(f"✓ Loaded {len(rules)} detection rules from CSV")
        except Exception as e:
            print(f"Warning: Could not load detection rules: {e}")
            rules = []
        
        return rules
    
    def analyze_image(self, image_path: str) -> Tuple[str, float, List[str]]:
        """
        Analyze image using HYBRID Infrastructure Detection + dynamic categorization:
        1. Infrastructure detector identifies damage patterns
        2. Dynamic categorizer assigns issue type AND priority to each object
        3. Return highest priority issue as primary detection
        
        Returns: (issue_type, confidence, detected_features)
        """
        try:
            print(f"🔍 Starting image analysis...")
            print(f"   Infrastructure detector available: {self.detector is not None}")
            
            # STEP 1: Try Infrastructure detection FIRST
            if self.detector:
                try:
                    print(f"   🔧 Attempting infrastructure detection...")
                    detections = self.detector.detect(image_path)
                    print(f"   Infrastructure result: {detections}")
                    
                    if detections['objects']:
                        print(f"✅ Infrastructure analysis found {detections['object_count']} issues")
                        
                        # STEP 2: Dynamically categorize and prioritize
                        categorized = DynamicIssueCategor.categorize_detection(
                            detections['objects']
                        )
                        print(f"✅ Categorized: {categorized['primary_issue']}")
                        
                        if categorized['primary_issue']:
                            primary = categorized['primary_issue']
                            
                            # Detailed logging
                            print(f"   PRIMARY: {primary['detected_object']} → {primary['category']}")
                            print(f"   PRIORITY: {primary['priority_name']}")
                            
                            # Log critical issues if any
                            if categorized['critical_issues']:
                                print(f"   ⚠️  CRITICAL ISSUES DETECTED: {len(categorized['critical_issues'])}")
                                for issue in categorized['critical_issues']:
                                    print(f"      - {issue['detected_object']} ({issue['category']})")
                            
                            # Build confidence based on detection confidence AND priority
                            detection_confidence = primary['confidence']
                            priority_boost = min(0.3, primary['priority'] * 0.03)
                            combined_confidence = min(0.95, 0.5 + detection_confidence * 0.3 + priority_boost)
                            
                            # Return primary issue
                            features = [
                                f"infrastructure_detected_{primary['detected_object']}",
                                f"priority_{primary['priority']}",
                                f"severity_{primary['severity']}"
                            ]
                            
                            # Add all detected objects to features
                            for issue in categorized['all_issues']:
                                features.append(f"also_detected_{issue['detected_object']}")
                            
                            print(f"✅ DETECTION SUCCESS: Returning {primary['category']} (confidence: {combined_confidence:.2f})")
                            return primary['category'], combined_confidence, features
                        else:
                            print(f"⚠️  Infrastructure found objects but categorization failed")
                    else:
                        print(f"⚠️  Infrastructure detector found 0 issues")
                
                except Exception as e:
                    print(f"❌ Infrastructure detection error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️  Infrastructure detector is None!")
            
            # STEP 3: Fallback to color-based analysis
            print("📊 Running color-based analysis as fallback...")
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract color information
            color_metrics = self._extract_color_metrics(img_array)
            
            # Run color-based classification
            color_result = self._classify_with_rules(color_metrics, image_path)
            
            return color_result
            
        except Exception as e:
            print(f"❌ FATAL ERROR in analyze_image: {e}")
            import traceback
            traceback.print_exc()
            return "other", 0.0, []

    
    def _extract_color_metrics(self, img_array: np.ndarray) -> dict:
        """Extract detailed color metrics from image"""
        metrics = {}
        
        # Basic channel stats
        red_channel = img_array[:, :, 0].astype(float)
        green_channel = img_array[:, :, 1].astype(float)
        blue_channel = img_array[:, :, 2].astype(float)
        
        total_pixels = img_array.shape[0] * img_array.shape[1]
        
        # Overall brightness and contrast
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        metrics['brightness'] = brightness
        metrics['contrast'] = contrast
        
        # Dark pixels (potential potholes/damage)
        dark_pixels = np.sum((red_channel < 100) & (green_channel < 100) & (blue_channel < 100))
        metrics['dark_ratio'] = dark_pixels / total_pixels
        
        # Brown/gray pixels (asphalt/concrete damage)
        brown_pixels = np.sum((red_channel > 100) & (red_channel < 180) & 
                             (green_channel > 80) & (green_channel < 150) & 
                             (blue_channel < 100))
        metrics['brown_ratio'] = brown_pixels / total_pixels
        
        # Green pixels (vegetation, grass)
        green_pixels = np.sum((green_channel > red_channel + 20) & (green_channel > blue_channel + 20))
        metrics['green_ratio'] = green_pixels / total_pixels
        
        # Blue pixels (water)
        blue_pixels = np.sum((blue_channel > red_channel + 20) & (blue_channel > green_channel + 20))
        metrics['blue_ratio'] = blue_pixels / total_pixels
        
        # Red pixels (vehicles, warnings, danger)
        red_pixels = np.sum((red_channel > green_channel + 30) & (red_channel > blue_channel + 30))
        metrics['red_ratio'] = red_pixels / total_pixels
        
        # Gray pixels (concrete, sidewalks)
        gray_pixels = np.sum((np.abs(red_channel - green_channel) < 30) & 
                            (np.abs(red_channel - blue_channel) < 30) &
                            (red_channel > 80) & (red_channel < 200))
        metrics['gray_ratio'] = gray_pixels / total_pixels
        
        # Moisture/wet surface detection (high green-blue, low warm colors)
        wet_pixels = np.sum((blue_channel > 100) & (green_channel > 100) & (red_channel < green_channel))
        metrics['wet_surface_ratio'] = wet_pixels / total_pixels
        
        # Tan/dust color (dust, sand, dirt)
        dust_pixels = np.sum((red_channel > 150) & (green_channel > 130) & 
                            (blue_channel < 120) & (red_channel > blue_channel))
        metrics['dust_ratio'] = dust_pixels / total_pixels
        
        # Check for circular dark patterns (potential holes)
        metrics['has_dark_circles'] = metrics['dark_ratio'] > 0.2 and contrast > 50
        
        # Check for structural damage (irregular dark patterns)
        metrics['structural_damage'] = metrics['dark_ratio'] > 0.25 and metrics['brown_ratio'] > 0.15
        
        return metrics
    
    def _classify_with_rules(self, color_metrics: dict, image_path: str) -> Tuple[str, float, List[str]]:
        """Classify image using CSV rules and color metrics
        
        PRIORITY: Detect PRIMARY issue (what covers most %) not secondary objects
        """
        detected_features = []
        best_match = None
        best_confidence = 0.0
        best_coverage = 0.0  # Track what % of image shows this issue
        
        # Extract location context from file path (if available)
        import os
        location_context = os.path.basename(os.path.dirname(image_path)).lower()
        
        # STEP 1: Find all matching rules and their "coverage" (how much of image)
        rule_matches = []
        
        for rule in self.rules:
            # Check if color requirements are met
            if not self._check_color_requirements(rule['color_requirements'], color_metrics):
                continue
            
            # Calculate coverage percentage for this rule
            coverage = self._calculate_issue_coverage(rule['issue_type'], color_metrics)
            
            if coverage > 0.05:  # Only consider if >5% of image shows this
                rule_matches.append({
                    'issue_type': rule['issue_type'],
                    'coverage': coverage,
                    'confidence_boost': rule['confidence_boost'],
                    'priority': self._get_issue_priority(rule['issue_type']),
                    'keywords': rule['context_keywords']
                })
        
        # STEP 2: Water has ABSOLUTE priority - if water >20%, suppress EVERYTHING else
        water_matches = [m for m in rule_matches if m['issue_type'] in ['flooding_episode', 'severe_flooding', 'monsoon_flooding', 'moderate_flooding', 'flood', 'water_accumulation']]
        
        # If water coverage >20%, ONLY detect water - suppress traffic lights, construction, vegetation, etc!
        if water_matches:
            max_water_coverage = max(m['coverage'] for m in water_matches)
            if max_water_coverage > 0.20:
                # This is DEFINITELY a water issue - ignore construction, vegetation, electrical, etc
                best_match = max(water_matches, key=lambda x: x['coverage'])['issue_type']
                best_confidence = min(0.92, 0.55 + (max_water_coverage * 0.35))
                best_coverage = max_water_coverage
                detected_features = ['water_detected']
                print(f"PRIMARY ISSUE (water dominant {max_water_coverage*100:.1f}%): {best_match} *** SUPPRESSING ALL OTHER DETECTIONS ***")
                return best_match, best_confidence, detected_features
        
        # STEP 3: No dominant water - sort by PRIORITY then COVERAGE
        sorted_matches = sorted(rule_matches, key=lambda x: (x['priority'], x['coverage']), reverse=True)
        
        if sorted_matches:
            best_rule = sorted_matches[0]
            best_match = best_rule['issue_type']
            best_coverage = best_rule['coverage']
            
            # Calculate confidence based on coverage and boost
            base_confidence = 0.4 + (best_coverage * 0.5)  # More coverage = more confidence
            context_boost = 0.05 if any(kw.lower() in location_context for kw in best_rule['keywords']) else 0
            best_confidence = min(0.85, base_confidence + best_rule['confidence_boost'] + context_boost)
            
            detected_features = [best_match]
            print(f"PRIMARY ISSUE (coverage {best_coverage*100:.1f}%): {best_match} (confidence: {best_confidence:.2f})")
        else:
            # No rules matched - fallback
            best_match, best_confidence = self._fallback_classification(color_metrics)
            detected_features = [best_match]
            print(f"FALLBACK: {best_match} (no rules matched)")
        
        # Ensure confidence is realistic
        best_confidence = max(0.25, min(0.85, best_confidence))
        
        return best_match, best_confidence, detected_features
    
    @staticmethod
    def _calculate_issue_coverage(issue_type: str, metrics: dict) -> float:
        """Calculate what % of image shows this type of issue"""
        if issue_type in ['flooding_episode', 'severe_flooding', 'monsoon_flooding', 'moderate_flooding', 'flood']:
            return metrics.get('blue_ratio', 0)  # Direct water coverage
        elif issue_type == 'water_accumulation':
            return metrics.get('blue_ratio', 0) * 0.9  # Slightly less water
        elif issue_type in ['pothole', 'critical_pothole', 'severe_pothole_cluster', 'pothole_cluster']:
            # Pothole = dark spots (limited area, not whole image)
            return min(metrics.get('dark_ratio', 0) * 0.65, 0.45)
        elif issue_type in ['severe_road_damage', 'moderate_road_damage']:
            return min((metrics.get('dark_ratio', 0) + metrics.get('brown_ratio', 0) * 0.5) * 0.35, 0.40)
        elif issue_type in ['dense_vegetation', 'severe_vegetation']:
            return metrics.get('green_ratio', 0)  # Green coverage
        elif issue_type == 'electrical_hazard':
            # Red items (wires, signals) = small portion of image
            return min(metrics.get('red_ratio', 0) * 0.55, 0.35)
        elif issue_type == 'trash_pollution':
            return min(metrics.get('dust_ratio', 0) * 0.65, 0.40)
        elif issue_type == 'blocked_drainage':
            return min((metrics.get('gray_ratio', 0) + metrics.get('blue_ratio', 0) * 0.3) * 0.4, 0.35)
        elif issue_type in ['active_construction', 'major_construction']:
            # CONSERVATIVE: Don't detect if green is also high (trees falling in water)
            green_ratio = metrics.get('green_ratio', 0)
            if green_ratio > 0.30:  # High vegetation present
                return 0.05  # Suppress construction detection - probably trees, not construction
            return min((metrics.get('gray_ratio', 0) * 0.6 + metrics.get('dark_ratio', 0) * 0.2), 0.30)
        elif issue_type == 'water_leak':
            return min((metrics.get('blue_ratio', 0) * 0.5 + metrics.get('gray_ratio', 0) * 0.1), 0.25)
        elif issue_type == 'dark_unlit_area':
            return min((metrics.get('dark_ratio', 0) * 0.4 + metrics.get('gray_ratio', 0) * 0.2), 0.35)
        elif issue_type == 'significant_dust':
            return min(metrics.get('dust_ratio', 0) * 0.7, 0.45)
        elif issue_type == 'sewage_issue':
            return min((metrics.get('blue_ratio', 0) * 0.4 + metrics.get('dust_ratio', 0) * 0.3) * 0.7, 0.50)
        else:
            return 0.08  # Fallback - very conservative
    
    @staticmethod
    def _get_issue_priority(issue_type: str) -> int:
        """Priority ranking: 0=lowest, 10=highest
        Only HIGH CONFIDENCE detections shown - colors can be deceiving
        """
        priority_map = {
            # CRITICAL (9-10): Water is ALWAYS critical
            'flooding_episode': 10,
            'severe_flooding': 10,
            'monsoon_flooding': 10,
            'sewage_issue': 10,
            'electrical_hazard': 9,
            
            # HIGH (7-8): Clear road issues
            'severe_pothole_cluster': 8,
            'critical_pothole': 8,
            'moderate_flooding': 7,
            'pothole_cluster': 7,
            
            # MEDIUM-HIGH (5-6): Significant hazards
            'flood': 6,
            'pothole': 6,
            'severe_road_damage': 6,
            'water_accumulation': 5,
            'severe_vegetation': 5,
            'water_leak': 4,
            
            # MEDIUM (3-4): Noticeable but not critical
            'moderate_road_damage': 4,
            'dense_vegetation': 4,
            'blocked_drainage': 3,
            'dark_unlit_area': 3,
            'trash_pollution': 3,
            'significant_dust': 2,
            
            # LOW (1-2): Hard to detect reliably by color alone
            'active_construction': 1,  # Gray can be anything
            'major_construction': 1,   # Gray can be anything
        }
        return priority_map.get(issue_type, 0)

    
    @staticmethod
    def _check_color_requirements(color_reqs: str, metrics: dict) -> bool:
        """Check if color requirements are met using metric expressions
        
        Supports:
        - AND logic: brown_ratio>0.30&dark_ratio>0.18&blue_ratio<0.15 (all must pass)
        - OR logic: blue_ratio>0.25|brown_ratio>0.1 (any can pass)
        """
        if not color_reqs or color_reqs == 'multicolor_pattern' or color_reqs == 'multicolor_scattered':
            return True
        
        # Check if this is AND logic (all conditions must pass)
        if '&' in color_reqs:
            conditions = color_reqs.split('&')
            for condition in conditions:
                if not SimpleImageAnalyzer._evaluate_condition(condition.strip(), metrics):
                    return False  # Any condition fails = whole expression fails
            return True  # All conditions passed
        
        # Check if this is OR logic (any condition can pass)
        elif '|' in color_reqs:
            conditions = color_reqs.split('|')
            for condition in conditions:
                if SimpleImageAnalyzer._evaluate_condition(condition.strip(), metrics):
                    return True  # Any condition passes = whole expression passes
            return False  # No conditions passed
        
        # Single condition (no & or |)
        else:
            return SimpleImageAnalyzer._evaluate_condition(color_reqs.strip(), metrics)
    
    @staticmethod
    def _evaluate_condition(condition: str, metrics: dict) -> bool:
        """Evaluate a single condition like 'blue_ratio>0.25' or 'dark_ratio<0.15'"""
        try:
            # Handle special cases
            if 'multicolor' in condition or 'equipment' in condition or 'patterns' in condition:
                return True
            if 'area_type' in condition or 'location_type' in condition:
                return True
            if 'damage_visible' in condition or 'shaped_object' in condition:
                return True
            
            # Parse metric > value
            if '>' in condition:
                metric_name, threshold_str = condition.split('>')
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                if metric_name in metrics:
                    return metrics[metric_name] > threshold
            
            # Parse metric < value
            elif '<' in condition:
                metric_name, threshold_str = condition.split('<')
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                if metric_name in metrics:
                    return metrics[metric_name] < threshold
            
            # Parse metric >= value
            elif '>=' in condition:
                metric_name, threshold_str = condition.split('>=')
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                if metric_name in metrics:
                    return metrics[metric_name] >= threshold
            
            # Parse metric <= value
            elif '<=' in condition:
                metric_name, threshold_str = condition.split('<=')
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                if metric_name in metrics:
                    return metrics[metric_name] <= threshold
        
        except Exception as e:
            print(f"Warning: Could not parse condition '{condition}': {e}")
        
        return False
    
    @staticmethod
    def _calculate_base_confidence(issue_type: str, metrics: dict) -> float:
        """Calculate base confidence for each issue type"""
        confidence = 0.3  # minimum baseline
        
        if issue_type == 'road_damage':
            confidence = 0.3 + (metrics.get('dark_ratio', 0) * 0.4) + (metrics.get('brown_ratio', 0) * 0.2)
        
        elif issue_type == 'water_leak':
            confidence = 0.3 + (metrics.get('blue_ratio', 0) * 0.5)
        
        elif issue_type == 'flood':
            confidence = 0.4 + (metrics.get('blue_ratio', 0) * 0.4)
        
        elif issue_type == 'drainage_problem':
            confidence = 0.35 + (metrics.get('blue_ratio', 0) * 0.4) + (metrics.get('wet_surface_ratio', 0) * 0.15)
        
        elif issue_type == 'landslide':
            confidence = 0.4 + (metrics.get('brown_ratio', 0) * 0.4) + (metrics.get('dark_ratio', 0) * 0.2)
        
        elif issue_type == 'vegetation':
            confidence = 0.35 + (metrics.get('green_ratio', 0) * 0.5)
        
        elif issue_type == 'construction':
            confidence = 0.35 + (metrics.get('gray_ratio', 0) * 0.3) + (metrics.get('dark_ratio', 0) * 0.2)
        
        elif issue_type == 'street_lighting':
            confidence = 0.3 + (metrics.get('dark_ratio', 0) * 0.4)
        
        elif issue_type == 'waste_pollution':
            confidence = 0.3 + (metrics.get('dust_ratio', 0) * 0.3) + (metrics.get('dark_ratio', 0) * 0.2)
        
        elif issue_type == 'vehicle_concern':
            confidence = 0.3 + (metrics.get('red_ratio', 0) * 0.4)
        
        elif issue_type == 'pothole':
            confidence = 0.35 + (metrics.get('dark_ratio', 0) * 0.4) if metrics.get('has_dark_circles') else 0.3
        
        elif issue_type == 'flooding_episode':
            confidence = 0.5 + (metrics.get('blue_ratio', 0) * 0.3)
        
        else:
            confidence = 0.3
        
        return min(0.9, confidence)
    
    @staticmethod
    def _fallback_classification(metrics: dict) -> Tuple[str, float]:
        """Fallback classification when no rules match"""
        if metrics['blue_ratio'] > 0.25:
            return 'flood', 0.60
        elif metrics['blue_ratio'] > 0.12:
            return 'water_leak', 0.50
        elif metrics['green_ratio'] > 0.25:
            return 'vegetation', 0.55
        elif metrics['brown_ratio'] > 0.20:
            return 'landslide', 0.55
        elif metrics['dark_ratio'] > 0.30:
            return 'road_damage', 0.50
        elif metrics['dust_ratio'] > 0.15:
            return 'dust_pollution', 0.45
        else:
            return 'other', 0.30
