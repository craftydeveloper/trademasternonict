# Easy 5-Minute Render Deployment

## Step 1: Download & Extract (30 seconds)
1. Click the download button on your dashboard
2. Extract `TradePro_Fixed_Complete.tar.gz` on your computer
3. You'll see a folder with all the trading bot files

## Step 2: Create Render Account (1 minute)
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Click "New +" → "Web Service"

## Step 3: Upload Files (2 minutes)
1. Choose "Deploy from source code"
2. Select "Upload from computer"
3. Drag the extracted folder or select all files
4. Click "Upload"

## Step 4: Configure Settings (1 minute)
**Runtime:** Python 3
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`

## Step 5: Add Environment Variables (30 seconds)
Click "Environment" and add:
- **Name:** `SESSION_SECRET`
- **Value:** `tradepro2025secure`

## Step 6: Deploy (30 seconds)
1. Choose "Starter" plan ($7/month for reliable performance)
2. Click "Create Web Service"
3. Wait 2-3 minutes for deployment

## Done! 🎉
Your trading bot will be live at: `https://your-app-name.onrender.com`

**What you get:**
- ADA SELL signal at 93.5% confidence
- Real-time market data
- Professional dashboard
- $500 account configuration
- All Analysis/Portfolio pages working

**Optional Database (for full features):**
- Click "New +" → "PostgreSQL" → "Free" plan
- Copy the database URL to your web service environment variables as `DATABASE_URL`

**Need help?** The trading bot works immediately without database for signal viewing. Add database later for portfolio tracking.