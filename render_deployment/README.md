# TradePro - Professional Cryptocurrency Trading Bot

## Render Deployment Instructions

This package contains all files needed to deploy TradePro on Render.com

### Quick Deploy Steps:

1. **Create Render Account**: Sign up at render.com
2. **Connect GitHub**: Fork or upload this code to your GitHub repository
3. **Create New Web Service**: Connect your GitHub repo to Render
4. **Configure Settings**:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 main:app`

### Environment Variables:
Set these in your Render dashboard:
- `DATABASE_URL`: PostgreSQL connection string (auto-generated)
- `SESSION_SECRET`: Random string for Flask sessions (auto-generated)

### Database Setup:
Render will automatically create and connect a PostgreSQL database.

### Features:
- Real-time cryptocurrency trading signals
- Professional dashboard with portfolio tracking
- Telegram notifications for trade alerts
- Advanced technical analysis with 90%+ confidence signals
- $500 account configuration with proper risk management

### Live Trading:
The bot provides Bybit futures trading configurations for immediate execution.

Deploy URL will be: `https://your-app-name.onrender.com`

### Support:
All market data is sourced from authentic APIs (Coinbase, Binance) with proper fallback systems.