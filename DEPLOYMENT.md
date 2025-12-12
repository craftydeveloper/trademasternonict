# Deployment Guide

## GitHub Deployment Steps

### 1. Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: Futures Trading Bot"
```

### 2. Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `futures-trading-bot` or your preferred name
3. Don't initialize with README (we already have one)
4. Copy the repository URL

### 3. Connect Local to GitHub

```bash
git remote add origin https://github.com/yourusername/futures-trading-bot.git
git branch -M main
git push -u origin main
```

### 4. Environment Variables Setup

Create a `.env.example` file showing required variables:

```
DATABASE_URL=postgresql://username:password@localhost/tradingbot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SESSION_SECRET=your_secret_key_here
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET_KEY=your_bybit_secret_key
```

**Important**: Never commit actual secrets to GitHub!

## Production Deployment Options

### Option 1: Heroku

1. Install Heroku CLI
2. Create new app: `heroku create your-app-name`
3. Add PostgreSQL addon: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables: `heroku config:set TELEGRAM_BOT_TOKEN=your_token`
5. Deploy: `git push heroku main`

### Option 2: Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

### Option 3: DigitalOcean App Platform

1. Connect GitHub repository
2. Configure environment variables
3. Set up managed PostgreSQL database
4. Deploy with automatic scaling

### Option 4: Self-Hosted VPS

1. Set up Ubuntu/CentOS server
2. Install Python, PostgreSQL, Nginx
3. Clone repository and install dependencies
4. Configure systemd service for auto-restart
5. Set up SSL certificate with Let's Encrypt

## Security Checklist

- [ ] All API keys stored as environment variables
- [ ] `.env` files added to `.gitignore`
- [ ] GitHub repository set to private (if needed)
- [ ] Two-factor authentication enabled on GitHub
- [ ] Regular security updates scheduled
- [ ] Database backups configured
- [ ] SSL/TLS encryption enabled in production
- [ ] Rate limiting configured for API endpoints

## Monitoring and Maintenance

### Health Checks

Add health check endpoint in `routes.py`:

```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

### Logging

Configure production logging:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/trading_bot.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Database Backups

Set up automated PostgreSQL backups:

```bash
# Daily backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
# Upload to cloud storage (AWS S3, Google Cloud, etc.)
```

## Scaling Considerations

- Use Redis for session storage in multi-instance deployments
- Implement database connection pooling
- Set up load balancing for high traffic
- Consider microservices architecture for large-scale deployment
- Implement caching for frequently accessed data

## Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL format
2. **Telegram Alerts**: Verify bot token and chat ID
3. **API Limits**: Implement rate limiting and error handling
4. **Memory Usage**: Monitor for memory leaks in long-running processes

### Debug Mode

Enable debug logging:

```python
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

Consider integrating:
- Sentry for error tracking
- New Relic for performance monitoring
- Datadog for infrastructure monitoring