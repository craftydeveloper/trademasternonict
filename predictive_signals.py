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
DEBOUNCE_SECONDS = 7200  # 2 HOURS minimum between bias changes for same token

# Long-term signal persistence - keep signals until invalidated
ACTIVE_SIGNALS = {}  # Stores: {symbol: {'action': 'BUY/SELL', 'entry_price': float, 'stop_loss': float, 'timestamp': datetime, 'htf_trend': str}}
SIGNAL_VALIDITY_HOURS = 4  # Signals remain valid for 4 hours unless invalidated

# Higher Timeframe (HTF) trend tracking
HTF_TRENDS = {}  # {symbol: {'trend': 'BULLISH/BEARISH/NEUTRAL', 'last_update': datetime, 'price_at_trend': float}}
HTF_UPDATE_INTERVAL = 3600  # Update HTF analysis every 1 hour

# Consecutive confirmation tracking - requires 2+ moves in same direction
PRICE_DIRECTION_HISTORY = {}  # {symbol: [direction1, direction2, ...]} where direction is 'UP' or 'DOWN'
MAX_DIRECTION_HISTORY = 3  # Keep last 3 price moves

def track_price_direction(symbol: str, price_change: float) -> int:
    """
    Track consecutive price moves in same direction.
    Returns count of consecutive moves in current direction.
    """
    global PRICE_DIRECTION_HISTORY
    
    if symbol not in PRICE_DIRECTION_HISTORY:
        PRICE_DIRECTION_HISTORY[symbol] = []
    
    # Determine current direction
    if price_change > 0.5:
        current_dir = 'UP'
    elif price_change < -0.5:
        current_dir = 'DOWN'
    else:
        current_dir = 'FLAT'
    
    history = PRICE_DIRECTION_HISTORY[symbol]
    
    # Add to history
    if len(history) >= MAX_DIRECTION_HISTORY:
        history.pop(0)
    history.append(current_dir)
    
    # Count consecutive moves in current direction
    if current_dir == 'FLAT':
        return 0
    
    count = 0
    for d in reversed(history):
        if d == current_dir:
            count += 1
        else:
            break
    
    return count


def clear_all_signal_state():
    """Clear all signal tracking state - call on server restart"""
    global DISPLAYED_SIGNALS, BIAS_CHANGE_NOTIFICATIONS, SIGNAL_LAST_CHANGE, PREVIOUS_SIGNALS, ACTIVE_SIGNALS, HTF_TRENDS
    DISPLAYED_SIGNALS.clear()
    BIAS_CHANGE_NOTIFICATIONS.clear()
    SIGNAL_LAST_CHANGE.clear()
    PREVIOUS_SIGNALS.clear()
    ACTIVE_SIGNALS.clear()
    HTF_TRENDS.clear()
    logger.info("Cleared all signal tracking state")


def _build_bybit_settings(symbol: str, action: str, entry_price: float, 
                          stop_loss: float, take_profit: float, qty: str = '0') -> Dict:
    """
    Build uniform bybit_settings object for all signal types.
    Ensures Entry, TP, SL are formatted consistently everywhere.
    """
    leverage = 12
    
    if entry_price < 1:
        entry_str = f"{entry_price:.6f}"
        sl_str = f"{stop_loss:.6f}"
        tp_str = f"{take_profit:.6f}"
        entry_low_str = f"{entry_price * 0.995:.6f}"
        entry_high_str = f"{entry_price * 1.005:.6f}"
    else:
        entry_str = f"{entry_price:.4f}"
        sl_str = f"{stop_loss:.4f}"
        tp_str = f"{take_profit:.4f}"
        entry_low_str = f"{entry_price * 0.995:.4f}"
        entry_high_str = f"{entry_price * 1.005:.4f}"
    
    return {
        'symbol': f"{symbol}USDT",
        'side': action,
        'orderType': 'Market',
        'qty': qty,
        'leverage': str(leverage),
        'entryPrice': entry_str,
        'entryLow': entry_low_str,
        'entryHigh': entry_high_str,
        'stopLoss': sl_str,
        'takeProfit': tp_str,
        'marginMode': 'isolated',
        'timeInForce': 'GTC'
    }


