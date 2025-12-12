# TradePro Setup Guide

## Quick Setup for GitHub Deployment

### 1. Environment Configuration

Create a `.env` file in your project root:

```bash
# Database
DATABASE_URL=postgresql://username:password@hostname:port/database

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN (DISABLED - no longer required)=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional: Bybit API (for live trading)
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET_KEY=your_bybit_secret_key

# Flask Configuration
SESSION_SECRET=your_random_secret_key_here
```

### 2. Telegram Bot Setup

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Save the bot token to your `.env` file
4. Start a chat with your bot and send any message
5. Visit `http://localhost:5000/setup` to get your Chat ID

### 3. Database Setup

The application automatically creates all necessary tables on first run. For production, ensure PostgreSQL is configured with proper permissions.

### 4. Running the Application

```bash
# Development
python main.py

# Production
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### 5. Accessing Features

- **Dashboard**: `http://localhost:5000`
- **Analysis**: `http://localhost:5000/analysis`
- **Reports**: `http://localhost:5000/reports`
- **Setup Helper**: `http://localhost:5000/setup`

## System Requirements

- **Python**: 3.11 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 1GB free space
- **Network**: Stable internet for API calls

## Configuration Options

### Risk Management
- Modify `fast_signals.py` for risk percentages
- Adjust leverage limits in signal generation
- Customize position sizing algorithms

### Alert Frequency
- Change monitoring intervals in `auto_monitor.py`
- Adjust confidence thresholds for alerts
- Modify Telegram message formatting

### Market Data
- Add new data sources in `backup_data_provider.py`
- Configure API rate limits
- Set up additional exchange connections

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL format
   - Check PostgreSQL service status
   - Ensure proper network connectivity

2. **Telegram Alerts Not Working**
   - Verify bot token and chat ID
   - Check bot permissions
   - Test with `/setup` endpoint

3. **Market Data Issues**
   - API rate limiting active (normal)
   - Fallback to cached data
   - Check internet connectivity

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export FLASK_DEBUG=1
```

## Performance Optimization

### For High-Frequency Trading
- Increase monitoring frequency in `auto_monitor.py`
- Optimize database queries
- Use Redis for caching (optional)

### For Resource Constraints
- Reduce API call frequency
- Limit historical data range
- Disable non-essential features

## Security Best Practices

1. Never commit `.env` files to version control
2. Use strong passwords for database access
3. Regularly rotate API keys
4. Monitor application logs for suspicious activity
5. Keep dependencies updated

## Scaling Considerations

### Multiple Accounts
- Duplicate configuration for each account
- Separate database schemas
- Individual Telegram bots

### Cloud Deployment
- Use environment variables for all secrets
- Configure auto-scaling for traffic spikes
- Set up monitoring and alerting
- Implement backup strategies

## Support

For technical issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Create a GitHub issue with detailed information
4. Join the community Telegram group