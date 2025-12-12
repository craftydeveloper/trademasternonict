"""
Modern API routes for professional trading dashboard
"""
from flask import jsonify, request, render_template
from models import db, Portfolio, Position, Trade, TradeRecommendation
from fast_signals import FastSignalGenerator
from backup_data_provider import BackupDataProvider
from datetime import datetime, timedelta
import json

def register_modern_routes(app):
    """Register modern dashboard routes"""
    
    @app.route('/')
    def modern_dashboard():
        """Render the modern professional dashboard"""
        return render_template('dashboard_fixed.html')
    
    @app.route('/portfolio')
    def portfolio_page():
        """Render the portfolio management page"""
        return render_template('portfolio.html')
    
    @app.route('/analysis')
    def analysis_page():
        """Render the analysis page"""
        return render_template('professional_dashboard.html')
    
    @app.route('/reports')
    def reports_page():
        """Render the comprehensive trade reports page"""
        return render_template('trade_reports_modern.html')
    
    @app.route('/settings')
    def settings_page():
        """Render the settings page"""
        return render_template('modern_dashboard.html')
    
    @app.route('/api/portfolio-summary')
    def api_portfolio_summary():
        """Get comprehensive portfolio summary"""
        try:
            # Get or create default portfolio
            portfolio = Portfolio.query.first()
            if not portfolio:
                portfolio = Portfolio()
                db.session.add(portfolio)
                db.session.commit()
                # Update with correct values after creation
                portfolio.name = 'Main Portfolio'
                portfolio.initial_balance = 50.0
                portfolio.current_balance = 50.0
                db.session.commit()
            
            # Calculate current positions value
            positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
            total_position_value = 0
            unrealized_pnl = 0
            
            # Get current market data for position valuation
            data_provider = BackupDataProvider()
            market_data = data_provider.get_market_data()
            
            for position in positions:
                if market_data and position.symbol in market_data:
                    current_price = market_data[position.symbol]['price']
                    position_value = position.quantity * current_price
                    position_pnl = (current_price - position.avg_entry_price) * position.quantity
                    
                    total_position_value += position_value
                    unrealized_pnl += position_pnl
            
            # Get trade statistics
            trades = Trade.query.filter_by(portfolio_id=portfolio.id).all()
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t.pnl > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate total balance including positions
            total_balance = portfolio.current_balance + total_position_value
            total_pnl = total_balance - portfolio.initial_balance
            total_pnl_percentage = (total_pnl / portfolio.initial_balance * 100) if portfolio.initial_balance > 0 else 0
            
            return jsonify({
                'success': True,
                'total_balance': total_balance,
                'current_balance': portfolio.current_balance,
                'initial_balance': portfolio.initial_balance,
                'total_pnl': total_pnl,
                'total_pnl_percentage': total_pnl_percentage,
                'unrealized_pnl': unrealized_pnl,
                'realized_pnl': portfolio.total_pnl,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'active_positions': len(positions),
                'last_updated': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"Error in portfolio summary: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'total_balance': 50.0,
                'total_pnl': 0.0,
                'total_pnl_percentage': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0.0,
                'active_positions': 0
            })
    
    @app.route('/api/trading-signals')
    def api_trading_signals():
        """Get current trading signals"""
        try:
            # Get market data
            data_provider = BackupDataProvider()
            market_data = data_provider.get_market_data()
            
            if not market_data:
                return jsonify({
                    'success': False,
                    'error': 'Unable to retrieve market data',
                    'signals': []
                })
            
            # Generate signals
            signal_generator = FastSignalGenerator()
            signals = signal_generator.generate_fast_signals(market_data)
            
            # Convert signals to API format
            api_signals = []
            for signal in signals:
                api_signals.append({
                    'symbol': signal.get('symbol', ''),
                    'action': signal.get('action', 'HOLD'),
                    'entry_price': signal.get('entry_price', 0),
                    'stop_loss': signal.get('stop_loss', 0),
                    'take_profit': signal.get('take_profit', 0),
                    'leverage': signal.get('leverage', 1),
                    'confidence': signal.get('confidence', 0),
                    'risk_reward_ratio': signal.get('risk_reward_ratio', 1.0),
                    'strategy': signal.get('strategy', 'Technical Analysis'),
                    'timeframe': '1H',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            return jsonify({
                'success': True,
                'signals': api_signals,
                'count': len(api_signals),
                'last_updated': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"Error generating signals: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'signals': []
            })
    
    @app.route('/api/market-overview')
    def api_market_overview():
        """Get market overview data"""
        try:
            data_provider = BackupDataProvider()
            market_data = data_provider.get_market_data()
            
            if not market_data:
                return jsonify({
                    'success': False,
                    'error': 'Market data unavailable'
                })
            
            # Calculate market metrics
            total_volume = sum(data.get('volume_24h', 0) for data in market_data.values())
            avg_change = sum(data.get('change_24h', 0) for data in market_data.values()) / len(market_data)
            
            # Determine market sentiment
            positive_changes = len([d for d in market_data.values() if d.get('change_24h', 0) > 0])
            market_sentiment = 'Bullish' if positive_changes > len(market_data) / 2 else 'Bearish'
            
            return jsonify({
                'success': True,
                'market_sentiment': market_sentiment,
                'total_volume_24h': total_volume,
                'average_change_24h': avg_change,
                'active_pairs': len(market_data),
                'last_updated': datetime.utcnow().isoformat(),
                'pairs': [
                    {
                        'symbol': symbol,
                        'price': data.get('price', 0),
                        'change_24h': data.get('change_24h', 0),
                        'volume_24h': data.get('volume_24h', 0)
                    }
                    for symbol, data in market_data.items()
                ]
            })
            
        except Exception as e:
            print(f"Error in market overview: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @app.route('/api/recent-trades')
    def api_recent_trades():
        """Get recent trade history"""
        try:
            limit = request.args.get('limit', 10, type=int)
            
            trades = Trade.query.order_by(Trade.executed_at.desc()).limit(limit).all()
            
            trades_data = []
            for trade in trades:
                trades_data.append({
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'quantity': trade.quantity,
                    'price': trade.price,
                    'total_value': trade.total_value,
                    'pnl': trade.pnl,
                    'status': trade.status,
                    'executed_at': trade.executed_at.isoformat() if trade.executed_at else None
                })
            
            return jsonify({
                'success': True,
                'trades': trades_data,
                'count': len(trades_data)
            })
            
        except Exception as e:
            print(f"Error getting recent trades: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'trades': []
            })
    
    @app.route('/api/active-positions')
    def api_active_positions():
        """Get active trading positions"""
        try:
            positions = Position.query.all()
            
            # Get current market data for position valuation
            data_provider = BackupDataProvider()
            market_data = data_provider.get_market_data()
            
            positions_data = []
            for position in positions:
                current_price = 0
                unrealized_pnl = 0
                
                if market_data and position.symbol in market_data:
                    current_price = market_data[position.symbol]['price']
                    unrealized_pnl = (current_price - position.avg_entry_price) * position.quantity
                
                positions_data.append({
                    'id': position.id,
                    'symbol': position.symbol,
                    'quantity': position.quantity,
                    'avg_entry_price': position.avg_entry_price,
                    'current_price': current_price,
                    'unrealized_pnl': unrealized_pnl,
                    'created_at': position.created_at.isoformat() if position.created_at else None
                })
            
            return jsonify({
                'success': True,
                'positions': positions_data,
                'count': len(positions_data)
            })
            
        except Exception as e:
            print(f"Error getting positions: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'positions': []
            })
    
    @app.route('/api/performance-chart')
    def api_performance_chart():
        """Get portfolio performance chart data"""
        try:
            days = request.args.get('days', 30, type=int)
            
            # Get trades from the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            trades = Trade.query.filter(Trade.executed_at >= start_date).order_by(Trade.executed_at).all()
            
            # Calculate daily portfolio values
            portfolio = Portfolio.query.first()
            if not portfolio:
                return jsonify({
                    'success': False,
                    'error': 'No portfolio found'
                })
            
            chart_data = []
            running_balance = portfolio.initial_balance
            current_date = start_date
            
            # Generate daily data points
            for i in range(days):
                day_trades = [t for t in trades if t.executed_at.date() == current_date.date()]
                
                # Add PnL from trades on this day
                daily_pnl = sum(t.pnl for t in day_trades)
                running_balance += daily_pnl
                
                chart_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'value': running_balance,
                    'change': daily_pnl
                })
                
                current_date += timedelta(days=1)
            
            return jsonify({
                'success': True,
                'chart_data': chart_data,
                'initial_value': portfolio.initial_balance,
                'current_value': running_balance,
                'total_change': running_balance - portfolio.initial_balance,
                'period_days': days
            })
            
        except Exception as e:
            print(f"Error generating chart data: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'chart_data': []
            })