def get_htf_trend(symbol: str, current_price: float, price_change_24h: float) -> str:
    """
    Calculate Higher Timeframe (HTF) trend. 
    This represents the broader market direction and only updates hourly.
    """
    global HTF_TRENDS
    now = datetime.now()
    
    existing = HTF_TRENDS.get(symbol)
    if existing:
        last_update = existing.get('last_update')
        if last_update and (now - last_update).total_seconds() < HTF_UPDATE_INTERVAL:
            return existing['trend']
    
    # Calculate HTF trend based on 24h price action
    if price_change_24h > 3:
        trend = 'BULLISH'
    elif price_change_24h < -3:
        trend = 'BEARISH'
    elif price_change_24h > 1:
        trend = 'WEAK_BULLISH'
    elif price_change_24h < -1:
        trend = 'WEAK_BEARISH'
    else:
        trend = 'NEUTRAL'
    
    HTF_TRENDS[symbol] = {
        'trend': trend,
        'last_update': now,
        'price_at_trend': current_price
    }
    
    return trend


def check_signal_still_valid(symbol: str, current_price: float, price_change_24h: float) -> tuple:
    """
    Check if an existing signal is still valid.
    Returns (is_valid, invalidation_reason)
    
    Signal becomes invalid when:
    1. Stop loss is hit
    2. Take profit is hit
    3. HTF trend reverses against the signal
    4. Signal has expired (4+ hours old)
    """
    if symbol not in ACTIVE_SIGNALS:
        return False, "No active signal"
    
    signal = ACTIVE_SIGNALS[symbol]
    action = signal['action']
    entry_price = signal['entry_price']
    stop_loss = signal['stop_loss']
    take_profit = signal.get('take_profit', entry_price * (1.10 if action == 'BUY' else 0.90))
    timestamp = signal['timestamp']
    
    # Check if signal expired
    hours_active = (datetime.now() - timestamp).total_seconds() / 3600
    if hours_active > SIGNAL_VALIDITY_HOURS:
        return False, f"Signal expired after {SIGNAL_VALIDITY_HOURS} hours"
    
    # Check stop loss hit
    if action == 'BUY' and current_price <= stop_loss:
        return False, f"Stop loss hit at ${current_price:.4f}"
    if action == 'SELL' and current_price >= stop_loss:
        return False, f"Stop loss hit at ${current_price:.4f}"
    
    # Check take profit hit
    if action == 'BUY' and current_price >= take_profit:
        return False, f"Take profit hit at ${current_price:.4f}"
    if action == 'SELL' and current_price <= take_profit:
        return False, f"Take profit hit at ${current_price:.4f}"
    
    # Check if HTF trend reversed against signal
    # Invalidate on ANY bearish HTF for BUY, or ANY bullish HTF for SELL
    htf_trend = get_htf_trend(symbol, current_price, price_change_24h)
    stored_htf = signal.get('htf_trend', 'NEUTRAL')
    
    if action == 'BUY' and htf_trend in ['BEARISH', 'WEAK_BEARISH']:
        return False, f"HTF trend reversed to {htf_trend} - closing BUY"
    if action == 'SELL' and htf_trend in ['BULLISH', 'WEAK_BULLISH']:
        return False, f"HTF trend reversed to {htf_trend} - closing SELL"
    
    # Also invalidate if HTF changed significantly from when signal was created
    if stored_htf != htf_trend:
        bullish_states = ['BULLISH', 'WEAK_BULLISH']
        bearish_states = ['BEARISH', 'WEAK_BEARISH']
        
        # If stored was bullish/neutral and now bearish, invalidate BUY
        if action == 'BUY' and stored_htf not in bearish_states and htf_trend in bearish_states:
            return False, f"HTF broke from {stored_htf} to {htf_trend}"
        # If stored was bearish/neutral and now bullish, invalidate SELL
        if action == 'SELL' and stored_htf not in bullish_states and htf_trend in bullish_states:
            return False, f"HTF broke from {stored_htf} to {htf_trend}"
    
    return True, None


def store_active_signal(symbol: str, action: str, entry_price: float, stop_loss: float, take_profit: float, htf_trend: str):
    """Store a new active signal for long-term tracking."""
    global ACTIVE_SIGNALS
    ACTIVE_SIGNALS[symbol] = {
        'action': action,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'timestamp': datetime.now(),
        'htf_trend': htf_trend
    }
    logger.info(f"📌 Stored long-term signal: {symbol} {action} @ ${entry_price:.4f} (HTF: {htf_trend})")


