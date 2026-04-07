# 🚀 DEPLOY IN 10 MINUTES - Copy & Paste Commands Only

## ⚠️ Important: Read This First
- You need a **free GitHub account** (github.com - takes 1 minute)
- You need a **free Railway account** (railway.app - takes 1 minute)  
- You need a **free Vercel account** (vercel.com - takes 1 minute)
- Total setup time: **~15 minutes**

---

## STEP 1: Create GitHub Account (1 minute)

1. Go to **github.com**
2. Click "Sign up"
3. Create account with email
4. Confirm email
5. Done! ✅

---

## STEP 2: Create GitHub Repository

1. Go to **github.com/new**
2. Name: `local-problem-reporter`
3. Description: `AI-powered infrastructure issue reporting`
4. Choose "Public"
5. Click "Create repository"
6. Copy the URL shown (example: `https://github.com/YOUR-USERNAME/local-problem-reporter.git`)

---

## STEP 3: Push Your Code to GitHub

Open PowerShell in your project folder and run these commands ONE BY ONE:

```powershell
cd c:\Users\Vanshaj Sharma\OneDrive\Desktop\local-problem-reporter
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/local-problem-reporter.git
git push -u origin main
```

**Replace:**
- `your-email@example.com` with your real email
- `Your Name` with your real name
- `YOUR-USERNAME` with your GitHub username

After running these commands, refresh your GitHub repo page and you'll see your code! ✅

---

## STEP 4: Deploy Backend on Railway (FREE)

1. Go to **railway.app**
2. Click "Sign Up" → Choose "GitHub"
3. Click "Connect GitHub"
4. Click "New Project"
5. Click "Deploy from GitHub repo"
6. Find and click `local-problem-reporter`
7. Click "Deploy"
8. **Wait 3-5 minutes** for deployment to finish

Once done, you'll see a URL like: `https://local-problem-reporter-prod.railway.app`

**Copy this URL** - you'll need it next!

---

## STEP 5: Configure Backend Variables

1. In Railway dashboard, click your project
2. Click "Variables" tab
3. Click "Add Variable"
4. Add these one by one:

| Name | Value |
|------|-------|
| `SECRET_KEY` | `my-super-secret-key-12345` |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | Leave EMPTY for now |

Click "Deploy" button to apply changes.

---

## STEP 6: Deploy Frontend on Vercel (FREE)

1. Go to **vercel.com**
2. Click "Sign Up" → Choose "GitHub"
3. Click "Import Project"
4. Find `local-problem-reporter` and click it
5. Click "Select"
6. In "Import Project" settings, change:
   - **Root Directory**: `frontend` (use dropdown to select)
   - Keep everything else default
7. Scroll down to "Environment Variables"
8. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: Paste your Railway URL from STEP 4 (example: `https://local-problem-reporter-prod.railway.app`)
9. Click "Deploy"
10. **Wait 2-3 minutes** for deployment

When done, you'll get a URL like: `https://local-problem-reporter.vercel.app`

**Copy this URL!**

---

## STEP 7: Update Backend CORS

1. Go back to **Railway dashboard**
2. Click your project
3. Click "Variables" tab
4. Find `CORS_ORIGINS`
5. Set value to your Vercel URL from STEP 6
   - Example: `https://local-problem-reporter.vercel.app`
6. Click "Deploy"
7. **Wait 1-2 minutes**

---

## ✅ DONE! Your App is LIVE

Visit your frontend URL: https://local-problem-reporter.vercel.app

You can now:
- Report issues
- View issues
- Upvote
- Check analytics
- All working live! 🎉

---

## How to Update Your App

Whenever you make changes:

```powershell
cd c:\Users\Vanshaj Sharma\OneDrive\Desktop\local-problem-reporter
git add .
git commit -m "Your change description"
git push origin main
```

Then:
- **Vercel** auto-updates frontend (2-3 min)
- **Railway** auto-updates backend (2-3 min)

---

## Troubleshooting

### I see "Error connecting to API"
- Check that `REACT_APP_API_URL` is correct in Vercel
- Check that `CORS_ORIGINS` is correct in Railway
- Wait 2-3 minutes and refresh

### Railway says "Build failed"
- Check Railway "Logs" tab for error
- Usually just needs another push:
  ```powershell
  git commit --allow-empty -m "Rebuild"
  git push origin main
  ```

### Can't find my URL
- Railway: Go to Deployment tab, URL is there
- Vercel: Go to Deployments tab, URL is there

---

## Questions?

1. **Can I use a custom domain?** Yes (both offer free domains)
2. **What's the cost?** $0 forever on free tier
3. **How many users?** Railway free can handle ~100 active users
4. **Can I add more features?** Yes! Just push to GitHub and both update

Enjoy your live app! 🚀
