# Render Deployment Settings for TradePro Trading Bot

## Web Service Configuration

### Basic Settings
- **Name**: `tradepro-trading-bot` (or your preferred name)
- **Region**: Oregon (US West) or Frankfurt (Europe) 
- **Branch**: `main`
- **Runtime**: `Python 3`

### Build & Deploy Commands
```bash
# Build Command
pip install -r requirements.txt

# Start Command
gunicorn --bind 0.0.0.0:$PORT main:app
```

### Environment Variables
Add these in Render Dashboard → Environment:

```
SESSION_SECRET = "your-random-secret-key-here-make-it-long-and-secure"
DATABASE_URL = (will be auto-configured when you add PostgreSQL)
```

### Instance Type
- **Free Tier**: Free (512 MB RAM, 0.1 CPU)
- **Starter**: $7/month (512 MB RAM, 0.5 CPU) - Recommended
- **Standard**: $25/month (2 GB RAM, 1 CPU) - For high traffic

## Database Configuration

### Add PostgreSQL Database
1. In Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Choose same region as your web service
4. Select plan:
   - **Free**: $0/month (1 GB storage, expires in 90 days)
   - **Starter**: $7/month (1 GB storage, persistent)
   - **Standard**: $20/month (10 GB storage)

### Connect Database to Web Service
1. Go to your Web Service → Environment
2. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: (copy from PostgreSQL dashboard → Connections → External Database URL)

## Step-by-Step Deployment

### Method 1: GitHub Upload (Recommended)
1. Create new GitHub repository
2. Upload the TradePro_Fixed_Complete.tar.gz contents
3. Connect Render to GitHub repo
4. Deploy automatically

### Method 2: Direct Upload
1. Extract TradePro_Fixed_Complete.tar.gz locally
2. Create new Web Service in Render
3. Upload files directly via Render interface

## Health Check
After deployment, verify these URLs work:
- `https://your-app.onrender.com/` - Dashboard
- `https://your-app.onrender.com/healthz` - Health check
- `https://your-app.onrender.com/analysis` - Analysis page
- `https://your-app.onrender.com/portfolio` - Portfolio page

## Current Signal Status
- ADA SELL at 93.5% confidence
- $500 account configuration
- Real-time CoinGecko/Coinbase data
- Professional Bybit settings modal
- Working top gainers/losers

## Troubleshooting
If deployment fails:
1. Check build logs for Python dependency errors
2. Verify all environment variables are set
3. Ensure DATABASE_URL is properly configured
4. Check application logs for runtime errors

## Performance Notes
- App auto-sleeps after 15 minutes of inactivity (Free tier)
- Starter tier keeps app always running
- Database auto-pauses after 1 hour of inactivity (Free tier)
- Use Starter tiers for production use