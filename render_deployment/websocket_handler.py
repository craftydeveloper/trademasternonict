import logging
import threading
import time
from flask_socketio import emit
from app import socketio, app
from trading_engine import TradingEngine
from solana_client import SolanaClient

logger = logging.getLogger(__name__)

# Initialize clients
trading_engine = TradingEngine()
solana_client = SolanaClient()

# Global flag for price monitoring
price_monitoring_active = False
price_monitoring_thread = None

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'data': 'Connected to Solana Trading Bot'})
    
    # Start price monitoring if not already active
    global price_monitoring_active, price_monitoring_thread
    if not price_monitoring_active:
        start_price_monitoring()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('subscribe_prices')
def handle_subscribe_prices(data):
    """Handle price subscription request"""
    symbols = data.get('symbols', [])
    logger.info(f'Client subscribed to prices for: {symbols}')
    
    # Send current prices immediately
    try:
        price_data = solana_client.get_popular_tokens_data()
        emit('price_update', price_data)
    except Exception as e:
        logger.error(f"Error sending current prices: {e}")

@socketio.on('get_portfolio')
def handle_get_portfolio():
    """Handle portfolio data request"""
    try:
        portfolio_summary = trading_engine.get_portfolio_summary()
        emit('portfolio_update', portfolio_summary)
    except Exception as e:
        logger.error(f"Error sending portfolio data: {e}")

@socketio.on('execute_trade')
def handle_execute_trade(data):
    """Handle trade execution via WebSocket"""
    try:
        symbol = data['symbol'].upper()
        side = data['side'].upper()
        quantity = float(data['quantity'])
        price = float(data['price'])
        strategy = data.get('strategy', 'manual')
        
        result = trading_engine.execute_trade(symbol, side, quantity, price, strategy)
        
        emit('trade_result', result)
        
        # Send updated portfolio data
        if result['success']:
            portfolio_summary = trading_engine.get_portfolio_summary()
            emit('portfolio_update', portfolio_summary)
            
    except Exception as e:
        logger.error(f"Error executing trade via WebSocket: {e}")
        emit('trade_result', {'success': False, 'error': str(e)})

def start_price_monitoring():
    """Start the price monitoring thread"""
    global price_monitoring_active, price_monitoring_thread
    
    if price_monitoring_active:
        return
    
    price_monitoring_active = True
    price_monitoring_thread = threading.Thread(target=price_monitoring_worker)
    price_monitoring_thread.daemon = True
    price_monitoring_thread.start()
    logger.info("Price monitoring started")

def price_monitoring_worker():
    """Worker function for price monitoring"""
    global price_monitoring_active
    
    while price_monitoring_active:
        try:
            with app.app_context():
                # Get current prices
                price_data = solana_client.get_popular_tokens_data()
                
                if price_data:
                    # Emit price updates to all connected clients
                    socketio.emit('price_update', price_data)
                    
                    # Update position prices
                    trading_engine.update_positions_prices()
                    
                    # Execute strategy signals
                    trading_engine.execute_strategy_signals()
                    
                    # Send updated portfolio data
                    portfolio_summary = trading_engine.get_portfolio_summary()
                    socketio.emit('portfolio_update', portfolio_summary)
                
        except Exception as e:
            logger.error(f"Error in price monitoring worker: {e}")
        
        # Wait 30 seconds before next update
        time.sleep(30)

def stop_price_monitoring():
    """Stop the price monitoring thread"""
    global price_monitoring_active
    price_monitoring_active = False
    logger.info("Price monitoring stopped")
