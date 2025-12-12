"""
Professional Trading System Integration
Combines all advanced components for institutional-grade trading
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from risk_manager import RiskManager
from portfolio_optimizer import PortfolioOptimizer
from advanced_signals import AdvancedSignalGenerator, TradingSignal, SignalType
from market_data_client import MarketDataClient

logger = logging.getLogger(__name__)

@dataclass
class TradingRecommendation:
    symbol: str
    action: str
    confidence: float
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    leverage: float
    risk_amount: float
    expected_return: float
    time_horizon: str
    strategy_basis: str
    risk_metrics: Dict

class ProfessionalTradingSystem:
    """Complete professional trading system with risk management"""
    
    def __init__(self, initial_balance: float = 10000):
        self.risk_manager = RiskManager(initial_balance)
        self.portfolio_optimizer = PortfolioOptimizer()
        self.signal_generator = AdvancedSignalGenerator()
        self.market_client = MarketDataClient()
        
        self.active_positions = {}
        self.trade_journal = []
        self.performance_metrics = {}
        
    def generate_professional_recommendations(self) -> List[TradingRecommendation]:
        """Generate comprehensive trading recommendations"""
        
        recommendations = []
        
        # Get current market data
        current_prices = self.market_client.get_real_time_prices()
        if not current_prices:
            logger.error("Cannot generate recommendations without market data")
            return []
        
        # Generate signals for each symbol
        for symbol, price_data in current_prices.items():
            try:
                # Get historical data for analysis
                historical_data = self.market_client.get_historical_data(symbol, 30)
                if not historical_data:
                    continue
                
                current_price = price_data['price']
                
                # Generate advanced signals
                signals = self.signal_generator.generate_comprehensive_signals(
                    symbol, historical_data, current_price
                )
                
                # Process each signal
                for signal in signals:
                    if signal.confidence >= 65:  # High confidence threshold
                        recommendation = self._create_recommendation(signal, price_data)
                        if recommendation:
                            recommendations.append(recommendation)
                            
            except Exception as e:
                logger.error(f"Error generating recommendation for {symbol}: {e}")
                continue
        
        # Sort by confidence and expected return
        recommendations.sort(key=lambda x: (x.confidence, x.expected_return), reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _create_recommendation(self, signal: TradingSignal, 
                             market_data: Dict) -> Optional[TradingRecommendation]:
        """Create detailed trading recommendation from signal"""
        
        try:
            # Validate signal with risk management
            validation = self.risk_manager.validate_trade(
                symbol=signal.symbol,
                side=signal.signal_type.value,
                size=1000,  # Base size for calculation
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            if not validation['approved']:
                return None
            
            # Calculate optimal position size
            risk_percent = min(signal.confidence / 100 * 2, 2.0)  # Max 2% risk
            position_calc = self.risk_manager.calculate_position_size(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                risk_percent=risk_percent
            )
            
            # Calculate expected return
            if signal.signal_type == SignalType.BUY:
                expected_return = ((signal.take_profit - signal.entry_price) / 
                                 signal.entry_price) * 100
            else:
                expected_return = ((signal.entry_price - signal.take_profit) / 
                                 signal.entry_price) * 100
            
            # Adjust leverage based on volatility and confidence
            volatility = abs(market_data.get('change_24h', 0))
            base_leverage = signal.leverage
            
            if volatility > 10:  # High volatility
                adjusted_leverage = max(base_leverage * 0.7, 2.0)
            elif volatility < 3:  # Low volatility
                adjusted_leverage = min(base_leverage * 1.2, 10.0)
            else:
                adjusted_leverage = base_leverage
            
            # Risk metrics
            risk_metrics = {
                'var_95': position_calc['risk_amount'],
                'max_loss': position_calc['risk_amount'],
                'leverage_used': adjusted_leverage,
                'position_value': position_calc['position_value'],
                'risk_reward_ratio': signal.risk_reward_ratio,
                'volatility_24h': volatility
            }
            
            return TradingRecommendation(
                symbol=signal.symbol,
                action=signal.signal_type.value,
                confidence=signal.confidence,
                position_size=position_calc['position_size'],
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                leverage=adjusted_leverage,
                risk_amount=position_calc['risk_amount'],
                expected_return=expected_return,
                time_horizon=signal.timeframe,
                strategy_basis=signal.strategy_name,
                risk_metrics=risk_metrics
            )
            
        except Exception as e:
            logger.error(f"Error creating recommendation for {signal.symbol}: {e}")
            return None
    
    def generate_portfolio_analysis(self) -> Dict:
        """Generate comprehensive portfolio analysis"""
        
        current_prices = self.market_client.get_real_time_prices()
        if not current_prices:
            return {'error': 'Market data unavailable'}
        
        # Portfolio allocation recommendation
        allocation = self.portfolio_optimizer.generate_allocation_recommendation(
            market_data=current_prices,
            risk_tolerance='moderate'
        )
        
        # Risk assessment
        risk_report = self.risk_manager.generate_risk_report()
        
        # Market regime analysis
        btc_historical = self.market_client.get_historical_data('BTC', 30)
        regime_analysis = {}
        
        if btc_historical:
            btc_returns = []
            for i in range(1, len(btc_historical)):
                prev_price = btc_historical[i-1]['price']
                curr_price = btc_historical[i]['price']
                daily_return = (curr_price - prev_price) / prev_price
                btc_returns.append(daily_return)
            
            regime_analysis = self.portfolio_optimizer.detect_regime_change(btc_returns)
        
        return {
            'portfolio_allocation': allocation,
            'risk_assessment': risk_report,
            'market_regime': regime_analysis,
            'current_prices': current_prices,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_trade_performance(self, trade_result: Dict) -> Dict:
        """Calculate detailed trade performance metrics"""
        
        # Update risk manager with trade result
        self.risk_manager.update_performance(trade_result)
        
        # Calculate performance metrics
        entry_price = trade_result.get('entry_price', 0)
        exit_price = trade_result.get('exit_price', 0)
        size = trade_result.get('size', 0)
        side = trade_result.get('side', 'BUY')
        
        if side == 'BUY':
            pnl = (exit_price - entry_price) * size
            return_pct = ((exit_price - entry_price) / entry_price) * 100
        else:
            pnl = (entry_price - exit_price) * size
            return_pct = ((entry_price - exit_price) / entry_price) * 100
        
        # Risk-adjusted metrics
        risk_amount = trade_result.get('risk_amount', abs(pnl))
        risk_adjusted_return = return_pct / (risk_amount / self.risk_manager.account_balance * 100)
        
        performance = {
            'pnl': pnl,
            'return_percent': return_pct,
            'risk_adjusted_return': risk_adjusted_return,
            'trade_efficiency': abs(pnl) / risk_amount if risk_amount > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to trade journal
        self.trade_journal.append({
            **trade_result,
            **performance
        })
        
        return performance
    
    def get_market_insights(self) -> Dict:
        """Generate professional market insights"""
        
        current_prices = self.market_client.get_real_time_prices()
        if not current_prices:
            return {'error': 'Market data unavailable'}
        
        insights = {
            'market_overview': {},
            'sector_analysis': {},
            'volatility_assessment': {},
            'correlation_matrix': {},
            'trading_opportunities': []
        }
        
        # Market overview
        total_market_cap = sum(
            price_data['price'] * price_data.get('volume_24h', 0) / price_data['price']
            for price_data in current_prices.values()
        )
        
        avg_24h_change = sum(
            price_data.get('change_24h', 0) for price_data in current_prices.values()
        ) / len(current_prices)
        
        insights['market_overview'] = {
            'total_tracked_assets': len(current_prices),
            'average_24h_change': avg_24h_change,
            'market_sentiment': 'bullish' if avg_24h_change > 2 else 'bearish' if avg_24h_change < -2 else 'neutral',
            'volatility_level': 'high' if abs(avg_24h_change) > 5 else 'normal'
        }
        
        # Volatility assessment
        volatility_data = {}
        for symbol, price_data in current_prices.items():
            vol_24h = abs(price_data.get('change_24h', 0))
            volatility_data[symbol] = {
                'volatility_24h': vol_24h,
                'risk_level': 'high' if vol_24h > 8 else 'medium' if vol_24h > 4 else 'low'
            }
        
        insights['volatility_assessment'] = volatility_data
        
        # Top movers
        top_gainers = sorted(
            current_prices.items(),
            key=lambda x: x[1].get('change_24h', 0),
            reverse=True
        )[:3]
        
        top_losers = sorted(
            current_prices.items(),
            key=lambda x: x[1].get('change_24h', 0)
        )[:3]
        
        insights['top_movers'] = {
            'gainers': [(symbol, data['change_24h']) for symbol, data in top_gainers],
            'losers': [(symbol, data['change_24h']) for symbol, data in top_losers]
        }
        
        return insights
    
    def generate_bybit_settings(self, recommendation: TradingRecommendation) -> Dict:
        """Generate optimal Bybit futures trading settings"""
        
        return {
            'symbol': f"{recommendation.symbol}USDT",
            'side': recommendation.action,
            'orderType': 'Market',  # or 'Limit' for better fills
            'qty': str(recommendation.position_size),
            'leverage': str(int(recommendation.leverage)),
            'marginMode': 'isolated',  # Safer than cross margin
            'stopLoss': str(recommendation.stop_loss),
            'takeProfit': str(recommendation.take_profit),
            'timeInForce': 'GTC',  # Good Till Canceled
            'reduceOnly': False,
            'closeOnTrigger': False,
            'risk_management': {
                'max_risk_per_trade': f"{recommendation.risk_amount:.2f} USDT",
                'risk_percentage': f"{(recommendation.risk_amount / self.risk_manager.account_balance) * 100:.1f}%",
                'position_value': f"{recommendation.position_size * recommendation.entry_price:.2f} USDT",
                'leverage_ratio': f"{recommendation.leverage}x"
            },
            'trading_plan': {
                'entry_reason': recommendation.strategy_basis,
                'confidence_level': f"{recommendation.confidence:.1f}%",
                'expected_return': f"{recommendation.expected_return:.1f}%",
                'time_horizon': recommendation.time_horizon,
                'risk_reward_ratio': f"{recommendation.risk_metrics['risk_reward_ratio']:.2f}:1"
            }
        }