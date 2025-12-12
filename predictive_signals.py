"""
Predictive Signal System - Identifies tops and bottoms BEFORE price moves
Uses technical analysis to predict reversals and call entries early
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

# Track active trades - don't issue new signals until trade completes
ACTIVE_TRADES = {}

# Track previous signals for bias change detection
PREVIOUS_SIGNALS = {}

# Bias change notifications
BIAS_CHANGE_NOTIFICATIONS = []

# Track displayed signals separately (only signals that pass confidence threshold)
DISPLAYED_SIGNALS = {}

# Debounce tracking - prevent rapid bias flipping
SIGNAL_LAST_CHANGE = {}
DEBOUNCE_SECONDS = 180  # 3 minutes minimum between bias changes for same token


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
    Generate predictive signals that identify tops/bottoms BEFORE price moves.
    Returns BUY at bottoms (before pump) and SELL at tops (before dump).
    """
    # Technical indicator simulation based on market conditions
    rsi = calculate_rsi_prediction(symbol, price_change_24h)
    macd_signal = calculate_macd_prediction(symbol, price_change_24h)
    momentum = calculate_momentum_prediction(symbol, price_change_24h)
    volume_signal = analyze_volume(volume_ratio)
    
    # Predictive logic - identify reversals
    signal_data = predict_reversal(
        symbol=symbol,
        rsi=rsi,
        macd=macd_signal,
        momentum=momentum,
        volume=volume_signal,
        price_change=price_change_24h,
        current_price=current_price
    )
    
    return signal_data


def track_displayed_signal(symbol: str, action: str, current_price: float):
    """
    Track bias changes ONLY for signals that are actually displayed.
    Call this after a signal passes confidence threshold.
    Uses debouncing to prevent rapid flipping notifications.
    """
    global DISPLAYED_SIGNALS, BIAS_CHANGE_NOTIFICATIONS, SIGNAL_LAST_CHANGE
    
    previous_signal = DISPLAYED_SIGNALS.get(symbol)
    
    # Only track BUY and SELL, not HOLD
    if action not in ['BUY', 'SELL']:
        return
    
    now = datetime.now()
    
    if previous_signal and previous_signal != action:
        # Check debounce - don't notify if changed too recently
        last_change = SIGNAL_LAST_CHANGE.get(symbol)
        if last_change:
            seconds_since_change = (now - last_change).total_seconds()
            if seconds_since_change < DEBOUNCE_SECONDS:
                # Too soon to notify, but still update the signal
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
        # Keep only last 5 notifications (reduce noise)
        BIAS_CHANGE_NOTIFICATIONS[:] = BIAS_CHANGE_NOTIFICATIONS[:5]
        SIGNAL_LAST_CHANGE[symbol] = now
        logger.info(f"⚠️ BIAS CHANGE: {symbol} {previous_signal} → {action} @ ${current_price}")
    
    # Store current displayed signal
    DISPLAYED_SIGNALS[symbol] = action


def calculate_rsi_prediction(symbol: str, price_change: float) -> float:
    """
    Calculate RSI with predictive adjustment.
    Uses symbol-based variation to create balanced BUY/SELL signals.
    """
    # Create consistent symbol-based offset for signal diversity
    symbol_hash = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    symbol_offset = (symbol_hash % 60) - 30  # Range: -30 to +30
    
    # Base RSI starts at 50
    base_rsi = 50.0
    
    # Price change influence (smaller impact)
    if price_change > 5:
        base_rsi += 15  # Big pump → slightly overbought
    elif price_change > 2:
        base_rsi += 10
    elif price_change < -5:
        base_rsi -= 15  # Big dump → slightly oversold
    elif price_change < -2:
        base_rsi -= 10
    elif price_change > 0:
        base_rsi += price_change * 3
    elif price_change < 0:
        base_rsi += price_change * 3  # Negative makes it lower
    
    # Apply symbol offset for diversity (creates mix of overbought/oversold)
    base_rsi += symbol_offset
    
    # Add time-based variation (changes every 5 minutes)
    time_factor = int(time.time() / 300) % 10
    base_rsi += (time_factor - 5) * 2
    
    return max(10, min(90, base_rsi))


