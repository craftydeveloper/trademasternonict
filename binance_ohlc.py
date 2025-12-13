"""
Real OHLC Data Fetcher - Real candlestick data for accurate technical analysis
Uses CryptoCompare's free OHLC API (works globally, no restrictions)
Fallback to Bybit public API if needed
"""
import logging
import time
import requests
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading

logger = logging.getLogger(__name__)

CRYPTOCOMPARE_API_BASE = "https://min-api.cryptocompare.com/data/v2"
BYBIT_API_BASE = "https://api.bybit.com/v5/market"
BINANCE_US_API_BASE = "https://api.binance.us/api/v3"
KUCOIN_API_BASE = "https://api.kucoin.com/api/v1"

CACHE_DURATION = {
    '15m': 600,    # 10 min cache for 15m candles (increased for stability)
    '1h': 1800,    # 30 min cache for 1h candles
    '4h': 3600,    # 1 hour cache for 4h candles
    '1d': 7200,    # 2 hour cache for daily candles
    '1w': 14400,   # 4 hour cache for weekly candles
}

_last_api_call = {'time': 0}
_api_call_lock = threading.Lock()
API_RATE_LIMIT_MS = 200

CACHE_BACKUP_DIR = '/tmp/ohlc_cache'

def _ensure_cache_dir():
    """Ensure cache backup directory exists"""
    if not os.path.exists(CACHE_BACKUP_DIR):
        os.makedirs(CACHE_BACKUP_DIR, exist_ok=True)


def _save_cache_backup(cache_key: str, ohlc_data: List[Dict]):
    """Save OHLC data to disk as backup"""
    try:
        _ensure_cache_dir()
        filepath = os.path.join(CACHE_BACKUP_DIR, f"{cache_key}.json")
        serializable_data = []
        for candle in ohlc_data:
            item = {}
            for k, v in candle.items():
                if isinstance(v, datetime):
                    item[k] = v.isoformat()
                else:
                    item[k] = v
            serializable_data.append(item)
        with open(filepath, 'w') as f:
            json.dump({'timestamp': time.time(), 'data': serializable_data}, f)
    except Exception as e:
        logger.debug(f"Could not save cache backup for {cache_key}: {e}")


