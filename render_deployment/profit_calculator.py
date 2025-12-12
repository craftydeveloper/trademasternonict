"""
30-Day Profit Projection Calculator
Calculates realistic returns based on account size, risk management, and trading strategy
"""

import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ProfitProjectionCalculator:
    """Calculate realistic profit projections for small account trading"""
    
    def __init__(self, account_balance: float = 50.0):
        self.account_balance = account_balance
        self.primary_risk_percent = 5.0  # 5% risk on primary trades
        self.secondary_risk_percent = 2.0  # 2% risk on secondary trades
        self.max_daily_risk = 10.0  # Maximum 10% account risk per day
        
    def calculate_30_day_projection(self) -> dict:
        """Calculate comprehensive 30-day profit projections"""
        
        # Historical performance assumptions based on our signal system
        win_rate = 0.65  # 65% win rate (conservative estimate)
        avg_win_return = 8.5  # Average 8.5% return per winning trade
        avg_loss_return = -4.2  # Average 4.2% loss per losing trade
        
        # Trading frequency assumptions
        primary_trades_per_week = 2  # 2 primary trades per week
        secondary_trades_per_week = 3  # 3 secondary trades per week
        
        # Calculate position sizes
        primary_position_size = self.account_balance * (self.primary_risk_percent / 100)  # $2.50
        secondary_position_size = self.account_balance * (self.secondary_risk_percent / 100)  # $1.00
        
        # 30-day projections
        total_weeks = 4.3  # ~30 days
        total_primary_trades = int(primary_trades_per_week * total_weeks)
        total_secondary_trades = int(secondary_trades_per_week * total_weeks)
        
        # Calculate expected returns
        primary_wins = int(total_primary_trades * win_rate)
        primary_losses = total_primary_trades - primary_wins
        secondary_wins = int(total_secondary_trades * win_rate)
        secondary_losses = total_secondary_trades - secondary_wins
        
        # Calculate profit/loss
        primary_profit = (primary_wins * primary_position_size * (avg_win_return / 100)) + \
                        (primary_losses * primary_position_size * (avg_loss_return / 100))
        
        secondary_profit = (secondary_wins * secondary_position_size * (avg_win_return / 100)) + \
                          (secondary_losses * secondary_position_size * (avg_loss_return / 100))
        
        total_profit = primary_profit + secondary_profit
        total_return_percent = (total_profit / self.account_balance) * 100
        
        # Calculate different scenarios
        scenarios = self._calculate_scenarios()
        
        return {
            'account_balance': self.account_balance,
            'risk_management': {
                'primary_risk_per_trade': f"${primary_position_size:.2f} ({self.primary_risk_percent}%)",
                'secondary_risk_per_trade': f"${secondary_position_size:.2f} ({self.secondary_risk_percent}%)",
                'max_daily_risk': f"${self.account_balance * (self.max_daily_risk / 100):.2f} ({self.max_daily_risk}%)"
            },
            'trading_plan': {
                'primary_trades_per_month': total_primary_trades,
                'secondary_trades_per_month': total_secondary_trades,
                'total_trades_per_month': total_primary_trades + total_secondary_trades
            },
            'base_projection': {
                'expected_profit': f"${total_profit:.2f}",
                'expected_return': f"{total_return_percent:.1f}%",
                'final_balance': f"${self.account_balance + total_profit:.2f}",
                'win_rate_assumption': f"{win_rate * 100:.0f}%"
            },
            'scenarios': scenarios,
            'risk_warnings': self._get_risk_warnings()
        }
    
    def _calculate_scenarios(self) -> dict:
        """Calculate conservative, moderate, and optimistic scenarios"""
        
        scenarios = {}
        
        # Conservative scenario (50% win rate, lower returns)
        conservative = self._scenario_calculation(
            win_rate=0.50,
            avg_win=6.0,
            avg_loss=-3.5,
            name="Conservative"
        )
        scenarios['conservative'] = conservative
        
        # Moderate scenario (65% win rate, base returns)
        moderate = self._scenario_calculation(
            win_rate=0.65,
            avg_win=8.5,
            avg_loss=-4.2,
            name="Moderate"
        )
        scenarios['moderate'] = moderate
        
        # Optimistic scenario (75% win rate, higher returns)
        optimistic = self._scenario_calculation(
            win_rate=0.75,
            avg_win=12.0,
            avg_loss=-4.0,
            name="Optimistic"
        )
        scenarios['optimistic'] = optimistic
        
        return scenarios
    
    def _scenario_calculation(self, win_rate: float, avg_win: float, avg_loss: float, name: str) -> dict:
        """Calculate specific scenario returns"""
        
        total_weeks = 4.3
        primary_trades = int(2 * total_weeks)  # 2 per week
        secondary_trades = int(3 * total_weeks)  # 3 per week
        
        primary_position = self.account_balance * 0.05  # 5%
        secondary_position = self.account_balance * 0.02  # 2%
        
        # Primary trades
        primary_wins = int(primary_trades * win_rate)
        primary_losses = primary_trades - primary_wins
        primary_profit = (primary_wins * primary_position * (avg_win / 100)) + \
                        (primary_losses * primary_position * (avg_loss / 100))
        
        # Secondary trades
        secondary_wins = int(secondary_trades * win_rate)
        secondary_losses = secondary_trades - secondary_wins
        secondary_profit = (secondary_wins * secondary_position * (avg_win / 100)) + \
                          (secondary_losses * secondary_position * (avg_loss / 100))
        
        total_profit = primary_profit + secondary_profit
        return_percent = (total_profit / self.account_balance) * 100
        
        return {
            'name': name,
            'win_rate': f"{win_rate * 100:.0f}%",
            'profit': f"${total_profit:.2f}",
            'return': f"{return_percent:.1f}%",
            'final_balance': f"${self.account_balance + total_profit:.2f}"
        }
    
    def _get_risk_warnings(self) -> list:
        """Get important risk warnings for small account trading"""
        
        return [
            "Futures trading involves substantial risk of loss and is not suitable for all investors",
            "Small account sizes amplify both potential gains and losses",
            "Past performance does not guarantee future results",
            "Market volatility can cause rapid account value changes",
            "Never risk more than you can afford to lose completely",
            "These projections are estimates based on historical patterns and assumptions"
        ]
    
    def get_daily_profit_targets(self) -> dict:
        """Calculate realistic daily profit targets"""
        
        # Conservative daily targets
        daily_targets = {
            'conservative_daily': self.account_balance * 0.01,  # 1% per day
            'moderate_daily': self.account_balance * 0.02,     # 2% per day
            'aggressive_daily': self.account_balance * 0.03    # 3% per day
        }
        
        monthly_projections = {}
        for target_name, daily_amount in daily_targets.items():
            monthly_amount = daily_amount * 22  # 22 trading days
            monthly_percent = (monthly_amount / self.account_balance) * 100
            monthly_projections[target_name] = {
                'daily_target': f"${daily_amount:.2f}",
                'monthly_profit': f"${monthly_amount:.2f}",
                'monthly_return': f"{monthly_percent:.1f}%"
            }
        
        return monthly_projections

