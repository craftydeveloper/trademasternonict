from datetime import datetime
from app import db
from sqlalchemy import func

class TokenPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    mint_address = db.Column(db.String(44), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume_24h = db.Column(db.Float, default=0.0)
    price_change_24h = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'mint_address': self.mint_address,
            'price': self.price,
            'volume_24h': self.volume_24h,
            'price_change_24h': self.price_change_24h,
            'timestamp': self.timestamp.isoformat()
        }

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='Default Portfolio')
    initial_balance = db.Column(db.Float, nullable=False, default=10000.0)
    current_balance = db.Column(db.Float, nullable=False, default=10000.0)
    total_pnl = db.Column(db.Float, default=0.0)
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    positions = db.relationship('Position', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_pnl': self.total_pnl,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    mint_address = db.Column(db.String(44), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    avg_entry_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'mint_address': self.mint_address,
            'quantity': self.quantity,
            'avg_entry_price': self.avg_entry_price,
            'current_price': self.current_price,
            'market_value': self.quantity * self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'pnl_percentage': (self.unrealized_pnl / (self.quantity * self.avg_entry_price) * 100) if self.quantity > 0 else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    mint_address = db.Column(db.String(44), nullable=False)
    side = db.Column(db.String(4), nullable=False)  # 'BUY' or 'SELL'
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    pnl = db.Column(db.Float, default=0.0)
    strategy = db.Column(db.String(50), default='manual')
    status = db.Column(db.String(20), default='filled')  # filled, pending, cancelled
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'mint_address': self.mint_address,
            'side': self.side,
            'quantity': self.quantity,
            'price': self.price,
            'total_value': self.total_value,
            'fee': self.fee,
            'pnl': self.pnl,
            'strategy': self.strategy,
            'status': self.status,
            'executed_at': self.executed_at.isoformat()
        }

class TradingStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    strategy_type = db.Column(db.String(50), nullable=False)  # 'sma_crossover', 'rsi_oversold', etc.
    parameters = db.Column(db.Text)  # JSON string of strategy parameters
    is_active = db.Column(db.Boolean, default=True)
    position_size = db.Column(db.Float, default=100.0)  # USD amount per trade
    max_risk_per_trade = db.Column(db.Float, default=2.0)  # percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'strategy_type': self.strategy_type,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'position_size': self.position_size,
            'max_risk_per_trade': self.max_risk_per_trade,
            'created_at': self.created_at.isoformat()
        }

class SignalHistory(db.Model):
    """Track all signals issued by the system for history view"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    action = db.Column(db.String(10), nullable=False)  # 'LONG', 'SHORT', 'HOLD'
    entry_price = db.Column(db.Float, nullable=False)
    score = db.Column(db.Float, nullable=False)
    htf_trend = db.Column(db.String(20))
    liquidity_sweep = db.Column(db.Boolean, default=False)
    structure_shift = db.Column(db.String(20))
    confidence = db.Column(db.Float, default=0.0)
    analysis_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'score': self.score,
            'htf_trend': self.htf_trend,
            'liquidity_sweep': self.liquidity_sweep,
            'structure_shift': self.structure_shift,
            'confidence': self.confidence,
            'analysis_details': self.analysis_details,
            'created_at': self.created_at.isoformat()
        }


class TradeRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(4), nullable=False)  # 'BUY' or 'SELL'
    entry_price = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    leverage = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    risk_amount = db.Column(db.Float, nullable=False)
    expected_return = db.Column(db.Float, nullable=False)
    strategy_basis = db.Column(db.String(100), nullable=False)
    
    # Trade tracking
    status = db.Column(db.String(20), default='RECOMMENDED')  # RECOMMENDED, ACTIVE, CLOSED, CANCELLED
    actual_entry_price = db.Column(db.Float)
    actual_exit_price = db.Column(db.Float)
    actual_pnl = db.Column(db.Float)
    exit_reason = db.Column(db.String(50))  # 'TAKE_PROFIT', 'STOP_LOSS', 'MANUAL'
    
    # Timestamps
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow)
    entered_at = db.Column(db.DateTime)
    exited_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'confidence': self.confidence,
            'risk_amount': self.risk_amount,
            'expected_return': self.expected_return,
            'strategy_basis': self.strategy_basis,
            'status': self.status,
            'actual_entry_price': self.actual_entry_price,
            'actual_exit_price': self.actual_exit_price,
            'actual_pnl': self.actual_pnl,
            'exit_reason': self.exit_reason,
            'recommended_at': self.recommended_at.isoformat(),
            'entered_at': self.entered_at.isoformat() if self.entered_at else None,
            'exited_at': self.exited_at.isoformat() if self.exited_at else None,
            'updated_at': self.updated_at.isoformat()
        }
