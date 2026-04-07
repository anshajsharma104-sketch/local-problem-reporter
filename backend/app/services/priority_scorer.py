from typing import Dict, Tuple
from datetime import datetime, timedelta


class PriorityScorer:
    """
    Calculates priority scores for reported issues based on multiple factors:
    - Issue type severity
    - AI confidence
    - Number of reports (upvotes)
    - Location density
    - Time since report
    """
    
    # Issue type base severity (0-100)
    ISSUE_SEVERITY = {
        # Critical Infrastructure Issues
        "flooding": 95,
        "structural_collapse": 90,
        "electrical_hazard": 85,
        "sewage_overflow": 85,
        
        # High Severity
        "road_obstruction": 80,
        "pothole": 75,
        "landslide": 100,
        "water_leak": 75,
        "road_damage": 70,
        "manhole_hazard": 75,
        
        # Medium Severity
        "traffic": 60,
        "construction": 50,
        "drainage_problem": 50,
        "water_accumulation": 45,
        "vegetation_overgrowth": 35,
        
        # Lower Severity
        "garbage": 30,
        "dust_pollution": 25,
        "trash_pollution": 25,
        "graffiti": 20,
        
        # Default
        "other": 40,
        "unknown": 10
    }
    
    # Priority thresholds
    PRIORITY_THRESHOLDS = {
        "critical": 80,
        "high": 60,
        "medium": 40,
        "low": 0
    }

    @staticmethod
    def calculate_priority_score(
        issue_type: str,
        ai_confidence: float,
        upvotes: int,
        location_density: int = 1,  # Number of similar issues in same area
        time_since_report: int = 0,  # Hours
        status: str = "reported"
    ) -> Tuple[float, str]:
        """
        Calculate priority score and priority level
        
        Args:
            issue_type: Type of issue detected
            ai_confidence: AI model confidence (0-1)
            upvotes: Number of upvotes/confirmations
            location_density: Number of similar issues nearby
            time_since_report: Hours since report creation
            status: Current status (reported, investigating, resolved)
        
        Returns:
            Tuple of (priority_score, priority_level)
        """
        
        scorer = PriorityScorer()
        
        # Base score from issue type severity
        base_score = scorer.ISSUE_SEVERITY.get(issue_type.lower(), 20)
        
        # AI Confidence factor (0.6x to 1.0x multiplier)
        confidence_factor = 0.6 + (ai_confidence * 0.4)
        
        # Upvote factor (more confirmations = higher priority)
        # Each upvote adds 5 points, capped at 20
        upvote_factor = min(upvotes * 5, 20)
        
        # Location density factor
        # More reports in same area increase priority
        density_factor = min(location_density * 8, 25)
        
        # Time decay factor (older unresolved issues get boost)
        if status == "reported":
            time_factor = min(time_since_report / 24, 15)  # Up to 15 points over 24 hours
        else:
            time_factor = 0
        
        # Calculate final score
        priority_score = (base_score * confidence_factor) + upvote_factor + density_factor + time_factor
        priority_score = min(priority_score, 100)  # Cap at 100
        
        # Determine priority level
        priority_level = scorer._get_priority_level(priority_score, status)
        
        return priority_score, priority_level

    @staticmethod
    def _get_priority_level(score: float, status: str) -> str:
        """Determine priority level from score"""
        if status == "resolved":
            return "resolved"
        
        scorer = PriorityScorer()
        for level, threshold in sorted(scorer.PRIORITY_THRESHOLDS.items(), 
                                       key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return "low"

    @staticmethod
    def recalculate_location_density(db, lat: float, lon: float, 
                                    radius_km: float = 1.0) -> int:
        """
        Calculate number of similar issues within radius
        This would be called from the database layer
        """
        # Simple implementation - would use geospatial queries in production
        from sqlalchemy import and_
        from ..models import Issue
        
        # Rough conversion: 1 degree ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(cos(lat)))
        
        count = db.query(Issue).filter(
            and_(
                Issue.latitude >= lat - lat_delta,
                Issue.latitude <= lat + lat_delta,
                Issue.longitude >= lon - lon_delta,
                Issue.longitude <= lon + lon_delta,
                Issue.status != "resolved"
            )
        ).count()
        
        return count

    @staticmethod
    def get_scoring_info() -> Dict:
        """Get information about scoring system"""
        return {
            "severity_levels": PriorityScorer.ISSUE_SEVERITY,
            "priority_thresholds": PriorityScorer.PRIORITY_THRESHOLDS,
            "factors": {
                "base_severity": "Issue type determines base (20-100 points)",
                "ai_confidence": "Model confidence (0.6x - 1.0x multiplier)",
                "upvotes": "Community confirmations (5 points each, max 20)",
                "location_density": "Similar issues nearby (8 points each, max 25)",
                "time_decay": "Unresolved time boost (max 15 points over 24h)"
            }
        }
