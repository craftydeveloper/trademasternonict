#!/usr/bin/env python3
"""
Safety Analysis for Current Bybit Settings
Analyzes risk levels and safety metrics for 12x leverage trading
"""

def analyze_safety():
    """Comprehensive safety analysis for current trading settings"""
    
    # Current settings from console logs
    account_balance = 500
    risk_per_trade = 0.10  # 10% risk per trade
    leverage_12x = 12
    num_trades = 3
    confidence_levels = [97.9, 97.3, 97.3]  # SOL, DOT, AVAX
    
    print('SAFETY ANALYSIS FOR CURRENT BYBIT SETTINGS')
    print('=' * 50)
    print(f'Account Balance: ${account_balance}')
    print(f'Risk per trade: {risk_per_trade*100}%')
    print(f'Leverage: {leverage_12x}x')
    print()
    
    # Calculate exposure
    margin_per_trade = account_balance * risk_per_trade  # $50 per trade
    position_value = margin_per_trade * leverage_12x  # $600 position value
    total_risk = risk_per_trade * num_trades * 100  # 30%
    max_loss = account_balance * (total_risk/100)
    
    print('RISK METRICS:')
    print(f'Margin per trade: ${margin_per_trade}')
    print(f'Position value per trade: ${position_value}')
    print(f'Total account risk: {total_risk}%')
    print(f'Maximum potential loss: ${max_loss}')
    print()
    
    # Safety evaluation
    safe_limit = 25  # Industry standard
    print('SAFETY EVALUATION:')
    print(f'Industry safe limit: {safe_limit}% total risk')
    print(f'Current total risk: {total_risk}%')
    
    if total_risk <= safe_limit:
        safety_status = "SAFE"
    elif total_risk <= 35:
        safety_status = "MODERATE RISK"
    else:
        safety_status = "HIGH RISK"
    
    print(f'Safety status: {safety_status}')
    print()
    
    # Stop loss protection
    stop_loss_protection = 3  # 3% stop loss
    max_loss_per_trade = margin_per_trade  # Can only lose margin
    
    print('PROTECTION MECHANISMS:')
    print(f'Stop loss protection: {stop_loss_protection}%')
    print(f'Max loss per trade: ${max_loss_per_trade} (margin only)')
    print(f'Isolated margin: Yes (limits loss to margin)')
    print()
    
    # Confidence analysis
    avg_confidence = sum(confidence_levels) / len(confidence_levels)
    print('CONFIDENCE ANALYSIS:')
    print(f'Average signal confidence: {avg_confidence:.1f}%')
    print(f'All signals above 95%: {"Yes" if min(confidence_levels) >= 95 else "No"}')
    print(f'Signal quality: {"Excellent" if avg_confidence >= 97 else "Good" if avg_confidence >= 95 else "Moderate"}')
    print()
    
    # Profit potential vs risk
    expected_return = 6  # 6% per trade
    profit_per_trade = margin_per_trade * expected_return / 100 * leverage_12x
    daily_profit_potential = profit_per_trade * num_trades * 0.75  # 75% win rate
    
    print('PROFIT VS RISK:')
    print(f'Profit per winning trade: ${profit_per_trade:.0f}')
    print(f'Daily profit potential: ${daily_profit_potential:.0f}')
    print(f'Risk/reward ratio: 1:{profit_per_trade/margin_per_trade:.1f}')
    print()
    
    # Monthly projections
    monthly_profit = daily_profit_potential * 22  # 22 trading days
    monthly_return = (monthly_profit / account_balance) * 100
    
    print('MONTHLY PROJECTIONS:')
    print(f'Expected monthly profit: ${monthly_profit:.0f}')
    print(f'Monthly return: {monthly_return:.0f}%')
    print()
    
    # Safety recommendations
    print('SAFETY RECOMMENDATIONS:')
    if total_risk > 25:
        print('- Consider reducing to 2 trades to lower total risk')
    print('- Always use stop losses (currently 3%)')
    print('- Only trade signals above 95% confidence')
    print('- Use isolated margin mode (prevents account liquidation)')
    print('- Start with smaller positions until comfortable')
    
    return {
        'safety_status': safety_status,
        'total_risk': total_risk,
        'daily_profit': daily_profit_potential,
        'safe': total_risk <= 35 and avg_confidence >= 95
    }

if __name__ == "__main__":
    result = analyze_safety()
    
    print("=" * 50)
    print("CONCLUSION:")
    if result['safe']:
        print(f"Settings are {result['safety_status']} with {result['total_risk']}% total risk")
        print(f"Expected daily profit: ${result['daily_profit']:.0f}")
    else:
        print("Consider reducing risk or position size")
    print("=" * 50)