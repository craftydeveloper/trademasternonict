"""
Advanced Trading Signal Generation System
Professional-grade signal detection with multiple strategies
"""

# Removed numpy dependency - using built-in calculations
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SignalStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    leverage: float
    timeframe: str
    strategy_name: str
    risk_reward_ratio: float
    timestamp: datetime
    analysis: Dict

class AdvancedSignalGenerator:
    """Professional trading signal generation with multiple strategies"""
    
    def __init__(self):
        self.min_confidence = 60  # Minimum 60% confidence for signals
        self.strategies = [
            'multi_timeframe_trend',
            'mean_reversion',
            'breakout_momentum',
            'volume_price_analysis',
            'harmonic_patterns',
            'fibonacci_confluence',
            'support_resistance_zones'
        ]
    
    def generate_comprehensive_signals(self, symbol: str, price_data: List[Dict],
                                     current_price: float) -> List[TradingSignal]:
        """Generate signals using multiple advanced strategies"""
        
        if len(price_data) < 50:  # Need sufficient data
            return []
        
        signals = []
        
        # Extract price arrays
        prices = [p['price'] for p in price_data]
        volumes = [p.get('volume', 0) for p in price_data]
        
        # Strategy 1: Multi-timeframe trend analysis
        trend_signal = self._analyze_multi_timeframe_trend(symbol, prices, current_price)
        if trend_signal and trend_signal.confidence >= self.min_confidence:
            signals.append(trend_signal)
        
        # Strategy 2: Mean reversion with Bollinger Bands
        reversion_signal = self._analyze_mean_reversion(symbol, prices, current_price)
        if reversion_signal and reversion_signal.confidence >= self.min_confidence:
            signals.append(reversion_signal)
        
        # Strategy 3: Breakout momentum
        breakout_signal = self._analyze_breakout_momentum(symbol, prices, volumes, current_price)
        if breakout_signal and breakout_signal.confidence >= self.min_confidence:
            signals.append(breakout_signal)
        
        # Strategy 4: Volume-price divergence
        vpa_signal = self._analyze_volume_price(symbol, prices, volumes, current_price)
        if vpa_signal and vpa_signal.confidence >= self.min_confidence:
            signals.append(vpa_signal)
        
        return signals
    
    def _analyze_multi_timeframe_trend(self, symbol: str, prices: List[float], 
                                     current_price: float) -> Optional[TradingSignal]:
        """Multi-timeframe trend analysis with EMAs"""
        
        # Calculate multiple EMAs for trend confirmation
        ema_8 = self._calculate_ema(prices, 8)
        ema_21 = self._calculate_ema(prices, 21)
        ema_50 = self._calculate_ema(prices, 50)
        
        if len(ema_8) < 3 or len(ema_21) < 3:
            return None
        
        # Current trend analysis
        short_trend = ema_8[-1] > ema_21[-1]  # Short-term trend
        medium_trend = ema_21[-1] > ema_50[-1] if len(ema_50) > 0 else short_trend
        price_above_ema = current_price > ema_8[-1]
        
        # Trend strength calculation
        ema_separation = abs(ema_8[-1] - ema_21[-1]) / current_price
        trend_strength = min(ema_separation * 1000, 100)  # Scale to 0-100
        
        # Signal generation
        if short_trend and medium_trend and price_above_ema:
            # Bullish signal
            confidence = 65 + trend_strength * 0.3
            stop_loss = ema_21[-1] * 0.98
            take_profit = current_price * 1.04
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.MODERATE if confidence < 75 else SignalStrength.STRONG,
                confidence=min(confidence, 95),
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=3.0,
                timeframe="4H",
                strategy_name="Multi-Timeframe Trend",
                risk_reward_ratio=(take_profit - current_price) / (current_price - stop_loss),
                timestamp=datetime.now(),
                analysis={
                    'ema_8': ema_8[-1],
                    'ema_21': ema_21[-1],
                    'trend_strength': trend_strength,
                    'trend_direction': 'bullish'
                }
            )
        
        elif not short_trend and not medium_trend and not price_above_ema:
            # Bearish signal
            confidence = 65 + trend_strength * 0.3
            stop_loss = ema_21[-1] * 1.02
            take_profit = current_price * 0.96
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.MODERATE if confidence < 75 else SignalStrength.STRONG,
                confidence=min(confidence, 95),
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=3.0,
                timeframe="4H",
                strategy_name="Multi-Timeframe Trend",
                risk_reward_ratio=(current_price - take_profit) / (stop_loss - current_price),
                timestamp=datetime.now(),
                analysis={
                    'ema_8': ema_8[-1],
                    'ema_21': ema_21[-1],
                    'trend_strength': trend_strength,
                    'trend_direction': 'bearish'
                }
            )
        
        return None
    
    def _analyze_mean_reversion(self, symbol: str, prices: List[float], 
                              current_price: float) -> Optional[TradingSignal]:
        """Mean reversion strategy using Bollinger Bands and RSI"""
        
        # Bollinger Bands
        period = 20
        if len(prices) < period + 5:
            return None
        
        sma = sum(prices[-period:]) / period
        std = np.std(prices[-period:])
        
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        # RSI calculation
        rsi = self._calculate_rsi(prices, 14)
        if not rsi or len(rsi) < 2:
            return None
        
        current_rsi = rsi[-1]
        
        # Mean reversion signals
        bb_position = (current_price - lower_band) / (upper_band - lower_band)
        
        # Oversold condition (buy signal)
        if current_rsi < 30 and bb_position < 0.2:
            confidence = 70 + (30 - current_rsi) + (0.2 - bb_position) * 50
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG,
                confidence=min(confidence, 92),
                entry_price=current_price,
                stop_loss=lower_band * 0.99,
                take_profit=sma,
                leverage=2.0,
                timeframe="1H",
                strategy_name="Mean Reversion",
                risk_reward_ratio=(sma - current_price) / (current_price - lower_band * 0.99),
                timestamp=datetime.now(),
                analysis={
                    'rsi': current_rsi,
                    'bb_position': bb_position,
                    'upper_band': upper_band,
                    'lower_band': lower_band,
                    'sma': sma
                }
            )
        
        # Overbought condition (sell signal)
        elif current_rsi > 70 and bb_position > 0.8:
            confidence = 70 + (current_rsi - 70) + (bb_position - 0.8) * 50
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.STRONG,
                confidence=min(confidence, 92),
                entry_price=current_price,
                stop_loss=upper_band * 1.01,
                take_profit=sma,
                leverage=2.0,
                timeframe="1H",
                strategy_name="Mean Reversion",
                risk_reward_ratio=(current_price - sma) / (upper_band * 1.01 - current_price),
                timestamp=datetime.now(),
                analysis={
                    'rsi': current_rsi,
                    'bb_position': bb_position,
                    'upper_band': upper_band,
                    'lower_band': lower_band,
                    'sma': sma
                }
            )
        
        return None
    
    def _analyze_breakout_momentum(self, symbol: str, prices: List[float], 
                                 volumes: List[float], current_price: float) -> Optional[TradingSignal]:
        """Breakout momentum strategy with volume confirmation"""
        
        if len(prices) < 20:
            return None
        
        # Calculate 20-period high and low
        period_high = max(prices[-20:])
        period_low = min(prices[-20:])
        
        # Average volume for confirmation
        avg_volume = sum(volumes[-10:]) / 10 if volumes else 0
        current_volume = volumes[-1] if volumes else 0
        
        volume_surge = current_volume > avg_volume * 1.5
        
        # Breakout above resistance
        if current_price > period_high * 1.001 and volume_surge:
            confidence = 75 if volume_surge else 65
            range_size = period_high - period_low
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG,
                confidence=confidence,
                entry_price=current_price,
                stop_loss=period_high * 0.995,
                take_profit=current_price + range_size * 0.618,  # Fibonacci target
                leverage=4.0,
                timeframe="30M",
                strategy_name="Breakout Momentum",
                risk_reward_ratio=(current_price + range_size * 0.618 - current_price) / (current_price - period_high * 0.995),
                timestamp=datetime.now(),
                analysis={
                    'period_high': period_high,
                    'period_low': period_low,
                    'volume_surge': volume_surge,
                    'breakout_level': period_high
                }
            )
        
        # Breakdown below support
        elif current_price < period_low * 0.999 and volume_surge:
            confidence = 75 if volume_surge else 65
            range_size = period_high - period_low
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.STRONG,
                confidence=confidence,
                entry_price=current_price,
                stop_loss=period_low * 1.005,
                take_profit=current_price - range_size * 0.618,
                leverage=4.0,
                timeframe="30M",
                strategy_name="Breakout Momentum",
                risk_reward_ratio=(current_price - (current_price - range_size * 0.618)) / (period_low * 1.005 - current_price),
                timestamp=datetime.now(),
                analysis={
                    'period_high': period_high,
                    'period_low': period_low,
                    'volume_surge': volume_surge,
                    'breakdown_level': period_low
                }
            )
        
        return None
    
    def _analyze_volume_price(self, symbol: str, prices: List[float], 
                            volumes: List[float], current_price: float) -> Optional[TradingSignal]:
        """Volume-price analysis for divergence detection"""
        
        if len(prices) < 10 or not volumes:
            return None
        
        # Price momentum (last 5 periods)
        price_momentum = (prices[-1] - prices[-6]) / prices[-6] if len(prices) >= 6 else 0
        
        # Volume trend (last 5 periods vs previous 5)
        recent_vol = sum(volumes[-5:]) / 5
        previous_vol = sum(volumes[-10:-5]) / 5 if len(volumes) >= 10 else recent_vol
        
        volume_trend = (recent_vol - previous_vol) / previous_vol if previous_vol > 0 else 0
        
        # Bullish divergence: price falling but volume increasing
        if price_momentum < -0.02 and volume_trend > 0.2:
            confidence = 68 + min(volume_trend * 100, 20)
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=SignalStrength.MODERATE,
                confidence=min(confidence, 88),
                entry_price=current_price,
                stop_loss=current_price * 0.97,
                take_profit=current_price * 1.05,
                leverage=2.5,
                timeframe="2H",
                strategy_name="Volume-Price Analysis",
                risk_reward_ratio=(current_price * 1.05 - current_price) / (current_price - current_price * 0.97),
                timestamp=datetime.now(),
                analysis={
                    'price_momentum': price_momentum,
                    'volume_trend': volume_trend,
                    'divergence_type': 'bullish',
                    'recent_volume': recent_vol,
                    'previous_volume': previous_vol
                }
            )
        
        # Bearish divergence: price rising but volume decreasing
        elif price_momentum > 0.02 and volume_trend < -0.2:
            confidence = 68 + min(abs(volume_trend) * 100, 20)
            
            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=SignalStrength.MODERATE,
                confidence=min(confidence, 88),
                entry_price=current_price,
                stop_loss=current_price * 1.03,
                take_profit=current_price * 0.95,
                leverage=2.5,
                timeframe="2H",
                strategy_name="Volume-Price Analysis",
                risk_reward_ratio=(current_price - current_price * 0.95) / (current_price * 1.03 - current_price),
                timestamp=datetime.now(),
                analysis={
                    'price_momentum': price_momentum,
                    'volume_trend': volume_trend,
                    'divergence_type': 'bearish',
                    'recent_volume': recent_vol,
                    'previous_volume': previous_vol
                }
            )
        
        return None
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        ema = []
        multiplier = 2 / (period + 1)
        
        # First EMA is SMA
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        # Calculate remaining EMA values
        for i in range(period, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        rsi_values = []
        
        # Calculate initial average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate RSI for each subsequent period
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values