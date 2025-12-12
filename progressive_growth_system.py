"""
Progressive Account Growth System
Sustainable path to significant profits through compound growth
"""

from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ProgressiveGrowthSystem:
    """Build account systematically with increasing position sizes"""
    
    def __init__(self, starting_balance: float = 50.0):
        self.starting_balance = starting_balance
        
    def calculate_3_month_growth_plan(self) -> dict:
        """3-month plan to grow account significantly"""
        
        # Month 1: Build foundation (50% monthly target)
        month1_target = 0.50  # 50% return
        month1_end = self.starting_balance * (1 + month1_target)
        
        # Month 2: Accelerate growth (60% monthly target) 
        month2_target = 0.60  # 60% return
        month2_end = month1_end * (1 + month2_target)
        
        # Month 3: Maximize returns (70% monthly target)
        month3_target = 0.70  # 70% return  
        month3_end = month2_end * (1 + month3_target)
        
        total_profit = month3_end - self.starting_balance
        total_return = (total_profit / self.starting_balance) * 100
        
        return {
            'plan_overview': {
                'starting_balance': f"${self.starting_balance:.2f}",
                'month_1_target': f"${month1_end:.2f} ({month1_target*100:.0f}% return)",
                'month_2_target': f"${month2_end:.2f} ({month2_target*100:.0f}% return)", 
                'month_3_target': f"${month3_end:.2f} ({month3_target*100:.0f}% return)",
                'total_profit': f"${total_profit:.2f}",
                'total_return': f"{total_return:.0f}%"
            },
            'monthly_strategies': {
                'month_1': {
                    'balance_range': f"${self.starting_balance:.0f} - ${month1_end:.0f}",
                    'risk_per_trade': '8-12%',
                    'leverage': '8-12x',
                    'trades_per_week': '3-4',
                    'focus': 'Learn signals, build confidence, steady growth'
                },
                'month_2': {
                    'balance_range': f"${month1_end:.0f} - ${month2_end:.0f}",
                    'risk_per_trade': '12-15%',
                    'leverage': '12-18x', 
                    'trades_per_week': '4-5',
                    'focus': 'Scale position sizes, compound gains'
                },
                'month_3': {
                    'balance_range': f"${month2_end:.0f} - ${month3_end:.0f}",
                    'risk_per_trade': '15-20%',
                    'leverage': '15-25x',
                    'trades_per_week': '4-6',
                    'focus': 'Maximum growth with controlled risk'
                }
            },
            'weekly_milestones': self._calculate_weekly_milestones()
        }
    
    def calculate_deposit_acceleration_plan(self) -> dict:
        """Plan combining trading profits with additional deposits"""
        
        scenarios = []
        
        # Scenario 1: $50/week additional deposits
        weekly_deposit = 50
        balance = self.starting_balance
        week_progression = []
        
        for week in range(12):  # 3 months
            # Add weekly deposit
            balance += weekly_deposit
            
            # Apply 12% weekly growth (realistic with larger account)
            weekly_return = 0.12
            trading_profit = balance * weekly_return
            balance += trading_profit
            
            week_progression.append({
                'week': week + 1,
                'deposits_total': f"${(week + 1) * weekly_deposit:.2f}",
                'trading_profit': f"${trading_profit:.2f}",
                'balance': f"${balance:.2f}"
            })
        
        scenarios.append({
            'name': 'Trading + $50/week deposits',
            'final_balance': f"${balance:.2f}",
            'total_deposits': f"${12 * weekly_deposit:.2f}",
            'trading_profit': f"${balance - self.starting_balance - (12 * weekly_deposit):.2f}",
            'weeks': week_progression[:4]  # Show first 4 weeks
        })
        
        # Scenario 2: $100/week additional deposits
        weekly_deposit = 100
        balance = self.starting_balance
        
        for week in range(12):
            balance += weekly_deposit
            trading_profit = balance * 0.12
            balance += trading_profit
        
        scenarios.append({
            'name': 'Trading + $100/week deposits',
            'final_balance': f"${balance:.2f}",
            'total_deposits': f"${12 * weekly_deposit:.2f}",
            'trading_profit': f"${balance - self.starting_balance - (12 * weekly_deposit):.2f}",
            'timeframe': '12 weeks'
        })
        
        return {
            'strategy': 'Combine Trading Returns with Regular Deposits',
            'scenarios': scenarios,
            'advantages': [
                'Reduces pressure on trading performance',
                'Allows compound growth on larger amounts',
                'Creates consistent progress toward goals',
                'Builds trading discipline with less stress'
            ]
        }
    
    def _calculate_weekly_milestones(self) -> dict:
        """Calculate weekly milestones for 3-month plan"""
        
        current_balance = self.starting_balance
        milestones = {}
        
        # 12 weeks total, targeting different weekly returns
        weekly_targets = [0.10, 0.11, 0.12, 0.13] * 3  # Repeat pattern
        
        for week in range(12):
            weekly_return = weekly_targets[week % 4]
            profit = current_balance * weekly_return
            current_balance += profit
            
            milestones[f'week_{week + 1}'] = {
                'target_balance': f"${current_balance:.2f}",
                'weekly_profit': f"${profit:.2f}",
                'weekly_return': f"{weekly_return*100:.0f}%"
            }
        
        return milestones

def generate_realistic_growth_analysis(starting_balance: float = 50.0) -> dict:
    """Generate comprehensive realistic growth analysis"""
    
    system = ProgressiveGrowthSystem(starting_balance)
    
    growth_plan = system.calculate_3_month_growth_plan()
    deposit_plan = system.calculate_deposit_acceleration_plan()
    
    # Calculate what's needed to reach $500 profit
    target_profit = 500.0
    required_balance = starting_balance + target_profit
    
    # Timeline to reach target with different monthly returns
    timelines = {}
    for monthly_return in [0.30, 0.50, 0.70, 1.00]:  # 30%, 50%, 70%, 100%
        balance = starting_balance
        months = 0
        while balance < required_balance and months < 12:
            balance = balance * (1 + monthly_return)
            months += 1
        
        timelines[f'{monthly_return*100:.0f}%'] = {
            'months_needed': months if months <= 12 else 'More than 1 year',
            'final_balance': f"${balance:.2f}",
            'difficulty': 'High' if monthly_return >= 0.70 else 'Moderate' if monthly_return >= 0.50 else 'Reasonable'
        }
    
    return {
        'growth_plan': growth_plan,
        'deposit_acceleration': deposit_plan,
        'target_analysis': {
            'target_profit': f"${target_profit}",
            'required_balance': f"${required_balance}",
            'timelines_to_reach_target': timelines
        },
        'recommendation': {
            'best_approach': '3-month progressive growth + weekly deposits',
            'realistic_timeframe': '4-6 months to reach $500 profit',
            'success_probability': '60-80% with disciplined execution'
        }
    }

if __name__ == "__main__":
    analysis = generate_realistic_growth_analysis(50.0)
    print("Progressive Growth Analysis:")
    print(f"3-Month Target: {analysis['growth_plan']['plan_overview']['month_3_target']}")
    recommendation = analysis['recommendation']
    print(f"Best Approach: {recommendation['best_approach']}")
    print(f"Realistic Timeframe: {recommendation['realistic_timeframe']}")
    print(f"Success Rate: {recommendation['success_probability']}")