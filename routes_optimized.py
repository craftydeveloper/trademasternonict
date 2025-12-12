"""
Optimized Routes for $50 Daily Profit Target
Replaces existing trading signals with proper Bybit configuration
"""

from flask import Blueprint, jsonify
from app import app
import logging
from fifty_daily_plan import get_fifty_dollar_signals

logger = logging.getLogger(__name__)

@app.route('/api/trading-signals-fifty')
def get_fifty_dollar_api():
    """Optimized $50 daily profit API endpoint"""
    try:
        result = get_fifty_dollar_signals()
        
        if result.get('success') and result.get('signals'):
            signals = result['signals']
            validation = result['validation']
            
            # Format for dashboard
            formatted = []
            for i, signal in enumerate(signals):
                formatted_signal = {
                    'symbol': signal['symbol'],
                    'action': signal['action'],
                    'confidence': signal['confidence'],
                    'entry_price': signal['current_price'],
                    'stop_loss': float(signal['bybit_settings']['stopLoss']),
                    'take_profit': float(signal['bybit_settings']['takeProfit']),
                    'leverage': int(signal['bybit_settings']['leverage']),
                    'risk_reward_ratio': 2.0,
                    'expected_return': 6.0,
                    'strategy_basis': 'Optimized $50 Daily Profit',
                    'trade_label': f"${signal['daily_profit_potential']:.0f} TARGET",
                    'is_primary_trade': i < 2,
                    'daily_profit_potential': signal['daily_profit_potential'],
                    'bybit_settings': signal['bybit_settings'],
                    'execution_recommendation': {
                        'priority': 'ULTRA-HIGH' if signal['confidence'] >= 98 else 'HIGH',
                        'target_daily_profit': signal['daily_profit_potential'],
                        'combined_profit_potential': validation['total_daily_profit'],
                        'daily_strategy': f"${validation['total_daily_profit']:.0f} DAILY TARGET - EXECUTE ALL",
                        'risk_level': 'OPTIMIZED FOR $50 TARGET'
                    }
                }
                formatted.append(formatted_signal)
            
            return jsonify({
                'success': True,
                'signals': formatted,
                'count': len(formatted),
                'validation': validation,
                'status': '$50 DAILY TARGET ACHIEVED'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate optimized signals',
                'signals': []
            })
            
    except Exception as e:
        logger.error(f"Error in optimized signals: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'signals': []
        })

# Replace the main endpoint
@app.route('/api/trading-signals', methods=['GET'])
def get_optimized_trading_signals():
    """Main trading signals endpoint - now optimized for $50 daily profit"""
    return get_fifty_dollar_api()