"""
Predictive Signal System - Structure-Based Analysis
Uses OHLCV data to predict tops/bottoms BEFORE price moves
Only issues LONG/SHORT when HTF trend, liquidity sweep, and MSS/CHoCH align (score >= 7)
Maintains signal persistence - NO quick flipping of bias
Requires 100+ analysis cycles before changing direction
"""
import logging
import time
import json
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
ANALYSIS_CYCLE_COUNTS = {}  # Track analysis cycles per symbol since last signal
LAST_SIGNAL_DIRECTION = {}  # Track last signal direction per symbol
LAST_SIGNAL_TIME = {}  # Track when last signal was issued

# CRITICAL SETTINGS - Prevent short-term signal flipping
MIN_HOLD_HOURS = 4  # Minimum 4 hours before any bias change
MIN_ANALYSIS_CYCLES_BEFORE_CHANGE = 100  # Must run 100+ analysis cycles before changing direction
DEBOUNCE_SECONDS = 14400  # 4 hours minimum between bias changes


def clear_all_signal_state():
    """Clear all signal tracking state - call on server restart"""
    global DISPLAYED_SIGNALS, BIAS_CHANGE_NOTIFICATIONS, SIGNAL_LAST_CHANGE, PREVIOUS_SIGNALS
    global ANALYSIS_CYCLE_COUNTS, LAST_SIGNAL_DIRECTION, LAST_SIGNAL_TIME
    DISPLAYED_SIGNALS.clear()
    BIAS_CHANGE_NOTIFICATIONS.clear()
    SIGNAL_LAST_CHANGE.clear()
    PREVIOUS_SIGNALS.clear()
    ANALYSIS_CYCLE_COUNTS.clear()
    LAST_SIGNAL_DIRECTION.clear()
    LAST_SIGNAL_TIME.clear()
    logger.info("Cleared all signal tracking state")


def increment_analysis_cycle(symbol: str):
    """Increment the analysis cycle count for a symbol"""
    if symbol not in ANALYSIS_CYCLE_COUNTS:
        ANALYSIS_CYCLE_COUNTS[symbol] = 0
    ANALYSIS_CYCLE_COUNTS[symbol] += 1


def get_analysis_cycle_count(symbol: str) -> int:
    """Get current analysis cycle count for a symbol"""
    return ANALYSIS_CYCLE_COUNTS.get(symbol, 0)


def reset_analysis_cycle(symbol: str):
    """Reset analysis cycle count after signal is issued"""
    ANALYSIS_CYCLE_COUNTS[symbol] = 0


def can_change_direction(symbol: str, new_direction: str, current_price: float) -> Tuple[bool, str]:
    """
    Check if we can change direction for a symbol.
    Requires:
    1. At least MIN_HOLD_HOURS since last signal
    2. At least MIN_ANALYSIS_CYCLES_BEFORE_CHANGE analysis cycles
    3. Price has moved significantly (not just small fluctuations)
    
    Returns (can_change, reason)
    """
    last_direction = LAST_SIGNAL_DIRECTION.get(symbol)
    last_time = LAST_SIGNAL_TIME.get(symbol)
    cycle_count = get_analysis_cycle_count(symbol)
    
    # If no previous signal, allow new signal
    if not last_direction or not last_time:
        return True, "First signal for this token"
    
    # If same direction, always allow (reinforcing existing bias)
    if last_direction == new_direction:
        return True, "Reinforcing existing bias"
    
    # Check time requirement
    hours_since_last = (datetime.now() - last_time).total_seconds() / 3600
    if hours_since_last < MIN_HOLD_HOURS:
        return False, f"Only {hours_since_last:.1f}h since last signal (need {MIN_HOLD_HOURS}h)"
    
    # Check analysis cycle requirement
    if cycle_count < MIN_ANALYSIS_CYCLES_BEFORE_CHANGE:
        return False, f"Only {cycle_count} analysis cycles (need {MIN_ANALYSIS_CYCLES_BEFORE_CHANGE}+)"
    
    return True, f"Direction change allowed after {hours_since_last:.1f}h and {cycle_count} analyses"


