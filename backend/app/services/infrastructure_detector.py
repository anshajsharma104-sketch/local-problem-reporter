"""
Lightweight heuristic object detection for infrastructure issues.
Replaces YOLOv8 for infrastructure-specific detection without ML training.
"""

import numpy as np
from PIL import Image
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class InfrastructureDetector:
    """Detect infrastructure issues using color/texture analysis"""
    
    def __init__(self):
        """Initialize infrastructure detector"""
        self.conf = 0.45
        logger.info("✓ Infrastructure detector initialized (heuristic-based)")
    
    def detect(self, image_path: str) -> Dict:
        """
        Detect infrastructure issues using heuristics.
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with detected objects
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            h, w = img_array.shape[:2]
            
            detected_objects = []
            
            # Analyze image patches
            patch_size = 50
            for y in range(0, h - patch_size, patch_size):
                for x in range(0, w - patch_size, patch_size):
                    patch = img_array[y:y+patch_size, x:x+patch_size]
                    
                    # Check for potholes (dark + textured)
                    if self._is_pothole(patch):
                        detected_objects.append({
                            'class': 'pothole',
                            'confidence': 0.75,
                            'bbox': [x, y, x + patch_size, y + patch_size]
                        })
                    
                    # Check for water (high blue)
                    if self._is_water(patch):
                        detected_objects.append({
                            'class': 'water',
                            'confidence': 0.80,
                            'bbox': [x, y, x + patch_size, y + patch_size]
                        })
                    
                    # Check for vegetation (high green)
                    if self._is_vegetation(patch):
                        detected_objects.append({
                            'class': 'vegetation',
                            'confidence': 0.70,
                            'bbox': [x, y, x + patch_size, y + patch_size]
                        })
                    
                    # Check for rocks/debris (rough texture + dark)
                    if self._is_rock_debris(patch):
                        detected_objects.append({
                            'class': 'rock_debris',
                            'confidence': 0.68,
                            'bbox': [x, y, x + patch_size, y + patch_size]
                        })
            
            # Deduplicate nearby detections
            detected_objects = self._deduplicate(detected_objects)
            
            return {
                'objects': detected_objects,
                'object_count': len(detected_objects),
                'has_potholes': any(o['class'] == 'pothole' for o in detected_objects),
                'has_water': any(o['class'] == 'water' for o in detected_objects),
                'has_vegetation': any(o['class'] == 'vegetation' for o in detected_objects),
                'has_rocks': any(o['class'] == 'rock_debris' for o in detected_objects),
            }
        
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return {
                'objects': [],
                'object_count': 0,
                'has_potholes': False,
                'has_water': False,
                'has_vegetation': False,
                'has_rocks': False,
            }
    
    def _is_pothole(self, patch) -> bool:
        """Detect potholes: dark, highly textured"""
        r, g, b = patch[:,:,0], patch[:,:,1], patch[:,:,2]
        
        # Dark area
        brightness = (r.astype(float) + g + b) / 3
        if brightness.mean() > 120:
            return False
        
        # High texture variance (indicates surface damage)
        variance = brightness.std()
        return variance > 25  # High texture = damage
    
    def _is_water(self, patch) -> bool:
        """Detect water: high blue, low red"""
        r, g, b = patch[:,:,0].astype(float), patch[:,:,1].astype(float), patch[:,:,2].astype(float)
        
        # Blue dominant
        blue_ratio = b.mean() / (r.mean() + g.mean() + b.mean() + 1)
        red_ratio = r.mean() / (r.mean() + g.mean() + b.mean() + 1)
        
        return blue_ratio > 0.40 and red_ratio < 0.25
    
    def _is_vegetation(self, patch) -> bool:
        """Detect vegetation: high green, low blue"""
        r, g, b = patch[:,:,0].astype(float), patch[:,:,1].astype(float), patch[:,:,2].astype(float)
        
        # Green dominant
        green_ratio = g.mean() / (r.mean() + g.mean() + b.mean() + 1)
        blue_ratio = b.mean() / (r.mean() + g.mean() + b.mean() + 1)
        
        return green_ratio > 0.40 and blue_ratio < 0.20
    
    def _is_rock_debris(self, patch) -> bool:
        """Detect rocks/debris: brown/gray + textured"""
        r, g, b = patch[:,:,0].astype(float), patch[:,:,1].astype(float), patch[:,:,2].astype(float)
        
        # Brown/gray tone
        avg_color = (r + g + b) / 3
        brown = (r > 60) & (r < 180) & (g > 60) & (g < 150) & (b < 100)
        
        if brown.sum() < (patch.shape[0] * patch.shape[1] * 0.3):
            return False
        
        # Textured (variance)
        variance = avg_color.std()
        return variance > 20
    
    def _deduplicate(self, objects: List[Dict]) -> List[Dict]:
        """Remove duplicate detections in nearby areas"""
        if not objects:
            return objects
        
        kept = []
        for obj in sorted(objects, key=lambda x: x['confidence'], reverse=True):
            # Check if close to existing kept object of same class
            is_duplicate = False
            for kept_obj in kept:
                if obj['class'] != kept_obj['class']:
                    continue
                
                # If boxes overlap >70%, it's a duplicate
                x1, y1, x2, y2 = obj['bbox']
                kx1, ky1, kx2, ky2 = kept_obj['bbox']
                
                overlap = max(0, min(x2, kx2) - max(x1, kx1)) * max(0, min(y2, ky2) - max(y1, ky1))
                area = (x2 - x1) * (y2 - y1)
                
                if area > 0 and overlap / area > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                kept.append(obj)
        
        return kept


# Global instance
_detector = None


def get_detector() -> InfrastructureDetector:
    """Get or create global detector instance"""
    global _detector
    if _detector is None:
        _detector = InfrastructureDetector()
    return _detector