def _load_cache_backup(cache_key: str) -> Optional[List[Dict]]:
    """Load OHLC data from disk backup"""
    try:
        filepath = os.path.join(CACHE_BACKUP_DIR, f"{cache_key}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            saved = json.load(f)
        if time.time() - saved.get('timestamp', 0) > 86400:
            return None
        data = saved.get('data', [])
        parsed = []
        for candle in data:
            item = {}
            for k, v in candle.items():
                if k in ('open_time', 'close_time') and isinstance(v, str):
                    item[k] = datetime.fromisoformat(v)
                else:
                    item[k] = v
            parsed.append(item)
        return parsed if parsed else None
    except Exception as e:
        logger.debug(f"Could not load cache backup for {cache_key}: {e}")
        return None


CRYPTOCOMPARE_TF_MAP = {
    '15m': ('histominute', 15),
    '1h': ('histohour', 1),
    '4h': ('histohour', 4),
    '1d': ('histoday', 1),
    '1w': ('histoday', 7),
}

_ohlc_cache = {}
_cache_lock = threading.Lock()


def fetch_cryptocompare_ohlc(symbol: str, timeframe: str, limit: int = 50) -> Optional[List[Dict]]:
    """
    Fetch OHLC data from CryptoCompare (works globally, no geo-restrictions).
    """
    try:
        symbol = symbol.upper().strip()
        
        if timeframe not in CRYPTOCOMPARE_TF_MAP:
            logger.warning(f"Unknown timeframe: {timeframe}")
            return None
        
        endpoint, aggregation = CRYPTOCOMPARE_TF_MAP[timeframe]
        
        url = f"{CRYPTOCOMPARE_API_BASE}/{endpoint}"
        params = {
            'fsym': symbol,
            'tsym': 'USDT',
            'limit': limit,
            'aggregate': aggregation
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'Success' and data.get('Data', {}).get('Data'):
                ohlc_data = data['Data']['Data']
                parsed = []
                for candle in ohlc_data:
                    if candle.get('close', 0) > 0:
                        parsed.append({
                            'open_time': datetime.fromtimestamp(candle['time']),
                            'open': float(candle['open']),
                            'high': float(candle['high']),
                            'low': float(candle['low']),
                            'close': float(candle['close']),
                            'volume': float(candle.get('volumefrom', 0)),
                            'close_time': datetime.fromtimestamp(candle['time']),
                            'quote_volume': float(candle.get('volumeto', 0)),
                            'trades': 0
                        })
                if parsed:
                    logger.debug(f"✅ CryptoCompare: Got {len(parsed)} candles for {symbol} {timeframe}")
                    return parsed
        
        logger.warning(f"CryptoCompare returned no data for {symbol}")
        return None
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {symbol} {timeframe} from CryptoCompare")
        return None
    except Exception as e:
        logger.error(f"Error fetching OHLC for {symbol}: {e}")
        return None


def fetch_binance_us_ohlc(symbol: str, timeframe: str, limit: int = 50) -> Optional[List[Dict]]:
    """
    Primary: Fetch OHLC data from Binance.US API (works globally, not geo-blocked).
    Prices closely match Bybit for major pairs.
    """
    try:
        symbol = symbol.upper().strip()
        binance_symbol = f"{symbol}USDT"
        
        tf_map = {
            '15m': '15m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w',
        }
        
        if timeframe not in tf_map:
            return None
        
        url = f"{BINANCE_US_API_BASE}/klines"
        params = {
            'symbol': binance_symbol,
            'interval': tf_map[timeframe],
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            klines = response.json()
            if isinstance(klines, list) and len(klines) > 0:
                parsed = []
                for k in klines:
                    parsed.append({
                        'open_time': datetime.fromtimestamp(int(k[0]) / 1000),
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5]),
                        'close_time': datetime.fromtimestamp(int(k[6]) / 1000),
                        'quote_volume': float(k[7]),
                        'trades': int(k[8])
                    })
                if parsed:
                    logger.info(f"✅ Binance.US OHLC: {len(parsed)} candles for {symbol} {timeframe}")
                    return parsed
        else:
            logger.debug(f"Binance.US API HTTP {response.status_code} for {binance_symbol}")
        
        return None
        
    except requests.exceptions.Timeout:
        logger.warning(f"Binance.US timeout for {symbol} {timeframe}")
        return None
    except Exception as e:
        logger.warning(f"Binance.US OHLC failed for {symbol}: {e}")
        return None


def fetch_kucoin_ohlc(symbol: str, timeframe: str, limit: int = 50) -> Optional[List[Dict]]:
    """
    Secondary: Fetch OHLC data from KuCoin API (works globally).
    """
    try:
        symbol = symbol.upper().strip()
        kucoin_symbol = f"{symbol}-USDT"
        
        tf_map = {
            '15m': '15min',
            '1h': '1hour',
            '4h': '4hour',
            '1d': '1day',
            '1w': '1week',
        }
        
        if timeframe not in tf_map:
            return None
        
        end_time = int(time.time())
        hours_back = {'15m': 12, '1h': 50, '4h': 200, '1d': 50, '1w': 350}
        start_time = end_time - (hours_back.get(timeframe, 50) * 3600)
        
        url = f"{KUCOIN_API_BASE}/market/candles"
        params = {
            'type': tf_map[timeframe],
            'symbol': kucoin_symbol,
            'startAt': start_time,
            'endAt': end_time
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '200000' and data.get('data'):
                klines = data['data']
                parsed = []
                for k in reversed(klines):
                    parsed.append({
                        'open_time': datetime.fromtimestamp(int(k[0])),
                        'open': float(k[1]),
                        'high': float(k[3]),
                        'low': float(k[4]),
                        'close': float(k[2]),
                        'volume': float(k[5]),
                        'close_time': datetime.fromtimestamp(int(k[0])),
                        'quote_volume': float(k[6]) if len(k) > 6 else 0,
                        'trades': 0
                    })
                if parsed:
                    logger.info(f"✅ KuCoin OHLC: {len(parsed)} candles for {symbol} {timeframe}")
                    return parsed
        else:
            logger.debug(f"KuCoin API HTTP {response.status_code} for {kucoin_symbol}")
        
        return None
        
    except requests.exceptions.Timeout:
        logger.warning(f"KuCoin timeout for {symbol} {timeframe}")
        return None
    except Exception as e:
        logger.warning(f"KuCoin OHLC failed for {symbol}: {e}")
        return None


def fetch_bybit_ohlc(symbol: str, timeframe: str, limit: int = 50) -> Optional[List[Dict]]:
    """
    Fallback: Fetch OHLC data from Bybit public API (may be geo-blocked).
    """
    try:
        symbol = symbol.upper().strip()
        bybit_symbol = f"{symbol}USDT"
        
        tf_map = {
            '15m': '15',
            '1h': '60',
            '4h': '240',
            '1d': 'D',
            '1w': 'W',
        }
        
        if timeframe not in tf_map:
            logger.debug(f"Bybit: Unknown timeframe {timeframe}")
            return None
        
        url = f"{BYBIT_API_BASE}/kline"
        params = {
            'category': 'linear',
            'symbol': bybit_symbol,
            'interval': tf_map[timeframe],
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                klines = data['result']['list']
                parsed = []
                for k in reversed(klines):
                    parsed.append({
                        'open_time': datetime.fromtimestamp(int(k[0]) / 1000),
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5]),
                        'close_time': datetime.fromtimestamp(int(k[0]) / 1000),
                        'quote_volume': float(k[6]) if len(k) > 6 else 0,
                        'trades': 0
                    })
                if parsed:
                    logger.info(f"✅ Bybit OHLC: {len(parsed)} candles for {symbol} {timeframe}")
                    return parsed
            else:
                logger.debug(f"Bybit API returned retCode={data.get('retCode')} for {bybit_symbol}")
        else:
            logger.debug(f"Bybit API HTTP {response.status_code} for {bybit_symbol}")
        
        return None
        
    except requests.exceptions.Timeout:
        logger.warning(f"Bybit timeout for {symbol} {timeframe}")
        return None
    except Exception as e:
        logger.warning(f"Bybit OHLC failed for {symbol}: {e}")
        return None


def _rate_limit_wait():
    """Ensure we don't exceed API rate limits"""
    with _api_call_lock:
        now = time.time() * 1000
        elapsed = now - _last_api_call['time']
        if elapsed < API_RATE_LIMIT_MS:
            time.sleep((API_RATE_LIMIT_MS - elapsed) / 1000)
        _last_api_call['time'] = time.time() * 1000


def get_cached_ohlc(symbol: str, interval: str, limit: int = 50) -> Optional[List[Dict]]:
    """Get OHLC data with caching to prevent rate limiting.
    Priority: Binance (most reliable) > CryptoCompare > Bybit > Cache backup.
    Note: Bybit API is often geo-blocked, so we use Binance as primary."""
    cache_key = f"{symbol}_{interval}"
    cache_duration = CACHE_DURATION.get(interval, 600)
    
    with _cache_lock:
        if cache_key in _ohlc_cache:
            cached = _ohlc_cache[cache_key]
            if time.time() - cached['timestamp'] < cache_duration:
                return cached['data']
            if time.time() - cached['timestamp'] < cache_duration * 3:
                expired_data = cached['data']
            else:
                expired_data = None
        else:
            expired_data = None
    
    _rate_limit_wait()
    
    ohlc = fetch_binance_us_ohlc(symbol, interval, limit)
    
    if not ohlc or len(ohlc) < 10:
        _rate_limit_wait()
        ohlc = fetch_kucoin_ohlc(symbol, interval, limit)
    
    if not ohlc or len(ohlc) < 10:
        _rate_limit_wait()
        ohlc = fetch_cryptocompare_ohlc(symbol, interval, limit)
    
    if ohlc and len(ohlc) >= 10:
        with _cache_lock:
            _ohlc_cache[cache_key] = {
                'data': ohlc,
                'timestamp': time.time()
            }
        _save_cache_backup(cache_key, ohlc)
        return ohlc
    
    if expired_data:
        logger.info(f"Using expired cache for {symbol} {interval}")
        return expired_data
    
    backup = _load_cache_backup(cache_key)
    if backup:
        logger.info(f"Using backup cache for {symbol} {interval}")
        return backup
    
    return None


def calculate_rsi_from_closes(closes: List[float], period: int = 14) -> float:
    """
    Calculate RSI using actual closing prices.
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss
    """
    if len(closes) < period + 1:
        return 50.0
    
    changes = []
    for i in range(1, len(closes)):
        changes.append(closes[i] - closes[i-1])
    
    if len(changes) < period:
        return 50.0
    
    gains = []
    losses = []
    for change in changes[-period:]:
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_macd_from_closes(closes: List[float]) -> Dict:
    """
    Calculate MACD using actual closing prices.
    MACD Line = 12-period EMA - 26-period EMA
    Signal Line = 9-period EMA of MACD Line
    """
    if len(closes) < 26:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'NEUTRAL'}
    
    def ema(data: List[float], period: int) -> List[float]:
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        for price in data[1:]:
            ema_values.append((price * multiplier) + (ema_values[-1] * (1 - multiplier)))
        return ema_values
    
    ema_12 = ema(closes, 12)
    ema_26 = ema(closes, 26)
    
    macd_line = []
    for i in range(len(ema_26)):
        macd_line.append(ema_12[i + len(closes) - len(ema_26)] - ema_26[i])
    
    if len(macd_line) >= 9:
        signal_line = ema(macd_line, 9)
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        histogram = current_macd - current_signal
    else:
        current_macd = macd_line[-1] if macd_line else 0
        current_signal = 0
        histogram = 0
    
    if histogram > 0 and current_macd > 0:
        trend = 'BULLISH'
    elif histogram < 0 and current_macd < 0:
        trend = 'BEARISH'
    elif histogram > 0:
        trend = 'WEAKLY_BULLISH'
    elif histogram < 0:
        trend = 'WEAKLY_BEARISH'
    else:
        trend = 'NEUTRAL'
    
    return {
        'macd': round(current_macd, 6),
        'signal': round(current_signal, 6),
        'histogram': round(histogram, 6),
        'trend': trend
    }


