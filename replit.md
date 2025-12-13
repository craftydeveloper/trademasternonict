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
- **File-based persistence (Dec 13, 2025)**: ACTIVE_SIGNALS saved to /tmp/active_signals.json
  - Signals survive server restarts and load automatically on startup
  - Expired signals (>4h old) are filtered out on load
  - Ensures consistency between development and production environments

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

## RSI Divergence Detection & Fallback Strategy (Dec 13, 2025)

Enhanced signal generation with divergence detection and fallback for when confluence is weak:

**RSI Divergence Detection:**
- Bullish Divergence: Price makes LOWER low, RSI makes HIGHER low → reversal UP likely
- Bearish Divergence: Price makes HIGHER high, RSI makes LOWER high → reversal DOWN likely
- Hidden Bullish: Higher price low + Lower RSI low → uptrend continuation
- Hidden Bearish: Lower price high + Higher RSI high → downtrend continuation
- Divergence strength calculated from price/RSI delta (stronger = more reliable)
- Checked on 4h timeframe for optimal balance of noise reduction and responsiveness

**Fallback Strategy (No Confluence):**
When multiple timeframes don't agree, the system uses:
1. **RSI Divergence (85% confidence)** - If detected, overrides weak confluence
2. **Dominant Timeframe (70% confidence)** - Uses strongest signal from 4h > 1d > 1h
3. **HTF Filter Still Applied** - Fallback signals blocked if against HTF trend

**Signal Priority Hierarchy:**
1. Strong multi-TF confluence (highest confidence)
2. RSI divergence signal (85% confidence modifier)
3. Dominant single TF signal (70% confidence modifier)
4. HOLD if nothing clear

**Implementation:**
- `detect_rsi_divergence(symbol, timeframe)` - Detects classic/hidden divergences
- `get_dominant_timeframe_signal(symbol)` - Returns fallback signal with source
- Integrated into `predict_reversal()` as final fallback path
- Ensures opportunities aren't missed when TF confluence is weak

## Real OHLC Data Integration (Dec 13, 2025)

The analysis system now uses REAL historical candlestick data from multiple reliable APIs:

**Data Sources (Priority Order):**
- Primary: Binance.US OHLC API (works globally, not geo-blocked, matches Bybit prices closely)
- Secondary: KuCoin API (works globally, reliable fallback)
- Tertiary: CryptoCompare OHLC API (rate limited on free tier)
- Backup: Persistent file cache in /tmp/ohlc_cache/ (survives API failures)

**Reliability Improvements (Dec 13, 2025):**
- Increased cache durations: 10min (15m), 30min (1h), 1hr (4h), 2hr (1d), 4hr (1w)
- Request throttling: 200ms between API calls to prevent rate limiting
- Fallback chain: If one API fails, automatically tries the next
- Persistent backup: Cache saved to disk, usable for up to 24 hours
- Note: Bybit and Binance main APIs are geo-blocked from server, so Binance.US is used

**Real Calculations:**
- RSI: Calculated from actual 14-period closing prices (not simulated)
- MACD: Real 12/26/9 EMA calculations from historical closes
- Support/Resistance: Derived from actual high/low prices over 20 periods
- Momentum: Based on real 5-period and 20-period price changes
- Volume Analysis: Compares recent vs historical volume averages

**Implementation:**
- `binance_ohlc.py`: Module for fetching and caching real OHLC data
- `get_real_timeframe_rsi()`: Returns RSI for all 5 timeframes
- `get_real_support_resistance()`: Returns actual S/R levels from price data
- Falls back to simulated values if real data unavailable

## All-Timeframe Analysis (Dec 13, 2025)

The signal system now uses ALL timeframes for comprehensive analysis:

**Timeframes Analyzed:**
- 15m (short-term) - Most reactive to recent changes
- 1h (short-term) - Short-term momentum
- 4h (medium-term) - Medium-term trend
- 1d (daily) - Daily trend
- 1w (weekly) - Long-term trend (smoothest)

**Multi-Timeframe Confluence:**
- Each timeframe contributes weighted scores (longer TF = more weight)
- Confluence strength: VERY_STRONG (4+ TF agree), STRONG (3+), MODERATE (2+), WEAK
- Overall bias: STRONG_BULLISH, BULLISH, NEUTRAL, BEARISH, STRONG_BEARISH
- Color-coded RSI display: green for oversold (<35), red for overbought (>65)

**Per-Timeframe Bias Display (Dec 13, 2025):**
- Shows individual BUY/SELL/HOLD bias for each timeframe
- Displayed as: "TF Bias (15m / 1h / 4h / 1d / 1w)" row
- Color-coded: green for BUY, red for SELL, gray for HOLD
- Helps traders see which timeframes agree/disagree
- RSI thresholds for bias: <45 = BUY, >55 = SELL, 45-55 = HOLD
- This is analysis data only, not the main signal

**Implementation:**
- `calculate_all_timeframe_rsi()` - Calculates RSI for all 5 timeframes
- `get_multi_timeframe_confluence()` - Returns `timeframe_bias` dict with BUY/SELL/HOLD per TF
- `predict_reversal()` - Uses confluence for better signal scoring
- Frontend displays all 5 RSI values with color coding + confluence indicator

## Priority Markets Section (Dec 13, 2025)

A dedicated Priority Markets section displays deep analysis for BTC, ETH, and SOL:

**Display Features:**
- Golden-bordered cards with priority star icons
- Real-time BUY/SELL/HOLD signals - uniform with rest of bot
- Support and resistance levels
- All-timeframe RSI (15m / 1h / 4h / 1d / 1w) with color coding
- TF Confluence indicator showing overall bias
- Momentum direction (Strong Up/Up/Down/Strong Down/Flat)
- Market phase detection
- Volatility percentage
- Outlook/recommendation text

**Implementation:**
- Backend: PRIORITY_COINS = ['BTC', 'ETH', 'SOL'] in routes.py and predictive_signals.py
- API: /api/predictive-signals returns priority_coins array with enhanced_research data
- Frontend: displayPriorityMarkets() function renders priority cards in professional_dashboard.html
- **Bug fix (Dec 13, 2025)**: Fixed signal display to use `coin.action` instead of `coin.signal` for consistency

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