# Removed numpy dependency - using built-in Python calculations
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ChartAnalysis:
    """Advanced technical analysis for trading signals"""
    
    def __init__(self):
        self.signals = {
            'BUY': 'buy',
            'SELL': 'sell',
            'HOLD': 'hold'
        }
    
    def simple_moving_average(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(avg)
        return sma
    
    def exponential_moving_average(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # Start with SMA
        
        for i in range(period, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema
    
    def rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
        
        return rsi_values
    
    def macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return {'macd': [], 'signal': [], 'histogram': []}
        
        ema_fast = self.exponential_moving_average(prices, fast)
        ema_slow = self.exponential_moving_average(prices, slow)
        
        # Align the EMAs (slow EMA starts later)
        start_idx = slow - fast
        ema_fast_aligned = ema_fast[start_idx:]
        
        macd_line = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast_aligned, ema_slow)]
        signal_line = self.exponential_moving_average(macd_line, signal)
        
        # Calculate histogram (MACD - Signal)
        histogram = []
        signal_start = len(macd_line) - len(signal_line)
        for i in range(len(signal_line)):
            histogram.append(macd_line[signal_start + i] - signal_line[i])
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = self.simple_moving_average(prices, period)
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            subset = prices[i - period + 1:i + 1]
            # Calculate standard deviation manually
            mean = sum(subset) / len(subset)
            variance = sum((x - mean) ** 2 for x in subset) / len(subset)
            std = variance ** 0.5
            sma_val = sma[i - period + 1]
            
            upper_band.append(sma_val + (std * std_dev))
            lower_band.append(sma_val - (std * std_dev))
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def detect_support_resistance(self, prices: List[float], window: int = 5) -> Dict:
        """Detect support and resistance levels"""
        if len(prices) < window * 2 + 1:
            return {'support': [], 'resistance': []}
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # Check for local minimum (support)
            is_support = all(prices[i] <= prices[i + j] for j in range(-window, window + 1) if j != 0)
            if is_support:
                support_levels.append((i, prices[i]))
            
            # Check for local maximum (resistance)
            is_resistance = all(prices[i] >= prices[i + j] for j in range(-window, window + 1) if j != 0)
            if is_resistance:
                resistance_levels.append((i, prices[i]))
        
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }
    
    def generate_trading_signals(self, prices: List[float], volume: Optional[List[float]] = None) -> Dict:
        """Generate comprehensive trading signals"""
        if len(prices) < 50:  # Need enough data for analysis
            return {'signal': 'HOLD', 'confidence': 0, 'indicators': {}}
        
        signals = []
        confidence_scores = []
        indicators = {}
        
        # 1. Moving Average Crossover
        sma_short = self.simple_moving_average(prices, 10)
        sma_long = self.simple_moving_average(prices, 30)
        
        if len(sma_short) >= 2 and len(sma_long) >= 2:
            # Golden Cross (bullish) or Death Cross (bearish)
            if sma_short[-1] > sma_long[-1] and sma_short[-2] <= sma_long[-2]:
                signals.append('BUY')
                confidence_scores.append(0.7)
            elif sma_short[-1] < sma_long[-1] and sma_short[-2] >= sma_long[-2]:
                signals.append('SELL')
                confidence_scores.append(0.7)
            
            indicators['sma_trend'] = 'bullish' if sma_short[-1] > sma_long[-1] else 'bearish'
        
        # 2. RSI Analysis
        rsi_values = self.rsi(prices)
        if rsi_values:
            current_rsi = rsi_values[-1]
            indicators['rsi'] = current_rsi
            
            if current_rsi < 30:  # Oversold
                signals.append('BUY')
                confidence_scores.append(0.6)
            elif current_rsi > 70:  # Overbought
                signals.append('SELL')
                confidence_scores.append(0.6)
        
        # 3. MACD Analysis
        macd_data = self.macd(prices)
        if macd_data['histogram']:
            current_histogram = macd_data['histogram'][-1]
            prev_histogram = macd_data['histogram'][-2] if len(macd_data['histogram']) > 1 else 0
            
            # MACD bullish divergence
            if current_histogram > 0 and prev_histogram <= 0:
                signals.append('BUY')
                confidence_scores.append(0.5)
            elif current_histogram < 0 and prev_histogram >= 0:
                signals.append('SELL')
                confidence_scores.append(0.5)
            
            indicators['macd_trend'] = 'bullish' if current_histogram > 0 else 'bearish'
        
        # 4. Bollinger Bands
        bb_data = self.bollinger_bands(prices)
        if bb_data['upper'] and bb_data['lower']:
            current_price = prices[-1]
            upper_band = bb_data['upper'][-1]
            lower_band = bb_data['lower'][-1]
            
            # Price touching bands
            if current_price <= lower_band:
                signals.append('BUY')
                confidence_scores.append(0.4)
            elif current_price >= upper_band:
                signals.append('SELL')
                confidence_scores.append(0.4)
            
            # Band squeeze detection
            band_width = (upper_band - lower_band) / bb_data['middle'][-1]
            indicators['bollinger_squeeze'] = 'yes' if band_width < 0.1 else 'no'
        
        # 5. Support/Resistance Analysis
        sr_levels = self.detect_support_resistance(prices)
        current_price = prices[-1]
        
        # Check if price is near support (buy signal) or resistance (sell signal)
        for _, support_price in sr_levels['support'][-3:]:  # Last 3 support levels
            if abs(current_price - support_price) / support_price < 0.02:  # Within 2%
                signals.append('BUY')
                confidence_scores.append(0.3)
                break
        
        for _, resistance_price in sr_levels['resistance'][-3:]:  # Last 3 resistance levels
            if abs(current_price - resistance_price) / resistance_price < 0.02:  # Within 2%
                signals.append('SELL')
                confidence_scores.append(0.3)
                break
        
        indicators['support_levels'] = len(sr_levels['support'])
        indicators['resistance_levels'] = len(sr_levels['resistance'])
        
        # 6. Volume Analysis (if available)
        if volume is not None and len(volume) >= 10:
            avg_volume = sum(volume[-10:]) / 10
            current_volume = volume[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            indicators['volume_ratio'] = volume_ratio
            
            # High volume confirms signals
            if volume_ratio > 1.5:
                confidence_scores = [score * 1.2 for score in confidence_scores]
        
        # Combine all signals
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        if buy_signals > sell_signals:
            final_signal = 'BUY'
            confidence = min(0.95, sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0)
        elif sell_signals > buy_signals:
            final_signal = 'SELL'
            confidence = min(0.95, sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0)
        else:
            final_signal = 'HOLD'
            confidence = 0.5
        
        # Trend strength
        price_change = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0
        indicators['trend_strength'] = abs(price_change)
        indicators['price_momentum'] = 'strong' if abs(price_change) > 0.05 else 'weak'
        
        return {
            'signal': final_signal,
            'confidence': round(confidence, 2),
            'indicators': indicators,
            'signal_count': {'buy': buy_signals, 'sell': sell_signals},
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_token_chart(self, symbol: str, price_history: List[Dict]) -> Dict:
        """Comprehensive chart analysis for a specific token"""
        try:
            if not price_history or len(price_history) < 20:
                return {
                    'symbol': symbol,
                    'error': 'Insufficient price data for analysis',
                    'recommendation': 'HOLD'
                }
            
            # Extract price and volume data
            prices = [float(p.get('price', 0)) for p in price_history]
            volumes = [float(p.get('volume', 0)) for p in price_history if p.get('volume')]
            
            # Generate trading signals
            volume_data = volumes if len(volumes) == len(prices) else None
            signals = self.generate_trading_signals(prices, volume_data)
            
            # Calculate additional metrics
            current_price = prices[-1]
            price_7d_ago = prices[-7] if len(prices) >= 7 else prices[0]
            price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
            
            # Volatility calculation
            price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, min(30, len(prices)))]
            volatility = float(np.std(price_changes) * 100) if price_changes else 0.0
            
            # Generate Bybit futures trading settings
            trading_settings = self.generate_bybit_settings(
                symbol=symbol,
                current_price=current_price,
                signal=signals['signal'],
                confidence=signals['confidence'],
                volatility=volatility,
                indicators=signals['indicators']
            )

            return {
                'symbol': symbol,
                'current_price': current_price,
                'recommendation': signals['signal'],
                'confidence': signals['confidence'],
                'price_change_7d': round(price_change_7d, 2),
                'volatility': round(volatility, 2),
                'technical_indicators': signals['indicators'],
                'bybit_settings': trading_settings,
                'analysis_quality': 'high' if len(prices) > 50 else 'medium' if len(prices) > 30 else 'basic',
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing chart for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'recommendation': 'HOLD'
            }
    
    def generate_bybit_settings(self, symbol: str, current_price: float, signal: str, 
                               confidence: float, volatility: float, indicators: Dict) -> Dict:
        """Generate optimal Bybit futures trading settings based on analysis"""
        
        # Base settings by token volatility and market cap
        token_configs = {
            'BTC': {'base_leverage': 10, 'max_leverage': 20, 'risk_multiplier': 0.8},
            'ETH': {'base_leverage': 12, 'max_leverage': 25, 'risk_multiplier': 0.9},
            'SOL': {'base_leverage': 8, 'max_leverage': 15, 'risk_multiplier': 1.2},
            'ADA': {'base_leverage': 6, 'max_leverage': 12, 'risk_multiplier': 1.5},
            'DOT': {'base_leverage': 7, 'max_leverage': 15, 'risk_multiplier': 1.3},
            'MATIC': {'base_leverage': 8, 'max_leverage': 18, 'risk_multiplier': 1.4},
            'AVAX': {'base_leverage': 9, 'max_leverage': 20, 'risk_multiplier': 1.1},
            'LINK': {'base_leverage': 10, 'max_leverage': 22, 'risk_multiplier': 1.0}
        }
        
        config = token_configs.get(symbol, {'base_leverage': 5, 'max_leverage': 10, 'risk_multiplier': 1.5})
        
        # Determine margin mode based on confidence and volatility
        margin_mode = "isolated" if confidence < 0.7 or volatility > 5.0 else "cross"
        
        # Calculate optimal leverage based on confidence and volatility
        confidence_factor = min(confidence * 2, 1.0)  # Scale confidence 0-1
        volatility_factor = max(0.3, 1 - (volatility / 10))  # Reduce leverage for high volatility
        
        optimal_leverage = int(config['base_leverage'] * confidence_factor * volatility_factor)
        optimal_leverage = min(optimal_leverage, config['max_leverage'])
        optimal_leverage = max(optimal_leverage, 2)  # Minimum 2x leverage
        
        # Determine order type based on signal strength and market conditions
        rsi = indicators.get('rsi', 50)
        trend_strength = indicators.get('trend_strength', 0)
        
        if confidence > 0.8 and abs(trend_strength) > 0.1:
            order_type = "market"  # Strong signal, execute immediately
        elif confidence > 0.6:
            order_type = "limit"   # Good signal, wait for better price
        elif rsi > 70 or rsi < 30:
            order_type = "conditional"  # Overbought/oversold, wait for reversal
        else:
            order_type = "chase_limit"  # Moderate signal, chase the price
        
        # Calculate entry price based on signal and current price
        if signal == "BUY":
            if order_type == "market":
                entry_price = current_price
            elif order_type == "limit":
                entry_price = current_price * 0.998  # 0.2% below current
            else:
                entry_price = current_price * 0.995  # 0.5% below current
        elif signal == "SELL":
            if order_type == "market":
                entry_price = current_price
            elif order_type == "limit":
                entry_price = current_price * 1.002  # 0.2% above current
            else:
                entry_price = current_price * 1.005  # 0.5% above current
        else:  # HOLD
            entry_price = current_price
        
        # Calculate Take Profit and Stop Loss based on volatility and support/resistance
        support_levels = indicators.get('support_levels', 2)
        resistance_levels = indicators.get('resistance_levels', 2)
        
        # TP/SL percentages based on volatility and leverage
        base_tp_percent = max(1.5, min(6.0, volatility * 0.8))
        base_sl_percent = max(1.0, min(4.0, volatility * 0.6))
        
        # Adjust for leverage (higher leverage = tighter stops)
        leverage_adjustment = max(0.5, 1 - (optimal_leverage / 20))
        tp_percent = base_tp_percent * leverage_adjustment
        sl_percent = base_sl_percent * leverage_adjustment
        
        if signal == "BUY":
            take_profit = entry_price * (1 + tp_percent / 100)
            stop_loss = entry_price * (1 - sl_percent / 100)
        elif signal == "SELL":
            take_profit = entry_price * (1 - tp_percent / 100)
            stop_loss = entry_price * (1 + sl_percent / 100)
        else:
            take_profit = None
            stop_loss = None
        
        # Position sizing (USDT amount)
        if confidence > 0.8:
            position_size = 500  # High confidence
        elif confidence > 0.6:
            position_size = 300  # Medium confidence
        elif confidence > 0.4:
            position_size = 150  # Low confidence
        else:
            position_size = 100  # Very low confidence
        
        # Adjust position size based on volatility
        position_size = int(position_size * (1 / max(1, volatility / 3)))
        
        # Post only and reduce only settings
        post_only = confidence < 0.7  # Use post-only for lower confidence trades
        reduce_only = False  # Not typically used for opening positions
        
        return {
            'margin_mode': margin_mode,
            'leverage': f"{optimal_leverage}x",
            'order_type': order_type,
            'entry_price_usdt': round(entry_price, 6),
            'position_size_usdt': position_size,
            'take_profit_usdt': round(take_profit, 6) if take_profit else None,
            'stop_loss_usdt': round(stop_loss, 6) if stop_loss else None,
            'tp_percentage': f"{tp_percent:.1f}%" if take_profit else None,
            'sl_percentage': f"{sl_percent:.1f}%" if stop_loss else None,
            'post_only': post_only,
            'reduce_only': reduce_only,
            'risk_reward_ratio': f"1:{tp_percent/sl_percent:.1f}" if take_profit and stop_loss else None,
            'recommended_timeframe': '15m' if volatility > 4 else '1h' if volatility > 2 else '4h'
        }