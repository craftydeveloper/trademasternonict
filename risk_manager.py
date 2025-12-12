"""
Professional Risk Management System
Implements institutional-grade risk controls for futures trading
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class Position:
    symbol: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    leverage: float
    margin_used: float
    timestamp: datetime

@dataclass
class RiskMetrics:
    total_exposure: float
    portfolio_var: float  # Value at Risk
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    risk_reward_ratio: float

class RiskManager:
    """Professional risk management for futures trading"""
    
    def __init__(self, account_balance: float = 10000):
        self.account_balance = account_balance
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk
        self.max_position_risk = 0.01   # 1% max per position
        self.max_leverage = 10          # Maximum leverage allowed
        self.max_drawdown_limit = 0.20  # 20% max drawdown
        self.correlation_limit = 0.7    # Max correlation between positions
        
        # Track performance
        self.trade_history = []
        self.position_history = []
        self.daily_pnl = []
        
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                              risk_percent: float = 1.0) -> Dict:
        """Calculate optimal position size based on risk management"""
        
        # Risk amount in USD
        risk_amount = self.account_balance * (risk_percent / 100)
        
        # Distance to stop loss
        stop_distance = abs(entry_price - stop_loss)
        
        # Position size calculation
        position_size = risk_amount / stop_distance
        
        # Maximum position value (considering leverage)
        max_position_value = self.account_balance * self.max_leverage * 0.5
        
        # Adjust if position too large
        position_value = position_size * entry_price
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
            
        return {
            'position_size': position_size,
            'position_value': position_value,
            'risk_amount': risk_amount,
            'risk_percent': (risk_amount / self.account_balance) * 100,
            'leverage_required': position_value / self.account_balance
        }
    
    def validate_trade(self, symbol: str, side: str, size: float, 
                      entry_price: float, stop_loss: float, 
                      take_profit: float) -> Dict:
        """Validate trade against risk management rules"""
        
        validation = {
            'approved': True,
            'warnings': [],
            'errors': [],
            'adjustments': {}
        }
        
        # Calculate position metrics
        position_value = size * entry_price
        leverage = position_value / self.account_balance
        
        # Risk/Reward ratio check
        stop_distance = abs(entry_price - stop_loss)
        profit_distance = abs(take_profit - entry_price)
        rr_ratio = profit_distance / stop_distance if stop_distance > 0 else 0
        
        if rr_ratio < 1.5:
            validation['warnings'].append(f"Low risk/reward ratio: {rr_ratio:.2f} (recommend >1.5)")
        
        # Leverage check
        if leverage > self.max_leverage:
            validation['errors'].append(f"Leverage too high: {leverage:.1f}x (max: {self.max_leverage}x)")
            validation['approved'] = False
            
        # Position size check
        position_risk = (stop_distance / entry_price) * (position_value / self.account_balance)
        if position_risk > self.max_position_risk:
            validation['errors'].append(f"Position risk too high: {position_risk*100:.1f}% (max: {self.max_position_risk*100}%)")
            validation['approved'] = False
            
        # Portfolio exposure check
        current_exposure = self.calculate_total_exposure()
        new_exposure = current_exposure + position_value
        
        if new_exposure / self.account_balance > 0.8:  # 80% max exposure
            validation['warnings'].append(f"High portfolio exposure: {new_exposure/self.account_balance*100:.1f}%")
            
        return validation
    
    def calculate_total_exposure(self) -> float:
        """Calculate total portfolio exposure"""
        # This would integrate with actual positions
        return 0.0  # Placeholder
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if avg_loss <= 0:
            return 0
            
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Conservative Kelly (use 25% of full Kelly)
        return max(0, min(kelly_percent * 0.25, 0.05))  # Max 5%
    
    def monitor_drawdown(self, current_balance: float) -> Dict:
        """Monitor portfolio drawdown"""
        peak_balance = max(self.account_balance, current_balance)
        drawdown = (peak_balance - current_balance) / peak_balance
        
        status = {
            'current_drawdown': drawdown,
            'max_allowed': self.max_drawdown_limit,
            'warning_level': drawdown > (self.max_drawdown_limit * 0.5),
            'critical_level': drawdown > (self.max_drawdown_limit * 0.8),
            'stop_trading': drawdown >= self.max_drawdown_limit
        }
        
        return status
    
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk assessment report"""
        
        # Calculate performance metrics
        if len(self.trade_history) > 0:
            wins = [t for t in self.trade_history if t['pnl'] > 0]
            losses = [t for t in self.trade_history if t['pnl'] < 0]
            
            win_rate = len(wins) / len(self.trade_history) if self.trade_history else 0
            avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
            avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
            
            profit_factor = abs(sum(t['pnl'] for t in wins) / sum(t['pnl'] for t in losses)) if losses else float('inf')
        else:
            win_rate = avg_win = avg_loss = profit_factor = 0
        
        return {
            'account_balance': self.account_balance,
            'total_trades': len(self.trade_history),
            'win_rate': win_rate * 100,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'recommended_position_size': self.calculate_kelly_criterion(win_rate, avg_win, avg_loss) * 100,
            'risk_limits': {
                'max_position_risk': self.max_position_risk * 100,
                'max_portfolio_risk': self.max_portfolio_risk * 100,
                'max_leverage': self.max_leverage,
                'max_drawdown': self.max_drawdown_limit * 100
            }
        }
    
    def update_performance(self, trade_result: Dict):
        """Update performance tracking with new trade"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'symbol': trade_result.get('symbol'),
            'pnl': trade_result.get('pnl', 0),
            'size': trade_result.get('size', 0),
            'side': trade_result.get('side')
        })
        
        # Keep only last 1000 trades
        if len(self.trade_history) > 1000:
            self.trade_history = self.trade_history[-1000:]