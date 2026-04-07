# 🚀 Complete Setup Guide - Local Problem Reporter

This guide will get you from zero to running the full application locally.

## Prerequisites Check

Before starting, verify you have these installed:

```bash
# Python 3.8 or higher
python --version

# Node.js 14+ and npm
node --version
npm --version

# Git (optional, but recommended)
git --version
```

If any are missing, download from:
- Python: https://python.org/downloads/
- Node.js: https://nodejs.org/

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take a few minutes as it installs:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- YOLOv5 (AI model library)
- Pillow & OpenCV (image processing)
- And others...

**Note**: torch (PyTorch) is large (~500MB). The installation will take time.

### Step 4: Verify Installation

Test that everything works:

```bash
python -c "import yolov5; print('✓ YOLOv5 installed')"
python -c "import fastapi; print('✓ FastAPI installed')"
python -c "import sqlalchemy; print('✓ SQLAlchemy installed')"
```

### Step 5: Initialize Database

The database creates automatically when you first run the app, but you can pre-create it:

```bash
python
>>> from app.database import Base, engine
>>> from app.models import *
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

### Step 6: Download YOLOv5 Model

First time YOLOv5 runs, it downloads ~100MB model. Pre-download to avoid delays:

```bash
python -c "import yolov5; yolov5.load('yolov5s')"
```

### Step 7: Start Backend Server

```bash
python run.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Step 8: Test Backend API

Visit in your browser:
- **Main**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

You should see responses like `{"message": "Local Problem Reporter API"}`

---

## Frontend Setup

### Step 1: Open New Terminal (Keep Backend Running)

Open another terminal window/tab in the same workspace.

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Install Dependencies

```bash
npm install
```

This installs:
- React & React DOM
- React Router for navigation
- Axios for API requests
- Chart.js for analytics
- And others...

This may take 2-3 minutes.

### Step 4: Start Development Server

```bash
npm start
```

Expected output:
```
webpack compiled successfully...
You can now view local-problem-reporter-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

The browser may open automatically to http://localhost:3000

---

## ✅ Verify Everything Works

### 1. Backend Running?
- Check terminal with `python run.py` is active
- Visit http://localhost:8000/health
- Should see `{"status": "healthy"}`

### 2. Frontend Running?
- Check terminal with `npm start` is active
- Visit http://localhost:3000
- Should see homepage with "Local Problem Reporter"

### 3. CORS Working?
- Frontend should load without errors
- Check browser console (F12) for errors

If CORS error appears, it means backend isn't running or they can't communicate.

## 🧪 Test the Full Flow

### 1. Report an Issue

- Click "Report Issue"
- Select an image from your computer
- Fill in details
- Click "Get My Location" (requires location permission)
- Submit

Expected result:
- Issue is processed by AI
- Shows detected type and priority
- Redirects to issues list

### 2. View Issues

- Click "View Issues"
- See list of reported issues
- Filter by priority/status/type
- Click on an issue for details

### 3. Try Authority Mode

- Click "Authority Mode" button in nav
- New tabs appear: "Dashboard" and "Analytics"
- Visit Dashboard to see statistics
- Select an issue and update status

### 4. Database Check

Backend auto-creates `backend/problems.db` file. To inspect:

```bash
# Install sqlite3 if needed: pip install sqlite3
sqlite3 backend/problems.db

# Inside sqlite:
.tables                 # List tables
SELECT COUNT(*) FROM issues;  # Count issues
.quit                   # Exit
```

---

## 📁 Testing with Sample Images

To test without taking photos:

```bash
# Windows
curl -o test_image.jpg https://via.placeholder.com/500

# Or download from:
# - https://unsplash.com
# - https://picsum.photos
# - Your own photos
```

Then upload to test the system.

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "Port 8000 already in use"**
```bash
# Use different port
python -c "uvicorn app.main:app --port 8001"
```

**Error: "Module not found"**
```bash
# Reactivate venv and reinstall
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Error: "YOLOv5 download failed"**
```bash
# Manual download with proxy
pip install --proxy [user:passwd@]proxy.server:port yolov5

# Or update pip
pip install --upgrade pip
```

### Frontend won't start

**Error: "Port 3000 already in use"**
```bash
# Use different port
PORT=3001 npm start
```

**Error: "npm: command not found"**
```bash
# Node.js not installed properly
# Reinstall from nodejs.org
# Restart terminal/IDE after install
```

**CORS Error in browser console**
```
Access to XMLHttpRequest blocked by CORS policy
```
Solution:
- Ensure backend is running on http://localhost:8000
- Check `proxy` in frontend/package.json matches backend

### Database issues

**Error: "database is locked"**
```bash
# Delete and recreate
rm backend/problems.db
# Restart server
python run.py
```

**Error: "table issues already exists"**
```bash
# Delete database file
rm backend/problems.db
# Database auto-creates on startup
```

### Image upload fails

**Error: "File too large"**
- Resize image before upload
- Max default is ~10MB

**Error: "Invalid file format"**
- Upload only .jpg, .jpeg, .png, .gif
- Check file extension

---

## 📊 API Testing with curl

```bash
# Get all issues
curl http://localhost:8000/api/issues/all

# Get system info
curl http://localhost:8000/api/system/info

# Get dashboard analytics
curl http://localhost:8000/api/analytics/dashboard

# Get scoring info
curl http://localhost:8000/api/scoring-info

# Export to CSV
curl -O http://localhost:8000/api/analytics/export/csv
```

---

## 🔧 Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Backend**: Changes to Python files auto-reload
- **Frontend**: Changes to React files auto-reload in browser

### Debug Mode
- Backend: Change `DEBUG=False` to `DEBUG=True` in .env
- Frontend: Open DevTools (F12) to see console logs

### Database Inspection
```python
# In Python REPL:
from app.database import SessionLocal
from app.models import Issue

db = SessionLocal()
issues = db.query(Issue).all()
for issue in issues:
    print(f"ID: {issue.id}, Type: {issue.issue_type}, Priority: {issue.priority_level}")
```

### API Documentation
FastAPI auto-generates interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Try API endpoints directly from the docs!

---

## 🚀 Production Deployment

When ready for production:

1. **Use PostgreSQL instead of SQLite**
```python
# In backend/app/database.py
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

2. **Set DEBUG=False**

3. **Use environment variables** for configuration

4. **Enable HTTPS**

5. **Deploy with Gunicorn + Nginx**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

6. **Build React for production**
```bash
npm run build
```

7. **Use cloud hosting**: AWS, Heroku, DigitalOcean, etc.

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **YOLOv5 Docs**: https://github.com/ultralytics/yolov5
- **SQLAlchemy Docs**: https://sqlalchemy.org/

---

## ✨ You're Ready!

Congratulations! 🎉

Your Local Problem Reporter is now running locally. 

**Next steps:**
1. Try reporting an issue
2. Test authority features
3. Explore the API documentation
4. Customize for your needs
5. Deploy to production

**Questions?** Check the main README.md for more info!

---

Happy coding! 🚀