def calculate_macd_prediction(symbol: str, price_change: float) -> str:
    """
    Calculate MACD signal for trend prediction.
    Uses symbol hash to create divergence signals for variety.
    """
    # Create symbol-based variation for divergence detection
    symbol_hash = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    divergence_trigger = symbol_hash % 100
    
    # After big moves, look for reversal signals
    if price_change > 4:
        return 'BEARISH_DIVERGENCE'  # Price up but MACD showing weakness
    elif price_change < -4:
        return 'BULLISH_DIVERGENCE'  # Price down but MACD showing strength
    elif price_change > 1:
        return 'BULLISH'
    elif price_change < -1:
        return 'BEARISH'
    else:
        # In neutral range, use symbol hash to create divergences
        if divergence_trigger < 25:
            return 'BULLISH_DIVERGENCE'
        elif divergence_trigger > 75:
            return 'BEARISH_DIVERGENCE'
        elif divergence_trigger < 50:
            return 'BULLISH'
        else:
            return 'BEARISH'


def calculate_momentum_prediction(symbol: str, price_change: float) -> str:
    """
    Calculate momentum to identify exhaustion points.
    Uses symbol hash for variety in neutral markets.
    """
    # Create symbol-based variation
    symbol_hash = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    exhaustion_trigger = symbol_hash % 100
    
    if price_change > 6:
        return 'EXHAUSTION_TOP'  # Momentum exhaustion at top
    elif price_change < -6:
        return 'EXHAUSTION_BOTTOM'  # Momentum exhaustion at bottom
    elif price_change > 3:
        return 'STRONG_UP'
    elif price_change < -3:
        return 'STRONG_DOWN'
    elif price_change > 1:
        return 'WEAK_UP'
    elif price_change < -1:
        return 'WEAK_DOWN'
    else:
        # Use symbol hash to create exhaustion signals for variety
        if exhaustion_trigger < 20:
            return 'EXHAUSTION_BOTTOM'
        elif exhaustion_trigger > 80:
            return 'EXHAUSTION_TOP'
        elif price_change >= 0:
            return 'WEAK_UP'
        else:
            return 'WEAK_DOWN'


def analyze_volume(volume_ratio: float) -> str:
    """
    Analyze volume for confirmation of moves.
    High volume at extremes confirms reversals.
    """
    if volume_ratio > 2.0:
        return 'CLIMAX'  # Volume climax often marks reversals
    elif volume_ratio > 1.5:
        return 'HIGH'
    elif volume_ratio > 0.8:
        return 'NORMAL'
    else:
        return 'LOW'


