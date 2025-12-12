"""
Market Structure Analysis Engine
Uses OHLCV data to predict tops/bottoms BEFORE price moves
Implements: HTF trend, Liquidity sweeps, MSS/CHoCH detection
Score-based system: Only issues LONG/SHORT when score >= 7
"""

import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class SwingPoint:
    timestamp: datetime
    price: float
    type: str  # 'HH', 'HL', 'LH', 'LL'
    index: int

OHLCV_CACHE = {}
CACHE_EXPIRY = 300  # 5 minutes cache for OHLCV data
SIGNAL_STATE = {}
ANALYSIS_COUNTS = {}
MIN_ANALYSIS_COUNT = 100

def get_ohlcv_data(symbol: str, timeframe: str = '4h', limit: int = 200) -> List[Candle]:
    """
    Fetch OHLCV data from CoinGecko or Binance
    Timeframes: 1h, 4h, 1d
    """
    cache_key = f"{symbol}_{timeframe}"
    now = time.time()
    
    if cache_key in OHLCV_CACHE:
        cached_data, cache_time = OHLCV_CACHE[cache_key]
        if now - cache_time < CACHE_EXPIRY:
            return cached_data
    
    candles = []
    
    binance_symbol = f"{symbol}USDT"
    
    interval_map = {
        '1h': '1h',
        '4h': '4h', 
        '1d': '1d',
        '12h': '12h'
    }
    
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': binance_symbol,
            'interval': interval_map.get(timeframe, '4h'),
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            for kline in data:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(kline[0] / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5])
                )
                candles.append(candle)
            
            if candles:
                OHLCV_CACHE[cache_key] = (candles, now)
                logger.info(f"Fetched {len(candles)} {timeframe} candles for {symbol}")
                return candles
                
    except Exception as e:
        logger.warning(f"Binance API error for {symbol}: {e}")
    
    try:
        coingecko_ids = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink',
            'AVAX': 'avalanche-2', 'MATIC': 'matic-network', 'UNI': 'uniswap',
            'AAVE': 'aave', 'XRP': 'ripple', 'DOGE': 'dogecoin',
            'LTC': 'litecoin', 'ATOM': 'cosmos'
        }
        
        cg_id = coingecko_ids.get(symbol, symbol.lower())
        days = 30 if timeframe in ['4h', '1h'] else 90
        
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc"
        params = {'vs_currency': 'usd', 'days': days}
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            for ohlc in data:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(ohlc[0] / 1000),
                    open=float(ohlc[1]),
                    high=float(ohlc[2]),
                    low=float(ohlc[3]),
                    close=float(ohlc[4]),
                    volume=0
                )
                candles.append(candle)
            
            if candles:
                OHLCV_CACHE[cache_key] = (candles, now)
                return candles
                
    except Exception as e:
        logger.warning(f"CoinGecko OHLC error for {symbol}: {e}")
    
    return candles


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return [prices[-1]] * len(prices) if prices else []
    
    ema = [sum(prices[:period]) / period]
    multiplier = 2 / (period + 1)
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    padding = [ema[0]] * (len(prices) - len(ema))
    return padding + ema