def generate_profit_analysis(account_balance: float = 50.0) -> dict:
    """Generate comprehensive profit analysis for user"""
    
    calculator = ProfitProjectionCalculator(account_balance)
    projection = calculator.calculate_30_day_projection()
    daily_targets = calculator.get_daily_profit_targets()
    
    return {
        'projection': projection,
        'daily_targets': daily_targets,
        'summary': _generate_summary(projection, daily_targets),
        'generated_at': datetime.now().isoformat()
    }

def _generate_summary(projection: dict, daily_targets: dict) -> dict:
    """Generate executive summary of profit potential"""
    
    base_profit = float(projection['base_projection']['expected_profit'].replace('$', ''))
    conservative_profit = float(projection['scenarios']['conservative']['profit'].replace('$', ''))
    optimistic_profit = float(projection['scenarios']['optimistic']['profit'].replace('$', ''))
    
    return {
        'realistic_range': f"${conservative_profit:.2f} to ${optimistic_profit:.2f}",
        'most_likely': projection['base_projection']['expected_profit'],
        'key_factors': [
            "Signal accuracy and market conditions",
            "Consistent risk management execution",
            "Market volatility and trending patterns",
            "Emotional discipline in trade execution"
        ],
        'success_probability': "Moderate to High with disciplined execution"
    }

if __name__ == "__main__":
    # Test with $50 account
    analysis = generate_profit_analysis(50.0)
    print("30-Day Profit Analysis:")
    print(f"Realistic Range: {analysis['summary']['realistic_range']}")
    print(f"Most Likely: {analysis['summary']['most_likely']}")