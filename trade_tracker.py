"""
Trade Tracking and Reporting System
Automatically tracks all recommended trades and their outcomes
"""

from app import db
from models import TradeRecommendation
from market_data_client import MarketDataClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TradeTracker:
    """Tracks and monitors all trading recommendations"""
    
    def __init__(self):
        self.market_client = MarketDataClient()
    
    def log_recommendation(self, signal_data):
        """Log a new trade recommendation to database"""
        try:
            recommendation = TradeRecommendation(
                symbol=signal_data['symbol'],
                action=signal_data['action'],
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                quantity=signal_data['bybit_settings']['qty'],
                leverage=signal_data['leverage'],
                confidence=signal_data['confidence'],
                risk_amount=float(signal_data['bybit_settings']['risk_management']['risk_amount_usd']),
                expected_return=signal_data['expected_return'],
                strategy_basis=signal_data['strategy_basis']
            )
            
            db.session.add(recommendation)
            db.session.commit()
            
            logger.info(f"Logged recommendation: {signal_data['symbol']} {signal_data['action']} at ${signal_data['entry_price']}")
            return recommendation.id
            
        except Exception as e:
            logger.error(f"Error logging recommendation: {e}")
            db.session.rollback()
            return None
    
    def mark_trade_entered(self, trade_id, actual_entry_price):
        """Mark trade as entered with actual price"""
        try:
            trade = TradeRecommendation.query.get(trade_id)
            if trade:
                trade.status = 'ACTIVE'
                trade.actual_entry_price = actual_entry_price
                trade.entered_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Trade {trade_id} marked as entered at ${actual_entry_price}")
                return True
        except Exception as e:
            logger.error(f"Error marking trade entered: {e}")
            db.session.rollback()
        return False
    
    def check_active_trades(self):
        """Check all active trades for exit conditions"""
        active_trades = TradeRecommendation.query.filter_by(status='ACTIVE').all()
        
        for trade in active_trades:
            try:
                current_price = self._get_current_price(trade.symbol)
                if not current_price:
                    continue
                
                exit_reason = None
                should_exit = False
                
                if trade.action == 'BUY':
                    # Long position
                    if current_price >= trade.take_profit:
                        exit_reason = 'TAKE_PROFIT'
                        should_exit = True
                    elif current_price <= trade.stop_loss:
                        exit_reason = 'STOP_LOSS'
                        should_exit = True
                else:
                    # Short position
                    if current_price <= trade.take_profit:
                        exit_reason = 'TAKE_PROFIT'
                        should_exit = True
                    elif current_price >= trade.stop_loss:
                        exit_reason = 'STOP_LOSS'
                        should_exit = True
                
                if should_exit:
                    self._close_trade(trade, current_price, exit_reason)
                    
            except Exception as e:
                logger.error(f"Error checking trade {trade.id}: {e}")
    
    def _close_trade(self, trade, exit_price, exit_reason):
        """Close a trade and calculate PnL"""
        try:
            if trade.action == 'BUY':
                # Long position PnL
                price_diff = exit_price - trade.actual_entry_price
                pnl_percentage = (price_diff / trade.actual_entry_price) * 100
            else:
                # Short position PnL
                price_diff = trade.actual_entry_price - exit_price
                pnl_percentage = (price_diff / trade.actual_entry_price) * 100
            
            # Apply leverage
            leveraged_pnl = pnl_percentage * trade.leverage
            actual_pnl = (leveraged_pnl / 100) * trade.risk_amount
            
            trade.status = 'CLOSED'
            trade.actual_exit_price = exit_price
            trade.actual_pnl = actual_pnl
            trade.exit_reason = exit_reason
            trade.exited_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Trade {trade.id} closed: {trade.symbol} {trade.action} "
                       f"PnL: ${actual_pnl:.2f} ({leveraged_pnl:.1f}%) - {exit_reason}")
            
        except Exception as e:
            logger.error(f"Error closing trade {trade.id}: {e}")
            db.session.rollback()
    
    def _get_current_price(self, symbol):
        """Get current price for symbol"""
        try:
            prices = self.market_client.get_real_time_prices()
            if prices and symbol in prices:
                return prices[symbol].get('price')
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
        return None
    
    def get_trade_summary(self):
        """Get complete trading performance summary"""
        try:
            all_trades = TradeRecommendation.query.all()
            active_trades = TradeRecommendation.query.filter_by(status='ACTIVE').all()
            closed_trades = TradeRecommendation.query.filter_by(status='CLOSED').all()
            
            total_pnl = sum(trade.actual_pnl for trade in closed_trades if trade.actual_pnl)
            winning_trades = [t for t in closed_trades if t.actual_pnl and t.actual_pnl > 0]
            losing_trades = [t for t in closed_trades if t.actual_pnl and t.actual_pnl < 0]
            
            win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
            
            return {
                'total_recommendations': len(all_trades),
                'active_trades': len(active_trades),
                'closed_trades': len(closed_trades),
                'total_pnl': total_pnl,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'avg_win': sum(t.actual_pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
                'avg_loss': sum(t.actual_pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting trade summary: {e}")
            return {}
    
    def get_recent_trades(self, limit=10):
        """Get recent trade recommendations"""
        try:
            trades = TradeRecommendation.query.order_by(
                TradeRecommendation.recommended_at.desc()
            ).limit(limit).all()
            
            return [trade.to_dict() for trade in trades]
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []