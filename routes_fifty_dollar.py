"""
$50 Daily Profit API Routes
Replaces standard routes with optimized $50 daily profit signal generation
"""

from flask import jsonify
import logging
from fifty_daily_plan import get_fifty_dollar_signals

logger = logging.getLogger(__name__)

def get_fifty_dollar_trading_signals():
    """Generate optimized trading signals for $50 daily profit target"""
    
    try:
        # Get the optimized $50 daily signals
        fifty_result = get_fifty_dollar_signals()
        
        if fifty_result.get('success') and fifty_result.get('signals'):
            optimized_signals = fifty_result['signals']
            validation = fifty_result['validation']
            
            # Convert to dashboard-compatible format
            dashboard_signals = []
            
            for i, signal in enumerate(optimized_signals):
                # Format for dashboard display
                dashboard_signal = {
                    'symbol': signal['symbol'],
                    'action': signal['action'],
                    'confidence': signal['confidence'],
                    'entry_price': signal['current_price'],
                    'stop_loss': float(signal['bybit_settings']['stopLoss']),
                    'take_profit': float(signal['bybit_settings']['takeProfit']),
                    'leverage': int(signal['bybit_settings']['leverage']),
                    'risk_reward_ratio': float(signal['risk_management']['risk_reward_ratio'].split(':')[1]),
                    'expected_return': 6.0,
                    'strategy_basis': 'Optimized $50 Daily Profit',
                    'time_horizon': '4H',
                    'trade_label': f"${signal['daily_profit_potential']:.0f} TARGET",
                    'is_primary_trade': i < 2,  # Top 2 are primary
                    'daily_profit_potential': signal['daily_profit_potential'],
                    'bybit_settings': {
                        'symbol': signal['bybit_settings']['symbol'],
                        'side': signal['bybit_settings']['side'],
                        'orderType': signal['bybit_settings']['orderType'],
                        'qty': signal['bybit_settings']['qty'],
                        'leverage': signal['bybit_settings']['leverage'],
                        'stopLoss': signal['bybit_settings']['stopLoss'],
                        'takeProfit': signal['bybit_settings']['takeProfit'],
                        'marginMode': signal['bybit_settings']['marginMode'],
                        'timeInForce': signal['bybit_settings']['timeInForce']
                    },
                    'execution_recommendation': {
                        'priority': 'ULTRA-HIGH' if signal['confidence'] >= 98 else ('HIGH' if signal['confidence'] >= 96 else 'MODERATE'),
                        'target_daily_profit': signal['daily_profit_potential'],
                        'combined_profit_potential': validation['total_daily_profit'],
                        'risk_level': 'OPTIMIZED FOR $50 TARGET',
                        'execution_window': '4H timeframe alignment',
                        'daily_strategy': f"${validation['total_daily_profit']:.0f} DAILY TARGET - EXECUTE ALL",
                        'total_risk': validation['total_account_risk'],
                        'combined_margin_usage': '35% of account'
                    }
                }
                dashboard_signals.append(dashboard_signal)
            
            return {
                'success': True,
                'signals': dashboard_signals,
                'count': len(dashboard_signals),
                'validation': validation,
                'status': 'OPTIMIZED FOR $50 DAILY TARGET',
                'summary': {
                    'total_daily_profit': validation['total_daily_profit'],
                    'daily_return_rate': validation['daily_return_rate'],
                    'monthly_projection': validation['monthly_projection'],
                    'target_status': validation['status']
                }
            }
        
        else:
            # Return error if optimization fails
            return {
                'success': False,
                'error': 'Failed to generate $50 daily profit signals',
                'signals': [],
                'count': 0
            }
            
    except Exception as e:
        logger.error(f"Error in $50 daily profit signals: {e}")
        return {
            'success': False,
            'error': str(e),
            'signals': [],
            'count': 0
        }

def test_fifty_dollar_system():
    """Test the $50 daily profit system"""
    result = get_fifty_dollar_trading_signals()
    
    if result['success']:
        print("=== $50 DAILY PROFIT SYSTEM TEST ===")
        print(f"Total signals: {result['count']}")
        print(f"Total daily profit: ${result['validation']['total_daily_profit']}")
        print(f"Status: {result['validation']['status']}")
        
        for i, signal in enumerate(result['signals'], 1):
            bybit = signal['bybit_settings']
            print(f"\nSignal {i}: {signal['symbol']} {signal['action']}")
            print(f"  Confidence: {signal['confidence']}%")
            print(f"  Leverage: {bybit['leverage']}x")
            print(f"  Quantity: {bybit['qty']}")
            print(f"  Daily Profit: ${signal['daily_profit_potential']}")
        
        return True
    else:
        print(f"System test failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    test_fifty_dollar_system()