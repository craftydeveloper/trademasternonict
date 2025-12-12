from app import app

# Import routes
from flask import render_template, jsonify
from models import Portfolio, Trade

# Minimal backup data for signals
BACKUP_SIGNALS = [{
    "symbol": "ADA",
    "action": "SELL", 
    "confidence": 91.5,
    "entry_price": 0.5516,
    "stop_loss": 0.5681,
    "take_profit": 0.5185,
    "leverage": 8,
    "risk_reward_ratio": 2.0,
    "strategy_basis": "Momentum Volume Analysis",
    "time_horizon": "4H",
    "trade_label": "YOUR TRADE",
    "is_primary_trade": True
}]

@app.route('/')
def dashboard():
    return render_template('dashboard_simple.html')

@app.route('/api/signals')
def get_signals():
    return jsonify(BACKUP_SIGNALS)

@app.route('/api/portfolio')
def get_portfolio():
    return jsonify({
        'balance': 500.0,
        'total_trades': 0,
        'winning_trades': 0,
        'total_profit': 0.0,
        'win_rate': 0.0
    })

# Health check endpoint for Render
@app.route('/healthz')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)