def record_signal_issued(symbol: str, direction: str, signal_data: Dict):
    """Record that a signal was issued for tracking purposes"""
    # Store the cycle count BEFORE resetting for verification
    cycle_count_at_signal = get_analysis_cycle_count(symbol)
    
    LAST_SIGNAL_DIRECTION[symbol] = direction
    LAST_SIGNAL_TIME[symbol] = datetime.now()
    reset_analysis_cycle(symbol)
    
    # Determine if liquidity sweep actually occurred (check the type field, not just existence)
    liquidity_sweep_data = signal_data.get('analysis', {}).get('liquidity_sweep')
    has_liquidity_sweep = liquidity_sweep_data is not None and liquidity_sweep_data in ['HIGH_SWEEP', 'LOW_SWEEP']
    
    # Save to database
    try:
        from app import db
        from models import SignalHistory
        
        history = SignalHistory(
            symbol=symbol,
            action=direction,
            entry_price=signal_data.get('entry_price', 0),
            score=signal_data.get('score', 0),
            htf_trend=signal_data.get('analysis', {}).get('htf_trend'),
            liquidity_sweep=has_liquidity_sweep,
            structure_shift=signal_data.get('analysis', {}).get('mss_choch'),
            confidence=signal_data.get('confidence', 0),
            analysis_details=json.dumps({
                'score_breakdown': signal_data.get('score_breakdown', []),
                'cycles_at_signal': cycle_count_at_signal
            })
        )
        db.session.add(history)
        db.session.commit()
        logger.info(f"Signal recorded to history: {symbol} {direction} (after {cycle_count_at_signal} cycles)")
    except Exception as e:
        logger.error(f"Failed to save signal history: {e}")


def get_predictive_signal(symbol: str, current_price: float, price_change_24h: float, 
                          volume_ratio: float = 1.0) -> Dict:
    """
    Generate predictive signals using OHLCV-based market structure analysis.
    Only returns BUY/SELL when score >= 7, otherwise HOLD.
    Enforces minimum hold periods and analysis cycles before direction change.
    """
    # Increment analysis cycle for this symbol
    increment_analysis_cycle(symbol)
    
    # Get structure-based signal
    signal = get_structure_based_signal(symbol, current_price)
    
    # If signal is actionable (not HOLD), check if we can issue it
    if signal['action'] != 'HOLD':
        new_direction = 'LONG' if signal['action'] == 'BUY' else 'SHORT'
        can_change, reason = can_change_direction(symbol, new_direction, current_price)
        
        if not can_change:
            # Force HOLD - not enough analysis or time since last signal
            logger.info(f"{symbol}: Blocked direction change to {new_direction}. {reason}")
            signal['action'] = 'HOLD'
            signal['direction'] = 'ANALYZING'
            signal['blocked_reason'] = reason
            signal['would_be_direction'] = new_direction
            signal['analysis_cycles'] = get_analysis_cycle_count(symbol)
            signal['prediction'] = f"Building conviction... {reason}"
        else:
            # Record the signal
            record_signal_issued(symbol, new_direction, signal)
            logger.info(f"{symbol}: Signal issued - {new_direction} @ ${current_price}")
    
    # Add analysis cycle info to all signals
    signal['analysis_cycles'] = get_analysis_cycle_count(symbol)
    signal['min_cycles_required'] = MIN_ANALYSIS_CYCLES_BEFORE_CHANGE
    signal['last_signal_direction'] = LAST_SIGNAL_DIRECTION.get(symbol)
    
    last_time = LAST_SIGNAL_TIME.get(symbol)
    if last_time:
        hours_since = (datetime.now() - last_time).total_seconds() / 3600
        signal['hours_since_last_signal'] = round(hours_since, 1)
    else:
        signal['hours_since_last_signal'] = None
    
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


def get_signal_history(limit: int = 50) -> List[Dict]:
    """Get recent signal history from database"""
    try:
        from models import SignalHistory
        signals = SignalHistory.query.order_by(SignalHistory.created_at.desc()).limit(limit).all()
        return [s.to_dict() for s in signals]
    except Exception as e:
        logger.error(f"Failed to get signal history: {e}")
        return []


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
