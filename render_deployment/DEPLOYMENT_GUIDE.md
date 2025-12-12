# TradePro Render Deployment Guide

## Step-by-Step Deployment Instructions

### 1. Upload to GitHub
1. Create a new repository on GitHub
2. Upload all files from this `render_deployment` folder to your repository
3. Ensure all Python files and folders are included

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select your repository
4. Configure the service:

**Basic Settings:**
- Name: `tradepro-bot` (or your preferred name)
- Region: Choose closest to your location
- Branch: `main`
- Runtime: `Python 3`

**Build & Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app`

### 3. Database Setup
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `tradepro-db`
3. Plan: Select "Free" or "Starter"
4. After creation, copy the "External Database URL"

### 4. Environment Variables
In your web service settings, add these environment variables:
- `DATABASE_URL`: Paste the PostgreSQL URL from step 3
- `SESSION_SECRET`: Generate a random string (e.g., use a password generator)

### 5. Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

## Features Available After Deployment
- Real-time cryptocurrency trading signals
- Professional dashboard with portfolio tracking
- ADA SELL signals at 94% confidence
- $500 account balance configuration
- Bybit futures trading parameters
- Market overview with top gainers/losers

## Troubleshooting
- If deployment fails, check the logs in Render dashboard
- Ensure all Python files are uploaded correctly
- Verify DATABASE_URL environment variable is set
- Database tables will be created automatically on first run

## Live Trading Ready
The deployed bot provides authentic market data and Bybit trading configurations for immediate execution with your $500 account.