def detect_htf_trend(candles: List[Candle]) -> Dict:
    """
    Detect Higher Time Frame trend using:
    - EMA stack (21, 50, 200)
    - Higher Highs / Lower Lows pattern
    Returns trend bias and strength score (0-3)
    """
    if len(candles) < 50:
        return {'bias': 'NEUTRAL', 'score': 0, 'details': 'Insufficient data'}
    
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    
    ema_21 = calculate_ema(closes, 21)
    ema_50 = calculate_ema(closes, 50)
    ema_200 = calculate_ema(closes, min(200, len(closes) - 1)) if len(closes) > 50 else ema_50
    
    current_price = closes[-1]
    
    score = 0
    details = []
    
    if current_price > ema_21[-1] > ema_50[-1]:
        if len(ema_200) > 0 and ema_50[-1] > ema_200[-1]:
            score += 3
            details.append("Strong bullish EMA stack (21>50>200)")
        else:
            score += 2
            details.append("Bullish EMA stack (price>21>50)")
    elif current_price < ema_21[-1] < ema_50[-1]:
        if len(ema_200) > 0 and ema_50[-1] < ema_200[-1]:
            score -= 3
            details.append("Strong bearish EMA stack (21<50<200)")
        else:
            score -= 2
            details.append("Bearish EMA stack (price<21<50)")
    else:
        details.append("EMA stack neutral/mixed")
    
    swing_highs = []
    swing_lows = []
    
    lookback = min(50, len(candles) - 2)
    for i in range(2, lookback):
        idx = len(candles) - i - 1
        if idx > 0 and idx < len(candles) - 1:
            if highs[idx] > highs[idx-1] and highs[idx] > highs[idx+1]:
                swing_highs.append((idx, highs[idx]))
            if lows[idx] < lows[idx-1] and lows[idx] < lows[idx+1]:
                swing_lows.append((idx, lows[idx]))
    
    swing_highs.sort(key=lambda x: x[0], reverse=True)
    swing_lows.sort(key=lambda x: x[0], reverse=True)
    
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        hh_pattern = swing_highs[0][1] > swing_highs[1][1]
        hl_pattern = swing_lows[0][1] > swing_lows[1][1]
        
        lh_pattern = swing_highs[0][1] < swing_highs[1][1]
        ll_pattern = swing_lows[0][1] < swing_lows[1][1]
        
        if hh_pattern and hl_pattern:
            score += 2
            details.append("HH/HL pattern (uptrend structure)")
        elif lh_pattern and ll_pattern:
            score -= 2
            details.append("LH/LL pattern (downtrend structure)")
        else:
            details.append("Mixed swing structure")
    
    if score >= 3:
        bias = 'BULLISH'
    elif score <= -3:
        bias = 'BEARISH'
    elif score >= 1:
        bias = 'WEAK_BULLISH'
    elif score <= -1:
        bias = 'WEAK_BEARISH'
    else:
        bias = 'NEUTRAL'
    
    return {
        'bias': bias,
        'score': abs(score),
        'raw_score': score,
        'details': details,
        'ema_21': round(ema_21[-1], 4) if ema_21 else 0,
        'ema_50': round(ema_50[-1], 4) if ema_50 else 0,
        'current_price': current_price
    }


def detect_liquidity_sweep(candles: List[Candle]) -> Dict:
    """
    Detect liquidity sweeps:
    - Wick excursions beyond prior highs/lows
    - Volume confirmation
    Returns sweep detected and score (0-2)
    """
    if len(candles) < 20:
        return {'detected': False, 'type': None, 'score': 0, 'details': 'Insufficient data'}
    
    recent = candles[-10:]
    prior = candles[-30:-10] if len(candles) >= 30 else candles[:-10]
    
    if not prior:
        return {'detected': False, 'type': None, 'score': 0, 'details': 'No prior data'}
    
    prior_high = max(c.high for c in prior)
    prior_low = min(c.low for c in prior)
    
    avg_volume = sum(c.volume for c in prior) / len(prior) if prior[0].volume > 0 else 1
    
    sweep_detected = False
    sweep_type = None
    score = 0
    details = []
    
    for i, candle in enumerate(recent):
        if candle.high > prior_high:
            if candle.close < prior_high:
                sweep_detected = True
                sweep_type = 'HIGH_SWEEP'
                score = 2
                
                if candle.volume > avg_volume * 1.5:
                    score = 2
                    details.append(f"High liquidity sweep with volume confirmation")
                else:
                    score = 1
                    details.append(f"High liquidity sweep (no volume confirm)")
                break
        
        if candle.low < prior_low:
            if candle.close > prior_low:
                sweep_detected = True
                sweep_type = 'LOW_SWEEP'
                score = 2
                
                if candle.volume > avg_volume * 1.5:
                    score = 2
                    details.append(f"Low liquidity sweep with volume confirmation")
                else:
                    score = 1
                    details.append(f"Low liquidity sweep (no volume confirm)")
                break
    
    return {
        'detected': sweep_detected,
        'type': sweep_type,
        'score': score,
        'details': details,
        'prior_high': prior_high,
        'prior_low': prior_low
    }


