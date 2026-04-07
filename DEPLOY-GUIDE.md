# 🚀 Deployment Guide - Vercel + Railway (100% FREE)

## Quick Start (15 minutes)

### Prerequisites
- GitHub account (free)
- Railway account (free - railway.app)
- Vercel account (free - vercel.com)

---

## Step 1: Push Your Project to GitHub

```bash
# From your project root
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main

# Create a new repo on GitHub.com and then:
git remote add origin https://github.com/YOUR-USERNAME/local-problem-reporter.git
git push -u origin main
```

---

## Step 2: Deploy Backend on Railway (FREE)

### 2.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"

### 2.2 Deploy Backend
1. Select "Deploy from GitHub repo"
2. Select your `local-problem-reporter` repository
3. Railway automatically detects Python project
4. Click "Deploy Now"

⏳ **Wait 3-5 minutes for deployment**

### 2.3 Configure Environment Variables in Railway
1. Go to your Railway project dashboard
2. Click on the deployed service (Python app)
3. Go to "Variables" tab
4. Add these variables:

```
DATABASE_URL=leave blank (Railway creates PostgreSQL automatically)
SECRET_KEY=your-super-secret-key-12345
DEBUG=False
CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app
```

### 2.4 Get Your Backend URL
1. In Railway dashboard, find "Deployments"
2. Your URL will be like: `https://your-app-prod.railway.app`
3. Copy this URL (we need it for frontend)

---

## Step 3: Deploy Frontend on Vercel (FREE)

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"

### 3.2 Deploy Frontend
1. Select "Import GitHub Repository"
2. Search for and select `local-problem-reporter`
3. Choose project settings:
   - **Framework Preset**: Next.js ❌ → **NO**, select Create React App ✅
   - **Root Directory**: `frontend` ✅
   - **Build Command**: `npm run build` ✅
   - **Output Directory**: `build` ✅

### 3.3 Add Environment Variables
1. Before deploying, click "Environment Variables"
2. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-railway-backend-url.railway.app` (from Step 2.4)
3. Click "Deploy"

⏳ **Wait 2-3 minutes for deployment**

### 3.4 Get Your Frontend URL
Your Vercel project URL will be shown: `https://your-project-vercel.app`

---

## Step 4: Update Backend CORS Settings

1. Go back to Railway dashboard
2. Find your Python service
3. Go to "Variables" tab
4. Update `CORS_ORIGINS` to:
   ```
   https://your-project-vercel.app
   ```
5. Redeploy by pushing a commit to GitHub

---

## ✅ You're Done!

Your app is now live:
- **Frontend**: https://your-project-vercel.app
- **Backend API**: https://your-railway-backend.railway.app
- **Database**: PostgreSQL (managed by Railway)
- **Cost**: **$0/month** 🎉

---

## Automatic Updates

Any time you push to GitHub:
- Vercel auto-deploys frontend
- Railway auto-deploys backend

```bash
git add .
git commit -m "Updated feature"
git push origin main
# Both apps update automatically!
```

---

## Troubleshooting

### 404 errors after deployment
- Make sure frontend `REACT_APP_API_URL` is set correctly in Vercel
- Make sure backend `CORS_ORIGINS` includes your Vercel URL

### 500 errors
- Check Railway "Logs" tab for error messages
- Make sure DATABASE_URL is set in Railway variables (or leave blank for auto)

### Database issues
- Railway auto-creates PostgreSQL database
- If you get "database doesn't exist", Railway usually fixes it on next deploy
- Push an empty commit to trigger redeploy: `git commit --allow-empty -m "Redeploy"`

### File upload issues
- Railway free tier has file system (ephemeral)
- For production, consider adding AWS S3 (instructions available on request)

---

## Next Steps (Optional)

### Custom Domain
Both Vercel and Railway allow free custom domains:
- Vercel: Add domain in "Settings" → "Domains"
- Railway: Add domain in service settings

### Monitoring
- Railway: View logs in "Logs" tab
- Vercel: View logs in "Deployments" → "Logs"

### Database Backups
- Railway auto-backs up PostgreSQL
- Check Railway docs for backup settings

---

**Questions?** Check the DEPLOYMENT.md file in your project root!
