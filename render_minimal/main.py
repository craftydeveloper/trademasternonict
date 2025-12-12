"""
TradePro Trading Bot - Minimal Render Deployment
Fixed version without database dependencies
"""

import os
from flask import Flask, render_template, jsonify
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "tradepro2025secure")

# Market data provider
class SimpleMarketData:
    def __init__(self):
        self.cache = {}
        self.last_update = None
    
    def get_market_data(self):
        """Get real-time market data from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'cardano,bitcoin,ethereum,solana,chainlink,polkadot',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.cache = data
                self.last_update = datetime.now()
                return data
        except Exception as e:
            logger.error(f"Market data error: {e}")
        
        # Return cached data if available
        return self.cache if self.cache else self._get_fallback_data()
    
    def _get_fallback_data(self):
        """Fallback market data"""
        return {
            'cardano': {'usd': 0.55, 'usd_24h_change': -2.5},
            'bitcoin': {'usd': 64250, 'usd_24h_change': 1.2},
            'ethereum': {'usd': 3420, 'usd_24h_change': 0.8},
            'solana': {'usd': 145, 'usd_24h_change': -1.1},
            'chainlink': {'usd': 13.2, 'usd_24h_change': -0.9},
            'polkadot': {'usd': 7.8, 'usd_24h_change': -1.5}
        }

# Initialize market data
market_data = SimpleMarketData()

# Signal generator
class SimpleSignalGenerator:
    def __init__(self, market_data):
        self.market_data = market_data
    
    def generate_signals(self):
        """Generate trading signals based on market data"""
        data = self.market_data.get_market_data()
        signals = []
        
        # ADA signal based on current price action
        if 'cardano' in data:
            ada_price = data['cardano']['usd']
            ada_change = data['cardano'].get('usd_24h_change', 0)
            
            if ada_change < -1.5:  # Bearish momentum
                signal = {
                    'symbol': 'ADA',
                    'action': 'SELL',
                    'confidence': 93.5,
                    'entry_price': ada_price,
                    'stop_loss': round(ada_price * 1.03, 4),
                    'take_profit': round(ada_price * 0.94, 4),
                    'leverage': 8,
                    'risk_reward_ratio': 2.0,
                    'expected_return': 6,
                    'is_primary_trade': True,
                    'bybit_settings': {
                        'symbol': 'ADAUSDT',
                        'side': 'SELL',
                        'orderType': 'Market',
                        'qty': str(int(800 / ada_price)),
                        'leverage': '8',
                        'marginMode': 'isolated',
                        'stopLoss': str(round(ada_price * 1.03, 4)),
                        'takeProfit': str(round(ada_price * 0.94, 4)),
                        'timeInForce': 'GTC'
                    },
                    'execution_recommendation': {
                        'daily_strategy': '$50 DAILY TARGET - EXECUTE BOTH',
                        'priority': 'HIGH',
                        'risk_level': 'MODERATE-AGGRESSIVE',
                        'target_daily_profit': 48,
                        'combined_profit_potential': 48,
                        'total_risk': '14% of account',
                        'combined_margin_usage': '33% of account',
                        'execution_window': '4H timeframe alignment'
                    }
                }
                signals.append(signal)
        
        return signals

# Initialize signal generator
signal_generator = SimpleSignalGenerator(market_data)

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/healthz')
def health_check():
    """Health check for Render"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}, 200

@app.route('/api/signals')
def get_signals():
    """Get trading signals"""
    try:
        signals = signal_generator.generate_signals()
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
    except Exception as e:
        logger.error(f"Signals error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'signals': []
        })

@app.route('/api/market-data')
def get_market_data():
    """Get market data"""
    try:
        data = market_data.get_market_data()
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Market data error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/market-insights')
def get_market_insights():
    """Get market insights"""
    try:
        data = market_data.get_market_data()
        
        # Calculate basic insights
        changes = []
        for coin_data in data.values():
            if isinstance(coin_data, dict) and 'usd_24h_change' in coin_data:
                changes.append(coin_data['usd_24h_change'])
        
        if changes:
            avg_change = sum(changes) / len(changes)
            positive_count = sum(1 for c in changes if c > 0)
            total_count = len(changes)
            
            insights = {
                'success': True,
                'market_sentiment': 'Bullish' if avg_change > 1 else 'Bearish' if avg_change < -1 else 'Neutral',
                'avg_24h_change': f"{avg_change:+.1f}%",
                'positive_ratio': positive_count / total_count if total_count > 0 else 0,
                'volatility_level': 'High' if abs(avg_change) > 3 else 'Low',
                'volatility_ratio': abs(avg_change) / 10 if abs(avg_change) <= 10 else 1,
                'sentiment_class': 'text-success-clean' if avg_change > 0 else 'text-danger-clean' if avg_change < -1 else 'text-warning-clean',
                'change_class': 'text-success-clean' if avg_change > 0 else 'text-danger-clean',
                'volatility_class': 'text-warning-clean' if abs(avg_change) > 3 else 'text-success-clean'
            }
        else:
            insights = {
                'success': True,
                'market_sentiment': 'Neutral',
                'avg_24h_change': '+0.0%',
                'positive_ratio': 0,
                'volatility_level': 'Low',
                'volatility_ratio': 0,
                'sentiment_class': 'text-warning-clean',
                'change_class': 'text-success-clean',
                'volatility_class': 'text-success-clean'
            }
        
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Market insights error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)