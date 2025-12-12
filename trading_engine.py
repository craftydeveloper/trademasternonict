import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import desc
from app import db
from models import Portfolio, Position, Trade, TradingStrategy, TokenPrice
from solana_client import SolanaClient

logger = logging.getLogger(__name__)

class TradingEngine:
    def __init__(self):
        self.solana_client = SolanaClient()
        self.default_portfolio_id = 1
    
    def initialize_default_portfolio(self) -> Portfolio:
        """Initialize default portfolio if it doesn't exist"""
        portfolio = Portfolio.query.first()
        if not portfolio:
            portfolio = Portfolio(
                name='Default Portfolio',
                initial_balance=10000.0,
                current_balance=10000.0
            )
            db.session.add(portfolio)
            db.session.commit()
        return portfolio
    
    def execute_trade(self, symbol: str, side: str, quantity: float, price: float, strategy: str = 'manual') -> Dict:
        """Execute a paper trade"""
        try:
            portfolio = self.initialize_default_portfolio()
            
            # Get mint address for the symbol
            mint_address = self.solana_client.popular_tokens.get(symbol, '')
            if not mint_address:
                return {'success': False, 'error': f'Unknown symbol: {symbol}'}
            
            # Simulate trade execution
            execution_result = self.solana_client.simulate_trade_execution(symbol, side, quantity, price)
            
            # Check if portfolio has sufficient balance
            total_cost = execution_result['total_value'] + execution_result['fee']
            
            if side == 'BUY' and portfolio.current_balance < total_cost:
                return {'success': False, 'error': 'Insufficient balance'}
            
            # Create trade record
            trade = Trade(
                portfolio_id=portfolio.id,
                symbol=symbol,
                mint_address=mint_address,
                side=side,
                quantity=quantity,
                price=execution_result['executed_price'],
                total_value=execution_result['total_value'],
                fee=execution_result['fee'],
                strategy=strategy,
                status='filled'
            )
            
            # Update portfolio balance
            if side == 'BUY':
                portfolio.current_balance -= total_cost
            else:
                portfolio.current_balance += execution_result['total_value'] - execution_result['fee']
            
            # Update or create position
            position = Position.query.filter_by(
                portfolio_id=portfolio.id,
                symbol=symbol
            ).first()
            
            if side == 'BUY':
                if position:
                    # Update existing position
                    total_quantity = position.quantity + quantity
                    total_cost_basis = (position.quantity * position.avg_entry_price) + execution_result['total_value']
                    position.avg_entry_price = total_cost_basis / total_quantity
                    position.quantity = total_quantity
                else:
                    # Create new position
                    position = Position(
                        portfolio_id=portfolio.id,
                        symbol=symbol,
                        mint_address=mint_address,
                        quantity=quantity,
                        avg_entry_price=execution_result['executed_price'],
                        current_price=execution_result['executed_price']
                    )
                    db.session.add(position)
            
            else:  # SELL
                if position and position.quantity >= quantity:
                    # Calculate PnL
                    pnl = (execution_result['executed_price'] - position.avg_entry_price) * quantity
                    trade.pnl = pnl
                    
                    # Update position
                    position.quantity -= quantity
                    if position.quantity <= 0:
                        db.session.delete(position)
                    
                    # Update portfolio PnL
                    portfolio.total_pnl += pnl
                    if pnl > 0:
                        portfolio.winning_trades += 1
                else:
                    return {'success': False, 'error': 'Insufficient position to sell'}
            
            # Update portfolio stats
            portfolio.total_trades += 1
            portfolio.updated_at = datetime.utcnow()
            
            db.session.add(trade)
            db.session.commit()
            
            return {
                'success': True,
                'trade': trade.to_dict(),
                'portfolio': portfolio.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error executing trade: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_positions_prices(self):
        """Update current prices for all positions"""
        try:
            positions = Position.query.all()
            if not positions:
                return
            
            # Get unique symbols
            symbols = list(set([pos.symbol for pos in positions]))
            mint_addresses = [self.solana_client.popular_tokens.get(symbol, '') for symbol in symbols]
            mint_addresses = [addr for addr in mint_addresses if addr]
            
            # Get current prices
            price_data = self.solana_client.get_multiple_token_prices(mint_addresses)
            
            for position in positions:
                mint_address = self.solana_client.popular_tokens.get(position.symbol, '')
                if mint_address in price_data:
                    current_price = price_data[mint_address]['price']
                    position.current_price = current_price
                    position.unrealized_pnl = (current_price - position.avg_entry_price) * position.quantity
                    position.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating position prices: {e}")
            db.session.rollback()
    
    def simple_moving_average_strategy(self, symbol: str, short_period: int = 5, long_period: int = 20) -> Optional[str]:
        """Simple Moving Average Crossover Strategy"""
        try:
            # Get recent price data
            recent_prices = TokenPrice.query.filter_by(symbol=symbol)\
                .order_by(desc(TokenPrice.timestamp))\
                .limit(long_period)\
                .all()
            
            if len(recent_prices) < long_period:
                return None
            
            prices = [p.price for p in reversed(recent_prices)]
            
            # Calculate moving averages
            short_ma = sum(prices[-short_period:]) / short_period
            long_ma = sum(prices[-long_period:]) / long_period
            
            prev_short_ma = sum(prices[-(short_period+1):-1]) / short_period
            prev_long_ma = sum(prices[-(long_period+1):-1]) / long_period
            
            # Check for crossover
            if prev_short_ma <= prev_long_ma and short_ma > long_ma:
                return 'BUY'
            elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
                return 'SELL'
            
            return None
            
        except Exception as e:
            logger.error(f"Error in SMA strategy for {symbol}: {e}")
            return None
    
    def execute_strategy_signals(self):
        """Execute trades based on active trading strategies"""
        try:
            active_strategies = TradingStrategy.query.filter_by(is_active=True).all()
            
            for strategy in active_strategies:
                if strategy.strategy_type == 'sma_crossover':
                    params = json.loads(strategy.parameters) if strategy.parameters else {}
                    short_period = params.get('short_period', 5)
                    long_period = params.get('long_period', 20)
                    
                    signal = self.simple_moving_average_strategy(
                        strategy.symbol, short_period, long_period
                    )
                    
                    if signal:
                        # Get current price
                        current_price_data = self.solana_client.get_token_price(
                            self.solana_client.popular_tokens.get(strategy.symbol, '')
                        )
                        
                        if current_price_data:
                            current_price = current_price_data['price']
                            quantity = strategy.position_size / current_price
                            
                            # Execute trade
                            result = self.execute_trade(
                                strategy.symbol,
                                signal,
                                quantity,
                                current_price,
                                f"sma_crossover_{strategy.id}"
                            )
                            
                            if result['success']:
                                logger.info(f"Strategy {strategy.name} executed {signal} trade for {strategy.symbol}")
            
        except Exception as e:
            logger.error(f"Error executing strategy signals: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary with current positions and performance"""
        try:
            portfolio = self.initialize_default_portfolio()
            positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
            recent_trades = Trade.query.filter_by(portfolio_id=portfolio.id)\
                .order_by(desc(Trade.executed_at))\
                .limit(10)\
                .all()
            
            # Calculate total portfolio value
            total_position_value = sum([pos.quantity * pos.current_price for pos in positions])
            total_portfolio_value = portfolio.current_balance + total_position_value
            
            # Calculate unrealized PnL
            total_unrealized_pnl = sum([pos.unrealized_pnl for pos in positions])
            
            return {
                'portfolio': portfolio.to_dict(),
                'total_value': total_portfolio_value,
                'cash_balance': portfolio.current_balance,
                'position_value': total_position_value,
                'unrealized_pnl': total_unrealized_pnl,
                'total_return': ((total_portfolio_value - portfolio.initial_balance) / portfolio.initial_balance * 100),
                'positions': [pos.to_dict() for pos in positions],
                'recent_trades': [trade.to_dict() for trade in recent_trades]
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}
