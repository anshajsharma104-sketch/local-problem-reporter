from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_authority: bool
    created_at: datetime

    class Config:
        from_attributes = True


class IssueBase(BaseModel):
    title: str
    description: str
    location_description: str
    latitude: float
    longitude: float


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None


class Issue(IssueBase):
    id: int
    reporter_id: int
    issue_type: str
    image_path: str
    priority_score: float
    priority_level: str
    status: str
    ai_confidence: float
    ai_detected_objects: Optional[str]
    upvotes: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class IssueList(BaseModel):
    id: int
    title: str
    issue_type: str
    image_path: Optional[str] = None
    priority_level: str
    priority_score: float
    status: str
    created_at: datetime
    upvotes: int
    satisfaction_votes: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None
    street_address: Optional[str] = None

    class Config:
        from_attributes = True


class IssueUpdateResponse(BaseModel):
    id: int
    status_update: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class IssueDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    issue_type: str
    image_path: Optional[str] = None
    priority_level: str
    priority_score: float
    status: str
    ai_detected_objects: Optional[str]
    ai_confidence: float
    latitude: float
    longitude: float
    location_description: str
    street_address: Optional[str] = None
    upvotes: int
    satisfaction_votes: int = 0
    created_at: datetime
    resolved_at: Optional[datetime] = None
    updates: List[IssueUpdateResponse] = []
    reporter: Optional[User] = None


class AnalyticsResponse(BaseModel):
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    resolved_issues: int
    pending_issues: int
    issue_types: Dict[str, int]
    priority_distribution: Dict[str, int]


class DashboardResponse(BaseModel):
    total_issues: int
    issues_by_type: Dict[str, int]
    issues_by_priority: Dict[str, int]
    issues_by_status: Dict[str, int]
    recent_issues: List[IssueList]
    top_locations: List[Dict[str, Any]]