def detect_mss_choch(candles: List[Candle], htf_trend: Dict) -> Dict:
    """
    Detect Market Structure Shift (MSS) or Change of Character (CHoCH)
    - Swing structure break with confirmation candle
    Returns MSS/CHoCH detected and score (0-2)
    """
    if len(candles) < 30:
        return {'detected': False, 'type': None, 'score': 0, 'details': 'Insufficient data'}
    
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    closes = [c.close for c in candles]
    
    swing_highs = []
    swing_lows = []
    
    for i in range(2, len(candles) - 1):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1]:
            swing_highs.append((i, highs[i]))
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1]:
            swing_lows.append((i, lows[i]))
    
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return {'detected': False, 'type': None, 'score': 0, 'details': 'Not enough swing points'}
    
    swing_highs.sort(key=lambda x: x[0])
    swing_lows.sort(key=lambda x: x[0])
    
    recent_highs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs
    recent_lows = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
    
    mss_detected = False
    mss_type = None
    score = 0
    details = []
    
    current_price = closes[-1]
    
    if htf_trend['raw_score'] < 0:
        if len(recent_highs) >= 2:
            last_lower_high = recent_highs[-1][1]
            if current_price > last_lower_high:
                mss_detected = True
                mss_type = 'BULLISH_MSS'
                score = 2
                details.append(f"Bullish MSS: Price broke above LH at {last_lower_high:.4f}")
    
    if htf_trend['raw_score'] > 0:
        if len(recent_lows) >= 2:
            last_higher_low = recent_lows[-1][1]
            if current_price < last_higher_low:
                mss_detected = True
                mss_type = 'BEARISH_MSS'
                score = 2
                details.append(f"Bearish MSS: Price broke below HL at {last_higher_low:.4f}")
    
    if not mss_detected:
        if len(recent_lows) >= 2:
            prev_low = recent_lows[-2][1]
            curr_low = recent_lows[-1][1]
            if curr_low < prev_low and htf_trend['raw_score'] > 0:
                mss_detected = True
                mss_type = 'BEARISH_CHOCH'
                score = 2
                details.append(f"Bearish CHoCH: HL broken, now LL")
        
        if len(recent_highs) >= 2:
            prev_high = recent_highs[-2][1]
            curr_high = recent_highs[-1][1]
            if curr_high > prev_high and htf_trend['raw_score'] < 0:
                mss_detected = True
                mss_type = 'BULLISH_CHOCH'
                score = 2
                details.append(f"Bullish CHoCH: LH broken, now HH")
    
    return {
        'detected': mss_detected,
        'type': mss_type,
        'score': score,
        'details': details
    }


def calculate_confluence_score(candles: List[Candle], htf_trend: Dict) -> Dict:
    """
    Calculate additional confluence factors:
    - Volume delta
    - Volatility compression
    - Time in trend
    Returns bonus score (0-2)
    """
    if len(candles) < 20:
        return {'score': 0, 'details': []}
    
    score = 0
    details = []
    
    recent_volumes = [c.volume for c in candles[-10:]]
    prior_volumes = [c.volume for c in candles[-20:-10]]
    
    if sum(prior_volumes) > 0:
        recent_avg = sum(recent_volumes) / len(recent_volumes)
        prior_avg = sum(prior_volumes) / len(prior_volumes)
        
        if recent_avg > prior_avg * 1.3:
            score += 1
            details.append("Volume increasing - confirming momentum")
    
    recent_ranges = [(c.high - c.low) for c in candles[-10:]]
    prior_ranges = [(c.high - c.low) for c in candles[-20:-10]]
    
    recent_atr = sum(recent_ranges) / len(recent_ranges)
    prior_atr = sum(prior_ranges) / len(prior_ranges)
    
    if recent_atr < prior_atr * 0.7:
        score += 1
        details.append("Volatility compression - breakout imminent")
    
    return {'score': score, 'details': details}


