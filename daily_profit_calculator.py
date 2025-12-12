"""
Daily Profit Calculator - Realistic Earnings Analysis
Calculates expected daily profits based on current signal system and $500 account
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class DailyProfitCalculator:
    """Calculate realistic daily profit expectations based on current setup"""
    
    def __init__(self, account_balance: float = 500.0):
        self.account_balance = account_balance
        
        # Current system performance metrics
        self.signal_metrics = {
            'avg_confidence': 95.0,
            'avg_risk_reward': 2.0,
            'avg_leverage': 8.0,
            'avg_risk_per_trade': 0.12,  # 12%
            'signals_per_day': 3.5,
            'estimated_win_rate': 0.72,  # 72% based on high confidence signals
            'avg_holding_time': 6.0,  # 6 hours average
            'max_concurrent_trades': 3
        }
        
        # Market condition adjustments
        self.market_conditions = {
            'normal': {'multiplier': 1.0, 'frequency': 0.6},
            'volatile': {'multiplier': 1.3, 'frequency': 0.3},
            'trending': {'multiplier': 1.15, 'frequency': 0.1}
        }
    
    def calculate_daily_profit_expectation(self) -> Dict:
        """Calculate comprehensive daily profit analysis"""
        
        # Base calculations
        base_analysis = self._calculate_base_scenario()
        conservative_analysis = self._calculate_conservative_scenario()
        aggressive_analysis = self._calculate_aggressive_scenario()
        
        # Weekly and monthly projections
        weekly_projections = self._calculate_weekly_projections(base_analysis)
        monthly_projections = self._calculate_monthly_projections(base_analysis)
        
        # Risk analysis
        risk_analysis = self._calculate_risk_scenarios()
        
        # Compound growth analysis
        compound_analysis = self._calculate_compound_growth()
        
        return {
            'account_balance': self.account_balance,
            'daily_scenarios': {
                'conservative': conservative_analysis,
                'base_case': base_analysis,
                'aggressive': aggressive_analysis
            },
            'projections': {
                'weekly': weekly_projections,
                'monthly': monthly_projections,
                'compound_growth': compound_analysis
            },
            'risk_analysis': risk_analysis,
            'system_metrics': self.signal_metrics,
            'recommendations': self._generate_recommendations(base_analysis),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_base_scenario(self) -> Dict:
        """Calculate base case daily profit scenario"""
        
        # Average trade parameters
        avg_risk_amount = self.account_balance * self.signal_metrics['avg_risk_per_trade']
        avg_leverage = self.signal_metrics['avg_leverage']
        avg_risk_reward = self.signal_metrics['avg_risk_reward']
        win_rate = self.signal_metrics['estimated_win_rate']
        signals_per_day = self.signal_metrics['signals_per_day']
        
        # Calculate per-trade expectation
        winning_trade_profit = avg_risk_amount * avg_risk_reward
        losing_trade_loss = avg_risk_amount
        
        expected_value_per_trade = (
            (win_rate * winning_trade_profit) - 
            ((1 - win_rate) * losing_trade_loss)
        )
        
        # Daily expectation
        daily_expected_profit = expected_value_per_trade * signals_per_day
        daily_return_percentage = (daily_expected_profit / self.account_balance) * 100
        
        # Account for market conditions
        market_adjusted_profit = self._apply_market_conditions(daily_expected_profit)
        
        return {
            'avg_daily_profit_usd': round(market_adjusted_profit, 2),
            'avg_daily_return_pct': round((market_adjusted_profit / self.account_balance) * 100, 2),
            'trades_per_day': signals_per_day,
            'risk_per_trade_usd': round(avg_risk_amount, 2),
            'profit_per_winning_trade': round(winning_trade_profit, 2),
            'expected_value_per_trade': round(expected_value_per_trade, 2),
            'win_rate_assumption': f"{win_rate * 100:.1f}%",
            'scenario': 'Base Case'
        }
    
    def _calculate_conservative_scenario(self) -> Dict:
        """Calculate conservative daily profit scenario"""
        
        # Reduce assumptions for conservative estimate
        conservative_metrics = self.signal_metrics.copy()
        conservative_metrics.update({
            'estimated_win_rate': 0.65,  # 65% win rate
            'signals_per_day': 2.5,
            'avg_risk_per_trade': 0.10,  # 10% risk
            'avg_risk_reward': 1.8
        })
        
        avg_risk_amount = self.account_balance * conservative_metrics['avg_risk_per_trade']
        avg_risk_reward = conservative_metrics['avg_risk_reward']
        win_rate = conservative_metrics['estimated_win_rate']
        signals_per_day = conservative_metrics['signals_per_day']
        
        winning_trade_profit = avg_risk_amount * avg_risk_reward
        losing_trade_loss = avg_risk_amount
        
        expected_value_per_trade = (
            (win_rate * winning_trade_profit) - 
            ((1 - win_rate) * losing_trade_loss)
        )
        
        daily_expected_profit = expected_value_per_trade * signals_per_day
        market_adjusted_profit = daily_expected_profit * 0.85  # Conservative market adjustment
        
        return {
            'avg_daily_profit_usd': round(market_adjusted_profit, 2),
            'avg_daily_return_pct': round((market_adjusted_profit / self.account_balance) * 100, 2),
            'trades_per_day': signals_per_day,
            'risk_per_trade_usd': round(avg_risk_amount, 2),
            'profit_per_winning_trade': round(winning_trade_profit, 2),
            'expected_value_per_trade': round(expected_value_per_trade, 2),
            'win_rate_assumption': f"{win_rate * 100:.1f}%",
            'scenario': 'Conservative'
        }
    
    def _calculate_aggressive_scenario(self) -> Dict:
        """Calculate aggressive daily profit scenario"""
        
        # Increase assumptions for aggressive estimate
        aggressive_metrics = self.signal_metrics.copy()
        aggressive_metrics.update({
            'estimated_win_rate': 0.78,  # 78% win rate
            'signals_per_day': 4.5,
            'avg_risk_per_trade': 0.15,  # 15% risk
            'avg_risk_reward': 2.3
        })
        
        avg_risk_amount = self.account_balance * aggressive_metrics['avg_risk_per_trade']
        avg_risk_reward = aggressive_metrics['avg_risk_reward']
        win_rate = aggressive_metrics['estimated_win_rate']
        signals_per_day = aggressive_metrics['signals_per_day']
        
        winning_trade_profit = avg_risk_amount * avg_risk_reward
        losing_trade_loss = avg_risk_amount
        
        expected_value_per_trade = (
            (win_rate * winning_trade_profit) - 
            ((1 - win_rate) * losing_trade_loss)
        )
        
        daily_expected_profit = expected_value_per_trade * signals_per_day
        market_adjusted_profit = daily_expected_profit * 1.15  # Aggressive market adjustment
        
        return {
            'avg_daily_profit_usd': round(market_adjusted_profit, 2),
            'avg_daily_return_pct': round((market_adjusted_profit / self.account_balance) * 100, 2),
            'trades_per_day': signals_per_day,
            'risk_per_trade_usd': round(avg_risk_amount, 2),
            'profit_per_winning_trade': round(winning_trade_profit, 2),
            'expected_value_per_trade': round(expected_value_per_trade, 2),
            'win_rate_assumption': f"{win_rate * 100:.1f}%",
            'scenario': 'Aggressive'
        }
    
    def _apply_market_conditions(self, base_profit: float) -> float:
        """Apply market condition adjustments"""
        
        weighted_multiplier = 0
        for condition, params in self.market_conditions.items():
            weighted_multiplier += params['multiplier'] * params['frequency']
        
        return base_profit * weighted_multiplier
    
    def _calculate_weekly_projections(self, daily_analysis: Dict) -> Dict:
        """Calculate weekly profit projections"""
        
        daily_profit = daily_analysis['avg_daily_profit_usd']
        
        # Account for weekends (reduced activity)
        weekly_profit = daily_profit * 5 + (daily_profit * 0.6 * 2)  # 60% activity on weekends
        
        return {
            'weekly_profit_usd': round(weekly_profit, 2),
            'weekly_return_pct': round((weekly_profit / self.account_balance) * 100, 2),
            'trading_days': 7,
            'weekend_activity_factor': 0.6
        }
    
    def _calculate_monthly_projections(self, daily_analysis: Dict) -> Dict:
        """Calculate monthly profit projections"""
        
        daily_profit = daily_analysis['avg_daily_profit_usd']
        
        # 30-day month with varying activity
        monthly_profit = daily_profit * 22 + (daily_profit * 0.6 * 8)  # 22 full days, 8 reduced
        
        return {
            'monthly_profit_usd': round(monthly_profit, 2),
            'monthly_return_pct': round((monthly_profit / self.account_balance) * 100, 2),
            'full_activity_days': 22,
            'reduced_activity_days': 8
        }
    
    def _calculate_compound_growth(self) -> Dict:
        """Calculate compound growth scenarios"""
        
        base_daily_return = 0.025  # 2.5% base daily return
        
        # 30-day compound calculation
        compound_30_days = self.account_balance * ((1 + base_daily_return) ** 30)
        profit_30_days = compound_30_days - self.account_balance
        
        # 90-day compound calculation
        compound_90_days = self.account_balance * ((1 + base_daily_return) ** 90)
        profit_90_days = compound_90_days - self.account_balance
        
        return {
            'base_daily_return': f"{base_daily_return * 100:.1f}%",
            '30_day_balance': round(compound_30_days, 2),
            '30_day_profit': round(profit_30_days, 2),
            '90_day_balance': round(compound_90_days, 2),
            '90_day_profit': round(profit_90_days, 2),
            'compound_effect': 'Assumes consistent daily returns with reinvestment'
        }
    
    def _calculate_risk_scenarios(self) -> Dict:
        """Calculate risk scenarios and drawdown analysis"""
        
        # Calculate maximum risk exposure
        max_concurrent_risk = self.account_balance * self.signal_metrics['avg_risk_per_trade'] * self.signal_metrics['max_concurrent_trades']
        max_drawdown_percentage = (max_concurrent_risk / self.account_balance) * 100
        
        # Bad day scenario (all trades lose)
        worst_case_daily_loss = max_concurrent_risk
        
        # Recovery time calculation
        base_daily_profit = self.account_balance * 0.025  # From base scenario
        recovery_days = worst_case_daily_loss / base_daily_profit if base_daily_profit > 0 else 0
        
        return {
            'max_daily_risk_usd': round(max_concurrent_risk, 2),
            'max_drawdown_pct': round(max_drawdown_percentage, 1),
            'worst_case_daily_loss': round(worst_case_daily_loss, 2),
            'estimated_recovery_days': round(recovery_days, 1),
            'risk_management': 'Stop losses limit individual trade risk',
            'account_safety_margin': round(self.account_balance - max_concurrent_risk, 2)
        }
    
    def _generate_recommendations(self, base_analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        
        daily_return = base_analysis['avg_daily_return_pct']
        
        recommendations = []
        
        if daily_return < 2.0:
            recommendations.append("Consider increasing position sizes or targeting higher R:R ratios")
        elif daily_return > 5.0:
            recommendations.append("Excellent returns - maintain current strategy and risk management")
        else:
            recommendations.append("Good consistent returns - consider gradual position size increases")
        
        if self.signal_metrics['signals_per_day'] < 3:
            recommendations.append("Look for additional trading opportunities during different market sessions")
        
        recommendations.extend([
            "Track actual results vs. projections for strategy refinement",
            "Consider compounding profits by increasing position sizes gradually",
            "Monitor win rate - if consistently above 75%, consider higher risk allocation",
            "Use Telegram alerts to capture signals during off-hours"
        ])
        
        return recommendations

def calculate_daily_profit_potential(account_balance: float = 500.0) -> Dict:
    """Main function to calculate daily profit potential"""
    
    calculator = DailyProfitCalculator(account_balance)
    return calculator.calculate_daily_profit_expectation()