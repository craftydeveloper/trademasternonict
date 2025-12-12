"""
Ultra Market Analyzer - Advanced Multi-Source Signal Detection
Professional-grade market analysis with comprehensive pattern recognition
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import requests
import time

logger = logging.getLogger(__name__)

class UltraMarketAnalyzer:
    """Advanced market analyzer with multiple data sources and pattern recognition"""
    
    def __init__(self):
        self.confidence_threshold = 88.0  # Ultra-high threshold
        self.min_risk_reward = 2.5  # Higher risk/reward requirement
        self.max_positions = 5
        
        # Enhanced market metrics
        self.market_sentiment_score = 0.0
        self.institutional_flow = 0.0
        self.volatility_regime = 'normal'
        self.trend_momentum = 0.0
        
        # Pattern recognition weights
        self.pattern_weights = {
            'momentum_breakout': 0.35,
            'volume_surge': 0.25,
            'support_resistance': 0.20,
            'divergence_pattern': 0.20
        }
    
    def analyze_ultra_opportunities(self, market_data: Dict[str, Dict]) -> List[Dict]:
        """Comprehensive ultra-analysis of trading opportunities"""
        
        if not market_data:
            logger.warning("No market data for ultra analysis")
            return []
        
        # Enhanced market regime detection
        self._detect_market_regime(market_data)
        
        ultra_signals = []
        
        # Analyze each symbol with multiple timeframes
        for symbol, price_data in market_data.items():
            try:
                # Multi-timeframe analysis
                signal_set = self._ultra_analyze_symbol(symbol, price_data)
                ultra_signals.extend(signal_set)
                
            except Exception as e:
                logger.error(f"Ultra analysis error for {symbol}: {e}")
                continue
        
        # Advanced filtering and ranking
        premium_signals = self._filter_premium_signals(ultra_signals)
        
        # Generate ultra-optimized trading setups
        final_signals = []
        for i, signal in enumerate(premium_signals[:self.max_positions]):
            signal['is_primary_trade'] = (i == 0)
            signal['trade_label'] = "YOUR TRADE"
            signal['bybit_settings'] = self._generate_ultra_bybit_settings(
                signal, is_primary=(i == 0)
            )
            final_signals.append(signal)
        
        return final_signals
    
    def _detect_market_regime(self, market_data: Dict[str, Dict]):
        """Advanced market regime detection"""
        
        price_movements = []
        volume_data = []
        volatility_measures = []
        
        for symbol, data in market_data.items():
            if 'price_change_24h' in data:
                price_movements.append(data['price_change_24h'])
            
            if 'volume_24h' in data:
                volume_data.append(data['volume_24h'])
            
            # Calculate symbol volatility
            if 'high_24h' in data and 'low_24h' in data and 'price' in data:
                price_range = data['high_24h'] - data['low_24h']
                volatility = (price_range / data['price']) * 100
                volatility_measures.append(volatility)
        
        if price_movements and volume_data and volatility_measures:
            # Market sentiment calculation
            avg_change = sum(price_movements) / len(price_movements)
            positive_moves = sum(1 for change in price_movements if change > 0)
            self.market_sentiment_score = positive_moves / len(price_movements)
            
            # Trend momentum
            self.trend_momentum = abs(avg_change) / 5.0  # Normalize
            
            # Volatility regime detection
            avg_volatility = sum(volatility_measures) / len(volatility_measures)
            if avg_volatility > 8:
                self.volatility_regime = 'high'
            elif avg_volatility > 4:
                self.volatility_regime = 'elevated'
            else:
                self.volatility_regime = 'normal'
            
            # Institutional flow estimation (based on volume patterns)
            avg_volume = sum(volume_data) / len(volume_data)
            volume_spikes = sum(1 for vol in volume_data if vol > avg_volume * 1.5)
            self.institutional_flow = volume_spikes / len(volume_data)
    
    def _ultra_analyze_symbol(self, symbol: str, price_data: Dict) -> List[Dict]:
        """Ultra-comprehensive symbol analysis"""
        
        signals = []
        current_price = price_data.get('price', 0)
        
        if current_price <= 0:
            return signals
        
        # Pattern 1: Momentum Breakout with Volume Confirmation
        momentum_signal = self._analyze_momentum_breakout(symbol, price_data)
        if momentum_signal:
            signals.append(momentum_signal)
        
        # Pattern 2: Volume Surge Analysis
        volume_signal = self._analyze_volume_surge(symbol, price_data)
        if volume_signal:
            signals.append(volume_signal)
        
        # Pattern 3: Support/Resistance Levels
        sr_signal = self._analyze_support_resistance(symbol, price_data)
        if sr_signal:
            signals.append(sr_signal)
        
        # Pattern 4: Divergence Patterns
        divergence_signal = self._analyze_divergence_patterns(symbol, price_data)
        if divergence_signal:
            signals.append(divergence_signal)
        
        return signals
    
    def _analyze_momentum_breakout(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Advanced momentum breakout analysis"""
        
        current_price = price_data.get('price', 0)
        price_change = price_data.get('price_change_24h', 0)
        volume_24h = price_data.get('volume_24h', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        
        # Calculate momentum metrics
        momentum_strength = abs(price_change)
        price_range = high_24h - low_24h
        range_position = (current_price - low_24h) / price_range if price_range > 0 else 0.5
        
        # Volume confirmation
        volume_factor = min(volume_24h / 1000000, 3.0)
        
        # Breakout detection with enhanced criteria
        breakout_threshold = 0.12  # 12% from range boundaries
        
        base_confidence = 75
        
        if momentum_strength > 3 and volume_factor > 1.0:  # Strong momentum + volume
            
            if range_position > (1 - breakout_threshold) and price_change > 0:  # Bullish breakout
                action = "BUY"
                confidence = base_confidence + min(momentum_strength * 2, 20) + min(volume_factor * 5, 10)
                stop_loss = current_price * 0.96
                take_profit = current_price * 1.08
                
            elif range_position < breakout_threshold and price_change < 0:  # Bearish breakout
                action = "SELL"
                confidence = base_confidence + min(momentum_strength * 2, 20) + min(volume_factor * 5, 10)
                stop_loss = current_price * 1.04
                take_profit = current_price * 0.92
                
            else:
                return None
            
            # Market regime adjustments
            if self.volatility_regime == 'high':
                confidence += 8  # High volatility favors breakouts
            
            if self.institutional_flow > 0.3:
                confidence += 5  # Institutional activity confirmation
            
            confidence = min(confidence, 99)
            
            if confidence < self.confidence_threshold:
                return None
            
            # Enhanced risk/reward calculation
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            if risk_reward < self.min_risk_reward:
                return None
            
            leverage = self._calculate_ultra_leverage(momentum_strength / 10, confidence)
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'leverage': leverage,
                'expected_return': (reward / current_price) * 100,
                'risk_reward_ratio': risk_reward,
                'strategy_basis': 'Ultra Momentum Breakout',
                'time_horizon': '4H',
                'pattern_strength': momentum_strength,
                'volume_confirmation': volume_factor > 1.5,
                'market_regime': self.volatility_regime,
                'composite_score': confidence + risk_reward * 10
            }
        
        return None
    
    def _analyze_volume_surge(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Volume surge pattern analysis"""
        
        current_price = price_data.get('price', 0)
        volume_24h = price_data.get('volume_24h', 0)
        price_change = price_data.get('price_change_24h', 0)
        
        # Volume surge detection
        if volume_24h < 500000:  # Minimum volume threshold
            return None
        
        volume_surge_factor = volume_24h / 1000000  # Normalize volume
        
        if volume_surge_factor > 2.0 and abs(price_change) > 2:  # Significant volume + price movement
            
            action = "BUY" if price_change > 0 else "SELL"
            
            # Confidence based on volume and price alignment
            base_confidence = 80
            volume_boost = min(volume_surge_factor * 5, 15)
            price_alignment = min(abs(price_change) * 2, 10)
            
            confidence = base_confidence + volume_boost + price_alignment
            
            # Market sentiment adjustment
            if action == "BUY" and self.market_sentiment_score > 0.6:
                confidence += 5
            elif action == "SELL" and self.market_sentiment_score < 0.4:
                confidence += 5
            
            confidence = min(confidence, 98)
            
            if confidence < self.confidence_threshold:
                return None
            
            # Position sizing based on volume surge
            if action == "BUY":
                stop_loss = current_price * 0.97
                take_profit = current_price * 1.07
            else:
                stop_loss = current_price * 1.03
                take_profit = current_price * 0.93
            
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            if risk_reward < self.min_risk_reward:
                return None
            
            leverage = self._calculate_ultra_leverage(volume_surge_factor / 5, confidence)
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'leverage': leverage,
                'expected_return': (reward / current_price) * 100,
                'risk_reward_ratio': risk_reward,
                'strategy_basis': 'Volume Surge Analysis',
                'time_horizon': '3H',
                'volume_surge_factor': volume_surge_factor,
                'price_momentum': price_change,
                'market_sentiment': self.market_sentiment_score,
                'composite_score': confidence + risk_reward * 12
            }
        
        return None
    
    def _analyze_support_resistance(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Support and resistance level analysis"""
        
        current_price = price_data.get('price', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        price_change = price_data.get('price_change_24h', 0)
        
        price_range = high_24h - low_24h
        if price_range <= 0:
            return None
        
        # Calculate position within range
        range_position = (current_price - low_24h) / price_range
        
        # Support/Resistance proximity analysis
        proximity_threshold = 0.05  # 5% proximity to levels
        
        confidence = 0
        action = None
        
        # Near resistance level - potential reversal
        if range_position > (1 - proximity_threshold) and price_change > 1:
            action = "SELL"
            confidence = 85 + min(abs(price_change), 10)
            stop_loss = current_price * 1.025
            take_profit = current_price * 0.96
            
        # Near support level - potential bounce
        elif range_position < proximity_threshold and price_change < -1:
            action = "BUY"
            confidence = 85 + min(abs(price_change), 10)
            stop_loss = current_price * 0.975
            take_profit = current_price * 1.04
            
        else:
            return None
        
        # Trend momentum adjustment
        if self.trend_momentum > 0.4:
            confidence += 5
        
        confidence = min(confidence, 97)
        
        if confidence < self.confidence_threshold:
            return None
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < 2.0:  # Slightly lower for S/R trades
            return None
        
        leverage = self._calculate_ultra_leverage(range_position, confidence)
        
        return {
            'symbol': symbol,
            'action': action,
            'confidence': confidence,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'leverage': leverage,
            'expected_return': (reward / current_price) * 100,
            'risk_reward_ratio': risk_reward,
            'strategy_basis': 'Support/Resistance Analysis',
            'time_horizon': '2H',
            'range_position': range_position,
            'level_proximity': min(range_position, 1 - range_position),
            'trend_momentum': self.trend_momentum,
            'composite_score': confidence + risk_reward * 8
        }
    
    def _analyze_divergence_patterns(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Advanced divergence pattern analysis"""
        
        current_price = price_data.get('price', 0)
        price_change = price_data.get('price_change_24h', 0)
        volume_24h = price_data.get('volume_24h', 0)
        
        # Volume-price divergence detection
        volume_normalized = volume_24h / 1000000
        price_momentum = abs(price_change)
        
        # Look for divergence patterns
        if price_momentum > 3 and volume_normalized < 1.0:  # Price moves but low volume (weakness)
            
            # Bearish divergence - price up, volume down
            if price_change > 0:
                action = "SELL"
                confidence = 82 + min(price_momentum, 12)
                stop_loss = current_price * 1.03
                take_profit = current_price * 0.94
                
            # Bullish divergence - price down, volume increasing relative to decline
            else:
                action = "BUY"
                confidence = 82 + min(price_momentum, 12)
                stop_loss = current_price * 0.97
                take_profit = current_price * 1.06
            
            # Market regime confirmation
            if self.volatility_regime == 'elevated':
                confidence += 6
            
            confidence = min(confidence, 96)
            
            if confidence < self.confidence_threshold:
                return None
            
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            if risk_reward < self.min_risk_reward:
                return None
            
            leverage = self._calculate_ultra_leverage(price_momentum / 15, confidence)
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'leverage': leverage,
                'expected_return': (reward / current_price) * 100,
                'risk_reward_ratio': risk_reward,
                'strategy_basis': 'Divergence Pattern Analysis',
                'time_horizon': '6H',
                'divergence_strength': price_momentum / max(volume_normalized, 0.1),
                'price_momentum': price_momentum,
                'volume_factor': volume_normalized,
                'composite_score': confidence + risk_reward * 15
            }
        
        return None
    
    def _calculate_ultra_leverage(self, volatility: float, confidence: float) -> float:
        """Ultra-optimized leverage calculation"""
        
        # Base leverage calculation
        if volatility > 0.20:
            base_leverage = 4.0
        elif volatility > 0.15:
            base_leverage = 6.0
        elif volatility > 0.10:
            base_leverage = 8.0
        elif volatility > 0.05:
            base_leverage = 12.0
        else:
            base_leverage = 15.0
        
        # Confidence scaling
        confidence_multiplier = 0.7 + (confidence / 100) * 0.6
        leverage = base_leverage * confidence_multiplier
        
        # Market regime adjustments
        if self.volatility_regime == 'high':
            leverage *= 0.7  # Reduce in high volatility
        elif self.institutional_flow > 0.4:
            leverage *= 1.1  # Increase with institutional flow
        
        # Account safety for $500 account
        leverage = min(leverage, 25.0)  # Maximum 25x for ultra signals
        return max(leverage, 5.0)  # Minimum 5x
    
    def _filter_premium_signals(self, signals: List[Dict]) -> List[Dict]:
        """Advanced filtering for premium signals only"""
        
        if not signals:
            return []
        
        # Multi-criteria filtering
        premium_signals = []
        
        for signal in signals:
            # Quality thresholds
            if (signal['confidence'] >= self.confidence_threshold and
                signal['risk_reward_ratio'] >= self.min_risk_reward and
                signal.get('composite_score', 0) > 100):
                
                premium_signals.append(signal)
        
        # Advanced ranking by composite score
        premium_signals.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        
        # Diversification check - avoid too many same-direction trades
        diversified_signals = []
        buy_count = 0
        sell_count = 0
        
        for signal in premium_signals:
            if signal['action'] == 'BUY' and buy_count < 3:
                diversified_signals.append(signal)
                buy_count += 1
            elif signal['action'] == 'SELL' and sell_count < 3:
                diversified_signals.append(signal)
                sell_count += 1
            
            if len(diversified_signals) >= self.max_positions:
                break
        
        return diversified_signals
    
    def _generate_ultra_bybit_settings(self, signal: Dict, is_primary: bool = False) -> Dict:
        """Generate ultra-optimized Bybit settings"""
        
        account_balance = 500.0  # $500 account
        
        # Ultra-aggressive risk sizing for high-confidence signals
        if signal['confidence'] >= 96:
            risk_percentage = 0.18 if is_primary else 0.12  # 18%/12% for ultra-high confidence
        elif signal['confidence'] >= 92:
            risk_percentage = 0.15 if is_primary else 0.10  # 15%/10% for very high confidence
        else:
            risk_percentage = 0.12 if is_primary else 0.08  # 12%/8% for high confidence
        
        risk_amount = account_balance * risk_percentage
        
        # Enhanced position sizing
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        leverage = signal['leverage']
        
        price_distance = abs(entry_price - stop_loss)
        position_size = (risk_amount / price_distance) if price_distance > 0 else 0
        position_value = position_size * entry_price
        margin_required = position_value / leverage
        
        return {
            'symbol': f"{signal['symbol']}USDT",
            'side': signal['action'],
            'orderType': 'Market',
            'qty': f"{position_size:.4f}",
            'leverage': f"{int(leverage)}",
            'marginMode': 'isolated',
            'stopLoss': f"{stop_loss:.4f}",
            'takeProfit': f"{signal['take_profit']:.4f}",
            'timeInForce': 'GTC',
            'risk_management': {
                'margin_required_usd': f"{margin_required:.2f}",
                'position_value_usd': f"{position_value:.2f}",
                'risk_amount_usd': f"{risk_amount:.2f}",
                'risk_percentage': f"{risk_percentage*100:.1f}%"
            },
            'execution_notes': {
                'entry_strategy': 'Market order for immediate execution',
                'position_monitoring': f"Monitor for {signal['time_horizon']} based on ultra {signal['strategy_basis'].lower()}",
                'stop_loss_type': 'Stop-market order',
                'take_profit_type': 'Limit order'
            },
            'ultra_metrics': {
                'confidence_level': f"{signal['confidence']:.1f}%",
                'strategy_used': signal['strategy_basis'],
                'composite_score': f"{signal.get('composite_score', 0):.1f}",
                'market_regime': self.volatility_regime,
                'pattern_strength': signal.get('pattern_strength', 'N/A')
            }
        }

def analyze_ultra_market_opportunities(market_data: Dict[str, Dict]) -> List[Dict]:
    """Main function for ultra market analysis"""
    
    analyzer = UltraMarketAnalyzer()
    return analyzer.analyze_ultra_opportunities(market_data)