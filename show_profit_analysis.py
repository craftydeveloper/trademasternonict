#!/usr/bin/env python3
"""
Show Daily Profit Analysis for $500 Account
"""

from daily_profit_calculator import calculate_daily_profit_potential

def main():
    print("=== DAILY PROFIT ANALYSIS FOR $500 ACCOUNT ===\n")
    
    # Calculate analysis
    analysis = calculate_daily_profit_potential(500.0)
    
    # Show scenarios
    scenarios = analysis['daily_scenarios']
    
    print("DAILY EARNING SCENARIOS:")
    print("-" * 50)
    
    conservative = scenarios['conservative']
    base = scenarios['base_case']
    aggressive = scenarios['aggressive']
    
    print(f"CONSERVATIVE: ${conservative['avg_daily_profit_usd']}/day ({conservative['avg_daily_return_pct']}%)")
    print(f"  • {conservative['trades_per_day']} trades/day")
    print(f"  • {conservative['win_rate_assumption']} win rate")
    print(f"  • ${conservative['risk_per_trade_usd']} risk per trade\n")
    
    print(f"BASE CASE: ${base['avg_daily_profit_usd']}/day ({base['avg_daily_return_pct']}%)")
    print(f"  • {base['trades_per_day']} trades/day")
    print(f"  • {base['win_rate_assumption']} win rate")
    print(f"  • ${base['risk_per_trade_usd']} risk per trade\n")
    
    print(f"AGGRESSIVE: ${aggressive['avg_daily_profit_usd']}/day ({aggressive['avg_daily_return_pct']}%)")
    print(f"  • {aggressive['trades_per_day']} trades/day")
    print(f"  • {aggressive['win_rate_assumption']} win rate")
    print(f"  • ${aggressive['risk_per_trade_usd']} risk per trade\n")
    
    # Show projections
    weekly = analysis['projections']['weekly']
    monthly = analysis['projections']['monthly']
    
    print("PROFIT PROJECTIONS (Base Case):")
    print("-" * 50)
    print(f"Weekly:  ${weekly['weekly_profit_usd']} ({weekly['weekly_return_pct']}%)")
    print(f"Monthly: ${monthly['monthly_profit_usd']} ({monthly['monthly_return_pct']}%)\n")
    
    # Show compound growth
    compound = analysis['projections']['compound_growth']
    print("COMPOUND GROWTH POTENTIAL:")
    print("-" * 50)
    print(f"After 30 days: ${compound['30_day_balance']} (${compound['30_day_profit']} profit)")
    print(f"After 90 days: ${compound['90_day_balance']} (${compound['90_day_profit']} profit)\n")
    
    # Show risk analysis
    risk = analysis['risk_analysis']
    print("RISK MANAGEMENT:")
    print("-" * 50)
    print(f"Max daily risk: ${risk['max_daily_risk_usd']} ({risk['max_drawdown_pct']}%)")
    print(f"Worst case loss: ${risk['worst_case_daily_loss']}")
    print(f"Recovery time: {risk['estimated_recovery_days']} days")
    print(f"Safety margin: ${risk['account_safety_margin']}\n")
    
    # Show recommendations
    print("RECOMMENDATIONS:")
    print("-" * 50)
    for rec in analysis['recommendations']:
        print(f"• {rec}")

if __name__ == "__main__":
    main()