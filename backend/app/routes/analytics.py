from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Issue
from ..schemas import AnalyticsResponse, DashboardResponse

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive dashboard analytics for authorities"""
    
    # Total counts
    total_issues = db.query(func.count(Issue.id)).scalar() or 0
    critical = db.query(func.count(Issue.id)).filter(Issue.priority_level == "critical").scalar() or 0
    high = db.query(func.count(Issue.id)).filter(Issue.priority_level == "high").scalar() or 0
    medium = db.query(func.count(Issue.id)).filter(Issue.priority_level == "medium").scalar() or 0
    low = db.query(func.count(Issue.id)).filter(Issue.priority_level == "low").scalar() or 0
    resolved = db.query(func.count(Issue.id)).filter(Issue.status == "resolved").scalar() or 0
    pending = total_issues - resolved
    
    # Issues by type
    type_counts = db.query(Issue.issue_type, func.count(Issue.id)).group_by(Issue.issue_type).all()
    issues_by_type = {ic[0]: ic[1] for ic in type_counts}
    
    # Issues by priority
    priority_counts = db.query(Issue.priority_level, func.count(Issue.id)).group_by(Issue.priority_level).all()
    issues_by_priority = {pc[0]: pc[1] for pc in priority_counts}
    
    # Issues by status
    status_counts = db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
    issues_by_status = {sc[0]: sc[1] for sc in status_counts}
    
    # Recent issues
    recent = db.query(Issue).order_by(Issue.created_at.desc()).limit(10).all()
    recent_issues = [
        {
            "id": i.id,
            "title": i.title,
            "issue_type": i.issue_type,
            "priority_level": i.priority_level,
            "priority_score": i.priority_score,
            "status": i.status,
            "created_at": i.created_at,
            "upvotes": i.upvotes
        }
        for i in recent
    ]
    
    # Top locations (by issue count)
    location_counts = db.query(
        Issue.location_description,
        func.count(Issue.id).label('count'),
        func.avg(Issue.priority_score).label('avg_priority')
    ).group_by(Issue.location_description).order_by(func.count(Issue.id).desc()).limit(10).all()
    
    top_locations = [
        {
            "location": loc[0],
            "issue_count": loc[1],
            "avg_priority": round(loc[2], 2)
        }
        for loc in location_counts
    ]
    
    return {
        "total_issues": total_issues,
        "critical_issues": critical,
        "high_issues": high,
        "medium_issues": medium,
        "low_issues": low,
        "resolved_issues": resolved,
        "pending_issues": pending,
        "issue_types": issues_by_type,
        "priority_distribution": issues_by_priority,
        "issues_by_status": issues_by_status,
        "recent_issues": recent_issues,
        "top_locations": top_locations
    }


@router.get("/stats/by-type")
async def get_stats_by_type(db: Session = Depends(get_db)):
    """Get detailed statistics for each issue type"""
    
    type_stats = {}
    issue_types = db.query(Issue.issue_type).distinct().all()
    
    for (issue_type,) in issue_types:
        count = db.query(func.count(Issue.id)).filter(Issue.issue_type == issue_type).scalar()
        avg_priority = db.query(func.avg(Issue.priority_score)).filter(Issue.issue_type == issue_type).scalar()
        resolved = db.query(func.count(Issue.id)).filter(
            Issue.issue_type == issue_type,
            Issue.status == "resolved"
        ).scalar()
        
        type_stats[issue_type] = {
            "total": count,
            "avg_priority_score": round(avg_priority or 0, 2),
            "resolved": resolved,
            "pending": (count - resolved) if resolved else count,
            "resolution_rate": round((resolved / count * 100) if count > 0 else 0, 1)
        }
    
    return type_stats


@router.get("/stats/priority-timeline")
async def get_priority_timeline(
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    """Get priority statistics over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily counts by priority level
    daily_stats = db.query(
        func.date(Issue.created_at).label('date'),
        Issue.priority_level,
        func.count(Issue.id).label('count')
    ).filter(Issue.created_at >= start_date).group_by(
        func.date(Issue.created_at),
        Issue.priority_level
    ).all()
    
    # Organize data
    timeline = {}
    for date, priority, count in daily_stats:
        date_str = str(date)
        if date_str not in timeline:
            timeline[date_str] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        timeline[date_str][priority] = count
    
    return timeline


@router.get("/stats/top-priority")
async def get_top_priority_issues(limit: int = Query(20), db: Session = Depends(get_db)):
    """Get top priority unresolved issues"""
    
    top_issues = db.query(Issue).filter(
        Issue.status != "resolved"
    ).order_by(Issue.priority_score.desc()).limit(limit).all()
    
    return [
        {
            "id": i.id,
            "title": i.title,
            "issue_type": i.issue_type,
            "priority_score": i.priority_score,
            "priority_level": i.priority_level,
            "location": i.location_description,
            "upvotes": i.upvotes,
            "ai_confidence": i.ai_confidence,
            "created_at": i.created_at
        }
        for i in top_issues
    ]


@router.get("/stats/resolution-rate")
async def get_resolution_rate(db: Session = Depends(get_db)):
    """Get overall resolution rate statistics"""
    
    total = db.query(func.count(Issue.id)).scalar() or 0
    resolved = db.query(func.count(Issue.id)).filter(Issue.status == "resolved").scalar() or 0
    pending = total - resolved
    
    avg_resolution_time = db.query(
        func.avg(Issue.resolved_at - Issue.created_at)
    ).filter(Issue.resolved_at.isnot(None)).scalar()
    
    # By type
    by_type = {}
    type_counts = db.query(Issue.issue_type).distinct().all()
    for (issue_type,) in type_counts:
        type_total = db.query(func.count(Issue.id)).filter(Issue.issue_type == issue_type).scalar()
        type_resolved = db.query(func.count(Issue.id)).filter(
            Issue.issue_type == issue_type,
            Issue.status == "resolved"
        ).scalar()
        by_type[issue_type] = {
            "total": type_total,
            "resolved": type_resolved,
            "rate": round((type_resolved / type_total * 100) if type_total > 0 else 0, 1)
        }
    
    return {
        "total_issues": total,
        "resolved": resolved,
        "pending": pending,
        "overall_resolution_rate": round((resolved / total * 100) if total > 0 else 0, 1),
        "avg_resolution_time_hours": str(avg_resolution_time) if avg_resolution_time else "N/A",
        "by_type": by_type
    }


@router.get("/export/csv")
async def export_to_csv(db: Session = Depends(get_db)):
    """Export all issues to CSV format"""
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    issues = db.query(Issue).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Type", "Priority", "Status", "Location", 
        "Latitude", "Longitude", "Upvotes", "AI Confidence", "Created At", "Resolved At"
    ])
    
    for issue in issues:
        writer.writerow([
            issue.id,
            issue.title,
            issue.issue_type,
            issue.priority_level,
            issue.status,
            issue.location_description,
            issue.latitude,
            issue.longitude,
            issue.upvotes,
            issue.ai_confidence,
            issue.created_at,
            issue.resolved_at
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=issues_export.csv"}
    )