def get_support_resistance(ohlc_data: List[Dict], lookback: int = 20) -> Dict:
    """Calculate support and resistance levels from actual price data"""
    if not ohlc_data or len(ohlc_data) < lookback:
        return {'support': 0, 'resistance': 0}
    
    recent = ohlc_data[-lookback:]
    
    highs = [c['high'] for c in recent]
    lows = [c['low'] for c in recent]
    
    resistance = max(highs)
    support = min(lows)
    
    avg_high = sum(highs) / len(highs)
    avg_low = sum(lows) / len(lows)
    
    return {
        'support': round(support, 6),
        'resistance': round(resistance, 6),
        'avg_support': round(avg_low, 6),
        'avg_resistance': round(avg_high, 6)
    }


def get_real_timeframe_rsi(symbol: str) -> Dict:
    """
    Get REAL RSI values for all timeframes using actual OHLC data.
    Returns RSI for 15m, 1h, 4h, 1d, 1w timeframes.
    """
    result = {}
    timeframes = ['15m', '1h', '4h', '1d', '1w']
    
    for tf in timeframes:
        ohlc = get_cached_ohlc(symbol, tf, limit=50)
        if ohlc and len(ohlc) >= 15:
            closes = [c['close'] for c in ohlc]
            rsi = calculate_rsi_from_closes(closes, period=14)
            result[tf] = rsi
        else:
            result[tf] = 50.0
    
    return result


