# 🏛️ Architecture & System Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER (Browser)                       │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │          React Frontend (http://localhost:3000)         │     │
│  │                                                          │     │
│  │  • User Page - Report Issues                           │     │
│  │  • Issues List - Browse & Upvote                       │     │
│  │  • Issue Detail - View & Comment                       │     │
│  │  • Authority Dashboard - Statistics                    │     │
│  │  • Analytics Page - Detailed Reports                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                            ↕ HTTPS/HTTP                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI)                           │
│              (http://localhost:8000)                             │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Issue Routes     │  │ Analytics Routes │  │ Utility      │  │
│  │                  │  │                  │  │ Endpoints    │  │
│  │ • POST /upload   │  │ • /dashboard     │  │              │  │
│  │ • GET /all       │  │ • /stats/by-type │  │ • /health    │  │
│  │ • GET /:id       │  │ • /stats/res-rate│  │ • /system    │  │
│  │ • POST /:id/vote │  │ • /export/csv    │  │ • /info      │  │
│  │ • PATCH /:id/sts │  │                  │  │              │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│           ↕                    ↕                      ↕           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              SERVICES & AI LAYER                                  │
│                                                                   │
│  ┌────────────────────────┐  ┌─────────────────────────────┐   │
│  │  AI Issue Detector     │  │  Priority Scorer             │   │
│  │  (ai_detector.py)      │  │  (priority_scorer.py)        │   │
│  │                        │  │                             │   │
│  │ • YOLOv5 Model         │  │ Calculates Priority Score:  │   │
│  │ • Image Processing     │  │ • Base Severity (Type)      │   │
│  │ • Object Detection     │  │ • AI Confidence             │   │
│  │ • Category Mapping     │  │ • Community Upvotes         │   │
│  │                        │  │ • Location Density          │   │
│  │ Returns:               │  │ • Time Since Report         │   │
│  │ - issue_type (str)     │  │                             │   │
│  │ - confidence (0-1)     │  │ Returns:                    │   │
│  │ - objects (list)       │  │ - priority_score (0-100)    │   │
│  │                        │  │ - priority_level (text)     │   │
│  └────────────────────────┘  └─────────────────────────────┘   │
│           ↕                            ↕                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│               DATABASE LAYER (SQLite)                            │
│            (problems.db - local development)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Users Table  │  │ Issues Table │  │ Updates Tbl  │           │
│  │              │  │              │  │              │           │
│  │ • id         │  │ • id         │  │ • id         │           │
│  │ • email      │  │ • reporter_id│  │ • issue_id   │           │
│  │ • username   │  │ • title      │  │ • authority  │           │
│  │ • is_auth    │  │ • description│  │ • status_upd │           │
│  │              │  │ • type       │  │ • notes      │           │
│  │              │  │ • image_path │  │              │           │
│  │              │  │ • lat/lon    │  │              │           │
│  │              │  │ • priority   │  │              │           │
│  │              │  │ • status     │  │              │           │
│  │              │  │ • ai_conf    │  │              │           │
│  │              │  │ • upvotes    │  │              │           │
│  │              │  │ • timestamps │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              EXTERNAL RESOURCES                                   │
│                                                                   │
│  • YOLOv5 Model (from ultralytics)                              │
│  • Image Storage (uploads/ folder locally)                       │
│  • File System                                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Issue Reporting Flow

```
User                Frontend            Backend             AI Service           Database
│                    │                   │                   │                    │
├─ Upload image ────→│                   │                   │                    │
│                    │  POST /upload     │                   │                    │
│                    ├──────────────────→│                   │                    │
│                    │                   │  Detect issue     │                    │
│                    │                   ├─────────────────→│                    │
│                    │                   │←───────────────┬──│                    │
│                    │                   │                │                      │
│                    │                   │  Calculate priority                   │
│                    │                   │  (type, upvotes, density)             │
│                    │                   │                                       │
│                    │                   │  Store issue ──────────────────────→  │
│                    │                   │  and AI results                       │
│                    │←───── Response ────│                                      │
│ ← Display result ──│                   │                                      │
│                    │                   │                                      │
```

### Authority Update Flow

```
Authority           Frontend            Backend             Database
│                    │                   │                   │
├─ Select issue ────→│                   │                   │
│ ├─ Set status      │                   │                   │
│ ├─ Add notes       │                   │                   │
│ └─ Submit          │ PATCH /status     │                   │
│                    ├──────────────────→│                   │
│                    │                   │ Update status     │
│                    │                   │ Create update rec │
│                    │                   ├──────────────────→
│                    │                   │   Store issue     │
│                    │                   │   Store update    │
│                    │←─ 200 OK ─────────│   Resp with data  │
│ ← Confirm update ──│                   │                   │
│                    │                   │                   │
```

### Analytics Flow

```
Authority/Admin     Frontend            Backend             Database
│                    │                   │                   │
├─ View Dashboard ──→│                   │                   │
│                    │ GET /dashboard    │                   │
│                    ├──────────────────→│                   │
│                    │                   │ Query issues      │
│                    │                   │ Count by type     │
│                    │                   │ Count by priority │
│                    │                   │ Calculate stats   │
│                    │                   ├──────────────────→
│                    │                   │   Aggregate data  │
│                    │                   │←──────────────────┤
│                    │←─ JSON Response ──│                   │
│ ← Display charts ──│                   │                   │
│                    │                   │                   │
```

## Priority Scoring Algorithm

```
┌─────────────────────────────────────────────────────┐
│          PRIORITY SCORE CALCULATION                  │
│                                                      │
│  Final Score = (Base Score × Confidence) +          │
│                 Upvote Factor +                      │
│                 Density Factor +                     │
│                 Time Factor                          │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. BASE SCORE (by issue type):                     │
│     Landslide: 100                                  │
│     Water Leak: 75                                  │
│     Road Damage: 70                                 │
│     Traffic: 60                                     │
│     Construction: 50                                │
│     Garbage: 30                                     │
│     Other: 20                                       │
│                                                      │
│  2. CONFIDENCE FACTOR (0.6x - 1.0x):               │
│     AI Model confidence in detection                │
│     Lower confidence = lower multiplier             │
│                                                      │
│  3. UPVOTE FACTOR:                                  │
│     5 points per upvote (max 20)                    │
│     Community validates issue importance            │
│                                                      │
│  4. DENSITY FACTOR:                                 │
│     8 points per similar issue nearby (max 25)      │
│     Indicates area problem concentration            │
│                                                      │
│  5. TIME FACTOR:                                    │
│     Up to 15 points over 24 hours                   │
│     Older unresolved issues get boost               │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  PRIORITY LEVELS:                                   │
│  ┌─────────────────────────────────────┐           │
│  │ Score Range → Priority Level        │           │
│  ├─────────────────────────────────────┤           │
│  │ 80-100     → CRITICAL 🔴           │           │
│  │ 60-79      → HIGH     🟠           │           │
│  │ 40-59      → MEDIUM   🟡           │           │
│  │ 0-39       → LOW      🟢           │           │
│  └─────────────────────────────────────┘           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Issue Classification System

```
IMAGE INPUT
    ↓
    ├─→ YOLOv5 Model
    │   (Object Detection)
    │
    ├─→ Extract Detected Objects
    │   (bird, car, person, etc.)
    │
    └─→ Keyword Matching
        ↓
        ├─→ Road Keywords
        │   (pothole, crack, damage)
        │   → ROAD_DAMAGE
        │
        ├─→ Garbage Keywords
        │   (bottle, trash, bag, plastic)
        │   → GARBAGE
        │
        ├─→ Water Keywords
        │   (puddle, water, wet, flood)
        │   → WATER_LEAK
        │
        ├─→ Traffic Keywords
        │   (car, truck, bus, person)
        │   → TRAFFIC
        │
        ├─→ Construction Keywords
        │   (construction, barrier, cone)
        │   → CONSTRUCTION
        │
        ├─→ Landslide Keywords
        │   (dirt, rock, debris, mud)
        │   → LANDSLIDE
        │
        └─→ No Match
            → OTHER

RETURN: (issue_type, confidence_score, detected_objects)
```

## User Roles & Permissions

```
┌─────────────────────────────────────────────────┐
│                USER ROLES                        │
├─────────────────────────────────────────────────┤
│                                                  │
│  REGULAR USER                                   │
│  ├─ Report issues (upload image & details)     │
│  ├─ Browse all issues                          │
│  ├─ View issue details                         │
│  ├─ Upvote issues (increase priority)          │
│  ├─ View dashboard (read-only)                 │
│  └─ Cannot: Modify or resolve issues           │
│                                                  │
│  AUTHORITY (Admin)                             │
│  ├─ All user permissions                       │
│  ├─ View authority dashboard                   │
│  ├─ Update issue status                        │
│  ├─ Add notes to issues                        │
│  ├─ View detailed analytics                    │
│  ├─ Export data (CSV)                          │
│  ├─ View resolution statistics                 │
│  └─ Manage issue priorities                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│           TECHNOLOGY STACK              │
├─────────────────────────────────────────┤
│                                         │
│ FRONTEND                                │
│  • React 18.2.0                        │
│  • React Router (navigation)            │
│  • Axios (HTTP client)                  │
│  • Chart.js (analytics charts)          │
│  • Leaflet (mapping - future)           │
│  • CSS3 (responsive styling)            │
│                                         │
│ BACKEND                                 │
│  • Python 3.8+                         │
│  • FastAPI 0.104.1                     │
│  • Uvicorn (ASGI server)                │
│  • SQLAlchemy 2.0.23 (ORM)              │
│  • Pydantic 2.5.0 (validation)          │
│                                         │
│ AI/ML                                   │
│  • YOLOv5 7.0.13 (object detection)    │
│  • PyTorch 2.1.0 (deep learning)        │
│  • OpenCV 4.8.1.78 (image processing)   │
│  • Pillow 10.1.0 (image handling)       │
│                                         │
│ DATABASE                                │
│  • SQLite (development)                 │
│  • PostgreSQL (production ready)         │
│                                         │
│ DEPLOYMENT                              │
│  • Docker & Docker Compose              │
│  • Nginx (reverse proxy)                │
│  • Gunicorn (production server)         │
│                                         │
└─────────────────────────────────────────┘
```

## Deployment Architecture

```
                        PRODUCTION SETUP

┌──────────────────────────────────────────────────┐
│                   INTERNET                        │
│                (Load Balancer)                    │
│                       ↓                           │
├──────────────────────────────────────────────────┤
│               NGINX (Reverse Proxy)              │
│           (Port 80/443, HTTPS, caching)          │
│                       ↓                           │
├──────────────────────────────────────────────────┤
│         DOCKER CONTAINERS                        │
│                                                   │
│  ┌─────────────────┐   ┌─────────────────┐     │
│  │ Backend         │   │ Frontend         │     │
│  │ (Gunicorn)      │   │ (Node.js)        │     │
│  │ Port: 8000      │   │ Port: 3000       │     │
│  └────────┬────────┘   └────────┬────────┘     │
│           │                     │                │
│           └─────────────┬───────┘                │
│                         ↓                        │
│            ┌─────────────────────┐              │
│            │  PostgreSQL DB      │              │
│            │  (Persistent Volume)│              │
│            └─────────────────────┘              │
│                                                   │
│            ┌─────────────────────┐              │
│            │  File Storage       │              │
│            │  (Uploaded images)  │              │
│            └─────────────────────┘              │
│                                                   │
└──────────────────────────────────────────────────┘

Cloud Providers:
• AWS EC2 / ECS
• DigitalOcean
• Heroku
• Railway
• Azure Container Instances
```

## Performance Considerations

```
┌─────────────────────────────────────────────┐
│        OPTIMIZATION STRATEGIES              │
├─────────────────────────────────────────────┤
│                                             │
│ BACKEND                                     │
│  • Database indexing on common queries     │
│  • Caching (Redis for analytics)           │
│  • Pagination for large datasets           │
│  • Batch processing for AI detection       │
│  • Connection pooling                      │
│  • Async operations where possible         │
│                                             │
│ FRONTEND                                    │
│  • Code splitting (lazy loading)           │
│  • Image optimization (lazy load)          │
│  • Minification & compression              │
│  • Browser caching                         │
│  • CDN for static assets                   │
│                                             │
│ AI/ML                                       │
│  • YOLOv5 Small (lightweight model)        │
│  • GPU acceleration (optional)              │
│  • Batch inference                         │
│  • Model quantization                      │
│                                             │
│ DATABASE                                    │
│  • Proper indexing                         │
│  • Query optimization                      │
│  • Connection pooling                      │
│  • Archive old data                        │
│  • Replication for production               │
│                                             │
└─────────────────────────────────────────────┘
```

## Security Architecture

```
┌────────────────────────────────────────────┐
│         SECURITY LAYERS                    │
├────────────────────────────────────────────┤
│                                            │
│ 1. NETWORK LEVEL                          │
│    • HTTPS/TLS encryption                 │
│    • Firewall rules                       │
│    • DDoS protection                      │
│                                           │
│ 2. APPLICATION LEVEL                      │
│    • Input validation (Pydantic)         │
│    • Output sanitization                 │
│    • SQL injection prevention (ORM)      │
│    • CSRF protection                     │
│                                           │
│ 3. AUTHENTICATION & AUTHORIZATION          │
│    • JWT tokens (future)                 │
│    • Role-based access control           │
│    • Session management                  │
│                                           │
│ 4. DATA LEVEL                             │
│    • Password hashing (bcrypt)           │
│    • Sensitive data encryption           │
│    • Secure file upload handling         │
│    • Database backups                    │
│                                           │
│ 5. API LEVEL                              │
│    • Rate limiting                       │
│    • API key authentication              │
│    • Request size limits                 │
│    • CORS configuration                  │
│                                           │
└────────────────────────────────────────────┘
```

---

**Last Updated**: March 2024
**Version**: 1.0.0
