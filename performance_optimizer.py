"""
Performance Optimizer - Real-time Signal Quality Enhancement
Continuously optimizes signal parameters for maximum trading performance
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Real-time performance optimization for trading signals"""
    
    def __init__(self):
        # Performance tracking
        self.signal_history = []
        self.performance_metrics = {
            'total_signals': 0,
            'successful_signals': 0,
            'win_rate': 0.0,
            'avg_return': 0.0,
            'risk_adjusted_return': 0.0
        }
        
        # Dynamic thresholds
        self.dynamic_confidence_threshold = 88.0
        self.dynamic_risk_reward_minimum = 2.5
        self.performance_window = 100  # Last 100 signals
        
        # Strategy performance weights
        self.strategy_weights = {
            'Ultra Momentum Breakout': 1.0,
            'Volume Surge Analysis': 1.0,
            'Support/Resistance Analysis': 1.0,
            'Divergence Pattern Analysis': 1.0,
            'Breakout Pattern Analysis': 1.0
        }
        
    def optimize_signals(self, raw_signals: List[Dict]) -> List[Dict]:
        """Optimize signals based on historical performance"""
        
        if not raw_signals:
            return []
        
        # Update performance metrics
        self._update_performance_metrics()
        
        # Apply dynamic filtering
        optimized_signals = []
        
        for signal in raw_signals:
            # Strategy-specific optimization
            optimized_signal = self._optimize_signal_parameters(signal)
            
            if optimized_signal and self._passes_quality_filter(optimized_signal):
                optimized_signals.append(optimized_signal)
        
        # Rank and select best signals
        final_signals = self._rank_and_select_signals(optimized_signals)
        
        # Apply portfolio-level optimization
        portfolio_optimized = self._optimize_portfolio_allocation(final_signals)
        
        logger.info(f"Performance optimizer: {len(raw_signals)} → {len(portfolio_optimized)} signals")
        
        return portfolio_optimized
    
    def _optimize_signal_parameters(self, signal: Dict) -> Optional[Dict]:
        """Optimize individual signal parameters based on strategy performance"""
        
        strategy = signal.get('strategy_basis', 'Unknown')
        weight = self.strategy_weights.get(strategy, 1.0)
        
        # Adjust confidence based on strategy performance
        original_confidence = signal['confidence']
        adjusted_confidence = original_confidence * weight
        
        # Ensure confidence stays within reasonable bounds
        adjusted_confidence = max(75.0, min(99.0, adjusted_confidence))
        
        # Dynamic leverage optimization
        volatility_factor = signal.get('pattern_strength', 1.0) / 10.0
        market_regime = signal.get('market_regime', 'normal')
        
        optimized_leverage = self._calculate_optimized_leverage(
            signal['leverage'], adjusted_confidence, volatility_factor, market_regime
        )
        
        # Risk management optimization
        optimized_stops = self._optimize_stop_levels(signal)
        
        # Create optimized signal
        optimized_signal = signal.copy()
        optimized_signal.update({
            'confidence': adjusted_confidence,
            'leverage': optimized_leverage,
            'stop_loss': optimized_stops['stop_loss'],
            'take_profit': optimized_stops['take_profit'],
            'optimization_applied': True,
            'original_confidence': original_confidence,
            'strategy_weight': weight
        })
        
        # Recalculate risk/reward with optimized parameters
        risk = abs(optimized_signal['entry_price'] - optimized_signal['stop_loss'])
        reward = abs(optimized_signal['take_profit'] - optimized_signal['entry_price'])
        optimized_signal['risk_reward_ratio'] = reward / risk if risk > 0 else 0
        
        return optimized_signal
    
    def _calculate_optimized_leverage(self, base_leverage: float, confidence: float, 
                                    volatility: float, market_regime: str) -> float:
        """Calculate optimized leverage based on multiple factors"""
        
        # Start with base leverage
        optimized_leverage = base_leverage
        
        # Confidence adjustment
        confidence_multiplier = 0.8 + (confidence / 100.0) * 0.4
        optimized_leverage *= confidence_multiplier
        
        # Volatility adjustment
        if volatility > 0.15:
            optimized_leverage *= 0.7
        elif volatility > 0.10:
            optimized_leverage *= 0.85
        elif volatility < 0.05:
            optimized_leverage *= 1.15
        
        # Market regime adjustment
        if market_regime == 'high':
            optimized_leverage *= 0.75
        elif market_regime == 'elevated':
            optimized_leverage *= 0.9
        
        # Performance-based adjustment
        if self.performance_metrics['win_rate'] > 0.7:
            optimized_leverage *= 1.1
        elif self.performance_metrics['win_rate'] < 0.5:
            optimized_leverage *= 0.8
        
        # Ensure leverage stays within safe bounds for $500 account
        return max(3.0, min(20.0, optimized_leverage))
    
    def _optimize_stop_levels(self, signal: Dict) -> Dict:
        """Optimize stop loss and take profit levels"""
        
        entry_price = signal['entry_price']
        original_stop = signal['stop_loss']
        original_target = signal['take_profit']
        action = signal['action']
        
        # Calculate current risk/reward
        current_risk = abs(entry_price - original_stop)
        current_reward = abs(original_target - entry_price)
        
        # Optimize based on volatility and confidence
        volatility = signal.get('volatility_24h', 5.0) / 100.0
        confidence = signal['confidence']
        
        # Dynamic stop distance based on volatility
        if volatility > 0.08:  # High volatility
            stop_multiplier = 1.2
            target_multiplier = 1.3
        elif volatility > 0.05:  # Medium volatility
            stop_multiplier = 1.0
            target_multiplier = 1.1
        else:  # Low volatility
            stop_multiplier = 0.8
            target_multiplier = 0.9
        
        # Confidence-based adjustment
        if confidence > 95:
            stop_multiplier *= 0.9  # Tighter stops for high confidence
            target_multiplier *= 1.2  # Higher targets
        
        # Calculate optimized levels
        optimized_risk = current_risk * stop_multiplier
        optimized_reward = current_reward * target_multiplier
        
        if action == "BUY":
            optimized_stop = entry_price - optimized_risk
            optimized_target = entry_price + optimized_reward
        else:
            optimized_stop = entry_price + optimized_risk
            optimized_target = entry_price - optimized_reward
        
        # Ensure minimum risk/reward ratio
        risk_reward = optimized_reward / optimized_risk if optimized_risk > 0 else 0
        if risk_reward < 2.0:
            # Adjust target to maintain 2:1 minimum
            optimized_reward = optimized_risk * 2.0
            if action == "BUY":
                optimized_target = entry_price + optimized_reward
            else:
                optimized_target = entry_price - optimized_reward
        
        return {
            'stop_loss': optimized_stop,
            'take_profit': optimized_target
        }
    
    def _passes_quality_filter(self, signal: Dict) -> bool:
        """Apply dynamic quality filters"""
        
        # Dynamic confidence threshold
        if signal['confidence'] < self.dynamic_confidence_threshold:
            return False
        
        # Risk/reward requirement
        if signal['risk_reward_ratio'] < self.dynamic_risk_reward_minimum:
            return False
        
        # Strategy-specific filters
        strategy = signal.get('strategy_basis', '')
        
        # Volume surge signals need higher volume
        if 'Volume Surge' in strategy:
            volume_factor = signal.get('volume_surge_factor', 0)
            if volume_factor < 1.5:
                return False
        
        # Breakout signals need strong momentum
        if 'Breakout' in strategy:
            pattern_strength = signal.get('pattern_strength', 0)
            if pattern_strength < 3.0:
                return False
        
        # Divergence signals need clear divergence
        if 'Divergence' in strategy:
            divergence_strength = signal.get('divergence_strength', 0)
            if divergence_strength < 2.0:
                return False
        
        return True
    
    def _rank_and_select_signals(self, signals: List[Dict]) -> List[Dict]:
        """Rank signals by optimized composite score"""
        
        for signal in signals:
            # Calculate enhanced composite score
            confidence_score = signal['confidence'] * 0.35
            risk_reward_score = min(signal['risk_reward_ratio'] * 15, 50) * 0.25
            leverage_efficiency = min(signal['leverage'] / 15.0, 1.0) * 20 * 0.15
            
            # Strategy-specific bonuses
            strategy_bonus = 0
            strategy = signal.get('strategy_basis', '')
            
            if 'Ultra Momentum' in strategy:
                momentum = signal.get('pattern_strength', 0)
                strategy_bonus = min(momentum * 2, 10)
            elif 'Volume Surge' in strategy:
                volume_factor = signal.get('volume_surge_factor', 0)
                strategy_bonus = min(volume_factor * 3, 12)
            elif 'Support/Resistance' in strategy:
                proximity = signal.get('level_proximity', 0)
                strategy_bonus = min((1 - proximity) * 15, 8)
            
            # Market condition bonus
            market_bonus = 0
            if signal.get('volume_confirmation', False):
                market_bonus += 5
            if signal.get('trend_alignment', False):
                market_bonus += 3
            
            # Performance weight
            strategy_weight = signal.get('strategy_weight', 1.0)
            
            composite_score = (
                confidence_score + 
                risk_reward_score + 
                leverage_efficiency + 
                strategy_bonus + 
                market_bonus
            ) * strategy_weight
            
            signal['optimized_composite_score'] = composite_score
        
        # Sort by optimized composite score
        signals.sort(key=lambda x: x.get('optimized_composite_score', 0), reverse=True)
        
        # Select top 5 signals for optimal portfolio
        return signals[:5]
    
    def _optimize_portfolio_allocation(self, signals: List[Dict]) -> List[Dict]:
        """Optimize portfolio-level allocation"""
        
        if not signals:
            return signals
        
        # Calculate total risk allocation
        total_risk = 0.0
        for signal in signals:
            confidence = signal['confidence']
            if confidence >= 96:
                risk_percentage = 0.18 if signal.get('is_primary_trade') else 0.12
            elif confidence >= 92:
                risk_percentage = 0.15 if signal.get('is_primary_trade') else 0.10
            else:
                risk_percentage = 0.12 if signal.get('is_primary_trade') else 0.08
            
            total_risk += risk_percentage
        
        # Ensure total risk doesn't exceed 50% for safety
        max_total_risk = 0.45  # 45% maximum total risk
        
        if total_risk > max_total_risk:
            # Scale down risk allocation proportionally
            scale_factor = max_total_risk / total_risk
            
            for signal in signals:
                # Update Bybit settings with scaled risk
                if 'bybit_settings' in signal:
                    original_risk = float(signal['bybit_settings']['risk_management']['risk_percentage'].rstrip('%'))
                    scaled_risk = original_risk * scale_factor
                    
                    # Recalculate position sizing with scaled risk
                    account_balance = 500.0
                    risk_amount = account_balance * (scaled_risk / 100.0)
                    
                    entry_price = signal['entry_price']
                    stop_loss = signal['stop_loss']
                    leverage = signal['leverage']
                    
                    price_distance = abs(entry_price - stop_loss)
                    position_size = (risk_amount / price_distance) if price_distance > 0 else 0
                    position_value = position_size * entry_price
                    margin_required = position_value / leverage
                    
                    # Update Bybit settings
                    signal['bybit_settings'].update({
                        'qty': f"{position_size:.4f}",
                        'risk_management': {
                            'margin_required_usd': f"{margin_required:.2f}",
                            'position_value_usd': f"{position_value:.2f}",
                            'risk_amount_usd': f"{risk_amount:.2f}",
                            'risk_percentage': f"{scaled_risk:.1f}%"
                        }
                    })
        
        # Ensure diversification - limit same-direction trades
        buy_signals = [s for s in signals if s['action'] == 'BUY']
        sell_signals = [s for s in signals if s['action'] == 'SELL']
        
        # Maintain balance - max 60% in one direction
        max_directional = 3
        
        diversified_signals = []
        
        # Add top signals from each direction
        for i in range(max(len(buy_signals), len(sell_signals))):
            if i < len(sell_signals) and len([s for s in diversified_signals if s['action'] == 'SELL']) < max_directional:
                diversified_signals.append(sell_signals[i])
            
            if i < len(buy_signals) and len([s for s in diversified_signals if s['action'] == 'BUY']) < max_directional:
                diversified_signals.append(buy_signals[i])
            
            if len(diversified_signals) >= 5:
                break
        
        return diversified_signals
    
    def _update_performance_metrics(self):
        """Update performance metrics based on signal history"""
        
        # This would be enhanced with actual trade results
        # For now, simulate based on confidence levels
        
        if len(self.signal_history) > 0:
            recent_signals = self.signal_history[-self.performance_window:]
            
            # Estimate performance based on confidence
            estimated_wins = sum(1 for s in recent_signals if s.get('confidence', 0) > 90)
            total_signals = len(recent_signals)
            
            self.performance_metrics.update({
                'total_signals': total_signals,
                'successful_signals': estimated_wins,
                'win_rate': estimated_wins / total_signals if total_signals > 0 else 0.0
            })
            
            # Adjust dynamic thresholds based on performance
            if self.performance_metrics['win_rate'] > 0.75:
                self.dynamic_confidence_threshold = max(85.0, self.dynamic_confidence_threshold - 1.0)
            elif self.performance_metrics['win_rate'] < 0.60:
                self.dynamic_confidence_threshold = min(92.0, self.dynamic_confidence_threshold + 1.0)
    
    def record_signal_result(self, signal: Dict, result: Dict):
        """Record actual signal result for performance tracking"""
        
        signal_record = {
            'timestamp': datetime.utcnow(),
            'signal': signal,
            'result': result,
            'strategy': signal.get('strategy_basis', 'Unknown')
        }
        
        self.signal_history.append(signal_record)
        
        # Update strategy weights based on results
        strategy = signal.get('strategy_basis', 'Unknown')
        if strategy in self.strategy_weights:
            success = result.get('successful', False)
            
            if success:
                self.strategy_weights[strategy] = min(1.2, self.strategy_weights[strategy] + 0.05)
            else:
                self.strategy_weights[strategy] = max(0.8, self.strategy_weights[strategy] - 0.03)
        
        logger.info(f"Recorded signal result for {strategy}: {result}")

def optimize_trading_signals(raw_signals: List[Dict]) -> List[Dict]:
    """Main function to optimize trading signals for maximum performance"""
    
    optimizer = PerformanceOptimizer()
    return optimizer.optimize_signals(raw_signals)