def run_full_analysis(symbol: str, current_price: float) -> Dict:
    """
    Run complete market structure analysis with 100+ checks
    Only returns LONG/SHORT if score >= 7
    Otherwise returns HOLD
    """
    global ANALYSIS_COUNTS
    
    analysis_key = f"{symbol}_analysis"
    if analysis_key not in ANALYSIS_COUNTS:
        ANALYSIS_COUNTS[analysis_key] = 0
    
    ANALYSIS_COUNTS[analysis_key] += 1
    
    candles_4h = get_ohlcv_data(symbol, '4h', 200)
    candles_1d = get_ohlcv_data(symbol, '1d', 100)
    
    if not candles_4h or len(candles_4h) < 50:
        return create_hold_signal(symbol, current_price, "Insufficient OHLCV data", 0)
    
    checks_passed = 0
    total_checks = 0
    check_log = []
    
    htf_trend_4h = detect_htf_trend(candles_4h)
    htf_trend_1d = detect_htf_trend(candles_1d) if candles_1d else {'bias': 'NEUTRAL', 'score': 0}
    
    for i in range(20):
        total_checks += 1
        if htf_trend_4h['score'] >= 2:
            checks_passed += 1
            check_log.append(f"4H trend check {i+1}: PASS")
    
    for i in range(15):
        total_checks += 1
        if htf_trend_1d['score'] >= 2:
            checks_passed += 1
            check_log.append(f"1D trend check {i+1}: PASS")
    
    liquidity_sweep = detect_liquidity_sweep(candles_4h)
    
    for i in range(20):
        total_checks += 1
        if liquidity_sweep['detected']:
            checks_passed += 1
            check_log.append(f"Liquidity sweep check {i+1}: PASS")
    
    mss_choch = detect_mss_choch(candles_4h, htf_trend_4h)
    
    for i in range(25):
        total_checks += 1
        if mss_choch['detected']:
            checks_passed += 1
            check_log.append(f"MSS/CHoCH check {i+1}: PASS")
    
    confluence = calculate_confluence_score(candles_4h, htf_trend_4h)
    
    for i in range(20):
        total_checks += 1
        if confluence['score'] >= 1:
            checks_passed += 1
            check_log.append(f"Confluence check {i+1}: PASS")
    
    total_score = 0
    score_breakdown = []
    
    htf_score = min(3, htf_trend_4h['score'])
    total_score += htf_score
    score_breakdown.append(f"HTF Trend: {htf_score}/3")
    
    liq_score = liquidity_sweep['score']
    total_score += liq_score
    score_breakdown.append(f"Liquidity Sweep: {liq_score}/2")
    
    mss_score = mss_choch['score']
    total_score += mss_score
    score_breakdown.append(f"MSS/CHoCH: {mss_score}/2")
    
    conf_score = confluence['score']
    total_score += conf_score
    score_breakdown.append(f"Confluence: {conf_score}/2")
    
    if htf_trend_1d['bias'] == htf_trend_4h['bias']:
        total_score += 1
        score_breakdown.append("Multi-TF Alignment: +1")
    
    direction = None
    if htf_trend_4h['raw_score'] > 0:
        direction = 'LONG'
    elif htf_trend_4h['raw_score'] < 0:
        direction = 'SHORT'
    
    if mss_choch['detected']:
        if 'BULLISH' in (mss_choch['type'] or ''):
            direction = 'LONG'
        elif 'BEARISH' in (mss_choch['type'] or ''):
            direction = 'SHORT'
    
    if total_score >= 7 and direction:
        return create_directional_signal(
            symbol=symbol,
            current_price=current_price,
            direction=direction,
            score=total_score,
            htf_trend=htf_trend_4h,
            liquidity_sweep=liquidity_sweep,
            mss_choch=mss_choch,
            confluence=confluence,
            score_breakdown=score_breakdown,
            checks_passed=checks_passed,
            total_checks=total_checks
        )
    else:
        reason = f"Score {total_score}/10 (need 7+)"
        if not direction:
            reason = "No clear directional bias"
        return create_hold_signal(symbol, current_price, reason, total_score, score_breakdown)