def get_real_macd(symbol: str, timeframe: str = '1h') -> Dict:
    """Get REAL MACD using actual OHLC data"""
    ohlc = get_cached_ohlc(symbol, timeframe, limit=50)
    if ohlc and len(ohlc) >= 26:
        closes = [c['close'] for c in ohlc]
        return calculate_macd_from_closes(closes)
    return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'NEUTRAL'}


def get_real_support_resistance(symbol: str, timeframe: str = '4h') -> Dict:
    """Get REAL support/resistance from actual price data"""
    ohlc = get_cached_ohlc(symbol, timeframe, limit=30)
    if ohlc:
        return get_support_resistance(ohlc)
    return {'support': 0, 'resistance': 0, 'avg_support': 0, 'avg_resistance': 0}


def get_price_momentum(symbol: str, timeframe: str = '1h') -> Dict:
    """Calculate price momentum from real OHLC data"""
    ohlc = get_cached_ohlc(symbol, timeframe, limit=20)
    if not ohlc or len(ohlc) < 10:
        return {'momentum': 'NEUTRAL', 'strength': 0, 'direction': 'FLAT'}
    
    closes = [c['close'] for c in ohlc]
    
    recent_change = ((closes[-1] - closes[-5]) / closes[-5]) * 100 if closes[-5] > 0 else 0
    overall_change = ((closes[-1] - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0
    
    if recent_change > 3:
        momentum = 'STRONG_UP'
        direction = 'UP'
    elif recent_change > 1:
        momentum = 'UP'
        direction = 'UP'
    elif recent_change < -3:
        momentum = 'STRONG_DOWN'
        direction = 'DOWN'
    elif recent_change < -1:
        momentum = 'DOWN'
        direction = 'DOWN'
    else:
        momentum = 'NEUTRAL'
        direction = 'FLAT'
    
    return {
        'momentum': momentum,
        'strength': round(abs(recent_change), 2),
        'direction': direction,
        'recent_change_pct': round(recent_change, 2),
        'overall_change_pct': round(overall_change, 2)
    }


def get_volume_analysis(symbol: str, timeframe: str = '1h') -> Dict:
    """Analyze volume trends from real OHLC data"""
    ohlc = get_cached_ohlc(symbol, timeframe, limit=20)
    if not ohlc or len(ohlc) < 10:
        return {'volume_trend': 'NORMAL', 'ratio': 1.0}
    
    volumes = [c['volume'] for c in ohlc]
    
    recent_avg = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else sum(volumes) / len(volumes)
    historical_avg = sum(volumes[:-5]) / len(volumes[:-5]) if len(volumes) > 5 else recent_avg
    
    ratio = recent_avg / historical_avg if historical_avg > 0 else 1.0
    
    if ratio > 2.0:
        trend = 'VERY_HIGH'
    elif ratio > 1.5:
        trend = 'HIGH'
    elif ratio < 0.5:
        trend = 'LOW'
    elif ratio < 0.75:
        trend = 'BELOW_AVERAGE'
    else:
        trend = 'NORMAL'
    
    return {
        'volume_trend': trend,
        'ratio': round(ratio, 2),
        'recent_avg': recent_avg,
        'historical_avg': historical_avg
    }


def detect_rsi_divergence(symbol: str, timeframe: str = '4h') -> Dict:
    """
    Detect RSI Divergence - a powerful reversal signal.
    
    Bullish Divergence: Price makes LOWER low, but RSI makes HIGHER low
    -> Indicates selling pressure weakening, potential reversal UP
    
    Bearish Divergence: Price makes HIGHER high, but RSI makes LOWER high
    -> Indicates buying pressure weakening, potential reversal DOWN
    
    Hidden Bullish: Price makes HIGHER low, RSI makes LOWER low (trend continuation)
    Hidden Bearish: Price makes LOWER high, RSI makes HIGHER high (trend continuation)
    """
    try:
        ohlc = get_cached_ohlc(symbol, timeframe, limit=50)
        if not ohlc or len(ohlc) < 30:
            return {'divergence': 'NONE', 'type': None, 'strength': 0, 'description': 'Insufficient data'}
        
        closes = [c['close'] for c in ohlc]
        lows = [c['low'] for c in ohlc]
        highs = [c['high'] for c in ohlc]
        
        # Calculate RSI for each bar - synchronized with OHLC indices
        # rsi_by_bar[i] corresponds to ohlc[i]
        rsi_by_bar = [50.0] * 14  # First 14 bars don't have valid RSI
        for i in range(14, len(closes)):
            rsi = calculate_rsi_from_closes(closes[:i+1], period=14)
            rsi_by_bar.append(rsi)
        
        if len(rsi_by_bar) < 20:
            return {'divergence': 'NONE', 'type': None, 'strength': 0, 'description': 'Insufficient RSI data'}
        
        # Find swing lows with tolerance (within 1% of local minimum)
        def find_swing_lows(window=3):
            swings = []
            for i in range(window + 14, len(ohlc) - window):  # Start after RSI warmup
                local_min = min(lows[i-window:i+window+1])
                tolerance = local_min * 0.01
                if abs(lows[i] - local_min) <= tolerance:
                    swings.append({'idx': i, 'price': lows[i], 'rsi': rsi_by_bar[i]})
            return swings
        
        # Find swing highs with tolerance
        def find_swing_highs(window=3):
            swings = []
            for i in range(window + 14, len(ohlc) - window):
                local_max = max(highs[i-window:i+window+1])
                tolerance = local_max * 0.01
                if abs(highs[i] - local_max) <= tolerance:
                    swings.append({'idx': i, 'price': highs[i], 'rsi': rsi_by_bar[i]})
            return swings
        
        swing_lows = find_swing_lows()
        swing_highs = find_swing_highs()
        
        divergence = 'NONE'
        div_type = None
        strength = 0
        description = 'No divergence detected'
        
        # Check for BULLISH DIVERGENCE (most recent 2 swing lows)
        if len(swing_lows) >= 2:
            prev_low = swing_lows[-2]
            curr_low = swing_lows[-1]
            
            # Classic Bullish: Lower price low + Higher RSI low
            if curr_low['price'] < prev_low['price'] and curr_low['rsi'] > prev_low['rsi']:
                price_drop = ((prev_low['price'] - curr_low['price']) / prev_low['price']) * 100 if prev_low['price'] > 0 else 0
                rsi_rise = curr_low['rsi'] - prev_low['rsi']
                
                if price_drop > 1.5 and rsi_rise > 3:
                    divergence = 'BULLISH'
                    div_type = 'CLASSIC'
                    strength = min(100, int(price_drop * 8 + rsi_rise * 4))
                    description = f"Price made lower low (-{price_drop:.1f}%) but RSI rose (+{rsi_rise:.1f}) - reversal likely"
            
            # Hidden Bullish: Higher price low + Lower RSI low (trend continuation)
            elif curr_low['price'] > prev_low['price'] and curr_low['rsi'] < prev_low['rsi']:
                divergence = 'HIDDEN_BULLISH'
                div_type = 'HIDDEN'
                strength = 45
                description = "Hidden bullish divergence - uptrend continuation signal"
        
        # Check for BEARISH DIVERGENCE (most recent 2 swing highs)
        if len(swing_highs) >= 2 and divergence == 'NONE':
            prev_high = swing_highs[-2]
            curr_high = swing_highs[-1]
            
            # Classic Bearish: Higher price high + Lower RSI high
            if curr_high['price'] > prev_high['price'] and curr_high['rsi'] < prev_high['rsi']:
                price_rise = ((curr_high['price'] - prev_high['price']) / prev_high['price']) * 100 if prev_high['price'] > 0 else 0
                rsi_drop = prev_high['rsi'] - curr_high['rsi']
                
                if price_rise > 1.5 and rsi_drop > 3:
                    divergence = 'BEARISH'
                    div_type = 'CLASSIC'
                    strength = min(100, int(price_rise * 8 + rsi_drop * 4))
                    description = f"Price made higher high (+{price_rise:.1f}%) but RSI fell (-{rsi_drop:.1f}) - reversal likely"
            
            # Hidden Bearish: Lower price high + Higher RSI high (trend continuation)
            elif curr_high['price'] < prev_high['price'] and curr_high['rsi'] > prev_high['rsi']:
                divergence = 'HIDDEN_BEARISH'
                div_type = 'HIDDEN'
                strength = 45
                description = "Hidden bearish divergence - downtrend continuation signal"
        
        return {
            'divergence': divergence,
            'type': div_type,
            'strength': strength,
            'description': description,
            'timeframe': timeframe
        }
    except Exception as e:
        logger.warning(f"RSI divergence detection error for {symbol}: {e}")
        return {'divergence': 'NONE', 'type': None, 'strength': 0, 'description': f'Error: {e}'}


def get_dominant_timeframe_signal(symbol: str) -> Dict:
    """
    FALLBACK STRATEGY: When confluence is weak, use the most reliable single timeframe.
    
    Priority order (based on reliability for crypto):
    1. 4h - Best balance of noise filtering and responsiveness
    2. 1d - Very reliable but slower
    3. 1h - Good for faster setups
    
    Also checks for RSI divergence as a strong entry signal even without confluence.
    """
    all_rsi = get_real_timeframe_rsi(symbol)
    
    # Priority timeframes for fallback
    priority_tfs = ['4h', '1d', '1h']
    
    # Find the strongest signal from priority timeframes
    strongest_signal = None
    strongest_strength = 0
    
    for tf in priority_tfs:
        rsi = all_rsi.get(tf, 50)
        
        # Calculate signal strength based on distance from neutral (50)
        if rsi < 30:
            strength = (30 - rsi) * 3  # Very oversold = stronger
            signal = {'timeframe': tf, 'rsi': rsi, 'bias': 'STRONGLY_OVERSOLD', 'action': 'BUY', 'strength': strength}
        elif rsi < 40:
            strength = (40 - rsi) * 2
            signal = {'timeframe': tf, 'rsi': rsi, 'bias': 'OVERSOLD', 'action': 'BUY', 'strength': strength}
        elif rsi > 70:
            strength = (rsi - 70) * 3
            signal = {'timeframe': tf, 'rsi': rsi, 'bias': 'STRONGLY_OVERBOUGHT', 'action': 'SELL', 'strength': strength}
        elif rsi > 60:
            strength = (rsi - 60) * 2
            signal = {'timeframe': tf, 'rsi': rsi, 'bias': 'OVERBOUGHT', 'action': 'SELL', 'strength': strength}
        else:
            strength = 0
            signal = {'timeframe': tf, 'rsi': rsi, 'bias': 'NEUTRAL', 'action': 'HOLD', 'strength': 0}
        
        if strength > strongest_strength:
            strongest_signal = signal
            strongest_strength = strength
    
    # Check for RSI divergence (overrides weak confluence)
    divergence = detect_rsi_divergence(symbol, '4h')
    
    if divergence['divergence'] in ['BULLISH', 'BEARISH'] and divergence['strength'] > 40:
        # Divergence is a powerful signal even without confluence
        if divergence['divergence'] == 'BULLISH':
            return {
                'has_signal': True,
                'source': 'DIVERGENCE',
                'action': 'BUY',
                'confidence_modifier': 0.85,  # 85% confidence for divergence signals
                'timeframe': divergence['timeframe'],
                'reason': divergence['description'],
                'divergence': divergence,
                'dominant_rsi': strongest_signal
            }
        else:
            return {
                'has_signal': True,
                'source': 'DIVERGENCE',
                'action': 'SELL',
                'confidence_modifier': 0.85,
                'timeframe': divergence['timeframe'],
                'reason': divergence['description'],
                'divergence': divergence,
                'dominant_rsi': strongest_signal
            }
    
    # If no divergence, use dominant timeframe signal
    if strongest_signal and strongest_signal['strength'] > 20:
        return {
            'has_signal': True,
            'source': 'DOMINANT_TF',
            'action': strongest_signal['action'],
            'confidence_modifier': 0.70,  # 70% confidence for single TF (lower than confluence)
            'timeframe': strongest_signal['timeframe'],
            'reason': f"{strongest_signal['timeframe']} RSI at {strongest_signal['rsi']:.1f} ({strongest_signal['bias']})",
            'divergence': divergence,
            'dominant_rsi': strongest_signal
        }
    
    # No clear signal
    return {
        'has_signal': False,
        'source': 'NONE',
        'action': 'HOLD',
        'confidence_modifier': 0.5,
        'timeframe': None,
        'reason': 'No clear signal from any timeframe',
        'divergence': divergence,
        'dominant_rsi': strongest_signal
    }


def get_comprehensive_analysis(symbol: str) -> Dict:
    """
    Get comprehensive technical analysis using REAL OHLC data.
    """
    all_tf_rsi = get_real_timeframe_rsi(symbol)
    macd_1h = get_real_macd(symbol, '1h')
    macd_4h = get_real_macd(symbol, '4h')
    support_resistance = get_real_support_resistance(symbol, '4h')
    momentum = get_price_momentum(symbol, '1h')
    volume = get_volume_analysis(symbol, '1h')
    
    ohlc_1d = get_cached_ohlc(symbol, '1d', limit=2)
    if ohlc_1d and len(ohlc_1d) >= 2:
        current_price = ohlc_1d[-1]['close']
        prev_close = ohlc_1d[-2]['close']
        price_change_24h = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
    else:
        current_price = 0
        price_change_24h = 0
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'price_change_24h': round(price_change_24h, 2),
        'multi_tf_rsi': all_tf_rsi,
        'macd_1h': macd_1h,
        'macd_4h': macd_4h,
        'support_resistance': support_resistance,
        'momentum': momentum,
        'volume': volume,
        'data_source': 'REAL_OHLC',
        'timestamp': datetime.now().isoformat()
    }


def is_symbol_available(symbol: str) -> bool:
    """Check if a symbol is available"""
    ohlc = fetch_cryptocompare_ohlc(symbol, '1d', limit=1)
    return ohlc is not None and len(ohlc) > 0


def clear_cache():
    """Clear all cached OHLC data"""
    global _ohlc_cache
    with _cache_lock:
        _ohlc_cache.clear()
    logger.info("OHLC cache cleared")


logger.info("Real OHLC module loaded - CryptoCompare + Bybit data enabled")
