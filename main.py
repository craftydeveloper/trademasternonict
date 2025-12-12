"""
TradePro Trading Bot - Minimal Render Deployment
Fixed version without database dependencies
"""

import os
from flask import Flask, render_template, jsonify, send_file, abort
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "tradepro2025secure")

# Routes handled separately to avoid conflicts

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
            'polkadot': {'usd': 7.8, 'usd_24h_change': -1.5},
            'matic-network': {'usd': 0.85, 'usd_24h_change': 2.1},
            'avalanche-2': {'usd': 38.5, 'usd_24h_change': 1.8},
            'uniswap': {'usd': 8.2, 'usd_24h_change': -1.3},
            'aave': {'usd': 145, 'usd_24h_change': 2.7}
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
        
        # Define crypto mappings and generate signals for each
        crypto_symbols = {
            'cardano': 'ADA',
            'bitcoin': 'BTC', 
            'ethereum': 'ETH',
            'solana': 'SOL',
            'chainlink': 'LINK',
            'polkadot': 'DOT',
            'matic-network': 'MATIC',
            'avalanche-2': 'AVAX',
            'uniswap': 'UNI',
            'aave': 'AAVE'
        }
        
        for crypto_id, symbol in crypto_symbols.items():
            if crypto_id in data:
                price = data[crypto_id]['usd']
                change_24h = data[crypto_id].get('usd_24h_change', 0)
                
                # Generate signal based on price action (more inclusive)
                if abs(change_24h) > 0.1:  # Any movement above 0.1%
                    action = 'SELL' if change_24h < 0 else 'BUY'
                    confidence = min(88 + abs(change_24h) * 3, 98)
                    
                    # Calculate position parameters
                    leverage = 8 if confidence >= 93 else 6
                    
                    if action == 'SELL':
                        stop_loss = round(price * 1.03, 6)
                        take_profit = round(price * 0.94, 6)
                    else:
                        stop_loss = round(price * 0.97, 6)
                        take_profit = round(price * 1.06, 6)
                    
                    qty = int(400 / price) if price > 1 else int(400 / price)
                    
                    signal = {
                        'symbol': symbol,
                        'action': action,
                        'confidence': round(confidence, 1),
                        'entry_price': price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'leverage': leverage,
                        'risk_reward_ratio': 2.0,
                        'expected_return': 6,
                        'is_primary_trade': len(signals) == 0,
                        'bybit_settings': {
                            'symbol': f'{symbol}USDT',
                            'side': action,
                            'orderType': 'Market',
                            'qty': str(qty),
                            'leverage': str(leverage),
                            'marginMode': 'isolated',
                            'stopLoss': str(stop_loss),
                            'takeProfit': str(take_profit),
                            'timeInForce': 'GTC'
                        },
                        'execution_recommendation': {
                            'daily_strategy': '$50 DAILY TARGET - EXECUTE BOTH',
                            'priority': 'HIGH' if confidence >= 95 else 'MODERATE',
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

# Removed - using enhanced routes.py dashboard

@app.route('/analysis')
def analysis():
    """Analysis page"""
    return render_template('analysis.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio page"""
    return render_template('portfolio.html')

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

# Removed - using enhanced routes.py trading signals with exact Bybit pricing

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

# Removed - using enhanced routes.py market insights

@app.route('/api/tokens')
def get_tokens():
    """Get available tokens for analysis"""
    try:
        core_tokens = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'status': 'core'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'status': 'core'},
            {'symbol': 'ADA', 'name': 'Cardano', 'status': 'core'},
            {'symbol': 'SOL', 'name': 'Solana', 'status': 'core'},
            {'symbol': 'DOT', 'name': 'Polkadot', 'status': 'core'},
            {'symbol': 'LINK', 'name': 'Chainlink', 'status': 'core'}
        ]
        
        extended_tokens = [
            {'symbol': 'MATIC', 'name': 'Polygon', 'status': 'extended'},
            {'symbol': 'AVAX', 'name': 'Avalanche', 'status': 'extended'},
            {'symbol': 'UNI', 'name': 'Uniswap', 'status': 'extended'},
            {'symbol': 'AAVE', 'name': 'Aave', 'status': 'extended'}
        ]
        
        all_tokens = core_tokens + extended_tokens
        return jsonify({'tokens': all_tokens, 'success': True})
        
    except Exception as e:
        logger.error(f"Error getting tokens: {e}")
        return jsonify({'error': 'Failed to load tokens', 'success': False})

# Import enhanced routes with exact Bybit pricing for all 101 cryptocurrencies
from routes import *

# Override main route to use exact Bybit pricing system
@app.route('/')
def dashboard():
    """Main dashboard with cache-busting headers"""
    from flask import make_response
    response = make_response(render_template('professional_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache' 
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)