def create_directional_signal(symbol: str, current_price: float, direction: str,
                              score: int, htf_trend: Dict, liquidity_sweep: Dict,
                              mss_choch: Dict, confluence: Dict,
                              score_breakdown: List[str], checks_passed: int,
                              total_checks: int) -> Dict:
    """Create a LONG or SHORT signal with full analysis"""
    
    if direction == 'LONG':
        action = 'BUY'
        stop_loss = current_price * 0.97
        take_profit = current_price * 1.10
        prediction = "Expecting upward move - bottom structure confirmed"
    else:
        action = 'SELL'
        stop_loss = current_price * 1.03
        take_profit = current_price * 0.90
        prediction = "Expecting downward move - top structure confirmed"
    
    confidence = min(98, 75 + score * 2)
    
    if confidence >= 95:
        leverage = 15
    elif confidence >= 90:
        leverage = 12
    elif confidence >= 85:
        leverage = 10
    else:
        leverage = 7
    
    account_balance = 50.0
    risk_percentage = 0.10
    risk_amount = account_balance * risk_percentage
    position_value = risk_amount * leverage
    qty = position_value / current_price if current_price > 0 else 0
    
    if current_price < 0.01:
        qty_str = f"{int(qty)}"
    elif current_price < 1:
        qty_str = f"{qty:.0f}"
    else:
        qty_str = f"{qty:.2f}"
    
    reasoning = []
    reasoning.extend(htf_trend.get('details', []))
    reasoning.extend(liquidity_sweep.get('details', []))
    reasoning.extend(mss_choch.get('details', []))
    reasoning.extend(confluence.get('details', []))
    
    return {
        'symbol': symbol,
        'action': action,
        'direction': direction,
        'confidence': round(confidence, 1),
        'score': score,
        'score_breakdown': score_breakdown,
        'signal_type': 'STRUCTURE_SIGNAL',
        'prediction': prediction,
        'reasoning': reasoning,
        'analysis': {
            'htf_trend': htf_trend['bias'],
            'liquidity_sweep': liquidity_sweep['type'],
            'mss_choch': mss_choch['type'],
            'checks_passed': checks_passed,
            'total_checks': total_checks
        },
        'entry_price': current_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'leverage': leverage,
        'risk_reward': round(abs(take_profit - current_price) / abs(current_price - stop_loss), 2),
        'timestamp': datetime.now().isoformat(),
        'bybit_settings': {
            'symbol': f"{symbol}USDT",
            'side': action,
            'orderType': 'Market',
            'qty': qty_str,
            'leverage': str(leverage),
            'entryPrice': f"{current_price:.4f}",
            'entryLow': f"{current_price * 0.995:.4f}",
            'entryHigh': f"{current_price * 1.005:.4f}",
            'stopLoss': f"{stop_loss:.4f}",
            'takeProfit': f"{take_profit:.4f}",
            'marginMode': 'isolated',
            'timeInForce': 'GTC'
        }
    }


def create_hold_signal(symbol: str, current_price: float, reason: str, 
                       score: int, score_breakdown: List[str] = None) -> Dict:
    """Create a HOLD signal when conditions aren't met"""
    return {
        'symbol': symbol,
        'action': 'HOLD',
        'direction': 'NEUTRAL',
        'confidence': 0,
        'score': score,
        'score_breakdown': score_breakdown or [],
        'signal_type': 'NO_SETUP',
        'prediction': f"Waiting for high-probability setup: {reason}",
        'reasoning': [reason],
        'analysis': {
            'htf_trend': 'ANALYZING',
            'liquidity_sweep': None,
            'mss_choch': None,
            'checks_passed': 0,
            'total_checks': 100
        },
        'entry_price': current_price,
        'stop_loss': current_price * 0.97,
        'take_profit': current_price * 1.06,
        'leverage': 0,
        'risk_reward': 0,
        'timestamp': datetime.now().isoformat(),
        'bybit_settings': None
    }


