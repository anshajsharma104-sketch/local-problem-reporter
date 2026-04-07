# 🚨 Local Problem Reporter - AI-Powered Infrastructure Issue Tracking

An intelligent platform where citizens can report local infrastructure issues (potholes, garbage, water leaks, traffic problems, landslides, etc.) with AI-powered categorization, automatic priority scoring, and a dashboard for authorities to respond efficiently.

## ✨ Features

### 🎯 Core Features
- **AI Image Recognition**: Upload photos of issues - YOLOv5 detects and categorizes them automatically
- **Smart Priority Scoring**: Issues are automatically prioritized based on:
  - Issue severity type
  - AI confidence level
  - Community upvotes
  - Location density (nearby similar issues)
  - Time since report
- **Community-Driven**: Users can upvote issues to increase priority
- **Real-Time Updates**: Track issue status as authorities respond
- **Interactive Dashboard**: Authorities view, filter, and manage issues

### 📊 Authority Dashboard
- **Statistics Overview**: Critical, high, medium, low priority counts
- **Charts & Analytics**: Visual breakdown by type, status, and priority
- **Status Management**: Update issue status (reported → investigating → resolved)
- **Location Tracking**: Top locations with most issues
- **CSV Export**: Download issue data for further analysis

### 🎨 Issue Detection Categories
- 🛣️ **Road Damage** (potholes, cracks, asphalt damage)
- ♻️ **Garbage/Litter** (bottles, trash, bags, plastic)
- 💧 **Water Leaks** (puddles, flooding, wet areas)
- 🚗 **Traffic Issues** (congestion, accidents, unsafe conditions)
- 🏗️ **Construction/Barriers** (construction sites, blockages)
- ⛰️ **Landslides** (dirt, rocks, debris, soil issues)
- ❓ **Other** (miscellaneous issues)

## 🏗️ Project Structure

```
local-problem-reporter/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── models.py               # SQLAlchemy database models
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── database.py             # Database configuration
│   │   ├── routes/
│   │   │   ├── issues.py           # Issue upload & retrieval endpoints
│   │   │   └── analytics.py        # Analytics & dashboard endpoints
│   │   └── services/
│   │       ├── ai_detector.py      # YOLOv5 image detection service
│   │       └── priority_scorer.py  # Priority calculation logic
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx                 # Main React component
│   │   ├── index.js                # React entry point
│   │   ├── index.css               # Global styles
│   │   ├── pages/
│   │   │   ├── ReportPage.jsx      # Issue reporting form
│   │   │   ├── IssuesListPage.jsx  # Browse all issues
│   │   │   ├── IssueDetailPage.jsx # Issue details & authority actions
│   │   │   ├── DashboardPage.jsx   # Authority dashboard
│   │   │   └── AnalyticsPage.jsx   # Analytics & reports
│   │   └── components/             # Reusable components
│   └── package.json
├── uploads/                        # Uploaded images directory
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Create Python virtual environment**:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download YOLOv5 model** (first run will auto-download):
```bash
python -c "import yolov5; yolov5.load('yolov5s')"
```

4. **Run the backend server**:
```bash
python run.py
```

Server will start at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start development server**:
```bash
npm start
```

Frontend will open at `http://localhost:3000`

## 📚 API Endpoints

### Issue Management

**Upload Issue**
```
POST /api/issues/upload
```
- Accepts multipart form data with image, title, description, location
- Returns: issue details with AI detection results

**Get All Issues**
```
GET /api/issues/all?priority=high&status=reported&issue_type=road_damage
```

**Get Issue Details**
```
GET /api/issues/{issue_id}
```

**Upvote Issue**
```
POST /api/issues/{issue_id}/upvote
```

**Update Issue Status** (Authority only)
```
PATCH /api/issues/{issue_id}/status?new_status=investigating&notes=...
```

### Analytics

**Dashboard Overview**
```
GET /api/analytics/dashboard
```

**Detailed Statistics by Type**
```
GET /api/analytics/stats/by-type
```

**Resolution Rate Statistics**
```
GET /api/analytics/stats/resolution-rate
```

**Priority Timeline**
```
GET /api/analytics/stats/priority-timeline?days=30
```

**Export to CSV**
```
GET /api/analytics/export/csv
```

## 🤖 AI Detection System

### How Priority Scoring Works

