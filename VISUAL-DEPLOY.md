# 🎬 VISUAL STEP-BY-STEP DEPLOYMENT GUIDE

## What You Need (Takes 3 Minutes to Create)
1. ✅ GitHub account (free)
2. ✅ Railway account (free)
3. ✅ Vercel account (free)

---

## SECTION A: GitHub Setup (5 minutes)

### A1: Create GitHub Account
```
Go to: https://github.com/signup
Email: your-email@gmail.com
Password: anything
Username: your-github-username
Click "Create account"
Click "Verify email" link in your email
Done! ✅
```

### A2: Create a New Repository
```
Go to: https://github.com/new
Name: local-problem-reporter
Description: AI infrastructure reporting app
Choose: Public
NO Need to add README/gitignore (we have them)
Click "Create repository"
You'll see something like:
  https://github.com/YOUR-USERNAME/local-problem-reporter.git
COPY THIS URL ↑
```

### A3: Upload Your Code to GitHub
Open PowerShell and paste each command:

```
cd c:\Users\Vanshaj Sharma\OneDrive\Desktop\local-problem-reporter
```

```
git config --global user.email "your-real-email@gmail.com"
```

```
git config --global user.name "Your Real Name"
```

```
git init
```

```
git add .
```

```
git commit -m "First upload"
```

```
git branch -M main
```

```
git remote add origin https://github.com/YOUR-USERNAME/local-problem-reporter.git
```

(Replace YOUR-USERNAME with your actual GitHub username)

```
git push -u origin main
```

**Wait for upload to finish** ✅

Go to github.com/your-username/local-problem-reporter and you'll see your code!

---

## SECTION B: Deploy Backend on Railway (5 minutes)

### B1: Create Railway Account
```
Go to: https://railway.app
Click "Start for free"
Click "Continue with GitHub"
Allow Railway to access your repositories
Done! ✅
```

### B2: Deploy Your Backend
```
Click "New Project"
Click "Deploy from GitHub repo"
Find and click "local-problem-reporter"
Click "Deploy Now"
Wait 3-5 minutes (GREEN checkmark means done)
```

### B3: Get Your Backend URL
```
Click your project
Click "Postgres" on left (the database)
Go to "Plugins" tab
You'll see DATABASE_URL - that's automatically created ✅
Now click back on your Python service
You'll see "View Logs" and other info
Look for a URL that looks like:
  https://local-problem-reporter-prod.railway.app
COPY THIS URL ↑
```

### B4: Configure Backend Settings
```
In Railway dashboard:
Click your project
Go to "Variables" tab
Add these variables (click "+"):

Variable 1:
  Key: SECRET_KEY
  Value: my-super-secret-key-123
  Click "Go to Railway"

Variable 2:
  Key: DEBUG
  Value: False
  Click "Go to Railway"

Variable 3:
  Key: CORS_ORIGINS
  Value: (leave blank for now, we'll add it later)
  Click "Go to Railway"

Click big "Deploy" button at bottom
Wait 2 minutes for redeploy ✅
```

**SAVE YOUR URL** - you need it for next section!

---

## SECTION C: Deploy Frontend on Vercel (5 minutes)

### C1: Create Vercel Account
```
Go to: https://vercel.com/signup
Click "Continue with GitHub"
Allow Vercel to access your repositories
Done! ✅
```

### C2: Deploy Frontend
```
Click "Add New..."
Click "Project"
Find "local-problem-reporter"
Click it
```

### C3: Configure Frontend Settings
```
In the import screen:
- Root Directory: Click dropdown, select "frontend"
- Framework Preset: Next.js (should auto-select "Others")
- Leave build settings as they are
```

### C4: Add Environment Variable
```
Scroll down to "Environment Variables"
Click "Add"
  Name: REACT_APP_API_URL
  Value: https://your-railway-url.railway.app
  (The URL from Section B3)
Click "Add"
```

### C5: Deploy
```
Click "Deploy"
Wait 2-3 minutes
You'll get a URL like:
  https://local-problem-reporter.vercel.app
COPY THIS URL ↑
```

---

## SECTION D: Final Connection (2 minutes)

### D1: Tell Backend About Frontend
```
Go back to Railway dashboard
Go to "Variables" tab
Find CORS_ORIGINS
Set it to: https://your-vercel-url.vercel.app
  (From Section C5)
Click "Go to Railway"
Click "Deploy"
Wait 2 minutes ✅
```

---

## 🎉 YOU'RE DONE!

Your app is now LIVE at:
```
https://your-vercel-url.vercel.app
```

Try it:
- Sign up/Login
- Report an issue
- Upvote issues
- Everything works! ✅

---

## What Now?

### Make Changes Locally
```
Edit files on your computer
git add .
git commit -m "My change"
git push origin main
```

### Auto-Updates
- Frontend updates in 2-3 minutes automatically
- Backend updates in 2-3 minutes automatically

---

## Quick Troubleshooting

**"Can't connect to API"**
- ✅ Check CORS_ORIGINS is set correctly in Railway
- ✅ Check REACT_APP_API_URL is correct in Vercel
- ✅ Wait 5 minutes and refresh

**"Build failed on Railway"**
- Click "View Logs" in Railway
- See what's wrong
- Fix it in your code
- Push to GitHub again
- It rebuilds automatically

**"Vercel shows error"**
- Go to Deployments tab
- Click "Logs"
- Copy the error
- Ask for help with the error message

---

## Done! 🚀
Your app is deployed FREE forever!
