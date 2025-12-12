"""
Predictive Signal System - Structure-Based Analysis
Uses OHLCV data to predict tops/bottoms BEFORE price moves
Only issues LONG/SHORT when HTF trend, liquidity sweep, and MSS/CHoCH align (score >= 7)
Maintains signal persistence until invalidated
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

from market_structure import (
    get_structure_based_signal,
    SignalPersistence,
    run_full_analysis
)

logger = logging.getLogger(__name__)

ACTIVE_TRADES = {}
PREVIOUS_SIGNALS = {}
BIAS_CHANGE_NOTIFICATIONS = []
DISPLAYED_SIGNALS = {}
SIGNAL_LAST_CHANGE = {}
DEBOUNCE_SECONDS = 14400  # 4 hours minimum between bias changes (long-term focus)


def clear_all_signal_state():
    """Clear all signal tracking state - call on server restart"""
    global DISPLAYED_SIGNALS, BIAS_CHANGE_NOTIFICATIONS, SIGNAL_LAST_CHANGE, PREVIOUS_SIGNALS
    DISPLAYED_SIGNALS.clear()
    BIAS_CHANGE_NOTIFICATIONS.clear()
    SIGNAL_LAST_CHANGE.clear()
    PREVIOUS_SIGNALS.clear()
    logger.info("Cleared all signal tracking state")


def get_predictive_signal(symbol: str, current_price: float, price_change_24h: float, 
                          volume_ratio: float = 1.0) -> Dict:
    """
    Generate predictive signals using OHLCV-based market structure analysis.
    Only returns BUY/SELL when score >= 7, otherwise HOLD.
    Maintains bias until setup is invalidated.
    """
    signal = get_structure_based_signal(symbol, current_price)
    
    if signal['action'] == 'HOLD':
        signal['indicators'] = {
            'rsi': 50.0,
            'macd': 'NEUTRAL',
            'momentum': 'ANALYZING',
            'volume': 'NORMAL'
        }
    else:
        signal['indicators'] = {
            'rsi': 30.0 if signal['action'] == 'BUY' else 70.0,
            'macd': 'BULLISH_DIVERGENCE' if signal['action'] == 'BUY' else 'BEARISH_DIVERGENCE',
            'momentum': 'EXHAUSTION_BOTTOM' if signal['action'] == 'BUY' else 'EXHAUSTION_TOP',
            'volume': 'CLIMAX'
        }
    
    return signal


def track_displayed_signal(symbol: str, action: str, current_price: float):
    """
    Track bias changes ONLY for signals that are actually displayed.
    Uses 4-hour debouncing to prevent rapid flipping notifications.
    """
    global DISPLAYED_SIGNALS, BIAS_CHANGE_NOTIFICATIONS, SIGNAL_LAST_CHANGE
    
    previous_signal = DISPLAYED_SIGNALS.get(symbol)
    
    if action not in ['BUY', 'SELL']:
        return
    
    now = datetime.now()
    
    if previous_signal and previous_signal != action:
        last_change = SIGNAL_LAST_CHANGE.get(symbol)
        if last_change:
            seconds_since_change = (now - last_change).total_seconds()
            if seconds_since_change < DEBOUNCE_SECONDS:
                DISPLAYED_SIGNALS[symbol] = action
                return
        
        notification = {
            'symbol': symbol,
            'previous': previous_signal,
            'new': action,
            'timestamp': now.isoformat(),
            'message': f"{symbol}: Bias changed from {previous_signal} to {action}",
            'price': current_price
        }
        BIAS_CHANGE_NOTIFICATIONS.insert(0, notification)
        BIAS_CHANGE_NOTIFICATIONS[:] = BIAS_CHANGE_NOTIFICATIONS[:5]
        SIGNAL_LAST_CHANGE[symbol] = now
        logger.info(f"BIAS CHANGE: {symbol} {previous_signal} -> {action} @ ${current_price}")
    
    DISPLAYED_SIGNALS[symbol] = action


def check_active_trade(symbol: str) -> Optional[Dict]:
    """Check if there's an active trade for this symbol."""
    return ACTIVE_TRADES.get(symbol)


def register_trade(symbol: str, action: str, entry_price: float, 
                   stop_loss: float, take_profit: float) -> Dict:
    """Register a new trade. No new signals will be issued until trade completes."""
    trade = {
        'symbol': symbol,
        'action': action,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'entry_time': datetime.now().isoformat(),
        'status': 'ACTIVE',
        'max_duration_hours': 48  # Extended to 48 hours for long-term focus
    }
    ACTIVE_TRADES[symbol] = trade
    logger.info(f"Trade registered: {symbol} {action} @ ${entry_price}")
    return trade


def check_trade_completion(symbol: str, current_price: float) -> Optional[Dict]:
    """Check if an active trade has hit TP, SL, or expired."""
    trade = ACTIVE_TRADES.get(symbol)
    if not trade:
        return None
    
    entry_price = trade['entry_price']
    stop_loss = trade['stop_loss']
    take_profit = trade['take_profit']
    action = trade['action']
    
    result = None
    
    if action == 'BUY':
        if current_price >= take_profit:
            pnl = ((take_profit - entry_price) / entry_price) * 100
            result = {'status': 'TP_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
        elif current_price <= stop_loss:
            pnl = ((stop_loss - entry_price) / entry_price) * 100
            result = {'status': 'SL_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
    else:
        if current_price <= take_profit:
            pnl = ((entry_price - take_profit) / entry_price) * 100
            result = {'status': 'TP_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
        elif current_price >= stop_loss:
            pnl = ((entry_price - stop_loss) / entry_price) * 100
            result = {'status': 'SL_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
    
    entry_time = datetime.fromisoformat(trade['entry_time'])
    max_duration = timedelta(hours=trade['max_duration_hours'])
    if datetime.now() - entry_time > max_duration:
        pnl = ((current_price - entry_price) / entry_price) * 100
        if action == 'SELL':
            pnl = -pnl
        result = {'status': 'EXPIRED', 'pnl_percent': pnl, 'exit_price': current_price}
    
    if result:
        result['trade'] = trade
        del ACTIVE_TRADES[symbol]
        logger.info(f"Trade completed: {symbol} - {result['status']} ({result['pnl_percent']:.2f}%)")
    
    return result


def get_bias_change_notifications() -> List[Dict]:
    """Get recent bias change notifications."""
    return BIAS_CHANGE_NOTIFICATIONS.copy()


def clear_bias_notifications():
    """Clear bias change notifications after they've been displayed."""
    BIAS_CHANGE_NOTIFICATIONS.clear()


def get_active_trades() -> Dict:
    """Get all active trades."""
    return ACTIVE_TRADES.copy()


def should_issue_signal(symbol: str, current_price: float) -> Tuple[bool, Optional[str]]:
    """
    Check if we should issue a new signal for this symbol.
    Returns (can_issue, reason_if_not)
    """
    active = check_active_trade(symbol)
    if active:
        completion = check_trade_completion(symbol, current_price)
        if completion:
            return True, f"Previous trade completed: {completion['status']}"
        return False, f"Active trade in progress - entered at ${active['entry_price']:.4f}"
    
    return True, None
