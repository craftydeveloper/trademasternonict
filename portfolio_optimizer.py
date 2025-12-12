"""
Portfolio Optimization and Performance Analytics
Advanced portfolio management for professional trading
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class PortfolioMetrics:
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    sortino_ratio: float
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR 95%

class PortfolioOptimizer:
    """Advanced portfolio optimization and analytics"""
    
    def __init__(self):
        self.correlation_matrix = {}
        self.price_history = {}
        self.position_weights = {}
        self.risk_free_rate = 0.045  # Current risk-free rate ~4.5%
        
    def calculate_portfolio_metrics(self, returns: List[float], 
                                  trading_days: int = 252) -> PortfolioMetrics:
        """Calculate comprehensive portfolio performance metrics"""
        
        if not returns or len(returns) < 2:
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        returns_array = np.array(returns)
        
        # Total and annualized returns
        total_return = (1 + returns_array).prod() - 1
        periods_per_year = trading_days / len(returns)
        annualized_return = (1 + total_return) ** periods_per_year - 1
        
        # Volatility (annualized)
        volatility = np.std(returns_array) * np.sqrt(trading_days)
        
        # Sharpe ratio
        excess_return = annualized_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns_array).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = abs(np.min(drawdowns))
        
        # Calmar ratio
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Sortino ratio (downside deviation)
        negative_returns = returns_array[returns_array < 0]
        downside_deviation = np.std(negative_returns) * np.sqrt(trading_days) if len(negative_returns) > 0 else 0
        sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns_array, 5)  # 5th percentile
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = np.mean(returns_array[returns_array <= var_95]) if np.any(returns_array <= var_95) else var_95
        
        return PortfolioMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            sortino_ratio=sortino_ratio,
            var_95=var_95,
            cvar_95=cvar_95
        )
    
    def optimize_portfolio_weights(self, expected_returns: Dict[str, float],
                                 covariance_matrix: np.ndarray,
                                 symbols: List[str],
                                 target_return: Optional[float] = None) -> Dict[str, float]:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        
        n_assets = len(symbols)
        
        # Convert expected returns to array
        mu = np.array([expected_returns.get(symbol, 0) for symbol in symbols])
        
        # Objective function: minimize portfolio variance
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(covariance_matrix, weights))
        
        def portfolio_return(weights):
            return np.dot(weights, mu)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},  # Weights sum to 1
        ]
        
        if target_return:
            constraints.append({
                'type': 'eq', 
                'fun': lambda x: portfolio_return(x) - target_return
            })
        
        # Bounds (no short selling, max 40% in any single asset)
        bounds = tuple((0, 0.4) for _ in range(n_assets))
        
        # Initial guess (equal weights)
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        try:
            from scipy.optimize import minimize
            
            result = minimize(
                portfolio_variance,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                weights = dict(zip(symbols, result.x))
                # Filter out very small weights
                weights = {k: v for k, v in weights.items() if v > 0.01}
                return weights
            
        except ImportError:
            logger.warning("SciPy not available, using equal weights")
        
        # Fallback to equal weights
        equal_weight = 1.0 / len(symbols)
        return {symbol: equal_weight for symbol in symbols}
    
    def calculate_correlation_matrix(self, price_data: Dict[str, List[float]]) -> np.ndarray:
        """Calculate correlation matrix between assets"""
        
        symbols = list(price_data.keys())
        
        # Calculate returns for each asset
        returns_matrix = []
        for symbol in symbols:
            prices = price_data[symbol]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                      for i in range(1, len(prices))]
            returns_matrix.append(returns)
        
        # Convert to numpy array and calculate correlation
        returns_array = np.array(returns_matrix)
        correlation_matrix = np.corrcoef(returns_array)
        
        return correlation_matrix
    
    def detect_regime_change(self, returns: List[float], window: int = 20) -> Dict:
        """Detect market regime changes for dynamic allocation"""
        
        if len(returns) < window * 2:
            return {'regime': 'normal', 'confidence': 0.5}
        
        recent_returns = returns[-window:]
        historical_returns = returns[:-window]
        
        # Calculate volatility regimes
        recent_vol = np.std(recent_returns)
        historical_vol = np.std(historical_returns)
        vol_ratio = recent_vol / historical_vol if historical_vol > 0 else 1
        
        # Calculate trend regimes
        recent_trend = np.mean(recent_returns)
        historical_trend = np.mean(historical_returns)
        
        # Determine regime
        if vol_ratio > 1.5:
            regime = 'high_volatility'
            confidence = min(vol_ratio / 2, 1.0)
        elif vol_ratio < 0.7:
            regime = 'low_volatility'
            confidence = min(2 - vol_ratio, 1.0)
        elif recent_trend > historical_trend * 1.5:
            regime = 'bull_market'
            confidence = 0.7
        elif recent_trend < historical_trend * 0.5:
            regime = 'bear_market'
            confidence = 0.7
        else:
            regime = 'normal'
            confidence = 0.5
        
        return {
            'regime': regime,
            'confidence': confidence,
            'volatility_ratio': vol_ratio,
            'trend_change': recent_trend - historical_trend
        }
    
    def generate_allocation_recommendation(self, market_data: Dict[str, Dict],
                                         risk_tolerance: str = 'moderate') -> Dict:
        """Generate portfolio allocation recommendations"""
        
        symbols = list(market_data.keys())
        
        # Base allocations by risk tolerance
        base_allocations = {
            'conservative': {
                'BTC': 0.3, 'ETH': 0.2, 'SOL': 0.1, 'ADA': 0.1,
                'DOT': 0.1, 'AVAX': 0.1, 'LINK': 0.1
            },
            'moderate': {
                'BTC': 0.25, 'ETH': 0.20, 'SOL': 0.15, 'ADA': 0.15,
                'DOT': 0.10, 'AVAX': 0.10, 'LINK': 0.05
            },
            'aggressive': {
                'BTC': 0.2, 'ETH': 0.2, 'SOL': 0.2, 'ADA': 0.15,
                'DOT': 0.10, 'AVAX': 0.10, 'LINK': 0.05
            }
        }
        
        allocation = base_allocations.get(risk_tolerance, base_allocations['moderate'])
        
        # Adjust based on momentum and volatility
        for symbol in symbols:
            if symbol in market_data:
                data = market_data[symbol]
                momentum = data.get('change_24h', 0)
                
                # Increase allocation for positive momentum (within limits)
                if momentum > 5:
                    allocation[symbol] *= 1.1
                elif momentum < -5:
                    allocation[symbol] *= 0.9
        
        # Normalize to sum to 1
        total = sum(allocation.values())
        if total > 0:
            allocation = {k: v/total for k, v in allocation.items()}
        
        return {
            'recommended_allocation': allocation,
            'risk_profile': risk_tolerance,
            'rebalance_threshold': 0.05,  # Rebalance when weights drift 5%
            'review_frequency': '7_days'
        }