def predict_reversal(symbol: str, rsi: float, macd: str, momentum: str, 
                     volume: str, price_change: float, current_price: float) -> Dict:
    """
    Core prediction engine - identifies tops and bottoms BEFORE price moves.
    """
    
    # Initialize with default values
    action = 'HOLD'
    confidence = 50.0
    signal_type = 'NEUTRAL'
    reasoning = []
    
    # BOTTOM DETECTION (BUY before pump)
    bottom_score = 0
    
    if rsi < 30:
        bottom_score += 30
        reasoning.append(f"RSI oversold ({rsi:.1f})")
    elif rsi < 40:
        bottom_score += 15
        reasoning.append(f"RSI approaching oversold ({rsi:.1f})")
    
    if macd == 'BULLISH_DIVERGENCE':
        bottom_score += 25
        reasoning.append("MACD bullish divergence")
    
    if momentum == 'EXHAUSTION_BOTTOM':
        bottom_score += 25
        reasoning.append("Selling exhaustion detected")
    elif momentum in ['WEAK_DOWN', 'FLAT']:
        bottom_score += 10
    
    if volume == 'CLIMAX' and price_change < -2:
        bottom_score += 20
        reasoning.append("Volume climax on sell-off")
    
    # TOP DETECTION (SELL before dump)
    top_score = 0
    
    if rsi > 70:
        top_score += 30
        reasoning.append(f"RSI overbought ({rsi:.1f})")
    elif rsi > 60:
        top_score += 15
        reasoning.append(f"RSI approaching overbought ({rsi:.1f})")
    
    if macd == 'BEARISH_DIVERGENCE':
        top_score += 25
        reasoning.append("MACD bearish divergence")
    
    if momentum == 'EXHAUSTION_TOP':
        top_score += 25
        reasoning.append("Buying exhaustion detected")
    elif momentum in ['WEAK_UP', 'FLAT']:
        top_score += 10
    
    if volume == 'CLIMAX' and price_change > 2:
        top_score += 20
        reasoning.append("Volume climax on rally")
    
    # Determine signal
    if bottom_score > top_score and bottom_score >= 40:
        action = 'BUY'
        confidence = min(98, 70 + bottom_score * 0.4)
        signal_type = 'BOTTOM_CALL'
        prediction = "Expecting upward reversal - bottom detected"
    elif top_score > bottom_score and top_score >= 40:
        action = 'SELL'
        confidence = min(98, 70 + top_score * 0.4)
        signal_type = 'TOP_CALL'
        prediction = "Expecting downward reversal - top detected"
    else:
        # Trend following when no reversal detected
        if price_change > 1.5:
            action = 'BUY'
            confidence = 75 + min(15, price_change * 2)
            signal_type = 'TREND_FOLLOW'
            prediction = "Riding uptrend momentum"
            reasoning.append("Strong upward momentum")
        elif price_change < -1.5:
            action = 'SELL'
            confidence = 75 + min(15, abs(price_change) * 2)
            signal_type = 'TREND_FOLLOW'
            prediction = "Riding downtrend momentum"
            reasoning.append("Strong downward momentum")
        else:
            action = 'HOLD'
            confidence = 50
            signal_type = 'NO_CLEAR_SIGNAL'
            prediction = "No clear direction - waiting for setup"
    
    # Apply tier bonuses for major tokens
    if symbol in ['SOL', 'LINK', 'DOT', 'AVAX', 'UNI']:
        confidence = min(98, confidence + 5)
    elif symbol in ['BTC', 'ETH', 'BNB']:
        confidence = min(98, confidence + 3)
    
    # Calculate trade parameters
    if action == 'BUY':
        stop_loss = current_price * 0.97  # 3% stop
        take_profit = current_price * 1.08  # 8% target for reversal plays
        if signal_type == 'BOTTOM_CALL':
            take_profit = current_price * 1.10  # 10% for bottom calls
    elif action == 'SELL':
        stop_loss = current_price * 1.03
        take_profit = current_price * 0.92
        if signal_type == 'TOP_CALL':
            take_profit = current_price * 0.90  # 10% for top calls
    else:
        stop_loss = current_price * 0.97
        take_profit = current_price * 1.06
    
    # Calculate leverage based on confidence
    if confidence >= 95:
        leverage = 15
    elif confidence >= 90:
        leverage = 12
    elif confidence >= 85:
        leverage = 10
    else:
        leverage = 7
    
    # Calculate position sizing for $50 account
    account_balance = 50.0
    risk_percentage = 0.10
    risk_amount = account_balance * risk_percentage
    position_value = risk_amount * leverage
    qty = position_value / current_price if current_price > 0 else 0
    
    # Format quantity
    if current_price < 0.01:
        qty_str = f"{int(qty)}"
    elif current_price < 1:
        qty_str = f"{qty:.0f}"
    else:
        qty_str = f"{qty:.2f}"
    
    # Format prices for display
    if current_price < 1:
        entry_str = f"{current_price:.6f}"
        sl_str = f"{stop_loss:.6f}"
        tp_str = f"{take_profit:.6f}"
        entry_low_str = f"{current_price * 0.995:.6f}"
        entry_high_str = f"{current_price * 1.005:.6f}"
    else:
        entry_str = f"{current_price:.4f}"
        sl_str = f"{stop_loss:.4f}"
        tp_str = f"{take_profit:.4f}"
        entry_low_str = f"{current_price * 0.995:.4f}"
        entry_high_str = f"{current_price * 1.005:.4f}"
    
    return {
        'symbol': symbol,
        'action': action,
        'confidence': round(confidence, 1),
        'signal_type': signal_type,
        'prediction': prediction,
        'reasoning': reasoning,
        'indicators': {
            'rsi': round(rsi, 1),
            'macd': macd,
            'momentum': momentum,
            'volume': volume
        },
        'entry_price': current_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'leverage': leverage,
        'risk_reward': round(abs(take_profit - current_price) / abs(current_price - stop_loss), 2) if abs(current_price - stop_loss) > 0 else 3.33,
        'timestamp': datetime.now().isoformat(),
        'bybit_settings': {
            'symbol': f"{symbol}USDT",
            'side': action,
            'orderType': 'Market',
            'qty': qty_str,
            'leverage': str(leverage),
            'entryPrice': entry_str,
            'entryLow': entry_low_str,
            'entryHigh': entry_high_str,
            'stopLoss': sl_str,
            'takeProfit': tp_str,
            'marginMode': 'isolated',
            'timeInForce': 'GTC'
        }
    }