The system calculates priority using multiple factors:

```
Priority Score = (Base Score × Confidence Factor) + Upvote Factor + Density Factor + Time Factor

Where:
- Base Score = Issue type severity (10-100)
- Confidence Factor = 0.6 to 1.0 (based on AI model confidence)
- Upvote Factor = 5 points per upvote (max 20)
- Density Factor = 8 points per nearby similar issue (max 25)
- Time Factor = Up to 15 points over 24 hours for unresolved

Final Score: 0-100
- 80+: CRITICAL 🔴
- 60-79: HIGH 🟠
- 40-59: MEDIUM 🟡
- 0-39: LOW 🟢
```

### YOLOv5 Integration

- **Model**: YOLOv5 Small (lightweight, fast)
- **Categories**: Trained on COCO dataset with custom labels
- **Confidence Threshold**: 0.45
- **Detection Output**: Object names, confidence scores, bounding boxes

## 🗄️ Database Schema

### Users Table
- id, email, username, full_name, is_authority, created_at

### Issues Table
- id, reporter_id, title, description, issue_type, image_path
- latitude, longitude, location_description
- priority_score, priority_level, status
- ai_confidence, ai_detected_objects
- upvotes, created_at, updated_at, resolved_at

### IssueUpdate Table
- id, issue_id, authority_id, status_update, notes, created_at

### Analytics Table
- id, date, issue_type, count, avg_priority, resolution_rate

## 🔐 Security Considerations

- **Authentication** (TODO): Implement JWT token-based auth
- **Authorization**: Authority actions require role verification
- **File Validation**: Validate image file size and format
- **Rate Limiting**: Implement API rate limiting
- **CORS**: Currently allows all origins (configure in production)
- **Input Validation**: All inputs validated via Pydantic schemas

## 🎨 Customization

### Adding New Issue Types

Edit `backend/app/services/ai_detector.py`:
```python
new_keywords = ['keyword1', 'keyword2']
object_confidence['new_type'] = max(...)
```

### Changing Priority Weights

Edit `backend/app/services/priority_scorer.py`:
```python
ISSUE_SEVERITY = {
    "your_type": 85,  # Adjust severity
}
```

### Styling

All CSS is in `frontend/src/index.css`. Customize colors by changing:
```css
--primary-color: #667eea;
--secondary-color: #764ba2;
```

## 📱 Usage Examples

### As a User

1. Go to "Report Issue"
2. Upload a photo of the problem
3. Fill in title and location
4. Click "Get My Location" for auto-location
5. Submit - AI categorizes automatically
6. Browse "View Issues" and upvote for higher priority

### As an Authority

1. Switch to "Authority Mode"
2. View "Dashboard" for overview
3. Check "Analytics" for detailed statistics
4. Click "View Issues" and select one
5. Update status and add notes
6. Issue status changes to "Investigating" or "Resolved"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📋 TODO / Future Enhancements

- [ ] User authentication & authorization
- [ ] Email notifications for issue updates
- [ ] SMS alerts for critical issues
- [ ] Mobile app (React Native)
- [ ] Advanced mapping with issue clusters
- [ ] Machine learning model training pipeline
- [ ] Multi-language support
- [ ] Offline issue reporting
- [ ] Photo gallery for each issue
- [ ] Community forums & comments
- [ ] Performance metrics & leaderboards
- [ ] Integration with third-party services

## 🐛 Troubleshooting

### YOLOv5 Model Download Issues
```bash
# Manual download
python -c "import yolov5; model = yolov5.load('yolov5s')"
```

### CORS Errors
- Update `backend/app/main.py` to restrict origin in production
- Frontend proxy in `frontend/package.json` should match backend URL

### Database Errors
- Delete `backend/problems.db` to reset database
- Ensure `sqlite` is available (usually pre-installed with Python)

### Port Already in Use
```bash
# Change backend port
python -c "uvicorn app.main:app --port 8001"

# Change frontend port
PORT=3001 npm start
```

## 📄 License

MIT License - see LICENSE file for details

## 📞 Contact & Support

For issues, questions, or suggestions:
- GitHub Issues: [Create an issue]
- Email: support@localproblemsreporter.xyz
- Discord: [Join our community]

---

**Made with ❤️ for better communities**

*"Report it. We'll fix it. Together."*