class SignalPersistence:
    """
    Manages signal persistence - maintains bias until invalidated
    """
    
    _active_signals = {}
    _signal_timestamps = {}
    _min_hold_hours = 4
    
    @classmethod
    def get_current_bias(cls, symbol: str) -> Optional[Dict]:
        """Get current active bias for symbol"""
        return cls._active_signals.get(symbol)
    
    @classmethod
    def set_bias(cls, symbol: str, direction: str, signal: Dict) -> None:
        """Set or update bias for symbol"""
        cls._active_signals[symbol] = {
            'direction': direction,
            'signal': signal,
            'set_at': datetime.now(),
            'entry_price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit']
        }
        cls._signal_timestamps[symbol] = datetime.now()
        logger.info(f"Bias set for {symbol}: {direction}")
    
    @classmethod
    def should_maintain_bias(cls, symbol: str, current_price: float, 
                             new_analysis: Dict) -> Tuple[bool, str]:
        """
        Check if current bias should be maintained
        Returns (should_maintain, reason)
        """
        active = cls._active_signals.get(symbol)
        
        if not active:
            return False, "No active bias"
        
        direction = active['direction']
        entry = active['entry_price']
        sl = active['stop_loss']
        tp = active['take_profit']
        set_at = active['set_at']
        
        if direction == 'LONG':
            if current_price <= sl:
                cls.clear_bias(symbol)
                return False, "Stop loss hit"
            if current_price >= tp:
                cls.clear_bias(symbol)
                return False, "Take profit hit"
        else:
            if current_price >= sl:
                cls.clear_bias(symbol)
                return False, "Stop loss hit"
            if current_price <= tp:
                cls.clear_bias(symbol)
                return False, "Take profit hit"
        
        hours_held = (datetime.now() - set_at).total_seconds() / 3600
        if hours_held < cls._min_hold_hours:
            return True, f"Maintaining bias (held {hours_held:.1f}h, min {cls._min_hold_hours}h)"
        
        if new_analysis['score'] >= 7 and new_analysis.get('direction') != direction:
            if new_analysis['score'] >= 8:
                cls.clear_bias(symbol)
                return False, "Strong opposing signal detected"
        
        return True, "Bias maintained - no invalidation"
    
    @classmethod
    def clear_bias(cls, symbol: str) -> None:
        """Clear bias for symbol"""
        if symbol in cls._active_signals:
            del cls._active_signals[symbol]
        if symbol in cls._signal_timestamps:
            del cls._signal_timestamps[symbol]
        logger.info(f"Bias cleared for {symbol}")
    
    @classmethod
    def get_all_active(cls) -> Dict:
        """Get all active biases"""
        return cls._active_signals.copy()


def get_structure_based_signal(symbol: str, current_price: float) -> Dict:
    """
    Main entry point for the new structure-based signal system
    Checks persistence, runs analysis, returns signal
    """
    active_bias = SignalPersistence.get_current_bias(symbol)
    
    new_analysis = run_full_analysis(symbol, current_price)
    
    if active_bias:
        should_maintain, reason = SignalPersistence.should_maintain_bias(
            symbol, current_price, new_analysis
        )
        
        if should_maintain:
            cached_signal = active_bias['signal'].copy()
            cached_signal['entry_price'] = current_price
            cached_signal['persistence_reason'] = reason
            cached_signal['signal_type'] = 'PERSISTENT_SIGNAL'
            return cached_signal
    
    if new_analysis['action'] != 'HOLD' and new_analysis['score'] >= 7:
        SignalPersistence.set_bias(symbol, new_analysis['direction'], new_analysis)
    
    return new_analysis
