# Deployment Guide

## Hosting Provider: Render (Free Tier)

**Recommended Provider:** Render (https://render.com)

**Why Render:**
- Free tier: 750 hours/month
- Automatic GitHub deployments
- SSL included
- Native Python/FastAPI support
- Simple setup

## Deployment Steps

### 1. Push Code to GitHub
Ensure all code is pushed to the GitHub repository `jeremiasapaz/Truth-Serum`.

### 2. Connect to Render
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select the `Truth-Serum` repository
5. Configure:
   - **Name:** truth-serum
   - **Region:** Oregon (or closest to you)
   - **Branch:** master
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables
Add these environment variables in Render:
```
PYTHON_VERSION=3.11.9
DATABASE_URL=sqlite:///./transparency.db
VERIFY_SSL=false
```

### 4. Deploy
Click "Create Web Service". Render will:
- Build the application
- Deploy to a public URL
- Provide SSL automatically

### 5. Access Your App
Once deployed, Render will provide a URL like:
```
https://truth-serum.onrender.com
```

## Important Notes

### SQLite on Render
Render's free tier uses **ephemeral storage**. This means:
- SQLite database will be **reset on every redeploy**
- All ingested data (leaders, evidence, country indicators) will be lost on redeploy
- This is acceptable for demonstration purposes

**For Production:**
- Switch to PostgreSQL (Render offers free PostgreSQL)
- Update `DATABASE_URL` to: `postgresql://user:pass@host/db`
- No code changes needed (SQLAlchemy handles both)

### Rate Limits
- Free tier: 750 hours/month
- App spins down after 15 minutes of inactivity
- Cold start takes ~30 seconds on first request after inactivity

### Alternative: Railway
If Render is unavailable, Railway is an alternative:
- Free tier has been restricted recently
- Similar setup process
- Use `railway up` CLI command

## GitHub Auto-Deployment

Render automatically deploys on every push to the connected branch (master). No additional configuration needed.

## Monitoring

- View logs in Render dashboard
- Monitor deployment status
- Check resource usage (free tier limits)

## Troubleshooting

### Build Fails
- Check Python version matches (3.11.9)
- Verify all dependencies in `requirements.txt`
- Check build logs in Render dashboard

### App Won't Start
- Verify start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check environment variables are set
- Review application logs

### Data Lost After Redeploy
- This is expected with SQLite on free tier
- For persistent data, switch to PostgreSQL
- Or use Render's disk add-on (paid)

## Custom Domain (Optional)

To use a custom domain:
1. Purchase domain from registrar
2. Add custom domain in Render dashboard
3. Update DNS records (CNAME)
4. SSL provisioned automatically

## Scaling

If you need more resources:
- Upgrade to paid Render tier
- Add Redis for caching
- Use PostgreSQL for persistent data
- Add CDN for static assets