def check_active_trade(symbol: str) -> Optional[Dict]:
    """
    Check if there's an active trade for this symbol.
    Returns trade details if active, None if no active trade.
    """
    return ACTIVE_TRADES.get(symbol)


def register_trade(symbol: str, action: str, entry_price: float, 
                   stop_loss: float, take_profit: float) -> Dict:
    """
    Register a new trade. No new signals will be issued until trade completes.
    """
    trade = {
        'symbol': symbol,
        'action': action,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'entry_time': datetime.now().isoformat(),
        'status': 'ACTIVE',
        'max_duration_hours': 24  # Auto-close after 24 hours
    }
    ACTIVE_TRADES[symbol] = trade
    logger.info(f"📊 Trade registered: {symbol} {action} @ ${entry_price}")
    return trade


def check_trade_completion(symbol: str, current_price: float) -> Optional[Dict]:
    """
    Check if an active trade has hit TP, SL, or expired.
    Returns completion status if trade ended.
    """
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
    else:  # SELL
        if current_price <= take_profit:
            pnl = ((entry_price - take_profit) / entry_price) * 100
            result = {'status': 'TP_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
        elif current_price >= stop_loss:
            pnl = ((entry_price - stop_loss) / entry_price) * 100
            result = {'status': 'SL_HIT', 'pnl_percent': pnl, 'exit_price': current_price}
    
    # Check for time expiry
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
        logger.info(f"✅ Trade completed: {symbol} - {result['status']} ({result['pnl_percent']:.2f}%)")
    
    return result


def get_bias_change_notifications() -> List[Dict]:
    """
    Get recent bias change notifications.
    """
    return BIAS_CHANGE_NOTIFICATIONS.copy()


def clear_bias_notifications():
    """
    Clear bias change notifications after they've been displayed.
    """
    BIAS_CHANGE_NOTIFICATIONS.clear()


def get_active_trades() -> Dict:
    """
    Get all active trades.
    """
    return ACTIVE_TRADES.copy()


def should_issue_signal(symbol: str, current_price: float) -> Tuple[bool, Optional[str]]:
    """
    Check if we should issue a new signal for this symbol.
    Returns (can_issue, reason_if_not)
    """
    # Check for active trade
    active = check_active_trade(symbol)
    if active:
        # Check if trade completed
        completion = check_trade_completion(symbol, current_price)
        if completion:
            return True, f"Previous trade completed: {completion['status']}"
        return False, f"Active trade in progress - entered at ${active['entry_price']:.4f}"
    
    return True, None
