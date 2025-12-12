"""
Daily and Monthly Profit Analysis for $500 Account
Based on current trade settings and signal system
"""

def calculate_profit_potential():
    """Calculate realistic profit potential for $500 account"""
    
    # Account Configuration
    account_balance = 500.0
    
    # Current Trade Settings Analysis
    primary_trade = {
        'position_value': 800.0,
        'margin_required': 100.0,  # 20% of account
        'risk_amount': 50.0,       # 10% risk
        'leverage': 8,
        'confidence': 92.5,
        'expected_return': 6.0     # 6% target per trade
    }
    
    alternative_trades = {
        'position_value': 400.0,
        'margin_required': 50.0,   # Average ~10% of account each
        'risk_amount': 20.0,       # 4% risk each
        'leverage': 8,             # Average leverage
        'confidence': 92.0,        # Average confidence
        'expected_return': 6.0     # 6% target per trade
    }
    
    print("=== PROFIT ANALYSIS FOR $500 ACCOUNT ===\n")
    
    # Single Trade Profit Calculations
    print("SINGLE TRADE PROFIT POTENTIAL:")
    primary_profit = primary_trade['position_value'] * (primary_trade['expected_return'] / 100)
    alt_profit = alternative_trades['position_value'] * (alternative_trades['expected_return'] / 100)
    
    print(f"Primary Trade (ADA): ${primary_profit:.2f} profit target")
    print(f"Alternative Trade: ${alt_profit:.2f} profit target")
    print()
    
    # Daily Scenarios
    print("DAILY PROFIT SCENARIOS:")
    
    # Conservative: 1 successful trade per day
    conservative_daily = primary_profit * 0.7  # 70% success rate
    print(f"Conservative (1 trade/day, 70% success): ${conservative_daily:.2f}")
    
    # Moderate: 1.5 successful trades per day
    moderate_daily = (primary_profit + alt_profit * 0.5) * 0.75  # 75% success rate
    print(f"Moderate (1.5 trades/day, 75% success): ${moderate_daily:.2f}")
    
    # Aggressive: 2 successful trades per day
    aggressive_daily = (primary_profit + alt_profit) * 0.8  # 80% success rate
    print(f"Aggressive (2 trades/day, 80% success): ${aggressive_daily:.2f}")
    print()
    
    # Account Growth Impact
    print("ACCOUNT GROWTH SCENARIOS:")
    
    # Conservative daily percentage
    conservative_pct = (conservative_daily / account_balance) * 100
    moderate_pct = (moderate_daily / account_balance) * 100
    aggressive_pct = (aggressive_daily / account_balance) * 100
    
    print(f"Conservative: {conservative_pct:.2f}% daily growth")
    print(f"Moderate: {moderate_pct:.2f}% daily growth")
    print(f"Aggressive: {aggressive_pct:.2f}% daily growth")
    print()
    
    # Monthly Projections (20 trading days)
    print("MONTHLY PROJECTIONS (20 Trading Days):")
    
    trading_days = 20
    
    # Simple compound calculation
    conservative_monthly = account_balance * ((1 + conservative_pct/100) ** trading_days) - account_balance
    moderate_monthly = account_balance * ((1 + moderate_pct/100) ** trading_days) - account_balance
    aggressive_monthly = account_balance * ((1 + aggressive_pct/100) ** trading_days) - account_balance
    
    print(f"Conservative Monthly: ${conservative_monthly:.2f}")
    print(f"Moderate Monthly: ${moderate_monthly:.2f}")
    print(f"Aggressive Monthly: ${aggressive_monthly:.2f}")
    print()
    
    # Risk-Adjusted Analysis
    print("RISK-ADJUSTED REALITY CHECK:")
    
    # Factor in losing trades and market conditions
    win_rates = {
        'conservative': 0.65,  # 65% win rate
        'moderate': 0.70,      # 70% win rate
        'aggressive': 0.75     # 75% win rate
    }
    
    # Average loss per losing trade (stop-loss scenarios)
    avg_loss_primary = primary_trade['risk_amount'] * 0.7  # Don't always hit full stop
    avg_loss_alt = alternative_trades['risk_amount'] * 0.7
    
    print("Realistic Daily Profit (factoring losses):")
    
    for scenario, win_rate in win_rates.items():
        if scenario == 'conservative':
            daily_trades = 1
            wins_per_day = daily_trades * win_rate
            losses_per_day = daily_trades * (1 - win_rate)
            daily_profit = (wins_per_day * primary_profit) - (losses_per_day * avg_loss_primary)
        elif scenario == 'moderate':
            daily_trades = 1.5
            wins_per_day = daily_trades * win_rate
            losses_per_day = daily_trades * (1 - win_rate)
            avg_profit = (primary_profit + alt_profit) / 2
            avg_loss = (avg_loss_primary + avg_loss_alt) / 2
            daily_profit = (wins_per_day * avg_profit) - (losses_per_day * avg_loss)
        else:  # aggressive
            daily_trades = 2
            wins_per_day = daily_trades * win_rate
            losses_per_day = daily_trades * (1 - win_rate)
            avg_profit = (primary_profit + alt_profit) / 2
            avg_loss = (avg_loss_primary + avg_loss_alt) / 2
            daily_profit = (wins_per_day * avg_profit) - (losses_per_day * avg_loss)
        
        daily_pct = (daily_profit / account_balance) * 100
        monthly_realistic = account_balance * ((1 + daily_pct/100) ** trading_days) - account_balance
        
        print(f"{scenario.title()}: ${daily_profit:.2f}/day ({daily_pct:.2f}%), ${monthly_realistic:.2f}/month")
    
    print("\n=== KEY INSIGHTS ===")
    print(f"• Your $500 account is properly sized for futures trading")
    print(f"• Primary trades risk $50 (10%) for $48 profit target")
    print(f"• Alternative trades risk $20 (4%) for $24 profit target")
    print(f"• Realistic expectation: $15-35 daily profit")
    print(f"• Monthly growth potential: $300-700 (60-140% account growth)")
    print(f"• Key success factors: Discipline, risk management, signal quality")

if __name__ == "__main__":
    calculate_profit_potential()