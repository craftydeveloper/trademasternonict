"""
Fast Trading Signal Generation
Optimized for immediate loading with accurate Bybit recommendations
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
# Removed numpy dependency - using built-in calculations

logger = logging.getLogger(__name__)

class FastSignalGenerator:
    """High-speed signal generation for immediate dashboard loading"""
    
    def __init__(self):
        self.min_confidence = 60
        
    def generate_fast_signals(self, current_prices: Dict[str, Dict]) -> List[Dict]:
        """Generate trading signals using current price data only"""
        signals = []
        
        for symbol, price_data in current_prices.items():
            try:
                signal = self._analyze_fast_signal(symbol, price_data)
                if signal and signal['confidence'] >= self.min_confidence:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating fast signal for {symbol}: {e}")
                continue
        
        # Sort by confidence and mark the best trade
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Mark the best signal as balanced trade and regenerate Bybit settings
        if signals:
            # Update primary trade with balanced parameters
            signals[0]['is_primary_trade'] = True
            signals[0]['trade_label'] = "YOUR TRADE"
            signals[0]['bybit_settings'] = self._generate_bybit_settings(
                signals[0]['symbol'], signals[0]['action'], signals[0]['entry_price'],
                signals[0]['stop_loss'], signals[0]['take_profit'], signals[0]['leverage'], True
            )
            
            # Mark others as secondary balanced opportunities
            for i in range(1, len(signals)):
                signals[i]['is_primary_trade'] = False
                signals[i]['trade_label'] = "YOUR TRADE"
                signals[i]['bybit_settings'] = self._generate_bybit_settings(
                    signals[i]['symbol'], signals[i]['action'], signals[i]['entry_price'],
                    signals[i]['stop_loss'], signals[i]['take_profit'], signals[i]['leverage'], False
                )
        
        return signals  # Return all signals with labels
    
    def _analyze_fast_signal(self, symbol: str, price_data: Dict) -> Optional[Dict]:
        """Analyze using current price data and momentum indicators"""
        
        current_price = price_data['price']
        change_24h = price_data.get('change_24h', 0)
        volume_24h = price_data.get('volume_24h', 0)
        
        # Enhanced momentum analysis for balanced trading
        momentum_strength = abs(change_24h)
        trend_direction = 1 if change_24h > 0 else -1
        
        # Volume confirmation with lower threshold for more opportunities
        volume_factor = min(volume_24h / 500000, 15) / 15  # Lower threshold, higher scaling
        
        # Store confidence for position sizing
        self._current_confidence = 0
        
        # Generate signal with balanced risk parameters
        if momentum_strength > 0.5 or volume_factor > 0.15:  # More inclusive for frequent trading
            
            # Enhanced confidence calculation
            base_confidence = 70 + momentum_strength * 8 + volume_factor * 20
            volatility_bonus = min(momentum_strength * 0.5, 8) if momentum_strength > 3 else 0
            confidence = min(base_confidence + volatility_bonus, 98)
            
            # Store for position sizing
            self._current_confidence = confidence
            
            if trend_direction > 0:  # Bullish signal
                stop_loss = current_price * 0.97
                take_profit = current_price * 1.06
                action = "BUY"
            else:  # Bearish signal  
                stop_loss = current_price * 1.03
                take_profit = current_price * 0.94
                action = "SELL"
            
            # Calculate risk/reward
            if action == "BUY":
                risk_amount = current_price - stop_loss
                reward_amount = take_profit - current_price
            else:
                risk_amount = stop_loss - current_price
                reward_amount = current_price - take_profit
            
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            # Generate signal with reasonable risk/reward threshold
            if risk_reward_ratio >= 1.2:
                
                # Calculate optimal leverage based on volatility
                leverage = self._calculate_optimal_leverage(momentum_strength)
                
                # Ensure exact price consistency for Bybit settings
                signal_data = {
                    'symbol': symbol,
                    'action': action,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'leverage': leverage,
                    'expected_return': (reward_amount / current_price) * 100,
                    'risk_reward_ratio': risk_reward_ratio,
                    'strategy_basis': 'Momentum Volume Analysis',
                    'time_horizon': '4H'
                }
                
                # Generate Bybit settings using exact same prices
                signal_data['bybit_settings'] = self._generate_bybit_settings(
                    symbol, action, current_price, stop_loss, take_profit, leverage
                )
                
                return signal_data
        
        return None
    
    def _calculate_optimal_leverage(self, volatility: float, confidence: float = 85.0) -> float:
        """Calculate optimal leverage based on market volatility and confidence for balanced trading"""
        
        # Conservative base leverage from volatility
        if volatility > 8:
            base_leverage = 2.0  # Very low for high volatility
        elif volatility > 5:
            base_leverage = 3.0
        elif volatility > 3:
            base_leverage = 5.0
        else:
            base_leverage = 8.0  # Maximum for stable markets
        
        # Confidence multiplier for balanced approach
        if confidence >= 95:
            multiplier = 1.2  # Slight boost for very high confidence
        elif confidence >= 90:
            multiplier = 1.1
        elif confidence >= 85:
            multiplier = 1.0
        else:
            multiplier = 0.8  # Reduce leverage for lower confidence
        
        # Cap at 15x for moderate approach  
        optimal_leverage = min(base_leverage * multiplier, 15.0)
        return max(optimal_leverage, 6.0)  # Minimum 6x for moderate strategy
    
    def _generate_bybit_settings(self, symbol: str, action: str, entry_price: float,
                                stop_loss: float, take_profit: float, leverage: float, 
                                is_primary: bool = False) -> Dict:
        """Generate optimized Bybit futures settings with exact price consistency"""
        
        # Use current account balance for trading strategy
        account_balance = 500.0  # Updated account size
        
        # MODERATE RISK SIZING - Balanced growth approach
        # Sustainable risk management for steady growth
        if leverage >= 12:
            risk_percentage = 0.08 if is_primary else 0.05  # 8%/5% - High leverage trades
        elif leverage >= 8:
            risk_percentage = 0.10 if is_primary else 0.06  # 10%/6% - Medium leverage
        else:
            risk_percentage = 0.12 if is_primary else 0.08  # 12%/8% - Lower leverage trades
        
        risk_amount = account_balance * risk_percentage
        
        if action == "BUY":
            price_distance = entry_price - stop_loss
        else:
            price_distance = stop_loss - entry_price
        
        # Position size calculation
        position_size = (risk_amount / price_distance) if price_distance > 0 else 0
        position_value = position_size * entry_price
        
        # Adjust for leverage
        margin_required = position_value / leverage
        
        return {
            'symbol': f"{symbol}USDT",
            'side': action,
            'orderType': 'Market',
            'qty': f"{position_size:.4f}",
            'leverage': f"{int(leverage)}",
            'marginMode': 'isolated',
            'stopLoss': f"{stop_loss:.4f}",
            'takeProfit': f"{take_profit:.4f}",
            'timeInForce': 'GTC',
            'risk_management': {
                'risk_amount_usd': f"{risk_amount:.2f}",
                'position_value_usd': f"{position_value:.2f}",
                'margin_required_usd': f"{margin_required:.2f}",
                'risk_percentage': f"{risk_percentage*100:.1f}%"
            },
            'execution_notes': {
                'entry_strategy': 'Market order for immediate execution',
                'stop_loss_type': 'Stop-market order',
                'take_profit_type': 'Limit order',
                'position_monitoring': 'Monitor for 4-8 hours based on momentum'
            }
        }
    
    def generate_market_overview(self, current_prices: Dict[str, Dict]) -> Dict:
        """Generate fast market overview"""
        
        if not current_prices:
            return {'error': 'No market data available'}
        
        # Calculate market metrics
        total_symbols = len(current_prices)
        price_changes = [data.get('change_24h', 0) for data in current_prices.values()]
        
        avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
        positive_moves = len([c for c in price_changes if c > 0])
        
        # Market sentiment
        if avg_change > 2:
            sentiment = 'bullish'
        elif avg_change < -2:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        # Volatility assessment
        volatility_levels = [abs(change) for change in price_changes]
        avg_volatility = sum(volatility_levels) / len(volatility_levels) if volatility_levels else 0
        
        if avg_volatility > 6:
            volatility = 'high'
        elif avg_volatility > 3:
            volatility = 'moderate'
        else:
            volatility = 'low'
        
        # Top movers
        symbol_changes = [(symbol, data.get('change_24h', 0)) 
                         for symbol, data in current_prices.items()]
        
        top_gainers = sorted(symbol_changes, key=lambda x: x[1], reverse=True)[:3]
        top_losers = sorted(symbol_changes, key=lambda x: x[1])[:3]
        
        return {
            'market_overview': {
                'total_tracked_assets': total_symbols,
                'average_24h_change': avg_change,
                'market_sentiment': sentiment,
                'volatility_level': volatility,
                'bullish_ratio': (positive_moves / total_symbols) * 100 if total_symbols > 0 else 0
            },
            'top_movers': {
                'gainers': top_gainers,
                'losers': top_losers
            },
            'trading_conditions': {
                'recommended_leverage': self._get_market_leverage_recommendation(avg_volatility),
                'risk_level': 'high' if avg_volatility > 6 else 'moderate' if avg_volatility > 3 else 'low',
                'optimal_timeframes': ['4H', '1D'] if volatility == 'low' else ['1H', '4H'],
                'market_phase': self._determine_market_phase(avg_change, avg_volatility)
            }
        }
    
    def _get_market_leverage_recommendation(self, volatility: float) -> str:
        """Recommend leverage based on market volatility"""
        if volatility > 6:
            return "2-3x (High volatility - use caution)"
        elif volatility > 3:
            return "3-5x (Moderate volatility - standard risk)"
        else:
            return "5-8x (Low volatility - opportunity for higher leverage)"
    
    def _determine_market_phase(self, avg_change: float, volatility: float) -> str:
        """Determine current market phase"""
        if abs(avg_change) > 5 and volatility > 6:
            return "High volatility trend"
        elif avg_change > 3:
            return "Bull run"
        elif avg_change < -3:
            return "Bear market"
        elif volatility < 2:
            return "Consolidation"
        else:
            return "Normal trading"