from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional

from ..database import get_db
from ..models import Issue, User, IssueUpdate, IssueUpvote
from ..schemas import (
    IssueList, IssueDetailResponse, Issue as IssueSchema, IssueCreate, IssueUpdate as IssueUpdateSchema
)
from ..services import AIIssueDetector, PriorityScorer
from ..services.geocoding import GeocodingService

router = APIRouter(prefix="/api/issues", tags=["issues"])

# Initialize AI detector (lazy initialization)
detector = None

def get_detector():
    global detector
    if detector is None:
        try:
            from ..services import AIIssueDetector
            detector = AIIssueDetector()
        except Exception as e:
            print(f"Warning: Could not initialize AI detector: {e}")
            detector = None
    return detector


@router.post("/upload", response_model=IssueDetailResponse)
async def upload_issue(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(default=""),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_description: str = Form(default=""),
    issue_type: str = Form(default="other"),  # User can manually select
    reporter_id: int = Form(default=1),  # In production, would use authentication
    db: Session = Depends(get_db)
):
    """
    Upload a new issue with image
    - Runs AI detection on image
    - Calculates priority score
    - Stores in database
    """
    try:
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Store as URL path for frontend access
        url_path = f"/uploads/{file.filename}"
        
        # Use user-provided issue type, or try AI detection if "auto" selected
        confidence = 0.0
        detected_objects = []
        priority_type_for_scoring = issue_type  # May differ from stored issue_type
        
        if issue_type == "auto":
            # Try AI detection for auto-detect
            detector = get_detector()
            if detector:
                detected_issue_type, confidence, detected_objects = detector.detect_issue_type(file_path)
                if confidence > 0.3:
                    # AI found something - use it
                    issue_type = detected_issue_type
                    priority_type_for_scoring = detected_issue_type
                print(f"✓ AI detected: {issue_type} (confidence: {confidence:.2f})")
            else:
                # AI has low confidence - keep "other" but report actual AI confidence
                issue_type = "other"
                priority_type_for_scoring = "other"
                confidence = max(confidence, 0.3)
                print(f"✓ AI confidence {confidence:.2f}, using 'other' type")
        elif issue_type != "other":
            # User selected a specific type - use that with high confidence
            confidence = 0.95
            priority_type_for_scoring = issue_type
            print(f"✓ User selected: {issue_type}")
        else:
            # User selected "other" - try AI but keep as "other" if fails
            detector = get_detector()
            if detector:
                detected_issue_type, detected_conf, detected_objects = detector.detect_issue_type(file_path)
                if detected_conf > 0.7:
                    # AI found something with HIGH confidence - use detected type for BOTH storage and priority
                    issue_type = detected_issue_type
                priority_type_for_scoring = detected_issue_type
                confidence = detected_conf
                print(f"✓ AI detected with high confidence: {issue_type} ({confidence:.2%})")
            elif detected_conf > 0.5:
                # AI found something with medium confidence - use detected type for priority only
                priority_type_for_scoring = detected_issue_type
                confidence = detected_conf
                print(f"✓ AI detected: {issue_type} (confidence: {confidence:.2f}, using for priority)")
            else:
                # Keep as "other" 
                priority_type_for_scoring = "other"
                confidence = max(detected_conf, 0.3)
                detected_objects = []
                print(f"✓ Keeping as 'other' type with AI confidence {confidence:.2f}")
        
        # Calculate priority score using the appropriate issue type
        priority_score, priority_level = PriorityScorer.calculate_priority_score(
            issue_type=priority_type_for_scoring,
            ai_confidence=confidence,
            upvotes=0,
            status="reported"
        )
        
        # Create issue record
        db_issue = Issue(
            reporter_id=reporter_id,
            title=title,
            description=description,
            issue_type=issue_type,
            image_path=url_path,
            latitude=latitude,
            longitude=longitude,
            location_description=location_description,
            priority_score=priority_score,
            priority_level=priority_level,
            ai_confidence=confidence,
            ai_detected_objects=json.dumps(detected_objects),
            status="reported"
        )
        
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        
        return {
            "id": db_issue.id,
            "title": db_issue.title,
            "description": db_issue.description,
            "issue_type": db_issue.issue_type,
            "image_path": db_issue.image_path,
            "priority_level": db_issue.priority_level,
            "priority_score": db_issue.priority_score,
            "status": db_issue.status,
            "ai_detected_objects": db_issue.ai_detected_objects,
            "ai_confidence": db_issue.ai_confidence,
            "latitude": db_issue.latitude,
            "longitude": db_issue.longitude,
            "location_description": db_issue.location_description,
            "upvotes": db_issue.upvotes,
            "created_at": db_issue.created_at,
            "resolved_at": db_issue.resolved_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing issue: {str(e)}")


@router.get("/all", response_model=List[IssueList])
async def get_all_issues(
    db: Session = Depends(get_db),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    issue_type: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """
    Get all issues with optional filtering
    """
    query = db.query(Issue)
    
    if priority:
        query = query.filter(Issue.priority_level == priority)
    if status:
        query = query.filter(Issue.status == status)
    if issue_type:
        query = query.filter(Issue.issue_type == issue_type)
    
    issues = query.order_by(Issue.priority_score.desc(), Issue.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        IssueList(
            id=i.id,
            title=i.title,
            issue_type=i.issue_type,
            image_path=i.image_path,
            priority_level=i.priority_level,
            priority_score=i.priority_score,
            status=i.status,
            created_at=i.created_at,
            upvotes=i.upvotes,
            satisfaction_votes=i.satisfaction_votes,
            latitude=i.latitude,
            longitude=i.longitude,
            location_description=i.location_description,
            street_address=i.street_address
        )
        for i in issues
    ]


@router.get("/{issue_id}", response_model=IssueDetailResponse)
async def get_issue_detail(issue_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    reporter = db.query(User).filter(User.id == issue.reporter_id).first()
    
    # Get all updates for this issue
    updates = db.query(IssueUpdate).filter(IssueUpdate.issue_id == issue_id).order_by(IssueUpdate.created_at.desc()).all()
    
    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "issue_type": issue.issue_type,
        "image_path": issue.image_path,
        "priority_level": issue.priority_level,
        "priority_score": issue.priority_score,
        "status": issue.status,
        "ai_detected_objects": issue.ai_detected_objects,
        "ai_confidence": issue.ai_confidence,
        "latitude": issue.latitude,
        "longitude": issue.longitude,
        "location_description": issue.location_description,
        "street_address": issue.street_address,
        "upvotes": issue.upvotes,
        "satisfaction_votes": issue.satisfaction_votes,
        "created_at": issue.created_at,
        "resolved_at": issue.resolved_at,
        "updates": [
            {
                "id": u.id,
                "status_update": u.status_update,
                "notes": u.notes,
                "created_at": u.created_at
            }
            for u in updates
        ],
        "reporter": reporter
    }


@router.post("/{issue_id}/upvote")
async def upvote_issue(
    issue_id: int,
    token: str = Query(...),
    vote_type: str = Query("priority"),  # 'priority' or 'satisfaction'
    db: Session = Depends(get_db)
):
    """Add upvote to an issue (authenticated users only, one vote per type per user)"""
    from ..services.auth import decode_access_token
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    
    # Check if issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check if user has already voted with this type on this issue
    existing_upvote = db.query(IssueUpvote).filter(
        IssueUpvote.issue_id == issue_id,
        IssueUpvote.user_id == user_id,
        IssueUpvote.vote_type == vote_type
    ).first()
    
    if existing_upvote:
        raise HTTPException(status_code=400, detail=f"You have already voted for {vote_type} on this issue")
    
    # Create new upvote record with vote type
    upvote = IssueUpvote(issue_id=issue_id, user_id=user_id, vote_type=vote_type)
    db.add(upvote)
    
    # Increment appropriate vote count
    if vote_type == "satisfaction":
        issue.satisfaction_votes += 1
    else:  # priority
        issue.upvotes += 1
    
    # Recalculate priority (only for priority votes)
    if vote_type == "priority":
        priority_score, priority_level = PriorityScorer.calculate_priority_score(
            issue_type=issue.issue_type,
            ai_confidence=issue.ai_confidence,
            upvotes=issue.upvotes,
            status=issue.status
        )
        issue.priority_score = priority_score
        issue.priority_level = priority_level
    
    db.commit()
    db.refresh(issue)
    
    return {
        "upvotes": issue.upvotes,
        "satisfaction_votes": issue.satisfaction_votes,
        "priority_score": issue.priority_score,
        "message": f"✓ {vote_type.capitalize()} vote added"
    }


@router.get("/{issue_id}/has-upvoted")
async def has_user_upvoted(
    issue_id: int,
    token: str = Query(...),
    vote_type: str = Query("priority"),  # 'priority' or 'satisfaction'
    db: Session = Depends(get_db)
):
    """Check if current user has voted (with specific type) on this issue"""
    from ..services.auth import decode_access_token
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    
    # Check if user has voted with this type
    upvote = db.query(IssueUpvote).filter(
        IssueUpvote.issue_id == issue_id,
        IssueUpvote.user_id == user_id,
        IssueUpvote.vote_type == vote_type
    ).first()
    
    return {"has_upvoted": upvote is not None}


@router.get("/{issue_id}/address")
async def get_issue_address(
    issue_id: int,
    db: Session = Depends(get_db)
):
    """Get street address for an issue (with caching), returns lat/lon fallback if geocoding fails"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # If address already cached, return it
    if issue.street_address:
        return {
            "location_description": issue.location_description,
            "street_address": issue.street_address,
            "latitude": issue.latitude,
            "longitude": issue.longitude
        }
    
    # Otherwise, try to get address from Nominatim and cache it
    address = await GeocodingService.get_address_from_coordinates(issue.latitude, issue.longitude)
    
    if address:
        issue.street_address = address
        db.commit()
        db.refresh(issue)
        return {
            "location_description": issue.location_description,
            "street_address": address,
            "latitude": issue.latitude,
            "longitude": issue.longitude
        }
    else:
        # If geocoding fails, return lat/lon format as fallback
        return {
            "location_description": issue.location_description,
            "street_address": f"Lat: {issue.latitude:.4f}, Lon: {issue.longitude:.4f}",
            "latitude": issue.latitude,
            "longitude": issue.longitude
        }


@router.patch("/{issue_id}/status")
async def update_issue_status(
    issue_id: int,
    new_status: str = Query(...),
    notes: str = Query(""),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update issue status (for authorities only)"""
    from ..services.auth import decode_access_token
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if user is authority
    is_authority = payload.get("is_authority", False)
    if not is_authority:
        raise HTTPException(status_code=403, detail="Only authorities can update issue status")
    
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    old_status = issue.status
    issue.status = new_status
    
    if new_status == "resolved":
        issue.resolved_at = datetime.utcnow()
    
    # Add update record
    update = IssueUpdate(
        issue_id=issue_id,
        authority_id=int(payload.get("sub")),
        status_update=f"{old_status} → {new_status}",
        notes=notes
    )
    
    db.add(update)
    db.commit()
    
    return {"status": issue.status, "updated_at": issue.updated_at}


@router.get("/by-type/{issue_type}")
async def get_issues_by_type(issue_type: str, db: Session = Depends(get_db)):
    """Get all issues of a specific type"""
    issues = db.query(Issue).filter(Issue.issue_type == issue_type).all()
    return [
        {
            "id": i.id,
            "title": i.title,
            "priority_level": i.priority_level,
            "status": i.status,
            "location": {"lat": i.latitude, "lon": i.longitude}
        }
        for i in issues
    ]


@router.get("/resolved/list", response_model=List[IssueList])
async def get_resolved_issues(
    db: Session = Depends(get_db),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Get all resolved issues (visible to all users)"""
    issues = db.query(Issue).filter(Issue.status == "resolved").order_by(Issue.upvotes.desc(), Issue.resolved_at.desc()).offset(skip).limit(limit).all()
    
    return [
        IssueList(
            id=i.id,
            title=i.title,
            issue_type=i.issue_type,
            image_path=i.image_path,
            priority_level=i.priority_level,
            priority_score=i.priority_score,
            status=i.status,
            created_at=i.created_at,
            upvotes=i.upvotes,
            satisfaction_votes=i.satisfaction_votes,
            latitude=i.latitude,
            longitude=i.longitude,
            location_description=i.location_description,
            street_address=i.street_address
        )
        for i in issues
    ]


@router.delete("/{issue_id}/delete")
async def delete_issue(
    issue_id: int,
    user_id: int = Query(...),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a resolved issue (authority only, requires 5+ upvotes)"""
    from ..services.auth import decode_access_token
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if user is authority
    is_authority = payload.get("is_authority", False)
    if not is_authority:
        raise HTTPException(status_code=403, detail="Only authorities can delete issues")
    
    # Get the issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check if issue is resolved
    if issue.status != "resolved":
        raise HTTPException(status_code=400, detail="Only resolved issues can be deleted")
    
    # Check if issue has at least 5 upvotes
    if issue.upvotes < 5:
        raise HTTPException(
            status_code=400, 
            detail=f"Issue needs at least 5 upvotes to be deleted (current: {issue.upvotes})"
        )
    
    # Delete the issue
    db.delete(issue)
    db.commit()
    
    return {"message": "Issue deleted successfully", "issue_id": issue_id}
