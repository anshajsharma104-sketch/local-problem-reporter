# Deployment Configuration Guide

## FREE Deployment: Vercel + Railway

### Backend (Railway - FREE)
1. Create account at railway.app (FREE)
2. Connect GitHub repo
3. Railway will automatically:
   - Detect Python project
   - Install requirements
   - Run Procfile command
   - Provision free PostgreSQL database

### Frontend (Vercel - FREE) 
1. Create account at vercel.com (FREE)
2. Connect GitHub repo
3. Select `frontend` folder as root
4. Vercel auto-detects React app
5. Auto-deploys on every push

## Environment Variables (Set in Railway Dashboard)

```
# Database (Railway provides this automatically)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Backend Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
CORS_ORIGINS=["https://your-vercel-frontend.vercel.app"]

# API URL (in Vercel environment)
REACT_APP_API_URL=https://your-railway-backend.railway.app
```

## Steps to Deploy (10 minutes)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy Backend on Railway
- Go to railway.app
- Click "New Project"
- Connect GitHub
- Select this repository
- Railway auto-detects and runs
- Get your URL (e.g., your-app.railway.app)
- Set environment variables in Railway dashboard

### 3. Deploy Frontend on Vercel
- Go to vercel.com/new
- Import GitHub repository
- Select `frontend` as root directory
- Add environment variable: `REACT_APP_API_URL=your-railway-url`
- Deploy (auto-deploys on every push)

### 4. Update CORS
After deployment, update your backend:
- In Railway dashboard, set: `CORS_ORIGINS=["https://your-vercel-url"]`

Done! Your app is live and FREE forever! 🎉

## Limits (FREE tier)
- Railway: $5 free credits/month (enough for small projects)
- Vercel: Unlimited (truly free)
- Both have excellent uptime

## After Exceeding Free Tier
- Railway: ~$5-10/month for small usage
- Vercel: Still free (production ready)
