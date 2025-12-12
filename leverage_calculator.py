#!/usr/bin/env python3
"""
Leverage Calculator for $50 Daily Profit Goal
Analyzes current Bybit settings and calculates optimal leverage
"""

def calculate_optimal_leverage():
    """Calculate optimal leverage for $50 daily profit with $500 account"""
    
    # Account parameters
    account_balance = 500
    daily_target = 50
    required_return = (daily_target / account_balance) * 100  # 10% daily return
    
    print(f'Account Balance: ${account_balance}')
    print(f'Daily Target: ${daily_target}')
    print(f'Required Daily Return: {required_return}%')
    print()
    
    # Current settings analysis from console logs
    current_leverage = 7
    current_expected_return = 6  # 6% per trade from expected_return field
    current_risk_per_trade = 0.10  # 10% risk per trade (more aggressive for $50 target)
    
    # Calculate current profit potential
    trades_needed = 3  # Top 3 signals (SOL, DOT, AVAX)
    current_profit_per_trade = (account_balance * current_risk_per_trade * current_leverage * current_expected_return / 100)
    total_current_profit = current_profit_per_trade * trades_needed
    
    print(f'CURRENT SETTINGS (7x leverage):')
    print(f'Risk per trade: {current_risk_per_trade*100}%')
    print(f'Profit per trade: ${current_profit_per_trade:.2f}')
    print(f'Total profit (3 trades): ${total_current_profit:.2f}')
    print(f'Gap to target: ${daily_target - total_current_profit:.2f}')
    print()
    
    # Calculate optimal leverage
    optimal_leverage = (daily_target / trades_needed) / (account_balance * current_risk_per_trade * current_expected_return / 100)
    
    print(f'OPTIMAL LEVERAGE CALCULATION:')
    print(f'Needed leverage: {optimal_leverage:.1f}x')
    print(f'Recommended: {min(15, max(10, optimal_leverage)):.0f}x (capped at 15x for safety)')
    print()
    
    # Validate optimal settings
    optimal_lev = min(15, max(10, optimal_leverage))
    optimal_profit_per_trade = (account_balance * current_risk_per_trade * optimal_lev * current_expected_return / 100)
    optimal_total_profit = optimal_profit_per_trade * trades_needed
    
    print(f'OPTIMAL SETTINGS ({optimal_lev:.0f}x leverage):')
    print(f'Profit per trade: ${optimal_profit_per_trade:.2f}')
    print(f'Total profit (3 trades): ${optimal_total_profit:.2f}')
    print(f'Achievement: {(optimal_total_profit/daily_target)*100:.1f}% of daily target')
    print()
    
    # Risk analysis
    total_risk = current_risk_per_trade * trades_needed * 100
    print(f'RISK ANALYSIS:')
    print(f'Total account risk: {total_risk}%')
    print(f'Risk per $1000: ${(total_risk/100)*1000:.0f}')
    print(f'Maximum potential loss: ${(total_risk/100)*account_balance:.0f}')
    print()
    
    # Confidence-based leverage recommendations
    print(f'CONFIDENCE-BASED LEVERAGE:')
    print(f'98%+ confidence: 15x leverage (ultra-high confidence)')
    print(f'95-97% confidence: 12x leverage (high confidence)')
    print(f'90-94% confidence: 10x leverage (moderate confidence)')
    print()
    
    return {
        'current_leverage': current_leverage,
        'optimal_leverage': optimal_lev,
        'current_profit': total_current_profit,
        'optimal_profit': optimal_total_profit,
        'meets_target': optimal_total_profit >= daily_target
    }

if __name__ == "__main__":
    result = calculate_optimal_leverage()
    
    print("="*50)
    print("CONCLUSION:")
    if result['meets_target']:
        print(f"✓ Optimal {result['optimal_leverage']:.0f}x leverage ACHIEVES $50 daily target")
    else:
        print(f"✗ Current {result['current_leverage']}x leverage falls SHORT of $50 target")
    print("="*50)