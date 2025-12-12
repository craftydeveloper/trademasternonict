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