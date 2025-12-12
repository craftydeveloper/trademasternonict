"""
Enhanced Signal Scanner - Advanced Trading Signal Detection
Comprehensive scanning system for optimal trading opportunities
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class EnhancedSignalScanner:
    """Advanced signal scanner with multiple analysis layers"""
    
    def __init__(self):
        self.confidence_threshold = 85.0  # Higher threshold for quality
        self.min_risk_reward = 2.0
        self.max_signals = 6
        
        # Market conditions assessment
        self.market_volatility = 0.0
        self.trend_strength = 0.0
        self.volume_momentum = 0.0
        
    def scan_all_opportunities(self, market_data: Dict[str, Dict]) -> List[Dict]:
        """Comprehensive scan of all trading opportunities"""
        
        if not market_data:
            logger.warning("No market data available for scanning")
            return []
        
        # Assess overall market conditions
        self._assess_market_conditions(market_data)
        
        all_signals = []
        
        for symbol, price_data in market_data.items():
            try:
                # Multi-layer analysis for each symbol
                signals = self._analyze_symbol_comprehensive(symbol, price_data)
                all_signals.extend(signals)
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        # Filter and rank signals
        filtered_signals = self._filter_and_rank_signals(all_signals)
        
        # Generate optimized Bybit settings
        enhanced_signals = []
        for i, signal in enumerate(filtered_signals[:self.max_signals]):
            signal['is_primary_trade'] = (i == 0)
            signal['trade_label'] = "YOUR TRADE"
            signal['bybit_settings'] = self._generate_enhanced_bybit_settings(
                signal, is_primary=(i == 0)
            )
            enhanced_signals.append(signal)
        
        return enhanced_signals
    
    def _assess_market_conditions(self, market_data: Dict[str, Dict]):
        """Assess overall market conditions for context"""
        
        price_changes = []
        volumes = []
        
        for symbol, data in market_data.items():
            if 'price_change_24h' in data:
                price_changes.append(data['price_change_24h'])
            if 'volume_24h' in data:
                volumes.append(data['volume_24h'])
        
        if price_changes:
            avg_change = sum(price_changes) / len(price_changes)
            volatility = sum(abs(change - avg_change) for change in price_changes) / len(price_changes)
            
            self.market_volatility = min(volatility, 20.0) / 20.0  # Normalize 0-1
            self.trend_strength = abs(avg_change) / 10.0  # Normalize trend strength
        
        if volumes:
            avg_volume = sum(volumes) / len(volumes)
            self.volume_momentum = min(avg_volume / 1000000, 1.0)  # Normalize volume
    
    def _analyze_symbol_comprehensive(self, symbol: str, price_data: Dict) -> List[Dict]:
        """Comprehensive multi-strategy analysis for a symbol"""
        
        signals = []
        current_price = price_data.get('price', 0)
        
        if current_price <= 0:
            return signals
        
        # Strategy 1: Momentum + Volume Analysis
        momentum_signal = self._analyze_momentum_volume(symbol, price_data)
        if momentum_signal:
            signals.append(momentum_signal)
        
        # Strategy 2: Support/Resistance Breakout
        breakout_signal = self._analyze_breakout_patterns(symbol, price_data)
        if breakout_signal:
            signals.append(breakout_signal)
        
        # Strategy 3: Mean Reversion with RSI
        reversion_signal = self._analyze_mean_reversion(symbol, price_data)
        if reversion_signal:
            signals.append(reversion_signal)
        
        # Strategy 4: Volatility Expansion
        volatility_signal = self._analyze_volatility_expansion(symbol, price_data)
        if volatility_signal:
            signals.append(volatility_signal)
        
        return signals
    
    def _analyze_momentum_volume(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Enhanced momentum analysis with volume confirmation"""
        
        current_price = price_data.get('price', 0)
        price_change = price_data.get('price_change_24h', 0)
        volume_24h = price_data.get('volume_24h', 0)
        
        # Calculate momentum strength
        momentum = abs(price_change)
        volume_factor = min(volume_24h / 1000000, 2.0)  # Volume boost factor
        
        # Confidence calculation with multiple factors
        base_confidence = min(momentum * 2 + volume_factor * 10, 100)
        
        # Market condition adjustments
        market_boost = self.market_volatility * 5 + self.volume_momentum * 10
        confidence = min(base_confidence + market_boost, 99)
        
        if confidence < self.confidence_threshold:
            return None
        
        # Determine direction and targets
        if price_change < -2:  # Bearish momentum
            action = "SELL"
            stop_loss = current_price * 1.03  # 3% stop loss
            take_profit = current_price * 0.94  # 6% target
        elif price_change > 2:  # Bullish momentum
            action = "BUY"
            stop_loss = current_price * 0.97  # 3% stop loss
            take_profit = current_price * 1.06  # 6% target
        else:
            return None
        
        # Calculate risk/reward
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < self.min_risk_reward:
            return None
        
        # Enhanced leverage calculation
        volatility_factor = momentum / 10.0
        leverage = self._calculate_optimal_leverage(volatility_factor, confidence)
        
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
            'strategy_basis': 'Enhanced Momentum Volume Analysis',
            'time_horizon': '4H',
            'market_factors': {
                'momentum_strength': momentum,
                'volume_factor': volume_factor,
                'market_volatility': self.market_volatility,
                'trend_alignment': price_change > 0
            }
        }
    
    def _analyze_breakout_patterns(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Analyze breakout patterns with enhanced detection"""
        
        current_price = price_data.get('price', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        volume_24h = price_data.get('volume_24h', 0)
        
        # Calculate breakout strength
        price_range = high_24h - low_24h
        if price_range <= 0:
            return None
        
        # Position within range
        range_position = (current_price - low_24h) / price_range
        
        # Breakout detection
        breakout_threshold = 0.15  # 15% from range extremes
        
        if range_position > (1 - breakout_threshold):  # Near high - potential continuation
            action = "BUY"
            confidence = 75 + (range_position - 0.85) * 100  # Scale confidence
            stop_loss = current_price * 0.96
            take_profit = current_price * 1.08
            
        elif range_position < breakout_threshold:  # Near low - potential reversal
            action = "SELL"
            confidence = 75 + (0.15 - range_position) * 100
            stop_loss = current_price * 1.04
            take_profit = current_price * 0.92
            
        else:
            return None
        
        # Volume confirmation
        if volume_24h > 500000:  # High volume confirmation
            confidence += 10
        
        confidence = min(confidence, 98)
        
        if confidence < self.confidence_threshold:
            return None
        
        # Risk/reward validation
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < self.min_risk_reward:
            return None
        
        leverage = self._calculate_optimal_leverage(price_range / current_price, confidence)
        
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
            'strategy_basis': 'Breakout Pattern Analysis',
            'time_horizon': '6H',
            'pattern_data': {
                'range_position': range_position,
                'breakout_strength': abs(range_position - 0.5) * 2,
                'volume_confirmation': volume_24h > 500000
            }
        }
    
    def _analyze_mean_reversion(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Mean reversion analysis with RSI-like indicators"""
        
        current_price = price_data.get('price', 0)
        price_change = price_data.get('price_change_24h', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        
        # Calculate relative position and momentum
        price_range = high_24h - low_24h
        if price_range <= 0:
            return None
        
        relative_position = (current_price - low_24h) / price_range
        momentum = abs(price_change)
        
        # Mean reversion conditions
        if relative_position > 0.8 and price_change > 5:  # Overbought
            action = "SELL"
            confidence = 70 + min(momentum, 20)
            stop_loss = current_price * 1.025
            take_profit = current_price * 0.955
            
        elif relative_position < 0.2 and price_change < -5:  # Oversold
            action = "BUY"
            confidence = 70 + min(momentum, 20)
            stop_loss = current_price * 0.975
            take_profit = current_price * 1.045
            
        else:
            return None
        
        # Market condition adjustments
        if self.market_volatility > 0.6:  # High volatility favors reversion
            confidence += 8
        
        confidence = min(confidence, 97)
        
        if confidence < self.confidence_threshold:
            return None
        
        # Risk/reward validation
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < 1.8:  # Slightly lower threshold for reversion
            return None
        
        leverage = self._calculate_optimal_leverage(momentum / 15.0, confidence)
        
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
            'strategy_basis': 'Mean Reversion Analysis',
            'time_horizon': '2H',
            'reversion_data': {
                'relative_position': relative_position,
                'momentum_factor': momentum,
                'market_volatility': self.market_volatility
            }
        }
    
    def _analyze_volatility_expansion(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Volatility expansion pattern analysis"""
        
        current_price = price_data.get('price', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        price_change = price_data.get('price_change_24h', 0)
        
        # Calculate volatility metrics
        price_range = high_24h - low_24h
        volatility_ratio = price_range / current_price if current_price > 0 else 0
        
        # Look for volatility expansion opportunities
        if volatility_ratio < 0.02:  # Low volatility - compression
            return None
        
        if volatility_ratio > 0.08:  # High volatility - expansion opportunity
            
            # Direction based on recent momentum
            if abs(price_change) > 3:
                action = "SELL" if price_change < 0 else "BUY"
                
                confidence = 65 + min(volatility_ratio * 200, 25)
                
                if action == "BUY":
                    stop_loss = current_price * 0.965
                    take_profit = current_price * 1.07
                else:
                    stop_loss = current_price * 1.035
                    take_profit = current_price * 0.93
                
                # Volume and market condition boosts
                volume_24h = price_data.get('volume_24h', 0)
                if volume_24h > 1000000:
                    confidence += 8
                
                if self.trend_strength > 0.3:
                    confidence += 5
                
                confidence = min(confidence, 96)
                
                if confidence < self.confidence_threshold:
                    return None
                
                # Risk/reward validation
                risk = abs(current_price - stop_loss)
                reward = abs(take_profit - current_price)
                risk_reward = reward / risk if risk > 0 else 0
                
                if risk_reward < self.min_risk_reward:
                    return None
                
                leverage = self._calculate_optimal_leverage(volatility_ratio * 2, confidence)
                
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
                    'strategy_basis': 'Volatility Expansion Analysis',
                    'time_horizon': '3H',
                    'volatility_data': {
                        'volatility_ratio': volatility_ratio,
                        'expansion_strength': min(volatility_ratio * 10, 1.0),
                        'momentum_alignment': abs(price_change) > 3
                    }
                }
        
        return None
    
    def _calculate_optimal_leverage(self, volatility: float, confidence: float) -> float:
        """Calculate optimal leverage based on volatility and confidence"""
        
        # Base leverage from volatility (inverse relationship)
        if volatility > 0.15:
            base_leverage = 3.0
        elif volatility > 0.10:
            base_leverage = 5.0
        elif volatility > 0.05:
            base_leverage = 8.0
        else:
            base_leverage = 12.0
        
        # Confidence multiplier
        confidence_factor = confidence / 100.0
        leverage = base_leverage * (0.8 + confidence_factor * 0.5)
        
        # Market condition adjustments
        if self.market_volatility > 0.7:  # High market volatility
            leverage *= 0.8
        elif self.volume_momentum > 0.6:  # High volume
            leverage *= 1.1
        
        # Account size consideration ($500 account)
        leverage = min(leverage, 20.0)  # Maximum 20x for safety
        return max(leverage, 4.0)  # Minimum 4x
    
    def _filter_and_rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """Filter and rank signals by quality metrics"""
        
        if not signals:
            return []
        
        # Filter by minimum criteria
        filtered = []
        for signal in signals:
            if (signal['confidence'] >= self.confidence_threshold and 
                signal['risk_reward_ratio'] >= self.min_risk_reward):
                filtered.append(signal)
        
        # Rank by composite score
        for signal in filtered:
            score = (
                signal['confidence'] * 0.4 +
                signal['risk_reward_ratio'] * 20 * 0.3 +
                signal['expected_return'] * 0.2 +
                signal['leverage'] * 0.1
            )
            signal['composite_score'] = score
        
        # Sort by composite score
        filtered.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return filtered
    
    def _generate_enhanced_bybit_settings(self, signal: Dict, is_primary: bool = False) -> Dict:
        """Generate enhanced Bybit settings with optimal position sizing"""
        
        account_balance = 500.0  # $500 account
        
        # Dynamic risk sizing based on confidence and signal quality
        if signal['confidence'] >= 95:
            risk_percentage = 0.15 if is_primary else 0.10  # 15%/10% for ultra-high confidence
        elif signal['confidence'] >= 90:
            risk_percentage = 0.12 if is_primary else 0.08  # 12%/8% for very high confidence
        else:
            risk_percentage = 0.10 if is_primary else 0.06  # 10%/6% for high confidence
        
        risk_amount = account_balance * risk_percentage
        
        # Position sizing calculation
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
                'position_monitoring': f"Monitor for {signal['time_horizon']} based on {signal['strategy_basis'].lower()}",
                'stop_loss_type': 'Stop-market order',
                'take_profit_type': 'Limit order'
            },
            'signal_quality': {
                'confidence_level': f"{signal['confidence']:.1f}%",
                'strategy_used': signal['strategy_basis'],
                'composite_score': f"{signal.get('composite_score', 0):.1f}"
            }
        }

def scan_enhanced_opportunities(market_data: Dict[str, Dict]) -> List[Dict]:
    """Main function to scan for enhanced trading opportunities"""
    
    scanner = EnhancedSignalScanner()
    return scanner.scan_all_opportunities(market_data)