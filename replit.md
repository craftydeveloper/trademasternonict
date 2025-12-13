# Chart Analysis Trading Bot

## Overview

This project is a technical analysis trading bot, built with Flask, designed to provide comprehensive technical analysis and generate trading signals for major cryptocurrencies. It utilizes indicators like moving averages, RSI, MACD, Bollinger Bands, and support/resistance detection. The bot also features an automated token discovery system and a paper trading execution simulator. The core purpose is to offer reliable analysis and trading signal generation without relying on external APIs for core functionality, focusing on balanced and sustainable trading.

## User Preferences

Preferred communication style: Simple, everyday language.
Request: User wants automated token sourcing to avoid manual hunting for trading opportunities.
Investment strategy: Balanced growth with sensible profit-taking and risk management.
Growth approach: Steady, sustainable trading with proper risk management.
Account balance: Starting with conservative position sizing and realistic targets.
User preference: Prefers simple, working solutions without complex setup procedures.

## System Architecture

The application employs a web application architecture with a Flask backend, SQLAlchemy ORM, and SQLite for development (PostgreSQL configurable). Real-time communication is handled via Flask-SocketIO. The frontend uses Jinja2 templates, Bootstrap 5 (dark theme), vanilla JavaScript, and Chart.js for visualizations, with Socket.IO for live updates.

Key components include:
- **Database Models**: `TokenPrice`, `Portfolio`, `Position`, `Trade`, `TradingStrategy` for managing trading data.
- **Token Discovery System**: Automates the sourcing and scoring of trending tokens across various categories (DeFi, Gaming, Infrastructure, Meme) based on metrics like volume, market cap, and liquidity.
- **Trading Engine**: Simulates paper trade execution, manages portfolio calculations, and integrates with the Solana client for price data.
- **Solana Client**: Interfaces with the Jupiter API for token prices and manages Solana token configurations.
- **WebSocket Handler**: Manages real-time price broadcasting and live portfolio updates.
- **API Routes**: Provides RESTful endpoints for portfolio data, token prices, and discovery.
- **Token Discovery Interface**: An interactive dashboard for filtering and analyzing tokens.

The system incorporates a "MODERATE-AGGRESSIVE" strategy aiming for a daily profit target with enhanced signal detection and tiered risk allocation. UI/UX emphasizes a clean, modern, professional interface with a GitHub-inspired dark theme, glassmorphism effects, and responsive design.

## Long-Term Signal System (Updated Dec 2025)

The predictive signal system has been redesigned for long-term trading with patient analysis:

**Signal Persistence:**
- Signals persist for up to 4 hours unless invalidated
- Minimum 2-hour debounce between bias changes for the same token
- Signals only change when: Stop Loss hit, Take Profit hit, HTF trend reverses, or signal expires

**Higher Timeframe (HTF) Trend Tracking:**
- HTF trend updates hourly based on 24h price action
- BUY signals require bullish or neutral HTF (blocked in downtrends)
- SELL signals require bearish or neutral HTF (blocked in uptrends)
- Signals invalidate immediately if HTF reverses against position

**Deep Analysis Requirements:**
- Increased threshold to 60+ score (from 40+) for new signals
- Requires 3%+ price moves for trend-following signals (from 1.5%)
- Removed time-based variation that caused rapid flip-flopping
- Multiple confluences required before issuing new signals

**Enhanced Signal Accuracy (Dec 13, 2025):**
- Volume confirmation required - no signals on LOW volume
- Multiple indicator agreement - need 2+ indicators (RSI, MACD, momentum, HTF) to agree
- Tighter RSI buffers - SELL blocked at RSI ≤ 40, BUY blocked at RSI ≥ 60
- Prevents issuing SELL at bottoms or BUY at tops
- Signals now require stronger confluence before triggering

**Additional Safeguards (Dec 13, 2025):**
- Price near support/resistance - BUY gets bonus near support, SELL gets bonus near resistance
- Consecutive confirmation - requires 2+ price moves in same direction before signaling
- Volatility filter - blocks signals when price change exceeds 12% (extreme volatility)

**Uniform Entry/TP/SL Structure (Dec 12, 2025):**
- All signals now use `_build_bybit_settings()` helper for consistency
- Bybit settings always include: entryPrice, entryLow, entryHigh, stopLoss, takeProfit
- Prices formatted consistently: 6 decimals for <$1 tokens, 4 decimals for >=$1 tokens
- View Setup modal displays all fields correctly for both new signals and active positions

## Priority Markets Section (Dec 13, 2025)

A dedicated Priority Markets section displays deep analysis for BTC, ETH, and SOL:

**Display Features:**
- Golden-bordered cards with priority star icons
- Real-time BUY/SELL/HOLD signals - uniform with rest of bot
- Support and resistance levels
- Multi-timeframe RSI (4H / 1D)
- Momentum direction (Strong Up/Up/Down/Strong Down/Flat)
- Market phase detection
- Volatility percentage
- Outlook/recommendation text

**Implementation:**
- Backend: PRIORITY_COINS = ['BTC', 'ETH', 'SOL'] in routes.py and predictive_signals.py
- API: /api/predictive-signals returns priority_coins array with enhanced_research data
- Frontend: displayPriorityMarkets() function renders priority cards in professional_dashboard.html

## Telegram Integration (Dec 2025)

**Toggle Control:**
- Toggle button in navbar (top-right) to enable/disable notifications
- State persists in /tmp/telegram_enabled.json
- API endpoints: GET /api/telegram/status, POST /api/telegram/toggle

**Anti-Spam Protection:**
- File-based tracking persists across restarts (/tmp/telegram_sent_signals.json)
- 2-hour cooldown between same signal alerts for same coin
- Skips duplicate notifications with logging

**Notification Types:**
- New signal alerts (BUY/SELL with entry, SL, TP)
- Bias change alerts (when signal direction changes)

## External Dependencies

- **APIs**:
    - Jupiter API: Primary source for Solana token prices.
    - CoinGecko API: Backup price data source and for dynamic coin analysis.
    - Binance futures API: Secondary source for Bybit-compatible market data.
    - CoinCap, CryptoCompare APIs: Additional sources for pricing accuracy and fallback.
- **JavaScript Libraries**:
    - Chart.js: For price charts and performance visualization.
    - Socket.IO: For real-time client-side communication.
    - Bootstrap 5: UI framework.
- **Python Packages**:
    - Flask: Web framework.
    - Flask-SQLAlchemy: ORM for database interaction.
    - Flask-SocketIO: WebSocket integration.
    - Requests: HTTP client.
    - Gunicorn: WSGI server for production deployments.