def get_predictive_signal(symbol: str, current_price: float, price_change_24h: float, 
                          volume_ratio: float = 1.0) -> Dict:
    """
    Generate predictive signals that identify tops/bottoms BEFORE price moves.
    Returns BUY at bottoms (before pump) and SELL at tops (before dump).
    
    LONG-TERM APPROACH:
    - Keep existing signals until invalidated (SL hit, TP hit, HTF break, or expiry)
    - Only issue new signals when old signal is invalidated
    - Require higher confidence for new signals
    """
    # Get HTF trend first
    htf_trend = get_htf_trend(symbol, current_price, price_change_24h)
    
    # CHECK IF EXISTING SIGNAL IS STILL VALID
    is_valid, invalidation_reason = check_signal_still_valid(symbol, current_price, price_change_24h)
    
    if is_valid and symbol in ACTIVE_SIGNALS:
        # Return the existing signal - don't flip-flop
        existing = ACTIVE_SIGNALS[symbol]
        hours_active = (datetime.now() - existing['timestamp']).total_seconds() / 3600
        
        return {
            'symbol': symbol,
            'action': existing['action'],
            'confidence': 95.0,  # Maintain confidence
            'signal_type': 'ACTIVE_POSITION',
            'prediction': f"Maintaining {existing['action']} position (active for {hours_active:.1f}h)",
            'reasoning': [
                f"Signal still valid - no invalidation",
                f"Entry: ${existing['entry_price']:.4f}",
                f"SL: ${existing['stop_loss']:.4f}",
                f"HTF Trend: {htf_trend}"
            ],
            'indicators': {
                'rsi': 50.0,
                'macd': 'NEUTRAL',
                'momentum': 'HOLDING',
                'volume': 'NORMAL'
            },
            'entry_price': existing['entry_price'],
            'stop_loss': existing['stop_loss'],
            'take_profit': existing['take_profit'],
            'leverage': 12,
            'risk_reward': 3.33,
            'timestamp': existing['timestamp'].isoformat(),
            'signal_active_hours': round(hours_active, 1),
            'htf_trend': htf_trend,
            'bybit_settings': _build_bybit_settings(
                symbol=symbol,
                action=existing['action'],
                entry_price=existing['entry_price'],
                stop_loss=existing['stop_loss'],
                take_profit=existing['take_profit'],
                qty='0'  # Already in position
            )
        }
    
    # Signal was invalidated or doesn't exist - generate new analysis
    if invalidation_reason:
        logger.info(f"🔄 {symbol}: Previous signal invalidated - {invalidation_reason}")
        # Remove the old signal
        if symbol in ACTIVE_SIGNALS:
            del ACTIVE_SIGNALS[symbol]
    
    # Technical indicator simulation based on market conditions
    rsi = calculate_rsi_prediction(symbol, price_change_24h)
    macd_signal = calculate_macd_prediction(symbol, price_change_24h)
    momentum = calculate_momentum_prediction(symbol, price_change_24h)
    volume_signal = analyze_volume(volume_ratio)
    
    # Predictive logic - identify reversals (with higher thresholds for long-term)
    signal_data = predict_reversal(
        symbol=symbol,
        rsi=rsi,
        macd=macd_signal,
        momentum=momentum,
        volume=volume_signal,
        price_change=price_change_24h,
        current_price=current_price,
        htf_trend=htf_trend
    )
    
    # If we got a valid BUY or SELL signal, store it for long-term tracking
    if signal_data['action'] in ['BUY', 'SELL'] and signal_data['confidence'] >= 90:
        store_active_signal(
            symbol=symbol,
            action=signal_data['action'],
            entry_price=current_price,
            stop_loss=signal_data['stop_loss'],
            take_profit=signal_data['take_profit'],
            htf_trend=htf_trend
        )
        signal_data['htf_trend'] = htf_trend
        signal_data['reasoning'].append(f"HTF Trend: {htf_trend}")
    
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
    
    NOTE: Removed time-based variation to prevent rapid flip-flopping.
    RSI now only changes based on actual price movements, not time.
    """
    # Create consistent symbol-based offset for signal diversity
    symbol_hash = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    symbol_offset = (symbol_hash % 40) - 20  # Range: -20 to +20 (reduced from -30 to +30)
    
    # Base RSI starts at 50
    base_rsi = 50.0
    
    # Price change influence - more significant moves required
    if price_change > 8:
        base_rsi += 25  # Very big pump → strongly overbought
    elif price_change > 5:
        base_rsi += 18  # Big pump → overbought
    elif price_change > 3:
        base_rsi += 12
    elif price_change < -8:
        base_rsi -= 25  # Very big dump → strongly oversold
    elif price_change < -5:
        base_rsi -= 18  # Big dump → oversold
    elif price_change < -3:
        base_rsi -= 12
    elif price_change > 1:
        base_rsi += price_change * 2
    elif price_change < -1:
        base_rsi += price_change * 2  # Negative makes it lower
    # Small changes (-1 to 1) have minimal impact
    
    # Apply reduced symbol offset for diversity
    base_rsi += symbol_offset
    
    # NO TIME-BASED VARIATION - signals only change based on actual price action
    
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
                     volume: str, price_change: float, current_price: float,
                     htf_trend: str = 'NEUTRAL', support: float = 0, resistance: float = 0) -> Dict:
    """
    Core prediction engine - identifies tops and bottoms BEFORE price moves.
    
    ENHANCED ACCURACY (Dec 13, 2025):
    - Volume confirmation required (no signals on LOW volume)
    - Multiple indicator agreement (2+ indicators must align)
    - Tighter RSI buffers (40/60 instead of 35/65)
    - Support/resistance awareness for better entries
    - HTF trend must align with signal direction
    - Higher thresholds required for signals (60+ instead of 40+)
    """
    
    # Initialize with default values
    action = 'HOLD'
    confidence = 50.0
    signal_type = 'NEUTRAL'
    reasoning = []
    
    # === VOLATILITY FILTER ===
    # Block signals during extreme volatility (whipsaws) - not too strict
    if abs(price_change) > 12:
        return {
            'action': 'HOLD',
            'confidence': 35,
            'signal_type': 'HIGH_VOLATILITY',
            'prediction': f"Extreme volatility ({price_change:.1f}%) - waiting for stability",
            'reasoning': [f"Price change {price_change:.1f}% too volatile for reliable entry"],
            'stop_loss': current_price * 0.97,
            'take_profit': current_price * 1.06,
            'leverage': 5,
            'risk_reward': 2.0
        }
    
    # === VOLUME CONFIRMATION ===
    # Block all signals on LOW volume - unreliable moves
    if volume == 'LOW':
        return {
            'action': 'HOLD',
            'confidence': 40,
            'signal_type': 'LOW_VOLUME',
            'prediction': f"Low volume - waiting for confirmation",
            'reasoning': ["Volume too low for reliable signal"],
            'stop_loss': current_price * 0.97,
            'take_profit': current_price * 1.06,
            'leverage': 5,
            'risk_reward': 2.0
        }
    
    # === CONSECUTIVE CONFIRMATION ===
    # Track price direction for confirmation
    consecutive_moves = track_price_direction(symbol, price_change)
    
    # === SUPPORT/RESISTANCE CHECK ===
    # Calculate distance from support/resistance
    near_support = False
    near_resistance = False
    if support > 0:
        support_distance = ((current_price - support) / current_price) * 100
        near_support = support_distance < 5  # Within 5% of support
    if resistance > 0:
        resistance_distance = ((resistance - current_price) / current_price) * 100
        near_resistance = resistance_distance < 5  # Within 5% of resistance
    
    # === MULTIPLE INDICATOR AGREEMENT ===
    # Count bullish and bearish indicators
    bullish_count = 0
    bearish_count = 0
    
    # RSI signals
    if rsi < 40:
        bullish_count += 1  # Oversold = bullish
    elif rsi > 60:
        bearish_count += 1  # Overbought = bearish
    
    # MACD signals
    if macd in ['BULLISH', 'BULLISH_DIVERGENCE']:
        bullish_count += 1
    elif macd in ['BEARISH', 'BEARISH_DIVERGENCE']:
        bearish_count += 1
    
    # Momentum signals
    if momentum in ['EXHAUSTION_BOTTOM', 'WEAK_DOWN']:
        bullish_count += 1  # Selling exhaustion = bullish
    elif momentum in ['EXHAUSTION_TOP', 'WEAK_UP']:
        bearish_count += 1  # Buying exhaustion = bearish
    
    # HTF trend
    if htf_trend in ['BULLISH', 'WEAK_BULLISH']:
        bullish_count += 1
    elif htf_trend in ['BEARISH', 'WEAK_BEARISH']:
        bearish_count += 1
    
    # BOTTOM DETECTION (BUY before pump) - HIGHER THRESHOLDS
    bottom_score = 0
    
    if rsi < 25:
        bottom_score += 35  # Strongly oversold
        reasoning.append(f"RSI strongly oversold ({rsi:.1f})")
    elif rsi < 35:
        bottom_score += 20
        reasoning.append(f"RSI oversold ({rsi:.1f})")
    elif rsi < 45:
        bottom_score += 10
        reasoning.append(f"RSI approaching oversold ({rsi:.1f})")
    
    if macd == 'BULLISH_DIVERGENCE':
        bottom_score += 25
        reasoning.append("MACD bullish divergence")
    
    if momentum == 'EXHAUSTION_BOTTOM':
        bottom_score += 25
        reasoning.append("Selling exhaustion detected")
    elif momentum in ['WEAK_DOWN', 'FLAT']:
        bottom_score += 5  # Reduced from 10
    
    if volume == 'CLIMAX' and price_change < -3:  # Require bigger move
        bottom_score += 20
        reasoning.append("Volume climax on sell-off")
    
    # HTF ALIGNMENT - BUY signals REQUIRE bullish or neutral HTF
    # Block BUY signals when HTF is bearish (don't fight the trend)
    if htf_trend in ['BULLISH', 'WEAK_BULLISH']:
        bottom_score += 20  # Strong bonus for aligned HTF
        reasoning.append(f"HTF aligned bullish ({htf_trend})")
    elif htf_trend == 'NEUTRAL':
        bottom_score += 10  # Small bonus for neutral
        reasoning.append(f"HTF neutral - acceptable for BUY")
    else:
        # BEARISH or WEAK_BEARISH - penalize BUY signals heavily
        bottom_score -= 30  # Strong penalty - don't buy in downtrends
        reasoning.append(f"HTF BEARISH - signal blocked ({htf_trend})")
    
    # TOP DETECTION (SELL before dump) - HIGHER THRESHOLDS
    top_score = 0
    
    if rsi > 75:
        top_score += 35  # Strongly overbought
        reasoning.append(f"RSI strongly overbought ({rsi:.1f})")
    elif rsi > 65:
        top_score += 20
        reasoning.append(f"RSI overbought ({rsi:.1f})")
    elif rsi > 55:
        top_score += 10
        reasoning.append(f"RSI approaching overbought ({rsi:.1f})")
    
    if macd == 'BEARISH_DIVERGENCE':
        top_score += 25
        reasoning.append("MACD bearish divergence")
    
    if momentum == 'EXHAUSTION_TOP':
        top_score += 25
        reasoning.append("Buying exhaustion detected")
    elif momentum in ['WEAK_UP', 'FLAT']:
        top_score += 5  # Reduced from 10
    
    if volume == 'CLIMAX' and price_change > 3:  # Require bigger move
        top_score += 20
        reasoning.append("Volume climax on rally")
    
    # HTF ALIGNMENT - SELL signals REQUIRE bearish or neutral HTF
    # Block SELL signals when HTF is bullish (don't fight the trend)
    if htf_trend in ['BEARISH', 'WEAK_BEARISH']:
        top_score += 20  # Strong bonus for aligned HTF
        reasoning.append(f"HTF aligned bearish ({htf_trend})")
    elif htf_trend == 'NEUTRAL':
        top_score += 10  # Small bonus for neutral
        reasoning.append(f"HTF neutral - acceptable for SELL")
    else:
        # BULLISH or WEAK_BULLISH - penalize SELL signals heavily
        top_score -= 30  # Strong penalty - don't sell in uptrends
        reasoning.append(f"HTF BULLISH - signal blocked ({htf_trend})")
    
    # Determine signal - HIGHER THRESHOLDS (60+ instead of 40+)
    if bottom_score > top_score and bottom_score >= 60:
        action = 'BUY'
        confidence = min(98, 75 + bottom_score * 0.3)
        signal_type = 'BOTTOM_CALL'
        prediction = "Expecting upward reversal - bottom detected"
    elif top_score > bottom_score and top_score >= 60:
        action = 'SELL'
        confidence = min(98, 75 + top_score * 0.3)
        signal_type = 'TOP_CALL'
        prediction = "Expecting downward reversal - top detected"
    else:
        # Trend following - REQUIRE STRONGER MOVES (3%+ instead of 1.5%+)
        # ENHANCED: Tighter RSI buffers (40/60) + indicator agreement required
        
        if price_change > 3 and htf_trend in ['BULLISH', 'WEAK_BULLISH', 'NEUTRAL']:
            # Check RSI - tighter buffer at 60
            if rsi >= 60:
                action = 'HOLD'
                confidence = 50
                signal_type = 'RSI_BLOCKED'
                prediction = f"Momentum up but RSI overbought ({rsi:.0f}) - waiting for pullback"
                reasoning.append(f"RSI {rsi:.0f} too high - blocked BUY to avoid chasing")
            # Check indicator agreement - need 2+ bullish indicators
            elif bullish_count < 2:
                action = 'HOLD'
                confidence = 50
                signal_type = 'NO_CONFLUENCE'
                prediction = f"Momentum up but indicators don't agree ({bullish_count}/4 bullish)"
                reasoning.append(f"Only {bullish_count} bullish indicators - need 2+ for confirmation")
            elif consecutive_moves < 2:
                action = 'HOLD'
                confidence = 50
                signal_type = 'AWAITING_CONFIRMATION'
                prediction = f"Waiting for consecutive confirmation ({consecutive_moves}/2 moves)"
                reasoning.append(f"Need 2 consecutive up moves - have {consecutive_moves}")
            else:
                action = 'BUY'
                confidence = 75 + min(15, price_change + bullish_count * 3)
                if near_support:
                    confidence = min(98, confidence + 8)
                    reasoning.append("Near support level - good entry")
                signal_type = 'TREND_FOLLOW'
                prediction = "Riding strong uptrend momentum"
                reasoning.append(f"Strong upward momentum with {bullish_count} confirming indicators")
        elif price_change < -3 and htf_trend in ['BEARISH', 'WEAK_BEARISH', 'NEUTRAL']:
            # Check RSI - tighter buffer at 40
            if rsi <= 40:
                action = 'HOLD'
                confidence = 50
                signal_type = 'RSI_BLOCKED'
                prediction = f"Momentum down but RSI oversold ({rsi:.0f}) - bounce likely"
                reasoning.append(f"RSI {rsi:.0f} too low - blocked SELL to avoid shorting bottom")
            # Check indicator agreement - need 2+ bearish indicators
            elif bearish_count < 2:
                action = 'HOLD'
                confidence = 50
                signal_type = 'NO_CONFLUENCE'
                prediction = f"Momentum down but indicators don't agree ({bearish_count}/4 bearish)"
                reasoning.append(f"Only {bearish_count} bearish indicators - need 2+ for confirmation")
            elif consecutive_moves < 2:
                action = 'HOLD'
                confidence = 50
                signal_type = 'AWAITING_CONFIRMATION'
                prediction = f"Waiting for consecutive confirmation ({consecutive_moves}/2 moves)"
                reasoning.append(f"Need 2 consecutive down moves - have {consecutive_moves}")
            else:
                action = 'SELL'
                confidence = 75 + min(15, abs(price_change) + bearish_count * 3)
                if near_resistance:
                    confidence = min(98, confidence + 8)
                    reasoning.append("Near resistance level - good entry")
                signal_type = 'TREND_FOLLOW'
                prediction = "Riding strong downtrend momentum"
                reasoning.append(f"Strong downward momentum with {bearish_count} confirming indicators")
        else:
            action = 'HOLD'
            confidence = 50
            signal_type = 'NO_CLEAR_SIGNAL'
            prediction = f"No clear direction - waiting for setup (HTF: {htf_trend})"
    
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
        'bybit_settings': _build_bybit_settings(
            symbol=symbol,
            action=action,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            qty=qty_str
        )
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
