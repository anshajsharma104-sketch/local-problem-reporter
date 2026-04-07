# ⚡ Quick Reference Card

## 🚀 Getting Started (5 Minutes)

### Terminal 1: Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
✅ Backend running: http://localhost:8000

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm start
```
✅ Frontend running: http://localhost:3000

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main app |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive docs |
| ReDoc | http://localhost:8000/redoc | API documentation |
| Health | http://localhost:8000/health | Server status |

---

## 📊 Main Pages

| Page | Frontend URL | Purpose |
|------|-------------|---------|
| Home | http://localhost:3000/ | Landing page |
| Report | http://localhost:3000/report | Report issue |
| Issues | http://localhost:3000/issues | Browse issues |
| Detail | http://localhost:3000/issue/:id | Issue details |
| Dashboard* | http://localhost:3000/dashboard | Authority view |
| Analytics* | http://localhost:3000/analytics | Statistics |

*Switch to "Authority Mode" to access these

---

## 🔑 Quick API Tests (curl)

```bash
# Health check
curl http://localhost:8000/health

# System info
curl http://localhost:8000/api/system/info

# Get all issues
curl "http://localhost:8000/api/issues/all?limit=10"

# Get dashboard
curl http://localhost:8000/api/analytics/dashboard

# Get scoring info
curl http://localhost:8000/api/scoring-info
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `uvicorn app.main:app --port 8001` |
| Port 3000 in use | `PORT=3001 npm start` |
| venv not found | Delete venv, recreate: `python -m venv venv` |
| CORS error | Backend not running or firewall issue |
| DB locked | Delete `backend/problems.db`, restart |
| Module not found | Restart venv: `source venv/Scripts/activate` |

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry |
| `backend/app/routes/issues.py` | Issue endpoints |
| `backend/app/routes/analytics.py` | Analytics endpoints |
| `backend/app/services/ai_detector.py` | AI detection |
| `backend/app/services/priority_scorer.py` | Priority scoring |
| `frontend/src/App.jsx` | React main component |
| `frontend/src/pages/*.jsx` | Page components |
| `frontend/src/index.css` | Styling |

---

## 🎯 Test Workflow

1. **Open http://localhost:3000**
2. **Click "Report Issue"**
3. **Select image** (any JPG/PNG)
4. **Fill details** (title, description, location)
5. **Click Submit** → AI processes
6. **View in "Issues" list**
7. **Switch to "Authority Mode"** for dashboard

---

## 📋 Database Inspection

```bash
# SQLite queries
sqlite3 backend/problems.db

# Inside sqlite:
.tables                      # List tables
SELECT COUNT(*) FROM issues; # Count issues
SELECT * FROM issues LIMIT 5; # View issues
.quit                        # Exit
```

---

## 🔧 Environment Variables

Located in `.env.example`:

```env
BACKEND_URL=http://localhost:8000
DEBUG=True
DATABASE_URL=sqlite:///./problems.db
REACT_APP_API_URL=http://localhost:8000
```

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| README.md | Features & overview |
| SETUP.md | Installation guide |
| API_EXAMPLES.md | API testing |
| ARCHITECTURE.md | System design |
| PROJECT_SUMMARY.md | What was built |

---

## 🚀 Deployment Commands

### Docker Build
```bash
docker build -t localreporter .
docker run -p 8000:8000 localreporter
```

### Docker Compose
```bash
docker-compose up
# Access: http://localhost:8000 and http://localhost:3000
```

---

## 🎨 Key Hotkeys

| Hotkey | Action |
|--------|--------|
| F12 | DevTools (React debugging) |
| Ctrl+Shift+I | DevTools |
| Ctrl+C | Stop running process |
| Ctrl+/ | Toggle comment in code |

---

## 📊 Issue Types & Priority

**Categories:**
- 🛣️ road_damage (base score: 70)
- ♻️ garbage (base score: 30)
- 💧 water_leak (base score: 75)
- 🚗 traffic (base score: 60)
- 🏗️ construction (base score: 50)
- ⛰️ landslide (base score: 100)
- ❓ other (base score: 20)

**Priority Levels:**
- 🔴 critical (80-100)
- 🟠 high (60-79)
- 🟡 medium (40-59)
- 🟢 low (0-39)

---

## 🔗 External Resources

| Resource | Link |
|----------|------|
| FastAPI | https://fastapi.tiangolo.com/ |
| React | https://react.dev/ |
| YOLOv5 | https://github.com/ultralytics/yolov5 |
| SQLAlchemy | https://sqlalchemy.org/ |
| Axios | https://axios-http.com/ |

---

## 💬 Common Commands Reference

### Python
```bash
# Check Python version
python --version

# Create venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Update pip
pip install --upgrade pip
```

### Node/npm
```bash
# Check Node version
node --version

# Check npm version  
npm --version

# Install packages
npm install

# Start dev server
npm start

# Build for production
npm run build

# Install specific package
npm install package-name
```

---

## 🎯 First-Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed
- [ ] Backend venv created
- [ ] Backend requirements installed
- [ ] Frontend npm packages installed
- [ ] Backend running on :8000
- [ ] Frontend running on :3000
- [ ] Can access http://localhost:3000
- [ ] Can upload test image
- [ ] Can see issue in list
- [ ] Can view dashboard (Authority Mode)

---

## 🆘 Got Stuck?

1. **Check SETUP.md** - Step-by-step guide
2. **Check API_EXAMPLES.md** - Test API
3. **Check ARCHITECTURE.md** - Understand system
4. **Check browser console** - Frontend errors (F12)
5. **Check terminal output** - Backend errors
6. **Check README.md** - Common Q&A

---

## 📞 File Locations

```
local-problem-reporter/
├── backend/        ← Backend code here
├── frontend/       ← Frontend code here
├── uploads/        ← Uploaded images saved here
├── problems.db     ← SQLite database (auto-created)
├── *.md            ← Documentation
└── docker-compose.yml ← Docker config
```

---

## ✨ Pro Tips

- 💡 Use `npm start` in frontend for hot reload
- 💡 FastAPI auto-reloads on Python file changes
- 💡 Check `/docs` for interactive API testing
- 💡 Use browser DevTools for React debugging
- 💡 Check `problems.db` for database inspection
- 💡 Upload small images (~1MB) for faster processing

---

## 🎉 Success Indicators

✅ Backend console shows "Uvicorn running on http://0.0.0.0:8000"
✅ Frontend shows "webpack compiled successfully"
✅ Can upload issue without errors
✅ AI detection returns a result
✅ Issue appears in Issues list
✅ Dashboard shows statistics
✅ Analytics page loads

---

**Last Updated**: March 26, 2024
**Status**: ✅ Ready to Use
**Quick Start Time**: ~5 minutes

🚀 **Happy Coding!** 🚀
